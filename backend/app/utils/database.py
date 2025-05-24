import mysql.connector
import os
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """
        Estabelece conexão com o banco de dados MariaDB
        """
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "ocomon_6"),
                password=os.getenv("DB_PASSWORD", "senha_ocomon_mysql"),
                database=os.getenv("DB_NAME", "ocomon")
            )
            logger.info("Conexão com o banco de dados estabelecida com sucesso")
        except mysql.connector.Error as e:
            logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[List[Dict[str, Any]]]:
        """
        Executa uma consulta SQL e retorna os resultados
        
        Args:
            query: Consulta SQL a ser executada
            params: Parâmetros para a consulta (opcional)
        
        Returns:
            Lista de dicionários com os resultados ou None em caso de erro
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
                if not self.connection or not self.connection.is_connected():
                    return None
            
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            cursor.close()
            return results
        except mysql.connector.Error as e:
            logger.error(f"Erro ao executar consulta: {str(e)}")
            return None
    
    def execute_update(self, query: str, params: tuple = None) -> bool:
        """
        Executa uma operação de atualização (INSERT, UPDATE, DELETE) no banco de dados
        
        Args:
            query: Consulta SQL a ser executada
            params: Parâmetros para a consulta (opcional)
        
        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
                if not self.connection or not self.connection.is_connected():
                    return False
            
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows > 0
        except mysql.connector.Error as e:
            logger.error(f"Erro ao executar atualização: {str(e)}")
            return False
    
    def close(self):
        """
        Fecha a conexão com o banco de dados
        """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Conexão com o banco de dados fechada")

# Singleton para acesso ao banco de dados
db = Database()