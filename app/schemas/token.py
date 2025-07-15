# app/schemas/token.py - Esquemas de Pydantic para tokens

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .user import User

class Token(BaseModel):
    """
    Esquema para el token de acceso
    
    Estructura básica para respuestas de autenticación que solo
    incluyen el access token. Usado en implementaciones simples
    sin refresh tokens.
    
    Attributes:
        access_token (str): Token JWT para autenticación de requests
        token_type (str): Tipo de token, siempre "bearer" para JWT
        
    Usage:
        - Respuestas de login básico
        - Renovación de tokens simples
        - Compatibilidad con OAuth2 estándar
    """
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """
    Esquema para los datos del token
    
    Estructura interna para almacenar información extraída
    de tokens JWT durante el proceso de validación.
    
    Attributes:
        username (Optional[str]): Nombre de usuario extraído del token
        
    Usage:
        - Validación interna de tokens
        - Extracción de claims del JWT
        - Proceso de autenticación de middleware
        
    Note:
        Este esquema se usa internamente y no se expone en las APIs.
    """
    username: Optional[str] = None

class RefreshToken(BaseModel):
    """
    Esquema para el token de actualización
    
    Estructura simple que contiene solo el refresh token.
    Usado cuando se necesita enviar únicamente el refresh token.
    
    Attributes:
        refresh_token (str): Token de larga duración para renovar access tokens
        
    Usage:
        - Requests de renovación de tokens
        - Procesos de logout
        - Validación de refresh tokens
        
    Security:
        - Debe transmitirse de forma segura (HTTPS)
        - Se almacena en base de datos para validación
        - Puede ser revocado en cualquier momento
    """
    refresh_token: str

class TokenResponse(BaseModel):
    """
    Esquema completo de respuesta de autenticación con refresh token
    
    Respuesta completa del proceso de autenticación que incluye
    tanto access token como refresh token, junto con metadatos
    útiles para el cliente.
    
    Attributes:
        access_token (str): Token JWT para autenticación (30 min)
        refresh_token (str): Token para renovar access tokens (30 días)
        token_type (str): Tipo de token, siempre "bearer"
        expires_in (int): Tiempo de expiración del access token en segundos
        refresh_expires_in (int): Tiempo de expiración del refresh token en segundos
        user (User): Información completa del usuario autenticado
        
    Usage:
        - Respuesta de login exitoso
        - Respuesta de renovación de tokens
        - Información completa para el cliente
        
    Example:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "abc123def456...",
            "token_type": "bearer",
            "expires_in": 1800,
            "refresh_expires_in": 2592000,
            "user": {
                "id": 1,
                "username": "jperez",
                "email": "jperez@example.com",
                "full_name": "Juan Pérez",
                "is_active": true,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Tiempo de expiración del access token en segundos
    refresh_expires_in: int  # Tiempo de expiración del refresh token en segundos
    user: User

class RefreshTokenRequest(BaseModel):
    """
    Esquema para solicitar nuevo access token con refresh token
    
    Estructura de datos para el endpoint de renovación de tokens.
    Permite obtener un nuevo access token sin re-autenticación.
    
    Attributes:
        refresh_token (str): Token de larga duración válido y activo
        
    Usage:
        - Endpoint POST /api/v1/auth/refresh
        - Endpoint POST /api/v1/auth/logout
        - Renovación automática de tokens expirados
        
    Validation:
        - El refresh token debe existir en la base de datos
        - Debe estar marcado como activo (is_active=True)
        - No debe haber expirado
        - El usuario asociado debe estar activo
        
    Example:
        {
            "refresh_token": "abc123def456ghi789..."
        }
    """
    refresh_token: str

class RefreshTokenData(BaseModel):
    """
    Esquema para los datos del refresh token
    
    Estructura interna que contiene metadatos completos de un
    refresh token almacenado en la base de datos.
    
    Attributes:
        user_id (int): ID del usuario propietario del token
        device_info (Optional[str]): Información del dispositivo (User-Agent)
        ip_address (Optional[str]): Dirección IP desde donde se creó
        expires_at (datetime): Timestamp de expiración del token
        is_active (bool): Estado activo del token (default: True)
        
    Usage:
        - Validación interna de refresh tokens
        - Auditoría de sesiones de usuario
        - Control de dispositivos autorizados
        - Gestión de expiración de tokens
        
    Security:
        - Permite rastrear sesiones por dispositivo
        - Facilita revocación selectiva de tokens
        - Auditoría de accesos por IP
        - Control de límites de sesiones concurrentes
        
    Note:
        Este esquema se usa internamente para validación y auditoría.
        No se expone directamente en las APIs públicas.
    """
    user_id: int
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    expires_at: datetime
    is_active: bool = True