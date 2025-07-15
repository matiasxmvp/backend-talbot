# app/models/hotel.py - Modelo de hotel para SQLAlchemy

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class HotelStatus(enum.Enum):
    """Enumeración de estados de hotel"""
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"

class Hotel(Base):
    """Modelo de hotel en la base de datos"""
    
    __tablename__ = "hotels"
    
    # Campos de la tabla
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    location = Column(String(100), nullable=False)
    address = Column(Text, nullable=True)
    rooms = Column(Integer, nullable=False, default=0)
    manager = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), default=HotelStatus.ACTIVE.value, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Nuevos campos agregados
    cuenta_contable = Column(String(10), nullable=True, unique=True, index=True)  # Código contable único (ej: "001", "002")
    presupuesto = Column(Integer, nullable=True, default=0)  # Presupuesto del hotel en pesos chilenos
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Hotel(id={self.id}, name='{self.name}', location='{self.location}')>"