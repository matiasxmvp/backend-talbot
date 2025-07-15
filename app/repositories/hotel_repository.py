# app/repositories/hotel_repository.py - Repositorio para operaciones CRUD de hoteles

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from app.models.hotel import Hotel
from app.schemas.hotel import HotelCreate, HotelUpdate
from .base_repository import BaseRepository

class HotelRepository(BaseRepository[Hotel]):
    """Repositorio para manejar operaciones CRUD de hoteles"""
    
    def __init__(self, db: Session):
        """Inicializar el repositorio con la sesión de base de datos"""
        super().__init__(db, Hotel)
        self.db = db
    
    def get_by_name(self, name: str) -> Optional[Hotel]:
        """Obtener hotel por nombre"""
        return self.db.query(Hotel).filter(Hotel.name == name).first()
    
    def get_all_active(self, skip: int = 0, limit: int = 100) -> List[Hotel]:
        """Obtener todos los hoteles activos con paginación"""
        return self.db.query(Hotel).filter(Hotel.is_active == True).offset(skip).limit(limit).all()
    
    def get_count_active(self) -> int:
        """Obtener el número total de hoteles activos"""
        return self.db.query(func.count(Hotel.id)).filter(Hotel.is_active == True).scalar()
    
    def search(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Hotel]:
        """Buscar hoteles por nombre o ubicación (incluye activos e inactivos)"""
        return self.db.query(Hotel).filter(
            (Hotel.name.ilike(f"%{search_term}%") | 
             Hotel.location.ilike(f"%{search_term}%"))
        ).offset(skip).limit(limit).all()
    
    def create(self, hotel_data: HotelCreate) -> Hotel:
        """Crear un nuevo hotel"""
        # Generar cuenta contable automáticamente si no se proporciona
        cuenta_contable = hotel_data.cuenta_contable or self._generate_cuenta_contable()
        
        # Preparar datos del hotel
        hotel_dict = {
            "name": hotel_data.name,
            "location": hotel_data.location,
            "address": hotel_data.address,
            "manager": hotel_data.manager,
            "status": hotel_data.status,
            "cuenta_contable": cuenta_contable,
            "presupuesto": hotel_data.presupuesto
        }
        
        return super().create(hotel_dict)
    
    def _generate_cuenta_contable(self) -> str:
        """Generar el siguiente código de cuenta contable"""
        # Obtener el último hotel creado para generar el siguiente código
        last_hotel = self.db.query(Hotel).order_by(Hotel.id.desc()).first()
        
        if not last_hotel or not last_hotel.cuenta_contable:
            # Si no hay hoteles o el último no tiene cuenta contable, empezar con "001"
            return "001"
        
        try:
            # Extraer el número de la cuenta contable y incrementar
            last_number = int(last_hotel.cuenta_contable)
            next_number = last_number + 1
            # Formatear con ceros a la izquierda (3 dígitos)
            return f"{next_number:03d}"
        except (ValueError, TypeError):
            # Si hay error al convertir, buscar el máximo número existente
            return self._find_next_available_cuenta_contable()
    
    def _find_next_available_cuenta_contable(self) -> str:
        """Encontrar el siguiente código de cuenta contable disponible"""
        # Obtener todas las cuentas contables existentes
        existing_codes = self.db.query(Hotel.cuenta_contable).filter(
            Hotel.cuenta_contable.isnot(None)
        ).all()
        
        # Convertir a números y encontrar el máximo
        numbers = []
        for code_tuple in existing_codes:
            try:
                numbers.append(int(code_tuple[0]))
            except (ValueError, TypeError):
                continue
        
        if not numbers:
            return "001"
        
        # Retornar el siguiente número disponible
        next_number = max(numbers) + 1
        return f"{next_number:03d}"
    
    def update(self, hotel_id: int, hotel_data: HotelUpdate) -> Optional[Hotel]:
        """Actualizar un hotel existente"""
        # Preparar datos de actualización
        update_data = hotel_data.model_dump(exclude_unset=True)
        return super().update(hotel_id, update_data)
    
    def delete(self, hotel_id: int) -> bool:
        """Eliminar un hotel (soft delete)"""
        db_hotel = self.get_by_id(hotel_id)
        if not db_hotel:
            return False
        
        db_hotel.is_active = False
        self.db.commit()
        return True
    
    def hard_delete(self, hotel_id: int) -> bool:
        """Eliminar un hotel permanentemente"""
        db_hotel = self.get_by_id(hotel_id)
        if not db_hotel:
            return False
        
        self.db.delete(db_hotel)
        self.db.commit()
        return True
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Hotel]:
        """Obtener hoteles por estado"""
        return self.db.query(Hotel).filter(
            Hotel.status == status,
            Hotel.is_active == True
        ).offset(skip).limit(limit).all()