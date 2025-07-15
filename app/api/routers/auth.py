# app/api/routers/auth.py - Router de autenticación para Talbot Hotels

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import List
from app.models.user import User
from app.db.database import get_db
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, User as UserSchema, UserLogin, ChangePassword, UserUpdate, UserList
from app.schemas.token import TokenResponse, RefreshTokenRequest
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.models.user import User, UserRole

# Router de autenticación para el sistema hotelero
router = APIRouter()

# Dependencia para verificar que el usuario sea administrador
def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Verifica que el usuario actual sea administrador
    
    Args:
        current_user (User): Usuario extraído del token JWT
    
    Returns:
        User: Usuario administrador verificado
        
    Raises:
        HTTPException 403: Si el usuario no es administrador
    """
    if current_user.role != UserRole.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador para realizar esta acción"
        )
    return current_user

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Registrar un nuevo empleado en el sistema Talbot Hotels
    
    Este endpoint permite crear nuevas cuentas de usuario para empleados del hotel.
    Valida que el username y email sean únicos antes de crear el registro.
    
    Args:
        user_create (UserCreate): Datos del nuevo usuario incluyendo username, email, 
                                 password, full_name y estado activo
        db (Session): Sesión de base de datos inyectada automáticamente
    
    Returns:
        UserSchema: Información del usuario creado (sin contraseña)
        
    Raises:
        HTTPException 400: Si el username o email ya están registrados
        HTTPException 422: Si los datos de entrada no son válidos
        
    Example:
        POST /api/v1/auth/register
        {
            "username": "jperez",
            "email": "juan.perez@talbothotels.com",
            "password": "SecurePass123!",
            "full_name": "Juan Pérez",
            "is_active": true
        }
    """
    auth_service = AuthService(db)
    return auth_service.register(user_create)


