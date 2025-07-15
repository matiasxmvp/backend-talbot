# app/repositories/refresh_token_repository.py - Repositorio para refresh tokens

from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.refresh_token import RefreshToken
from app.schemas.token import RefreshTokenData
from datetime import datetime, timedelta
from typing import Optional, List
import secrets

class RefreshTokenRepository:
    """Repositorio para operaciones CRUD de refresh tokens"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: int, device_info: Optional[str] = None, 
               ip_address: Optional[str] = None, expires_days: int = 30) -> RefreshToken:
        """Crear un nuevo refresh token con token generado automáticamente"""
        # Generar token único y seguro
        token = secrets.token_urlsafe(64)
        
        # Calcular fecha de expiración
        expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        # Usar el método consolidado para crear el token
        return self.create_refresh_token(
            token=token,
            user_id=user_id,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=expires_at
        )
    
    def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """Obtener refresh token por token string"""
        return self.db.query(RefreshToken).filter(
            and_(
                RefreshToken.token == token,
                RefreshToken.is_active == True,
                RefreshToken.expires_at > datetime.utcnow()
            )
        ).first()
    
    def get_by_user_id(self, user_id: int) -> List[RefreshToken]:
        """Obtener todos los refresh tokens activos de un usuario"""
        return self._get_active_tokens_query(user_id).all()
    
    def revoke_token(self, token: str) -> bool:
        """Revocar un refresh token específico"""
        refresh_token = self.db.query(RefreshToken).filter(
            RefreshToken.token == token
        ).first()
        
        if refresh_token:
            refresh_token.is_active = False
            self.db.commit()
            return True
        return False
    
    def revoke_all_user_tokens(self, user_id: int) -> int:
        """Revocar todos los refresh tokens de un usuario"""
        count = self.db.query(RefreshToken).filter(
            and_(
                RefreshToken.user_id == user_id,
                RefreshToken.is_active == True
            )
        ).update({"is_active": False})
        
        self.db.commit()
        return count
    
    def update_last_used(self, token: str) -> bool:
        """Actualizar la fecha de último uso del token"""
        refresh_token = self.db.query(RefreshToken).filter(
            RefreshToken.token == token
        ).first()
        
        if refresh_token:
            refresh_token.last_used_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def cleanup_expired_tokens(self) -> int:
        """Limpiar tokens expirados de la base de datos"""
        count = self.db.query(RefreshToken).filter(
            RefreshToken.expires_at <= datetime.utcnow()
        ).delete()
        
        self.db.commit()
        return count
    
    def _get_active_tokens_query(self, user_id: int):
        """Query base para tokens activos de un usuario (método privado para evitar duplicación)"""
        return self.db.query(RefreshToken).filter(
            and_(
                RefreshToken.user_id == user_id,
                RefreshToken.is_active == True,
                RefreshToken.expires_at > datetime.utcnow()
            )
        )
    
    def create_refresh_token(self, token: str, user_id: int, device_info: Optional[str] = None,
                           ip_address: Optional[str] = None, expires_at: datetime = None) -> RefreshToken:
        """Crear un refresh token con token específico (método base consolidado)"""
        # Si no se proporciona fecha de expiración, usar configuración por defecto
        if expires_at is None:
            expires_at = datetime.utcnow() + timedelta(days=30)
            
        refresh_token = RefreshToken(
            token=token,
            user_id=user_id,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=expires_at,
            is_active=True
        )
        
        self.db.add(refresh_token)
        self.db.commit()
        self.db.refresh(refresh_token)
        
        return refresh_token
    
    def count_active_tokens_by_user(self, user_id: int) -> int:
        """Contar tokens activos por usuario"""
        return self._get_active_tokens_query(user_id).count()
    
    def get_oldest_token_by_user(self, user_id: int) -> Optional[RefreshToken]:
        """Obtener el token más antiguo de un usuario"""
        return self._get_active_tokens_query(user_id).order_by(RefreshToken.created_at.asc()).first()