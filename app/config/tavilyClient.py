from tavily import TavilyClient
from app.config.settings import settings

tavilyClient = TavilyClient(
    api_key=settings.TAVILY_API_KEY
)