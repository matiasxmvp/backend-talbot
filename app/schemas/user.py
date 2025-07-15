# app/schemas/user.py - Esquemas de Pydantic para validación de datos

from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from app.models.user import UserRole
from app.core.validators import FieldValidators, BusinessValidators, ValidationUtils

class UserBase(BaseModel):
    """
    Esquema base para usuario
    
    Clase base que contiene los campos comunes para todas las operaciones
    relacionadas con usuarios. Define la estructura básica de datos
    que se comparte entre diferentes esquemas de usuario.
    
    Attributes:
        username (str): Nombre de usuario único en el sistema
        email (EmailStr): Dirección de correo electrónico válida
        full_name (Optional[str]): Nombre completo del empleado
        role (UserRole): Rol del usuario en el sistema (default: HOUSEKEEPER)
        is_active (bool): Estado activo del usuario (default: True)
        hotel_id (Optional[int]): ID del hotel asociado (opcional para administradores)
    """
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.HOUSEKEEPER
    is_active: bool = True
    hotel_id: Optional[int] = None
    
    @validator('username')
    def validate_username(cls, v):
        """Normaliza el username"""
        # Solo normalizar, sin validaciones
        v = ValidationUtils.sanitize_string(v)
        return v
    
    @validator('email')
    def validate_email(cls, v):
        """Normaliza el formato del email"""
        # Solo normalizar el email, sin validaciones restrictivas
        v = ValidationUtils.normalize_email(v)
        return v
    
    @validator('full_name')
    def validate_full_name(cls, v):
        """Normaliza el nombre completo"""
        if v is None:
            return v
        # Solo normalizar, sin validaciones
        v = ValidationUtils.sanitize_string(v)
        return v
    
    @validator('hotel_id')
    def validate_hotel_id(cls, v, values):
        """Acepta cualquier hotel_id"""
        # Sin validaciones restrictivas
        return v

class UserCreate(UserBase):
    """
    Esquema para crear un usuario
    
    Extiende UserBase añadiendo el campo password necesario para
    el registro de nuevos usuarios. La contraseña se hashea antes
    de almacenarse en la base de datos.
    
    Attributes:
        password (str): Contraseña en texto plano (se hashea automáticamente)
        
    Inherited from UserBase:
        username, email, full_name, is_active
        
    Validation:
        - Email debe tener formato válido
        - Username debe ser único
        - Password se recomienda que tenga al menos 8 caracteres
    """
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        """Acepta cualquier contraseña"""
        # Sin validaciones restrictivas
        return v

class UserUpdate(BaseModel):
    """
    Esquema para actualizar usuario
    
    Permite actualización parcial de datos de usuario.
    Todos los campos son opcionales para permitir updates selectivos.
    
    Attributes:
        username (Optional[str]): Nuevo nombre de usuario
        email (Optional[EmailStr]): Nueva dirección de correo
        full_name (Optional[str]): Nuevo nombre completo
        role (Optional[UserRole]): Nuevo rol del usuario
        is_active (Optional[bool]): Nuevo estado activo
        password (Optional[str]): Nueva contraseña (se hashea automáticamente)
        hotel_id (Optional[int]): ID del hotel asociado
        
    Note:
        Solo se actualizan los campos que se proporcionen en el request.
        Los campos None se ignoran durante la actualización.
    """
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
    hotel_id: Optional[int] = None

class UserInDB(UserBase):
    """
    Esquema para usuario en base de datos
    
    Representa la estructura completa del usuario tal como se almacena
    en la base de datos, incluyendo campos internos como la contraseña
    hasheada y timestamps.
    
    Attributes:
        id (int): Identificador único del usuario
        hashed_password (str): Contraseña hasheada con bcrypt
        created_at (datetime): Timestamp de creación del registro
        updated_at (datetime): Timestamp de última actualización
        
    Inherited from UserBase:
        username, email, full_name, is_active
        
    Note:
        Este esquema se usa internamente y nunca se expone en las APIs.
        Contiene información sensible como la contraseña hasheada.
    """
    id: int
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class User(UserBase):
    """
    Esquema público de usuario (sin contraseña)
    
    Versión segura del esquema de usuario que se expone en las APIs.
    Excluye información sensible como contraseñas hasheadas.
    
    Attributes:
        id (int): Identificador único del usuario
        is_superuser (bool): Indica si el usuario tiene privilegios de administrador
        created_at (datetime): Timestamp de creación del registro
        updated_at (datetime): Timestamp de última actualización
        
    Inherited from UserBase:
        username, email, full_name, is_active
        
    Usage:
        - Respuestas de endpoints de autenticación
        - Información de perfil de usuario
        - Listados de usuarios (para administradores)
    """
    id: int
    is_superuser: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    """
    Esquema para login de usuario
    
    Estructura de datos para el proceso de autenticación.
    Contiene las credenciales necesarias para iniciar sesión.
    
    Attributes:
        username (str): Nombre de usuario registrado en el sistema
        password (str): Contraseña en texto plano
        
    Security:
        - La contraseña se transmite en texto plano pero debe usarse HTTPS
        - Se valida contra la contraseña hasheada almacenada en BD
        - Después de la validación, se generan tokens JWT
        
    Example:
        {
            "username": "jperez",
            "password": "SecurePass123!"
        }
    """
    username: str
    password: str

class ChangePassword(BaseModel):
    """
    Esquema para cambio de contraseña
    
    Estructura de datos para el proceso de cambio de contraseña.
    Requiere verificación de la contraseña actual por seguridad.
    
    Attributes:
        current_password (str): Contraseña actual del usuario
        new_password (str): Nueva contraseña deseada
        
    Security:
        - Requiere autenticación válida (token JWT)
        - Verifica contraseña actual antes del cambio
        - Nueva contraseña se hashea con bcrypt
        - Se recomienda que la nueva contraseña sea fuerte
        
    Validation:
        - current_password debe coincidir con la almacenada
        - new_password debe ser diferente a current_password
        - Se sugiere validación de complejidad en el frontend
        
    Example:
        {
            "current_password": "OldPass123!",
            "new_password": "NewSecurePass456!"
        }
    """
    current_password: str
    new_password: str

class UserList(BaseModel):
    """
    Esquema para lista de usuarios con paginación
    
    Proporciona una respuesta estructurada para endpoints que devuelven
    múltiples usuarios con información de paginación.
    
    Attributes:
        users (list[User]): Lista de usuarios
        total (int): Total de usuarios en la base de datos
        page (int): Página actual
        per_page (int): Elementos por página
        pages (int): Total de páginas disponibles
    """
    users: list[User]
    total: int
    page: int
    per_page: int
    pages: int