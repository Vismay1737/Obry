import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "OrbyTech API"
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = "orbytech_db"
    
    # Remote Execution (Kali Linux VM)
    KALI_HOST: str = os.getenv("KALI_HOST", "")
    KALI_USER: str = os.getenv("KALI_USER", "")
    KALI_PASSWORD: str = os.getenv("KALI_PASSWORD", "")
    SSH_PORT: int = int(os.getenv("SSH_PORT", "22"))

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
