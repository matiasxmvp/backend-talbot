# app/services/hotel_service.py - Servicio para lógica de negocio de hoteles

from sqlalchemy.orm import Session
from typing import Optional, List
from app.repositories.hotel_repository import HotelRepository
from app.repositories.user_repository import UserRepository
from app.schemas.hotel import HotelCreate, HotelUpdate, HotelResponse, HotelList
from app.models.hotel import Hotel
from fastapi import HTTPException, status
import math

class HotelService:
    """Servicio para manejar la lógica de negocio de hoteles"""
    
    def __init__(self, db: Session):
        """Inicializar el servicio con la sesión de base de datos"""
        self.db = db
        self.hotel_repository = HotelRepository(db)
        self.user_repository = UserRepository(db)
    
    def get_hotel_by_id(self, hotel_id: int) -> HotelResponse:
        """Obtener hotel por ID"""
        hotel = self.hotel_repository.get_by_id(hotel_id)
        if not hotel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hotel no encontrado"
            )
        return HotelResponse.model_validate(hotel)
    
    def get_all_hotels(self, page: int = 1, per_page: int = 10, active_only: bool = True) -> HotelList:
        """Obtener todos los hoteles con paginación"""
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
        
        skip = (page - 1) * per_page
        if active_only:
            hotels = self.hotel_repository.get_all_active(skip=skip, limit=per_page)
            total = self.hotel_repository.get_count_active()
        else:
            hotels = self.hotel_repository.get_all(skip=skip, limit=per_page)
            total = self.hotel_repository.count()
        pages = math.ceil(total / per_page) if total > 0 else 1
        
        return HotelList(
            hotels=[HotelResponse.model_validate(hotel) for hotel in hotels],
            total=total,
            page=page,
            per_page=per_page,
            pages=pages
        )
    
    def search_hotels(self, search_term: str, page: int = 1, per_page: int = 10) -> HotelList:
        """Buscar hoteles por nombre o ubicación"""
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
        
        skip = (page - 1) * per_page
        hotels = self.hotel_repository.search(search_term, skip=skip, limit=per_page)
        
        # Para la búsqueda, contamos manualmente ya que no tenemos un método específico
        total_hotels = self.hotel_repository.search(search_term, skip=0, limit=1000)
        total = len(total_hotels)
        pages = math.ceil(total / per_page) if total > 0 else 1
        
        return HotelList(
            hotels=[HotelResponse.model_validate(hotel) for hotel in hotels],
            total=total,
            page=page,
            per_page=per_page,
            pages=pages
        )
    
    def create_hotel(self, hotel_data: HotelCreate) -> HotelResponse:
        """Crear un nuevo hotel"""
        # Verificar si ya existe un hotel con el mismo nombre
        existing_hotel = self.hotel_repository.get_by_name(hotel_data.name)
        if existing_hotel:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un hotel con este nombre"
            )
        
        hotel = self.hotel_repository.create(hotel_data)
        return HotelResponse.model_validate(hotel)
    
    def update_hotel(self, hotel_id: int, hotel_data: HotelUpdate) -> HotelResponse:
        """Actualizar un hotel existente"""
        # Verificar si el hotel existe
        existing_hotel = self.hotel_repository.get_by_id(hotel_id)
        if not existing_hotel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hotel no encontrado"
            )
        
        # Si se está actualizando el nombre, verificar que no exista otro hotel con ese nombre
        if hotel_data.name and hotel_data.name != existing_hotel.name:
            name_exists = self.hotel_repository.get_by_name(hotel_data.name)
            if name_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un hotel con este nombre"
                )
        
        updated_hotel = self.hotel_repository.update(hotel_id, hotel_data)
        return HotelResponse.model_validate(updated_hotel)
    
    def delete_hotel(self, hotel_id: int) -> dict:
        """Eliminar un hotel permanentemente (hard delete)"""
        # Verificar que el hotel existe
        hotel = self.hotel_repository.get_by_id(hotel_id)
        if not hotel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hotel no encontrado"
            )
        
        # Actualizar usuarios asociados al hotel (establecer hotel_id a NULL)
        affected_users = self.user_repository.update_users_hotel_to_null(hotel_id)
        
        # Eliminar el hotel
        success = self.hotel_repository.hard_delete(hotel_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar el hotel"
            )
        
        message = f"Hotel eliminado exitosamente"
        if affected_users > 0:
            message += f". Se actualizaron {affected_users} usuarios asociados."
        
        return {"message": message}
    
    def get_hotels_by_status(self, status: str, page: int = 1, per_page: int = 10) -> HotelList:
        """Obtener hoteles por estado"""
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
        
        skip = (page - 1) * per_page
        hotels = self.hotel_repository.get_by_status(status, skip=skip, limit=per_page)
        
        # Contar hoteles por estado
        all_status_hotels = self.hotel_repository.get_by_status(status, skip=0, limit=1000)
        total = len(all_status_hotels)
        pages = math.ceil(total / per_page) if total > 0 else 1
        
        return HotelList(
            hotels=[HotelResponse.model_validate(hotel) for hotel in hotels],
            total=total,
            page=page,
            per_page=per_page,
            pages=pages
        )
    
    def get_hotel_stats(self) -> dict:
        """Obtener estadísticas de hoteles"""
        total_hotels = self.hotel_repository.count()
        active_hotels = self.hotel_repository.get_count_active()
        inactive_hotels = total_hotels - active_hotels
        
        active_by_status = {
            "active": len(self.hotel_repository.get_by_status("active", limit=1000)),
            "maintenance": len(self.hotel_repository.get_by_status("maintenance", limit=1000)),
            "inactive": len(self.hotel_repository.get_by_status("inactive", limit=1000))
        }
        
        return {
            "total_hotels": total_hotels,
            "active_hotels": active_hotels,
            "inactive_hotels": inactive_hotels,
            "by_status": active_by_status
        }