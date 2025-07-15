# app/services/auth_service.py - Servicio de autenticación

from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status, Request
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, verify_refresh_token, generate_secure_token
)
from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.schemas.user import UserCreate, User as UserSchema
from app.schemas.token import TokenResponse, RefreshTokenRequest
from app.models.user import User, UserRole

class AuthService:
    """Servicio para manejar la autenticación y autorización"""
    
    def __init__(self, db: Session):
        """Inicializar el servicio con la sesión de base de datos"""
        self.db = db
        self.user_repository = UserRepository(db)
        self.refresh_token_repository = RefreshTokenRepository(db)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Autenticar un usuario con username y contraseña"""
        # Normalizar username a minúsculas para evitar problemas de case sensitivity
        normalized_username = username.lower().strip()
        user = self.user_repository.get_by_username(normalized_username)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def login(self, username: str, password: str, request: Optional[Request] = None) -> TokenResponse:
        """Realizar login y generar tokens de acceso y actualización"""
        # Autenticar usuario
        user = self.authenticate_user(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificar que el usuario esté activo
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario inactivo"
            )
        
        # Limpiar tokens expirados del usuario
        self.refresh_token_repository.cleanup_expired_tokens()
        
        # Verificar límite de tokens activos por usuario
        active_tokens = self.refresh_token_repository.count_active_tokens_by_user(user.id)
        if active_tokens >= settings.max_refresh_tokens_per_user:
            # Revocar el token más antiguo
            oldest_token = self.refresh_token_repository.get_oldest_token_by_user(user.id)
            if oldest_token:
                self.refresh_token_repository.revoke_token(oldest_token.token)
        
        # Crear tokens
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        # Crear refresh token
        refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
        refresh_token_jwt = create_refresh_token(
            data={"sub": user.username, "user_id": user.id}, 
            expires_delta=refresh_token_expires
        )
        
        # Obtener información del dispositivo/IP
        device_info = None
        ip_address = None
        if request:
            device_info = request.headers.get("User-Agent", "Unknown")
            ip_address = request.client.host if request.client else "Unknown"
        
        # Guardar refresh token en la base de datos
        secure_token = generate_secure_token()
        self.refresh_token_repository.create_refresh_token(
            token=secure_token,
            user_id=user.id,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=datetime.utcnow() + refresh_token_expires
        )
        
        # Convertir el usuario a esquema para la respuesta
        from ..schemas.user import User as UserSchema
        user_schema = UserSchema.model_validate(user, from_attributes=True)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            refresh_token=secure_token,
            refresh_expires_in=settings.refresh_token_expire_days * 24 * 60 * 60,
            user=user_schema
        )
    
    def register(self, user_create: UserCreate) -> UserSchema:
        """Registrar un nuevo usuario"""
        # Normalizar username a minúsculas para consistencia
        user_create.username = user_create.username.lower().strip()
        
        # Normalizar rol solo si es string, si ya es enum UserRole no necesita normalización
        if isinstance(user_create.role, str):
            # Convertir string a enum UserRole
            role_str = user_create.role.lower().strip()
            try:
                user_create.role = UserRole(role_str)
                print(f"DEBUG: Rol convertido a enum: {user_create.role} (valor: {user_create.role.value})")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Rol inválido: {role_str}. Roles válidos: {[role.value for role in UserRole]}"
                )
        else:
            print(f"DEBUG: Rol ya es enum: {user_create.role} (valor: {user_create.role.value})")
        
        # Verificar que el username no exista
        if self.user_repository.exists_username(user_create.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está registrado"
            )
        
        # Verificar que el email no exista
        if self.user_repository.exists_email(user_create.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Crear el usuario
        db_user = self.user_repository.create(user_create)
        
        # Convertir a esquema de respuesta
        return UserSchema.model_validate(db_user, from_attributes=True)
    
    def get_current_user_info(self, user: User) -> UserSchema:
        """Obtener información del usuario actual"""
        return UserSchema.model_validate(user, from_attributes=True)
    
    def change_password(self, user: User, current_password: str, new_password: str) -> bool:
        """Cambiar la contraseña del usuario"""
        # Verificar la contraseña actual
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta"
            )
        
        # Actualizar la contraseña
        from app.schemas.user import UserUpdate
        user_update = UserUpdate(password=new_password)
        updated_user = self.user_repository.update(user.id, user_update)
        
        return updated_user is not None
    
    def refresh_access_token(self, refresh_token_request: RefreshTokenRequest) -> TokenResponse:
        """Renovar token de acceso usando refresh token"""
        # Verificar que el refresh token existe y está activo
        db_refresh_token = self.refresh_token_repository.get_by_token(refresh_token_request.refresh_token)
        if not db_refresh_token or not db_refresh_token.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido o expirado"
            )
        
        # Verificar que no haya expirado
        if db_refresh_token.expires_at < datetime.utcnow():
            # Revocar token expirado
            self.refresh_token_repository.revoke_token(refresh_token_request.refresh_token)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expirado"
            )
        
        # Obtener el usuario
        user = self.user_repository.get_by_id(db_refresh_token.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado o inactivo"
            )
        
        # Actualizar última fecha de uso del refresh token
        self.refresh_token_repository.update_last_used(refresh_token_request.refresh_token)
        
        # Crear nuevo access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            refresh_token=refresh_token_request.refresh_token,  # Mantener el mismo refresh token
            refresh_expires_in=int((db_refresh_token.expires_at - datetime.utcnow()).total_seconds()),
            user_id=user.id,
            username=user.username
        )
    
    def logout(self, refresh_token: str) -> bool:
        """Realizar logout revocando el refresh token"""
        return self.refresh_token_repository.revoke_token(refresh_token)
    
    def logout_all_devices(self, user_id: int) -> bool:
        """Realizar logout de todos los dispositivos del usuario"""
        return self.refresh_token_repository.revoke_all_user_tokens(user_id)