"""Configuración de la aplicación."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración de la aplicación."""
    
    APP_ENV = os.getenv("APP_ENV", "dev")
    DB_DSN = os.getenv("DB_DSN")
    API_KEY = os.getenv("API_KEY")
    ADMIN_USER = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASS = os.getenv("ADMIN_PASS", "admin")
    API_KEY_TTL_MINUTES = int(os.getenv("API_KEY_TTL_MINUTES", "60"))
