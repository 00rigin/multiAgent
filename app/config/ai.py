from openai import OpenAI
from app.config.settings import settings

EMBEDDING_MODEL_NAME = 'GPT-4o'

openai_chat = OpenAI(
    api_key = settings.OPENAI_KEY
)