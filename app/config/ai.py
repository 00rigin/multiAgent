from langchain_openai import ChatOpenAI

from app.config.settings import settings

EMBEDDING_MODEL_NAME = 'GPT-4o'

openai_chat = ChatOpenAI(
    api_key = settings.OPENAI_KEY
)