from pydantic_settings import BaseSettings

class LocalSettings(BaseSettings):
    OPENAI_KEY: str
    NAVER_CLIENT_ID: str
    NAVER_CLIENT_SECRET: str
    KAKAO_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def get_settings():
    return LocalSettings()

settings = get_settings()