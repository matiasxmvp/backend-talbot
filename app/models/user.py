# app/models/user.py - Modelo de usuario para SQLAlchemy

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class UserRole(enum.Enum):
    """Enumeración de roles de usuario en el sistema"""
    ADMINISTRADOR = "ADMINISTRADOR"
    ADMIN_BODEGA = "ADMIN_BODEGA"
    HOUSEKEEPER = "HOUSEKEEPER"
    JEFE_RECEPCION = "JEFE_RECEPCION"
    GERENTE = "GERENTE"
    CONTROLLER = "CONTROLLER"

class User(Base):
    """Modelo de usuario en la base de datos"""
    
    __tablename__ = "users"
    
    # Campos de la tabla
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(Enum(UserRole, length=20), default=UserRole.HOUSEKEEPER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=True)  # Hotel asociado (opcional para administradores)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relación con RefreshToken
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role='{self.role.value}')>"
    
    def __str__(self):
        return f"Usuario: {self.username} ({self.email}) - Rol: {self.role.value}"