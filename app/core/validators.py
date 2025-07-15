# app/core/validators.py - Validadores simplificados para backend
# Las validaciones principales se manejan en el frontend

from typing import Dict, Optional
from app.core.config import settings

class ValidationResult:
    """Resultado de validación simplificado"""
    
    def __init__(self, is_valid: bool, message: Optional[str] = None):
        self.is_valid = is_valid
        self.message = message

def validate_login(username: str, password: str) -> ValidationResult:
    """Validación básica de login - solo campos requeridos"""
    if not username or not password:
        return ValidationResult(False, "Usuario y contraseña son requeridos")
    return ValidationResult(True)

def hotel_required(user_role: str) -> bool:
    """Verifica si el rol requiere hotel asignado"""
    admin_roles = ["ADMINISTRADOR", "administrador", "admin"]
    return user_role not in admin_roles

def validate_user(user_data: dict) -> Dict[str, str]:
    """Validación simplificada de usuario - sin restricciones"""
    return {}  # Sin validaciones restrictivas

def validate_hotel(hotel_data: dict) -> Dict[str, str]:
    """Validación simplificada de hotel - sin restricciones"""
    return {}  # Sin validaciones restrictivas

def validate_email(email: str) -> ValidationResult:
    """Validación básica de email - solo formato mínimo"""
    if not email or "@" not in email:
        return ValidationResult(False, "Email inválido")
    return ValidationResult(True)

# Clases vacías para compatibilidad con imports existentes
class FieldValidators:
    """Clase vacía - validaciones movidas al frontend"""
    pass

class BusinessValidators:
    """Clase vacía - validaciones de negocio movidas al frontend"""
    pass

class ValidationUtils:
    """Utilidades de validación optimizadas"""
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Limpia y sanitiza una cadena básicamente"""
        return value.strip() if value else ""
    
    @staticmethod
    def normalize_email(email: str) -> str:
        """Normaliza email básicamente"""
        return email.lower().strip() if email else ""
    
    @staticmethod
    def normalize_phone(phone: str) -> str:
        """Normaliza número de teléfono"""
        if not phone:
            return ""
        return re.sub(r'[^0-9+]', '', phone)
    
    @staticmethod
    def is_strong_password(password: str) -> bool:
        """Verifica si la contraseña es fuerte (simplificado)"""
        return len(password) >= 6  # Validación mínima

class ValidationError(Exception):
    """Excepción para errores de validación"""
    
    def __init__(self, errors: Dict[str, str]):
        self.errors = errors
        super().__init__(str(errors))
