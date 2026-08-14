import google.generativeai as genai
from django.conf import settings
from google.api_core.exceptions import GoogleAPIError

class GeminiClient:
    _configured = False

    @classmethod
    def configure(cls):
        if not cls._configured:
            api_key = getattr(settings, 'GEMINI_API_KEY', '')
            if api_key:
                genai.configure(api_key=api_key)
            cls._configured = True

    @classmethod
    def get_embedding(cls, text):
        cls.configure()
        try:
            response = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            return response['embedding']
        except GoogleAPIError as e:
            # Handle rate-limit or quota failures gracefully
            raise e

    @classmethod
    def generate_answer(cls, prompt):
        cls.configure()
        try:
            model = genai.GenerativeModel("models/gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text
        except GoogleAPIError as e:
            raise e
