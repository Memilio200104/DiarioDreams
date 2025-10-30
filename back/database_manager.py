import os
from dotenv import load_dotenv
# pip install mysql-connector-python

load_dotenv() 

class DatabaseManager:
    """
    Clase que gestiona la conexión y las operaciones CRUD (Crear, Leer, Actualizar, Borrar)
    con el servidor MySQL.
    """
    def __init__(self):
        # NOTA: Los detalles de conexión (host, user, password, database) 
        # deben cargarse desde el .env y configurarse aquí en el Sprint 3. -Eix
        self.connection = None
        print("DatabaseManager: Inicializado. Conexión a MySQL pendiente (Sprint 3).")

    def connect(self):
        """Establece la conexión con la base de datos MySQL."""
        # Lógica de conexión real a MySQL se implementará en el Sprint 3
        try:
            # self.connection = mysql.connector.connect(...)
            pass
        except Exception as e:
            print(f"Error al conectar a MySQL: {e}")
            
    def close(self):
        if self.connection:
            self.connection.close()

    def save_dream(self, title: str, content: str, emotion: str, embedding: list):
        # Implementación SQL INSERT INTO... (Sprint 3)
        print(f"DatabaseManager: Guardando sueño '{title}' y su vector ({len(embedding)} dimensiones)...")

    def fetch_all_dreams(self):
        # Implementación SQL SELECT * FROM... (Sprint 3)
        return []

    def fetch_embeddings(self):
        # Implementación SQL SELECT id, embedding FROM... (Sprint 3)
        return []

    def fetch_dream_by_id(self, dream_id: int):
        # Implementación SQL SELECT * WHERE id=... (Sprint 3)
        return None