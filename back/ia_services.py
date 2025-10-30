import os
import openai
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import numpy as np

# Carga las variables de entorno desde .env
load_dotenv() 

class IAService:
    """
    Clase de servicio que maneja la lógica del Back-End
    y las interacciones con la API de OpenAI y los modelos de PLN.
    """
    # 5 Categorías emocionales basadas en el requisito de al menos 5 categorías
    EMOTION_CATEGORIES = ["Alegría", "Tristeza", "Miedo", "Ira", "Calma"]

    def __init__(self):
        try:
            # Inicialización del cliente OpenAI
            self.client = openai.OpenAI(
                api_key=os.environ.get("OPENAI_5ECRET_K3Y")
            )
            # Define el modelo de IA a usar
            self.model = "gpt-4o" 
            print("IAService: Conexión con OpenAI establecida.")

            # Inicialización del modelo de Embeddings para Búsqueda Semántica
            # Usando all-MiniLM-L6-v2 como un modelo eficiente para embeddings semánticos.
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2') 
            print("IAService: Modelo de Embeddings cargado.")

        except Exception as e:
            print(f"Error al inicializar IA: {e}")
            self.client = None
            self.embedder = None


    def analyze_emotion(self, dream_text: str) -> str:
        """
        Detecta y etiqueta automáticamente la emoción principal del sueño.
        """
        if not self.client:
            return "Error de conexión con la IA."
        
        system_prompt = (
            "Eres un analista de sueños profesional. Tu única tarea es leer el sueño "
            f"y clasificar la emoción principal que domina en el texto. "
            f"Debes responder ÚNICAMENTE con una de estas categorías: {', '.join(self.EMOTION_CATEGORIES)}."
            "No incluyas explicaciones ni texto adicional."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": dream_text}
                ],
                max_tokens=10,
                temperature=0.1 # Baja temperatura para clasificación precisa
            )
            emotion = response.choices[0].message.content.strip()
            
            # Validación de la respuesta
            if emotion in self.EMOTION_CATEGORIES:
                return emotion
            else:
                return "Indefinida" 

        except Exception as e:
            return f"Error en análisis de IA: {e}"


    def generate_creative(self, dream_text: str, format: str) -> str:
        """
        Transforma el sueño en un formato creativo (Poema, Historia o Guion).
        """
        if not self.client:
            return "Error de conexión con la IA."

        format = format.lower().strip()
        
        # Lógica de Prompt Engineering basada en el formato seleccionado
        if format == 'poema':
            task = "Escribe un poema lírico y reflexivo de 8-10 líneas"
        elif format == 'historia corta':
            task = "Escribe una historia corta y surrealista de 150 palabras"
        elif format == 'guion corto':
            task = "Escribe un guion corto (una escena de 1 minuto) con formato de diálogos y acciones"
        else:
            return "Formato creativo no soportado."
        
        prompt_user = (
            f"Basándote en el siguiente texto de un sueño: '{dream_text}', por favor, "
            f"{task} que capture la esencia y las emociones del sueño."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un artista y escritor creativo."},
                    {"role": "user", "content": prompt_user}
                ],
                max_tokens=500,
                temperature=0.8 # Alta temperatura para creatividad
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Error en generación creativa de IA: {e}"


    def generate_embedding(self, text: str) -> np.ndarray:
        """Genera el vector numérico (embedding) de un texto para la búsqueda semántica."""
        if not self.embedder:
            return None
        # Utiliza el modelo cargado para codificar el texto
        return self.embedder.encode(text)


    def semantic_search(self, query: str):
        """
        Lógica de Búsqueda Semántica. En el Sprint 3, esta función buscará en MySQL.
        """
        if not self.embedder:
             return "IAService: Error al cargar modelo de embeddings. Verifique la instalación de bibliotecas."

        # 1. Vectorizar la consulta del usuario
        query_embedding = self.generate_embedding(query)

        # 2. Búsqueda en MySQL (PENDIENTE - Sprint 3)
        # Aquí se llamará al DatabaseManager para obtener todos los embeddings de sueños
        # y se calculará la similitud coseno (o similar) para encontrar los más cercanos.
        
        return f"IAService: Búsqueda de '{query}' procesada. Vectorización exitosa. Requiere datos de MySQL para resultados (Sprint 3)."