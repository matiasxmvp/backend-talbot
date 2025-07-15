# app/repositories/base_repository.py - Repositorio base para evitar duplicación

from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Optional, List, Type

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Repositorio base con operaciones CRUD comunes"""
    
    def __init__(self, db: Session, model: Type[T]):
        """Inicializar repositorio base"""
        self.db = db
        self.model = model
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Obtener por ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Obtener todos los registros"""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, obj_data: dict) -> T:
        """Crear nuevo registro"""
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, id: int, obj_data: dict) -> Optional[T]:
        """Actualizar registro existente"""
        db_obj = self.get_by_id(id)
        if db_obj:
            for field, value in obj_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> bool:
        """Eliminar registro"""
        db_obj = self.get_by_id(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False
    
    def count(self) -> int:
        """Contar registros"""
        return self.db.query(self.model).count()
    
    def exists(self, id: int) -> bool:
        """Verificar si existe un registro"""
        return self.db.query(self.model).filter(self.model.id == id).first() is not None
