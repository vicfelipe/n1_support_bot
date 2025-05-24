import requests
import json
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class OcomonService:
    def __init__(self, base_url: str, app: str, login: str, token: str):
        self.base_url = base_url
        self.headers = {
            "app": app,
            "login": login,
            "token": token,
            "Content-Type": "application/x-www-form-urlencoded"
        }
    
    def create_ticket(self, ticket_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Cria um ticket no OCOMON
        
        Args:
            ticket_data: Dicionário com os dados do ticket
                - description (obrigatório): Descrição do chamado
                - area (opcional): código válido de área de atendimento
                - contact (opcional): campo contato
                - contact_email (opcional): campo e-mail do contato
                - phone (opcional): campo de telefone do contato
                - issue (opcional): código válido de tipo de problema
                - status (opcional): código válido de tipo de status
                - asset_unit (opcional): código válido de unidade
                - asset_tag (opcional): número/identificação da etiqueta do equipamento
                - priority (opcional): código válido de prioridade
                - input_tag (opcional): rótulos/tags que serão incorporados ao chamado
                - operator (opcional): código válido de operador
                - channel (opcional): código válido de canal de solicitação
        
        Returns:
            Dicionário com os dados do ticket criado ou None em caso de erro
        """
        try:
            url = f"{self.base_url}/tickets/"
            response = requests.post(url, headers=self.headers, data=ticket_data)
            
            if response.status_code >= 200 & response.status_code <= 299:
                return response.json()
            else:
                logger.error(f"Erro ao criar ticket: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Exceção ao criar ticket: {str(e)}")
            return None
    
    def get_ticket(self, ticket_number: str) -> Optional[Dict[str, Any]]:
        """
        Obtém os detalhes de um ticket no OCOMON
        
        Args:
            ticket_number: Número do ticket
        
        Returns:
            Dicionário com os dados do ticket ou None em caso de erro
        """
        try:
            url = f"{self.base_url}/tickets/{ticket_number}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao obter ticket: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Exceção ao obter ticket: {str(e)}")
            return None
    
    def search_knowledge_base(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Busca soluções na base de conhecimento do OCOMON
        
        Args:
            query: Texto para busca
        
        Returns:
            Dicionário com as soluções encontradas ou None em caso de erro
        """
        try:
            # Simulação de busca na base de conhecimento
            # Em um ambiente real, seria necessário implementar a integração com a API de busca do OCOMON
            # Esta é uma implementação de exemplo que retorna dados fictícios
            
            # Palavras-chave para simular resultados
            keywords = {
                "senha": {
                    "title": "Redefinição de senha",
                    "description": "Para redefinir sua senha, acesse o portal de autoatendimento em https://portal.example.com e clique em 'Esqueci minha senha'. Siga as instruções enviadas para seu e-mail."
                },
                "internet": {
                    "title": "Problemas de conexão com a internet",
                    "description": "1. Verifique se o cabo de rede está conectado corretamente.\n2. Reinicie o roteador/modem desligando-o por 30 segundos e ligando novamente.\n3. Verifique se o Wi-Fi está ativado no seu dispositivo.\n4. Tente conectar outro dispositivo para verificar se o problema é específico."
                },
                "impressora": {
                    "title": "Problemas com impressora",
                    "description": "1. Verifique se a impressora está ligada e conectada à rede.\n2. Verifique se há papel na bandeja e se não há papel preso.\n3. Reinicie a impressora.\n4. Reinstale o driver da impressora seguindo as instruções em https://suporte.example.com/drivers."
                },
                "email": {
                    "title": "Problemas com e-mail",
                    "description": "1. Verifique se você está conectado à internet.\n2. Confirme se seu nome de usuário e senha estão corretos.\n3. Verifique as configurações de servidor de entrada e saída.\n4. Limpe o cache do seu aplicativo de e-mail ou navegador."
                },
                "lento": {
                    "title": "Computador lento",
                    "description": "1. Reinicie o computador.\n2. Verifique programas que iniciam automaticamente (use o Gerenciador de Tarefas no Windows).\n3. Execute uma verificação de vírus.\n4. Limpe arquivos temporários usando o Limpador de Disco.\n5. Considere adicionar mais memória RAM se o problema persistir."
                }
            }
            
            # Busca por palavras-chave no texto da consulta
            results = []
            for keyword, solution in keywords.items():
                if keyword.lower() in query.lower():
                    results.append(solution)
            
            if results:
                return {"solutions": results}
            else:
                return None
        except Exception as e:
            logger.error(f"Exceção ao buscar na base de conhecimento: {str(e)}")
            return None