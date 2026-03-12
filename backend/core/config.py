import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "OrbyTech API"
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = "orbytech_db"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Remote Execution (Kali Linux VM)
    KALI_HOST: str = os.getenv("KALI_HOST", "")
    KALI_USER: str = os.getenv("KALI_USER", "")
    KALI_PASSWORD: str = os.getenv("KALI_PASSWORD", "")

    class Config:
        env_file = ".env"

settings = Settings()
