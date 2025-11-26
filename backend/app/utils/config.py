import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./contabiliza_ia.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "contabiliza-ia-super-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    PROJECT_NAME: str = "Contabiliza.IA"
    
    # SEFAZ API (para depois)
    SEFAZ_API_URL: str = os.getenv("SEFAZ_API_URL", "")
    SEFAZ_API_KEY: str = os.getenv("SEFAZ_API_KEY", "")

settings = Settings()