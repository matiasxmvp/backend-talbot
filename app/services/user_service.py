# app/services/user_service.py - Servicio para gestión de usuarios

import math
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserList, User

class UserService:
    """
    Servicio para manejar la lógica de negocio relacionada con usuarios
    
    Proporciona métodos para operaciones complejas de usuarios que requieren
    lógica de negocio adicional más allá de las operaciones CRUD básicas.
    """
    
    def __init__(self, db: Session):
        """Inicializar el servicio con la sesión de base de datos"""
        self.db = db
        self.user_repository = UserRepository(db)
    
    def get_all_users(self, page: int = 1, per_page: int = 10) -> UserList:
        """
        Obtener todos los usuarios con paginación
        
        Args:
            page (int): Número de página (mínimo 1)
            per_page (int): Elementos por página (1-100)
            
        Returns:
            UserList: Lista paginada de usuarios con metadatos de paginación
        """
        # Validar parámetros de paginación
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
        
        # Calcular offset para la consulta
        skip = (page - 1) * per_page
        
        # Obtener usuarios y total
        users = self.user_repository.get_all(skip=skip, limit=per_page)
        total = self.user_repository.get_count()
        
        # Calcular total de páginas
        pages = math.ceil(total / per_page) if total > 0 else 1
        
        # Retornar respuesta estructurada
        return UserList(
            users=[User.model_validate(user, from_attributes=True) for user in users],
            total=total,
            page=page,
            per_page=per_page,
            pages=pages
        )