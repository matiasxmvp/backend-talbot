# app/db/database.py - Configuración de la base de datos

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# Crear el motor de la base de datos
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Crear la fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos de SQLAlchemy
Base = declarative_base()

def get_db() -> Session:
    """Dependencia para obtener una sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Crear todas las tablas en la base de datos"""
    # Importar todos los modelos para asegurar que se registren
    from app.models.user import User
    from app.models.refresh_token import RefreshToken
    from app.models.hotel import Hotel
    
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Eliminar todas las tablas de la base de datos"""
    Base.metadata.drop_all(bind=engine)