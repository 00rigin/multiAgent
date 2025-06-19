from langchain_openai import ChatOpenAI

from app.config.settings import settings

EMBEDDING_MODEL_NAME = "gpt-4o-2024-08-06"

openai_chat = ChatOpenAI(
    api_key = settings.OPENAI_KEY,
    model=EMBEDDING_MODEL_NAME
) 