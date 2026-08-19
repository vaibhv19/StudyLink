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
        api_key = getattr(settings, 'GEMINI_API_KEY', '')
        if not api_key:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("GEMINI_API_KEY is not configured. Falling back to dummy embedding.")
            return [0.0] * 768
            
        try:
            response = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            return response['embedding']
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("Gemini embedding generation failed: %s. Falling back to dummy embedding.", str(e))
            return [0.0] * 768

    @classmethod
    def generate_answer(cls, prompt):
        cls.configure()
        try:
            model = genai.GenerativeModel("models/gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text
        except GoogleAPIError as e:
            raise e
