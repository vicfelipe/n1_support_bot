import spacy
from typing import Tuple, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class NLPService:
    def __init__(self):
        try:
            # Carregar modelo spaCy para português
            self.nlp = spacy.load("pt_core_news_sm")
            logger.info("Modelo spaCy carregado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo spaCy: {str(e)}")
            # Fallback para modelo menor se o grande não estiver disponível
            try:
                self.nlp = spacy.load("pt_core_news_sm")
                logger.info("Modelo spaCy (pequeno) carregado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao carregar modelo spaCy (pequeno): {str(e)}")
                # Criar um modelo vazio como último recurso
                self.nlp = spacy.blank("pt")
                logger.warning("Usando modelo spaCy vazio")
    
    def analyze_text(self, text: str) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Analisa o texto para identificar intenção e entidades
        
        Args:
            text: Texto a ser analisado
        
        Returns:
            Tupla contendo (intenção, entidades)
        """
        try:
            # Processar o texto com spaCy
            doc = self.nlp(text)
            
            # Identificar intenção
            intent = self._identify_intent(doc)
            
            # Extrair entidades
            entities = self._extract_entities(doc)
            
            return intent, entities
        except Exception as e:
            logger.error(f"Erro ao analisar texto: {str(e)}")
            return "unknown", None
    
    def _identify_intent(self, doc) -> str:
        """
        Identifica a intenção do usuário com base no texto processado
        
        Args:
            doc: Documento spaCy processado
        
        Returns:
            String representando a intenção identificada
        """
        # Palavras-chave para cada intenção
        intent_keywords = {
            "password_reset": ["senha", "password", "esqueci", "redefinir", "resetar", "trocar senha"],
            "connection_issue": ["internet", "conexão", "rede", "wifi", "wi-fi", "cabo", "ethernet"],
            "printer_issue": ["impressora", "imprimir", "scanner", "digitalizar", "toner", "cartucho"],
            "email_issue": ["email", "e-mail", "correio", "outlook", "gmail", "mensagem"],
            "performance_issue": ["lento", "travando", "performance", "desempenho", "congelando"],
            "general_inquiry": ["ajuda", "suporte", "informações", "informação", "dúvida", "duvida"],
            "ticket": ["ticket", "chamado", "suporte", "suporte técnico"],
        }
        
        # Contar ocorrências de palavras-chave para cada intenção
        intent_scores = {intent: 0 for intent in intent_keywords}
        
        # Texto normalizado para comparação
        text_lower = doc.text.lower()
        
        for intent, keywords in intent_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    intent_scores[intent] += 1
        
        # Verificar verbos e contexto para refinar a intenção
        for token in doc:
            if token.pos_ == "VERB":
                verb = token.lemma_.lower()
                
                # Verbos relacionados a problemas
                problem_verbs = ["quebrar", "falhar", "parar", "travar", "congelar"]
                if verb in problem_verbs:
                    # Verificar o objeto do verbo para determinar o tipo de problema
                    for child in token.children:
                        if child.dep_ in ["dobj", "obj", "obl"]:
                            obj_text = child.text.lower()
                            
                            if obj_text in ["impressora", "scanner"]:
                                intent_scores["printer_issue"] += 2
                            elif obj_text in ["internet", "rede", "wifi", "conexão"]:
                                intent_scores["connection_issue"] += 2
                            elif obj_text in ["email", "e-mail", "mensagem"]:
                                intent_scores["email_issue"] += 2
                            elif obj_text in ["computador", "pc", "notebook", "laptop"]:
                                intent_scores["performance_issue"] += 2
        
        # Determinar a intenção com maior pontuação
        if any(intent_scores.values()):
            max_intent = max(intent_scores, key=intent_scores.get)
            return max_intent
        else:
            return "general_inquiry"  # Intenção padrão se nenhuma for identificada
    
    def _extract_entities(self, doc) -> Dict[str, Any]:
        """
        Extrai entidades relevantes do texto processado
        
        Args:
            doc: Documento spaCy processado
        
        Returns:
            Dicionário com as entidades extraídas
        """
        entities = {}
        
        # Extrair entidades reconhecidas pelo spaCy
        for ent in doc.ents:
            if ent.label_ == "PER":
                entities["person"] = ent.text
            elif ent.label_ == "ORG":
                entities["organization"] = ent.text
            elif ent.label_ == "LOC":
                entities["location"] = ent.text
        
        # Extrair números que podem ser identificações de equipamentos
        equipment_patterns = [
            # Padrão para etiquetas de patrimônio (ex: PAT12345, EQ-5678)
            r"(PAT|EQ|EQUIP)[\-]?\d+",
            # Padrão para números de série
            r"S\/N[\:\s]?[A-Z0-9]+",
            # Padrão para endereços MAC
            r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})"
        ]
        
        # Buscar padrões de equipamentos no texto
        import re
        for pattern in equipment_patterns:
            matches = re.findall(pattern, doc.text)
            if matches:
                entities["equipment"] = matches[0]  # Pegar o primeiro match
                break
        
        # Extrair números de sala ou localização
        room_patterns = [
            r"sala\s+\d+",
            r"laboratório\s+\d+",
            r"lab\s+\d+",
            r"andar\s+\d+"
        ]
        
        for pattern in room_patterns:
            matches = re.findall(pattern, doc.text.lower())
            if matches:
                entities["room"] = matches[0]
                break
        
        return entities