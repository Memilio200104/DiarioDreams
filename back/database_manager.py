# ===== UPDATED: back/database_manager.py =====
import os
import json
import numpy as np
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.config = {
            'host': os.environ.get("MYSQL_HOST"),
            'user': os.environ.get("MYSQL_USER"),
            'password': os.environ.get("MYSQL_PASSWORD"),
            'database': os.environ.get("MYSQL_DATABASE"),
            'port': os.environ.get("MYSQL_PORT",)
        }
        self.connection = None
        self._ensure_database_and_table()

    def _ensure_database_and_table(self):
        temp_config = {k: v for k, v in self.config.items() if k != 'database'}
        try:
            conn = mysql.connector.connect(**temp_config)
            cursor = conn.cursor()

            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
            conn.database = self.config['database']

            create_table_query = """"""
            cursor.execute(create_table_query)
            conn.commit()
            cursor.close()
            conn.close()
            print(f"DatabaseManager: Base de datos y tabla '{self.config['database']}.dreams' listas.")

        except mysql.connector.Error as err:
            print(f"Error en _ensure_database_and_table: {err}")
            exit()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                return True
        except mysql.connector.Error as err:
            print(f"Error de conexión a MySQL: {err}")
            self.connection = None
            return False

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None
            
    def save_dream(self, title: str, content: str, emotion: str, embedding, creative_text: str = None, creative_format: str = None, analysis_text: str = None):
        if not self.connect():
            return False

        embedding_json = json.dumps(np.array(embedding).tolist()) if embedding is not None else json.dumps([])

        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO dreams (title, content, emotion_tag, creative_format, creative_text, analysis_text, embedding_vector)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            data = (title, content, emotion, creative_format, creative_text, analysis_text, embedding_json)
            cursor.execute(query, data)
            self.connection.commit()
            print(f"DatabaseManager: Sueño '{title}' guardado con ID: {cursor.lastrowid}")
            return True
        except mysql.connector.Error as err:
            print(f"Error al guardar sueño: {err}")
            self.connection.rollback()
            return False
        finally:
            self.close()

    def fetch_all_dreams(self) -> list:
        if not self.connect():
            return []
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT id, title, LEFT(content, 300) AS preview, date_recorded, emotion_tag, creative_format, LEFT(creative_text,300) AS creative_preview, LEFT(analysis_text,300) AS analysis_preview FROM dreams ORDER BY date_recorded DESC"
            cursor.execute(query)
            rows = [r for r in cursor]
            return rows
        except mysql.connector.Error as err:
            print(f"Error al recuperar sueños: {err}")
            return []
        finally:
            self.close()

    def fetch_dream_by_id(self, dream_id: int) -> dict:
        if not self.connect():
            return None
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT id, title, content, date_recorded, emotion_tag, creative_format, creative_text, analysis_text FROM dreams WHERE id = %s"
            cursor.execute(query, (dream_id,))
            row = cursor.fetchone()
            return row
        except mysql.connector.Error as err:
            print(f"Error al recuperar sueño por ID: {err}")
            return None
        finally:
            self.close()
    def fetch_metrics_data(self) -> list:
        if not self.connect(): return []
        
        results = []
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT date_recorded, emotion_tag, content FROM dreams ORDER BY date_recorded ASC"
            cursor.execute(query)

            results = [{
                'date': row['date_recorded'].isoformat(),
                'emotion': row['emotion_tag'],
                'content': row['content']
            } for row in cursor]
            
            return results

        except mysql.connector.Error as err:
            print(f"Error al recuperar datos para métricas: {err}")
            return []
        finally:
            self.close()

