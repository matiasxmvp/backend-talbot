# app/core/config.py - Configuración de la aplicación

from pydantic_settings import BaseSettings
from typing import Optional
import os
import secrets

class Settings(BaseSettings):
    """Configuración de la aplicación usando Pydantic"""
    
    # Configuración de la aplicación
    app_name: str = "API de Autenticación"
    debug: bool = False
    version: str = "1.0.0"
    
    # Configuración de la base de datos
    # Variables individuales para AWS RDS
    db_host: Optional[str] = os.getenv("DB_HOST")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: Optional[str] = os.getenv("DB_NAME")
    db_user: Optional[str] = os.getenv("DB_USER")
    db_password: Optional[str] = os.getenv("DB_PASSWORD")
    
    # Configuración específica para PostgreSQL (Docker - legacy)
    postgres_server: Optional[str] = None
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: Optional[str] = None
    postgres_port: int = 5432
    
    @property
    def database_url(self) -> str:
        """Construir URL de base de datos automáticamente"""
        # Si existe DATABASE_URL explícita, usarla
        explicit_url = os.getenv("DATABASE_URL")
        if explicit_url:
            return explicit_url
            
        # Si tenemos variables de AWS RDS, construir URL de PostgreSQL
        if all([self.db_host, self.db_name, self.db_user, self.db_password]):
            return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
            
        # Fallback a SQLite para desarrollo local
        return "sqlite:///./app.db"
    
    # Configuración de JWT
    # IMPORTANTE: Esta clave debe venir del archivo .env
    # Si no se encuentra, genera una temporal (solo para desarrollo)
    secret_key: str = os.getenv(
        "SECRET_KEY", 
        secrets.token_urlsafe(32)  # Genera una clave temporal si no existe
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    
    # Configuración de seguridad
    max_refresh_tokens_per_user: int = 5  # Máximo de tokens activos por usuario
    cleanup_expired_tokens_hours: int = 24  # Limpiar tokens expirados cada X horas
    
    # Configuración de CORS - Flexible para diferentes puertos
    cors_origins: str = os.getenv(
        "CORS_ORIGINS", 
        "http://localhost:3000,http://127.0.0.1:3000,https://main.d33nzehgrvy9qd.amplifyapp.com"
    )
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Convierte la cadena de orígenes CORS en una lista"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_postgresql(self) -> bool:
        """Verifica si se está usando PostgreSQL"""
        return self.database_url.startswith("postgresql://")
    
    @property
    def is_sqlite(self) -> bool:
        """Verifica si se está usando SQLite"""
        return self.database_url.startswith("sqlite:///")
    
    # Configuración del servidor
    host: str = "0.0.0.0"
    port: int = 8000  # Puerto principal de la aplicación
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    # Añadir esta línea
    environment: str = "development"
    
    # Resto de la configuración...

# Instancia global de configuración
settings = Settings()