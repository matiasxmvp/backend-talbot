# app/api/routers/hotels.py - Endpoints para gestión de hoteles

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.services.hotel_service import HotelService
from app.schemas.hotel import HotelCreate, HotelUpdate, HotelResponse, HotelList
from app.core.dependencies import get_current_admin_user, get_current_user
from app.models.user import User

router = APIRouter(prefix="/hotels", tags=["hotels"])

@router.get("/", response_model=HotelList)
async def get_hotels(
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(10, ge=1, le=100, description="Elementos por página"),
    active_only: bool = Query(True, description="Solo hoteles activos"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de hoteles con paginación
    
    Endpoint para obtener todos los hoteles del sistema con soporte
    para paginación y filtrado por estado activo.
    
    Args:
        page: Número de página (mínimo 1)
        per_page: Elementos por página (1-100)
        active_only: Si solo mostrar hoteles activos
        current_user: Usuario autenticado
        db: Sesión de base de datos
    
    Returns:
        HotelList: Lista paginada de hoteles
    """
    hotel_service = HotelService(db)
    return hotel_service.get_all_hotels(page=page, per_page=per_page, active_only=active_only)

@router.get("/search", response_model=HotelList)
async def search_hotels(
    q: str = Query(..., min_length=1, description="Término de búsqueda"),
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(10, ge=1, le=100, description="Elementos por página"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Buscar hoteles por nombre o ubicación
    
    Endpoint para buscar hoteles utilizando un término de búsqueda
    que se aplica tanto al nombre como a la ubicación.
    
    Args:
        q: Término de búsqueda
        page: Número de página
        per_page: Elementos por página
        current_user: Usuario autenticado
        db: Sesión de base de datos
    
    Returns:
        HotelList: Lista paginada de hoteles que coinciden con la búsqueda
    """
    hotel_service = HotelService(db)
    return hotel_service.search_hotels(search_term=q, page=page, per_page=per_page)

@router.get("/stats")
async def get_hotel_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de hoteles
    
    Endpoint para obtener estadísticas generales de los hoteles
    en el sistema. Requiere permisos de administrador.
    
    Args:
        current_user: Usuario administrador autenticado
        db: Sesión de base de datos
    
    Returns:
        dict: Estadísticas de hoteles
    """
    hotel_service = HotelService(db)
    return hotel_service.get_hotel_stats()

@router.get("/status/{status}", response_model=HotelList)
async def get_hotels_by_status(
    status: str,
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(10, ge=1, le=100, description="Elementos por página"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener hoteles por estado
    
    Endpoint para filtrar hoteles por su estado específico
    (active, maintenance, inactive).
    
    Args:
        status: Estado del hotel
        page: Número de página
        per_page: Elementos por página
        current_user: Usuario autenticado
        db: Sesión de base de datos
    
    Returns:
        HotelList: Lista paginada de hoteles con el estado especificado
    """
    hotel_service = HotelService(db)
    return hotel_service.get_hotels_by_status(status=status, page=page, per_page=per_page)

@router.get("/{hotel_id}", response_model=HotelResponse)
async def get_hotel(
    hotel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener hotel por ID
    
    Endpoint para obtener los detalles completos de un hotel específico.
    
    Args:
        hotel_id: ID del hotel
        current_user: Usuario autenticado
        db: Sesión de base de datos
    
    Returns:
        HotelResponse: Detalles del hotel
    
    Raises:
        HTTPException: Si el hotel no existe
    """
    hotel_service = HotelService(db)
    return hotel_service.get_hotel_by_id(hotel_id)

@router.post("/", response_model=HotelResponse, status_code=status.HTTP_201_CREATED)
async def create_hotel(
    hotel_data: HotelCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo hotel
    
    Endpoint para crear un nuevo hotel en el sistema.
    Requiere permisos de administrador.
    
    Args:
        hotel_data: Datos del hotel a crear
        current_user: Usuario administrador autenticado
        db: Sesión de base de datos
    
    Returns:
        HotelResponse: Hotel creado
    
    Raises:
        HTTPException: Si ya existe un hotel con el mismo nombre
    """
    hotel_service = HotelService(db)
    return hotel_service.create_hotel(hotel_data)

@router.put("/{hotel_id}", response_model=HotelResponse)
async def update_hotel(
    hotel_id: int,
    hotel_data: HotelUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar un hotel existente
    
    Endpoint para actualizar los datos de un hotel existente.
    Requiere permisos de administrador.
    
    Args:
        hotel_id: ID del hotel a actualizar
        hotel_data: Datos actualizados del hotel
        current_user: Usuario administrador autenticado
        db: Sesión de base de datos
    
    Returns:
        HotelResponse: Hotel actualizado
    
    Raises:
        HTTPException: Si el hotel no existe o el nombre ya está en uso
    """
    hotel_service = HotelService(db)
    return hotel_service.update_hotel(hotel_id, hotel_data)

@router.delete("/{hotel_id}")
async def delete_hotel(
    hotel_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar un hotel
    
    Endpoint para eliminar un hotel del sistema (soft delete).
    Requiere permisos de administrador.
    
    Args:
        hotel_id: ID del hotel a eliminar
        current_user: Usuario administrador autenticado
        db: Sesión de base de datos
    
    Returns:
        dict: Mensaje de confirmación
    
    Raises:
        HTTPException: Si el hotel no existe
    """
    hotel_service = HotelService(db)
    return hotel_service.delete_hotel(hotel_id)