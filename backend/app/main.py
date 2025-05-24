from uuid import uuid4
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json

# Importando serviços
from app.services.ocomon_service import OcomonService
from app.services.nlp_service import NLPService
from app.models.message import Message, MessageType
from app.models.conversation import Conversation

app = FastAPI(title="N1 Support Bot API")

# Configuração de CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens exatas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialização dos serviços
ocomon_service = OcomonService(
    base_url=os.getenv("OCOMON_API_URL"),
    app=os.getenv("OCOMON_APP"),
    login=os.getenv("OCOMON_LOGIN"),
    token=os.getenv("OCOMON_TOKEN")
)

nlp_service = NLPService()

# Armazenamento temporário de conversas (em produção, usar banco de dados)
conversations: Dict[str, Conversation] = {}

# Modelos de dados para API
class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    conversation_id: str
    messages: List[Dict[str, Any]]
    ticket_number: Optional[str] = None

bot_name = os.getenv("BOT_NAME", "Lulu")

@app.get("/")
async def read_root():
    return {"status": "online", "service": "N1 Support Bot API"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    user_id = request.user_id
    user_message = request.message
    
    # Verificar se já existe uma conversa para este usuário
    if user_id not in conversations:
        # Criar nova conversa
        conversations[user_id] = Conversation(user_id=user_id)
    
    # Adicionar mensagem do usuário à conversa
    conversations[user_id].add_message(
        Message(
            id=uuid4(),
            content=user_message,
            type=MessageType.USER
        )
    )
    
    # Processar a mensagem do usuário com NLP
    intent, entities = nlp_service.analyze_text(user_message)
    
    # Buscar solução na base de conhecimento do OCOMON
    knowledge_results = ocomon_service.search_knowledge_base(user_message)
    
    # Verificar se encontrou solução
    if knowledge_results and knowledge_results.get("solutions"):
        # Apresentar solução encontrada
        solution = knowledge_results["solutions"][0]  # Pegar a primeira solução
        bot_response = f"Encontrei uma possível solução para o seu problema: {solution['title']}\n\n{solution['description']}"
        
        # Adicionar mensagem do bot à conversa
        conversations[user_id].add_message(
            Message(
                id=uuid4(),
                content=bot_response,
                type=MessageType.BOT
            )
        )
        
        # Perguntar se a solução resolveu o problema
        conversations[user_id].add_message(
            Message(
                id=uuid4(),
                content="Esta solução resolveu o seu problema?",
                type=MessageType.BOT
            )
        )
        
        # Marcar que estamos esperando confirmação
        conversations[user_id].waiting_for_confirmation = True
    else:
        # Não encontrou solução, criar ticket
        ticket_data = {
            "description": user_message,
            "contact": user_id,
            "contact_email": f"{user_id}@example.com",  # Exemplo, ajustar conforme necessário
            "channel": 1  # Canal para chatbot
        }
        
        # Adicionar entidades identificadas pelo NLP ao ticket
        if entities:
            for entity, value in entities.items():
                if entity == "equipment" and value:
                    ticket_data["asset_tag"] = value
                # Adicionar outras entidades conforme necessário
        
        # Criar ticket no OCOMON
        ticket_result = ocomon_service.create_ticket(ticket_data)
        
        if ticket_result and ticket_result.get("ticket"):
            ticket_number = ticket_result.get("ticket", {}).get("numero")
            conversations[user_id].ticket_number = ticket_number
            
            # Informar ao usuário que o ticket foi criado
            bot_response = f"Não encontrei uma solução imediata para o seu problema. Criei um ticket de suporte com o número {ticket_number}. Um técnico entrará em contato em breve."
        else:
            # Erro ao criar ticket
            bot_response = "Desculpe, não consegui encontrar uma solução e houve um problema ao criar um ticket. Por favor, tente novamente mais tarde ou entre em contato diretamente com o suporte."
        
        # Adicionar mensagem do bot à conversa
        conversations[user_id].add_message(
            Message(
                id=uuid4(),
                content=bot_response,
                type=MessageType.BOT
            )
        )
    
    # Retornar a conversa atualizada
    return {
        "conversation_id": user_id,
        "messages": [msg.dict() for msg in conversations[user_id].messages],
        "ticket_number": conversations[user_id].ticket_number
    }

@app.post("/feedback")
async def feedback(request: ChatRequest):
    user_id = request.user_id
    feedback_message = request.message.lower()
    
    if user_id not in conversations or not conversations[user_id].waiting_for_confirmation:
        raise HTTPException(status_code=400, detail="Nenhuma confirmação pendente para esta conversa")
    
    # Resetar flag de confirmação
    conversations[user_id].waiting_for_confirmation = False
    
    # Adicionar mensagem do usuário à conversa
    conversations[user_id].add_message(
        Message(
            id=uuid4(),
            content=feedback_message,
            type=MessageType.USER
        )
    )
    
    # Verificar se a solução resolveu o problema
    if "sim" in feedback_message or "resolveu" in feedback_message or "funcionou" in feedback_message:
        # Registrar sucesso
        bot_response = "Ótimo! Fico feliz em saber que conseguimos resolver o seu problema. Se precisar de mais alguma coisa, é só me chamar."
        
        # TODO: Registrar feedback positivo para melhorar o sistema
    else:
        # Criar ticket, pois a solução não resolveu
        last_user_message = next((msg.content for msg in reversed(conversations[user_id].messages) 
                                if msg.type == MessageType.USER and msg.content != feedback_message), "")
        
        ticket_data = {
            "description": f"Problema não resolvido com solução sugerida. Descrição original: {last_user_message}",
            "contact": user_id,
            "contact_email": f"{user_id}@example.com",  # Exemplo, ajustar conforme necessário
            "channel": 1  # Canal para chatbot
        }
        
        # Criar ticket no OCOMON
        ticket_result = ocomon_service.create_ticket(ticket_data)
        
        if ticket_result and ticket_result.get("ticket"):
            ticket_number = ticket_result.get("ticket", {}).get("numero")
            conversations[user_id].ticket_number = ticket_number
            
            # Informar ao usuário que o ticket foi criado
            bot_response = f"Lamento que a solução não tenha resolvido o seu problema. Criei um ticket de suporte com o número {ticket_number}. Um técnico entrará em contato em breve."
        else:
            # Erro ao criar ticket
            bot_response = f"Desculpe, houve um problema ao criar um ticket. Por favor, tente novamente mais tarde ou entre em contato diretamente com o suporte. {ticket_result}"
    
    # Adicionar mensagem do bot à conversa
    conversations[user_id].add_message(
        Message(
            id=uuid4(),
            content=bot_response,
            type=MessageType.BOT
        )
    )
    
    # Retornar a conversa atualizada
    return {
        "conversation_id": user_id,
        "messages": [msg.dict() for msg in conversations[user_id].messages],
        "ticket_number": conversations[user_id].ticket_number
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)