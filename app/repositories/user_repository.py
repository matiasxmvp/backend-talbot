# app/repositories/user_repository.py - Repositorio para operaciones de usuario

from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from .base_repository import BaseRepository

class UserRepository(BaseRepository[User]):
    """Repositorio para manejar operaciones CRUD de usuarios"""
    
    def __init__(self, db: Session):
        """Inicializar el repositorio con la sesión de base de datos"""
        super().__init__(db, User)
        self.db = db
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Obtener usuario por nombre de usuario"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_count(self) -> int:
        """Obtener el total de usuarios en la base de datos"""
        return self.count()
    
    def create(self, user_create: UserCreate) -> User:
        """Crear un nuevo usuario"""
        # Hash de la contraseña
        hashed_password = get_password_hash(user_create.password)
        
        # Preparar datos para el usuario
        # Asegurar que el rol se guarde como valor del enum, no como nombre
        role_value = user_create.role.value if hasattr(user_create.role, 'value') else user_create.role
        
        user_data = {
            "username": user_create.username,
            "email": user_create.email,
            "hashed_password": hashed_password,
            "full_name": user_create.full_name,
            "role": role_value,
            "is_active": user_create.is_active if hasattr(user_create, 'is_active') else True,
            "is_superuser": False  # Por defecto no es superusuario
        }
        
        return super().create(user_data)
    
    def update(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Actualizar un usuario existente"""
        # Preparar datos de actualización
        update_data = user_update.model_dump(exclude_unset=True)
        
        # Si se actualiza la contraseña, hashearla
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        # Actualizar el rol si está presente
        if "role" in update_data:
            role_value = update_data["role"].value if hasattr(update_data["role"], 'value') else update_data["role"]
            update_data["role"] = role_value
        
        return super().update(user_id, update_data)
    
    def delete(self, user_id: int) -> bool:
        """Eliminar un usuario (soft delete)"""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return False
        
        # Soft delete - marcar como inactivo
        db_user.is_active = False
        self.db.commit()
        
        return True
    
    def exists_username(self, username: str) -> bool:
        """Verificar si existe un usuario con el nombre de usuario dado"""
        return self.db.query(User).filter(User.username == username).first() is not None
    
    def exists_email(self, email: str) -> bool:
        """Verificar si existe un usuario con el email dado"""
        return self.db.query(User).filter(User.email == email).first() is not None
    
    def update_users_hotel_to_null(self, hotel_id: int) -> int:
        """Actualizar todos los usuarios asociados a un hotel, estableciendo hotel_id a NULL"""
        affected_rows = self.db.query(User).filter(User.hotel_id == hotel_id).update({User.hotel_id: None})
        self.db.commit()
        return affected_rows