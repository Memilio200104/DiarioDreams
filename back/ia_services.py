import os
import json
import numpy as np
import openai
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from back.database_manager import DatabaseManager
load_dotenv()

class IAService:
    EMOTION_CATEGORIES = ["Alegría", "Tristeza", "Miedo", "Ira", "Calma"]

    def __init__(self):
        try:
            self.client = openai.OpenAI(api_key=os.environ.get("OPENAI_5ECRET_K3Y"))
            self.model = "gpt-4o"
            print("IAService: Conexión con OpenAI establecida.")

            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            print("IAService: Modelo de Embeddings cargado.")

            self.db_manager = DatabaseManager()
            print("IAService: DatabaseManager inicializado.")

        except Exception as e:
            print(f"Error al inicializar IA o DB: {e}")
            self.client = None
            self.embedder = None
            self.db_manager = None

    def analyze_emotion(self, dream_text: str) -> str:
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
                temperature=0.1
            )
            emotion = response.choices[0].message.content.strip()
            if emotion in self.EMOTION_CATEGORIES:
                return emotion
            else:
                for valid_emotion in self.EMOTION_CATEGORIES:
                    if valid_emotion.lower() in emotion.lower():
                        return valid_emotion
                return "Indefinida"

        except Exception as e:
            print(f"Error en análisis de IA: {e}")
            return "Error_IA"

    def generate_creative(self, dream_text: str, format: str) -> str:
        if not self.client:
            return "Error de conexión con la IA."

        fmt = format.lower().strip()
        if fmt == 'poema':
            task = "Escribe un poema lírico y reflexivo de 8-10 líneas"
        elif fmt == 'historia corta':
            task = "Escribe una historia corta y surrealista de 150 palabras"
        elif fmt == 'guion corto':
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
                temperature=0.8
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error en generación creativa de IA: {e}")
            return f"Error en generación creativa de IA: {e}"

    def generate_embedding(self, text: str) -> np.ndarray:
        if not self.embedder:
            return None
        return self.embedder.encode(text)
    
    def generate_analysis(self, dream_text: str) -> str:
        if not self.client:
            return "Error de conexión con la IA."

        prompt = (
            "Eres un intérprete de sueños profesional y conciso. "
            "Lee el siguiente texto de un sueño y devuelve: (1) una lista corta de símbolos importantes (máx 6), "
            "(2) una interpretación clara y breve del significado emocional o temático (10 - 40 oraciones), "
            "y (3) un consejo práctico o reflexión para la persona (1 oración). "
            "Responde en formato JSON con claves: symbols, interpretation, advice. "
            f"Texto del sueño: '''{dream_text}'''"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres experto en interpretación de sueños, claro y empático."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.6
            )
            content = response.choices[0].message.content.strip()
            return content
        except Exception as e:
            print(f"Error en generate_analysis: {e}")
            return f"Error en generación de análisis: {e}"

    def process_and_save_dream(self, title: str, content: str, format: str):
        if not self.db_manager:
            return "Error: Gestor de Base de Datos no inicializado.", "", ""

        emotion = self.analyze_emotion(content)

        creative_output = self.generate_creative(content, format)

        analysis_output = self.generate_analysis(content)

        embedding = self.generate_embedding(content)
        
        save_success = self.db_manager.save_dream(title, content, emotion, embedding, creative_text=creative_output, creative_format=format, analysis_text=analysis_output)

        if not save_success:
            return "Error al guardar sueño en la BD.", creative_output, analysis_output

        return emotion, creative_output, analysis_output
    def get_visual_metrics(self):
        if not self.db_manager:
            return "Error: DB no disponible.", "", ""

        data = self.db_manager.fetch_metrics_data()
        
        if not data:
            return "No hay sueños registrados.", "", ""

        emotion_counts = {e: 0 for e in self.EMOTION_CATEGORIES}
        full_text = []
        
        for item in data:
            emotion = item['emotion']
            if emotion in self.EMOTION_CATEGORIES:
                emotion_counts[emotion] += 1
            full_text.append(item['content'])
            
        evolution_data = [(item['date'], item['emotion']) for item in data]
        
        wordcloud_text = " ".join(full_text)
        
        return emotion_counts, evolution_data, wordcloud_text