@router.get("/users", response_model=UserList)
async def get_all_users(
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(10, ge=1, le=100, description="Elementos por página"),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de todos los usuarios con paginación (solo administradores)
    
    Endpoint exclusivo para administradores que permite obtener la lista
    completa de usuarios del sistema con paginación completa.
    
    Args:
        page (int): Número de página (mínimo 1)
        per_page (int): Elementos por página (1-100)
        current_admin (User): Usuario administrador extraído del token JWT
        db (Session): Sesión de base de datos inyectada automáticamente
    
    Returns:
        UserList: Lista paginada de usuarios con metadatos de paginación
        
    Raises:
        HTTPException 403: Si el usuario no es administrador
        HTTPException 401: Token inválido o expirado
        
    Example:
        GET /users?page=1&per_page=20
        Authorization: Bearer <admin_token>
    """
    from app.services.user_service import UserService
    user_service = UserService(db)
    return user_service.get_all_users(page=page, per_page=per_page)


@router.put("/users/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar un usuario existente (solo administradores)
    
    Endpoint exclusivo para administradores que permite actualizar
    la información de cualquier usuario del sistema.
    
    Args:
        user_id (int): ID del usuario a actualizar
        user_update (UserUpdate): Datos a actualizar del usuario
        current_admin (User): Usuario administrador extraído del token JWT
        db (Session): Sesión de base de datos inyectada automáticamente
    
    Returns:
        UserSchema: Información actualizada del usuario
        
    Raises:
        HTTPException 403: Si el usuario no es administrador
        HTTPException 404: Si el usuario no existe
        HTTPException 400: Si hay conflicto con username o email
        
    Example:
        PUT /users/123
        Authorization: Bearer <admin_token>
        {
            "full_name": "Nuevo Nombre",
            "email": "nuevo@email.com",
            "is_active": false
        }
    """
    from app.repositories.user_repository import UserRepository
    user_repository = UserRepository(db)
    
    # Verificar que el usuario existe
    existing_user = user_repository.get_by_id(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar conflictos de username y email si se están actualizando
    if user_update.username and user_update.username != existing_user.username:
        if user_repository.exists_username(user_update.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )
    
    if user_update.email and user_update.email != existing_user.email:
        if user_repository.exists_email(user_update.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está en uso"
            )
    
    # Actualizar el usuario
    updated_user = user_repository.update(user_id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar el usuario"
        )
    
    return updated_user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar un usuario (solo administradores)
    
    Endpoint exclusivo para administradores que permite eliminar
    usuarios del sistema. No se puede eliminar el propio usuario administrador.
    
    Args:
        user_id (int): ID del usuario a eliminar
        current_admin (User): Usuario administrador extraído del token JWT
        db (Session): Sesión de base de datos inyectada automáticamente
    
    Returns:
        dict: Mensaje de confirmación de eliminación
        
    Raises:
        HTTPException 403: Si el usuario no es administrador
        HTTPException 404: Si el usuario no existe
        HTTPException 400: Si intenta eliminar su propio usuario
        
    Example:
        DELETE /users/123
        Authorization: Bearer <admin_token>
    """
    from app.repositories.user_repository import UserRepository
    user_repository = UserRepository(db)
    
    # Verificar que el usuario existe
    existing_user = user_repository.get_by_id(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Prevenir que el administrador se elimine a sí mismo
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propio usuario"
        )
    
    # Eliminar el usuario
    success = user_repository.delete(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el usuario"
        )
    
    return {"message": f"Usuario {existing_user.username} eliminado exitosamente"}

@router.post("/login", response_model=TokenResponse)
async def login(
    user_login: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Iniciar sesión en el sistema Talbot Hotels
    
    Autentica las credenciales del usuario y genera un par de tokens JWT:
    - Access Token: Para autenticación en requests (30 min de duración)
    - Refresh Token: Para renovar access tokens (30 días de duración)
    
    El sistema registra información del dispositivo (User-Agent) e IP para
    auditoría y control de sesiones. Limita el número máximo de sesiones
    activas por usuario para mejorar la seguridad.
    
    Args:
        user_login (UserLogin): Credenciales del usuario (username y password)
        request (Request): Objeto request para extraer metadatos del cliente
        db (Session): Sesión de base de datos inyectada automáticamente
    
    Returns:
        TokenResponse: Contiene access_token, refresh_token, tiempos de expiración
                      e información básica del usuario
        
    Raises:
        HTTPException 401: Credenciales incorrectas
        HTTPException 400: Usuario inactivo
        
    Example:
        POST /api/v1/auth/login
        {
            "username": "jperez",
            "password": "SecurePass123!"
        }
    """
    auth_service = AuthService(db)
    return auth_service.login(user_login.username, user_login.password, request)

@router.get("/me", response_model=UserSchema)
async def get_current_user(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener información del empleado autenticado
    
    Endpoint protegido que retorna los datos del usuario actual basándose
    en el token JWT proporcionado en el header Authorization.
    Útil para obtener información del perfil y verificar el estado de la sesión.
    
    Args:
        current_user (User): Usuario extraído automáticamente del token JWT
    
    Returns:
        UserSchema: Información completa del usuario (sin contraseña)
        
    Raises:
        HTTPException 401: Token inválido, expirado o usuario inactivo
        
    Headers:
        Authorization: Bearer <access_token>
        
    Example:
        GET /api/v1/auth/me
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    return UserSchema.model_validate(current_user, from_attributes=True)

@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cambiar contraseña del empleado
    
    Permite al usuario autenticado cambiar su contraseña actual.
    Requiere verificación de la contraseña actual por seguridad.
    La nueva contraseña se hashea usando bcrypt antes de almacenarse.
    
    Args:
        password_data (ChangePassword): Contiene current_password y new_password
        current_user (User): Usuario extraído del token JWT
        db (Session): Sesión de base de datos inyectada automáticamente
    
    Returns:
        dict: Mensaje de confirmación del cambio exitoso
        
    Raises:
        HTTPException 400: Contraseña actual incorrecta
        HTTPException 401: Token inválido o usuario inactivo
        HTTPException 422: Nueva contraseña no cumple requisitos
        
    Security:
        - Verifica contraseña actual antes del cambio
        - Hashea la nueva contraseña con bcrypt
        - Requiere autenticación válida
        
    Example:
        POST /api/v1/auth/change-password
        {
            "current_password": "OldPass123!",
            "new_password": "NewSecurePass456!"
        }
    """
    auth_service = AuthService(db)
    success = auth_service.change_password(current_user, password_data.current_password, password_data.new_password)
    
    if success:
        return {"message": "Contraseña actualizada exitosamente"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Renovar token de acceso usando refresh token
    
    Permite obtener un nuevo access token cuando el actual ha expirado,
    sin necesidad de volver a autenticarse con credenciales.
    Valida que el refresh token sea válido, activo y no haya expirado.
    
    Args:
        refresh_request (RefreshTokenRequest): Contiene el refresh_token
        db (Session): Sesión de base de datos inyectada automáticamente
    
    Returns:
        TokenResponse: Nuevo access_token con el mismo refresh_token
        
    Raises:
        HTTPException 401: Refresh token inválido, expirado o revocado
        HTTPException 401: Usuario asociado no encontrado o inactivo
        
    Flow:
        1. Valida refresh token en base de datos
        2. Verifica que no haya expirado
        3. Confirma que el usuario sigue activo
        4. Genera nuevo access token
        5. Actualiza timestamp de último uso
        
    Example:
        POST /api/v1/auth/refresh
        {
            "refresh_token": "abc123def456..."
        }
    """
    auth_service = AuthService(db)
    return auth_service.refresh_access_token(refresh_request)

@router.post("/logout")
async def logout(
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Cerrar sesión del sistema
    
    Realiza un logout real revocando el refresh token en la base de datos.
    Esto invalida tanto el refresh token como hace que el access token
    asociado sea inútil para futuras renovaciones.
    
    Args:
        refresh_request (RefreshTokenRequest): Contiene el refresh_token a revocar
        db (Session): Sesión de base de datos inyectada automáticamente
    
    Returns:
        dict: Mensaje de confirmación del logout exitoso
        
    Raises:
        HTTPException 400: Error al revocar el token (token no encontrado)
        
    Security:
        - Marca el refresh token como inactivo en BD
        - Previene futuras renovaciones de access token
        - El access token actual expira naturalmente
        
    Note:
        Después del logout, el cliente debe descartar ambos tokens
        y redirigir al usuario a la pantalla de login.
        
    Example:
        POST /api/v1/auth/logout
        {
            "refresh_token": "abc123def456..."
        }
    """
    auth_service = AuthService(db)
    success = auth_service.logout(refresh_request.refresh_token)
    
    if success:
        return {"message": "Sesión cerrada exitosamente"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al cerrar sesión"
        )

@router.post("/logout-all")
async def logout_all_devices(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cerrar sesión en todos los dispositivos
    
    Revoca todos los refresh tokens activos del usuario autenticado,
    efectivamente cerrando sesión en todos los dispositivos donde
    el usuario tenga sesiones activas.
    
    Args:
        current_user (User): Usuario extraído del token JWT
        db (Session): Sesión de base de datos inyectada automáticamente
    
    Returns:
        dict: Mensaje de confirmación del logout masivo
        
    Raises:
        HTTPException 401: Token inválido o usuario inactivo
        HTTPException 400: Error al revocar tokens
        
    Use Cases:
        - Sospecha de compromiso de cuenta
        - Cambio de contraseña (forzar re-login)
        - Limpieza de sesiones por política de seguridad
        - Usuario perdió un dispositivo
        
    Security:
        - Requiere autenticación válida
        - Revoca TODOS los refresh tokens del usuario
        - Fuerza re-autenticación en todos los dispositivos
        
    Example:
        POST /api/v1/auth/logout-all
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    auth_service = AuthService(db)
    success = auth_service.logout_all_devices(current_user.id)
    
    if success:
        return {"message": "Sesión cerrada en todos los dispositivos"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al cerrar sesiones"
        )

@router.post("/create-user", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: UserCreate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo usuario (solo administradores)
    
    Endpoint exclusivo para administradores que permite crear nuevos usuarios
    del sistema con roles específicos (bodeguero o housekeeper).
    Valida que el username y email sean únicos antes de crear el registro.
    
    Args:
        user_create (UserCreate): Datos del nuevo usuario incluyendo username, email,
                                 password, full_name, role y estado activo
        current_admin (User): Usuario administrador extraído del token JWT
        db (Session): Sesión de base de datos inyectada automáticamente
    
    Returns:
        UserSchema: Información del usuario creado (sin contraseña)
        
    Raises:
        HTTPException 400: Si el username o email ya están registrados
        HTTPException 403: Si el usuario no es administrador
        HTTPException 422: Si los datos de entrada no son válidos
        
    Security:
        - Requiere autenticación válida
        - Solo usuarios con rol ADMINISTRADOR pueden acceder
        - Valida unicidad de username y email
        
    Example:
        POST /api/v1/auth/create-user
        Authorization: Bearer <admin_token>
        {
            "username": "mbodega",
            "email": "maria.bodega@talbothotels.com",
            "password": "SecurePass123!",
            "full_name": "María Bodega",
            "role": "bodeguero",
            "is_active": true
        }
    """
    auth_service = AuthService(db)
    return auth_service.register(user_create)