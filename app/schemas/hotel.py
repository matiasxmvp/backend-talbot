# app/schemas/hotel.py - Esquemas de hotel para Pydantic

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.core.validators import FieldValidators, BusinessValidators, ValidationUtils

class HotelBase(BaseModel):
    """
    Esquema base para hotel
    
    Clase base que contiene los campos esenciales para las operaciones
    relacionadas con hoteles.
    """
    name: str = Field(..., description="Nombre del hotel")
    location: str = Field(..., description="Ubicación del hotel")
    address: Optional[str] = Field(None, description="Dirección completa del hotel")
    manager: Optional[str] = Field(None, description="Nombre del gerente del hotel")
    status: str = Field(default="active", description="Estado del hotel")
    
    # Campos financieros y contables
    presupuesto: Optional[int] = Field(None, description="Presupuesto del hotel en pesos chilenos", ge=0)
    cuenta_contable: Optional[str] = Field(None, description="Código contable del hotel")
    
    @validator('name')
    def validate_name(cls, v):
        """Normaliza el nombre del hotel"""
        v = ValidationUtils.sanitize_string(v)
        return v
    
    @validator('location')
    def validate_location(cls, v):
        """Normaliza la ubicación del hotel"""
        v = ValidationUtils.sanitize_string(v)
        return v
    
    @validator('address')
    def validate_address(cls, v):
        """Normaliza la dirección del hotel"""
        if v is None:
            return v
        v = ValidationUtils.sanitize_string(v)
        return v

class HotelCreate(HotelBase):
    """
    Esquema para crear un hotel
    
    Hereda de HotelBase y define los campos esenciales requeridos
    para la creación de un nuevo hotel.
    """
    pass

class HotelUpdate(BaseModel):
    """
    Esquema para actualizar un hotel
    
    Todos los campos son opcionales para permitir actualizaciones parciales.
    Solo incluye los campos esenciales que se pueden actualizar.
    """
    name: Optional[str] = Field(None, description="Nombre del hotel")
    location: Optional[str] = Field(None, description="Ubicación del hotel")
    address: Optional[str] = Field(None, description="Dirección completa del hotel")
    status: Optional[str] = Field(None, description="Estado del hotel")
    is_active: Optional[bool] = Field(None, description="Estado activo del hotel")
    
    # Campos financieros y contables
    presupuesto: Optional[int] = Field(None, description="Presupuesto del hotel en pesos chilenos", ge=0)
    cuenta_contable: Optional[str] = Field(None, description="Código contable del hotel")

class HotelResponse(BaseModel):
    """
    Esquema para respuesta de hotel
    
    Define solo los campos esenciales que se devuelven en las respuestas de la API,
    excluyendo campos innecesarios como rooms, manager, phone y description.
    """
    id: int
    name: str = Field(..., description="Nombre del hotel")
    location: str = Field(..., description="Ubicación del hotel")
    address: Optional[str] = Field(None, description="Dirección completa del hotel")
    status: str = Field(default="active", description="Estado del hotel")
    is_active: bool
    
    # Campos financieros y contables
    presupuesto: Optional[int] = Field(None, description="Presupuesto del hotel en pesos chilenos")
    cuenta_contable: Optional[str] = Field(None, description="Código contable del hotel")
    
    # Campos de auditoría
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class HotelList(BaseModel):
    """
    Esquema para lista de hoteles con paginación
    """
    hotels: list[HotelResponse]
    total: int
    page: int
    per_page: int
    pages: int