"""Sesión de base de datos."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Config

engine = create_engine(Config.DB_DSN)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
