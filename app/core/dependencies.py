# app/core/dependencies.py - Dependencias compartidas

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.repositories.user_repository import UserRepository
from app.core.config import settings
from app.models.user import User, UserRole

# Configuración del esquema de autenticación OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Obtener el usuario actual desde el token JWT"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar el token JWT
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Buscar el usuario en la base de datos
    user_repo = UserRepository(db)
    user = user_repo.get_by_username(username)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Obtener el usuario actual y verificar que esté activo"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    return current_user


async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Obtener el usuario actual y verificar que sea administrador
    
    Esta función verifica que el usuario actual esté activo y tenga
    permisos de administrador (rol ADMIN). Se utiliza como dependencia
    en endpoints que requieren privilegios administrativos.
    
    Args:
        current_user (User): Usuario actual obtenido del token JWT
        
    Returns:
        User: Usuario con permisos de administrador
        
    Raises:
        HTTPException 403: Si el usuario no tiene permisos de administrador
        HTTPException 401: Si el token es inválido o el usuario no existe
        HTTPException 400: Si el usuario está inactivo
        
    Example:
        @router.get("/admin-only")
        async def admin_endpoint(admin: User = Depends(get_current_admin_user)):
            return {"message": "Solo administradores pueden ver esto"}
    """
    if current_user.role != UserRole.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador para realizar esta acción"
        )
    return current_user