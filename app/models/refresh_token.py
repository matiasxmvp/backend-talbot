# app/models/refresh_token.py - Modelo de refresh token para SQLAlchemy

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class RefreshToken(Base):
    """Modelo de refresh token en la base de datos"""
    
    __tablename__ = "refresh_tokens"
    
    # Campos de la tabla
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    token = Column(Text, unique=True, index=True, nullable=False)  # Token único
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Relación con usuario
    is_active = Column(Boolean, default=True, nullable=False)  # Token activo/revocado
    device_info = Column(String(255), nullable=True)  # Información del dispositivo
    ip_address = Column(String(45), nullable=True)  # IP del cliente
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)  # Fecha de expiración
    last_used_at = Column(DateTime(timezone=True), nullable=True)  # Último uso
    
    # Relación con el modelo User
    user = relationship("User", back_populates="refresh_tokens")
    
    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"
    
    def __str__(self):
        return f"RefreshToken para usuario {self.user_id} - Activo: {self.is_active}"