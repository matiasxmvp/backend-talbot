#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script consolidado para configuración completa de la base de datos

Este script unifica las funcionalidades de:
- init_db.py: Inicialización de tablas y usuario admin
- seed_data.py: Datos de ejemplo para desarrollo
- populate_hotel_data.py: Población de datos específicos de hoteles

Uso:
    python setup_database.py [--mode MODE]
    
Modos disponibles:
    - init: Solo crear tablas y usuario admin (por defecto)
    - seed: Crear tablas, usuario admin y datos de ejemplo
    - populate: Solo poblar datos faltantes en hoteles existentes
    - full: Ejecutar todo (init + seed + populate)
"""

import argparse
import random
import os
from sqlalchemy.orm import Session
from app.db.database import create_tables, get_db
from app.repositories.user_repository import UserRepository
from app.repositories.hotel_repository import HotelRepository
from app.schemas.user import UserCreate
from app.schemas.hotel import HotelCreate
from app.models.user import UserRole
from app.models.hotel import Hotel
from app.core.config import settings

# Datos de ejemplo para hoteles
HOTELES_EJEMPLO = [
    {
        "name": "Talbot Hotels Corporativo",
        "location": "Santiago",
        "address": "El Bosque Norte #0440",
        "rooms": 120,
        "manager": "Administrador",
        "phone": "+56 2 2345 6789",
        "description": "Hotel corporativo Talbot en Santiago",
        "status": "active",
        "presupuesto": 75000000
    },
    {
        "name": "Hyatt Centric Las Condes Santiago",
        "location": "Santiago",
        "address": "Enrique Foster 30",
        "rooms": 85,
        "manager": "Administrador",
        "phone": "+56 2 2345 6790",
        "description": "Hotel Hyatt Centric en Las Condes",
        "status": "active",
        "presupuesto": 65000000
    },
    {
        "name": "Holiday Inn Aeropuerto Terminal Santiago",
        "location": "Santiago",
        "address": "Armando Cortinez Norte #2150",
        "rooms": 95,
        "manager": "Administrador",
        "phone": "+56 2 2345 6791",
        "description": "Holiday Inn cerca del aeropuerto de Santiago",
        "status": "active",
        "presupuesto": 55000000
    }
]

# Usuarios de ejemplo
# Las contraseñas se obtienen de variables de entorno para mayor seguridad
# Si no están definidas, se usan valores por defecto (solo para desarrollo)
USUARIOS_EJEMPLO = [
    {
        "username": "gerente_santiago",
        "email": "gerente.santiago@talbothotels.cl",
        "password": os.getenv("DEFAULT_MANAGER_PASSWORD", "gerente123"),
        "full_name": "María González",
        "role": UserRole.GERENTE,
        "is_active": True
    },
    {
        "username": "housekeeper_1",
        "email": "housekeeper1@talbothotels.cl",
        "password": os.getenv("DEFAULT_HOUSEKEEPER_PASSWORD", "house123"),
        "full_name": "Ana Martínez",
        "role": UserRole.HOUSEKEEPER,
        "is_active": True
    },
    {
        "username": "controller_1",
        "email": "controller1@talbothotels.cl",
        "password": os.getenv("DEFAULT_CONTROLLER_PASSWORD", "control123"),
        "full_name": "Carlos Rodríguez",
        "role": UserRole.CONTROLLER,
        "is_active": True
    }
]

# Presupuestos de ejemplo para población
PRESUPUESTOS_EJEMPLO = [
    15000000, 25000000, 35000000, 45000000,
    55000000, 75000000, 100000000, 150000000
]

def init_database():
    """Inicializar la base de datos y crear usuario administrador"""
    try:
        print("🏗️  Creando tablas de la base de datos...")
        print(f"📊 Conectando a: {settings.database_url[:50]}...")
        create_tables()
        print("✅ Tablas creadas exitosamente")
    except Exception as e:
        print(f"❌ Error al crear tablas: {str(e)}")
        print(f"🔍 URL de base de datos: {settings.database_url}")
        raise
    
    # Crear usuario administrador por defecto
    try:
        print("🔗 Obteniendo conexión a la base de datos...")
        db = next(get_db())
        user_repo = UserRepository(db)
        
        try:
            # Verificar si ya existe un usuario admin
            print("🔍 Verificando si existe usuario admin...")
            admin_user = user_repo.get_by_username("admin")
            if not admin_user:
                print("👤 Creando usuario administrador por defecto...")
                admin_create = UserCreate(
                    username="admin",
                    email="admin@talbothotels.cl",
                    password=os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123"),
                    full_name="Administrador",
                    role=UserRole.ADMINISTRADOR,
                    is_active=True
                )
                
                admin_user = user_repo.create(admin_create)
                # Hacer que sea superusuario
                admin_user.is_superuser = True
                db.commit()
                
                print("✅ Usuario administrador creado:")
                print(f"   Username: admin")
                print(f"   Password: {os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin123')}")
                print(f"   Email: admin@talbothotels.cl")
                print("   ⚠️  Cambia la contraseña después del primer login")
            else:
                print("ℹ️  Usuario administrador ya existe")
        except Exception as e:
            print(f"❌ Error al crear usuario administrador: {str(e)}")
            raise
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Error al conectar con la base de datos: {str(e)}")
        raise

def seed_data():
    """Poblar la base de datos con datos de ejemplo"""
    print("🌱 Poblando datos de ejemplo...")
    
    db = next(get_db())
    user_repo = UserRepository(db)
    hotel_repo = HotelRepository(db)
    
    try:
        # Crear usuarios de ejemplo
        print("👥 Creando usuarios de ejemplo...")
        for user_data in USUARIOS_EJEMPLO:
            existing_user = user_repo.get_by_username(user_data["username"])
            if not existing_user:
                user_create = UserCreate(**user_data)
                user_repo.create(user_create)
                print(f"   ✅ Usuario creado: {user_data['username']}")
            else:
                print(f"   ℹ️  Usuario ya existe: {user_data['username']}")
        
        # Crear hoteles de ejemplo
        print("🏨 Creando hoteles de ejemplo...")
        for hotel_data in HOTELES_EJEMPLO:
            existing_hotel = hotel_repo.get_by_name(hotel_data["name"])
            if not existing_hotel:
                hotel_create = HotelCreate(**hotel_data)
                hotel_repo.create(hotel_create)
                print(f"   ✅ Hotel creado: {hotel_data['name']}")
            else:
                print(f"   ℹ️  Hotel ya existe: {hotel_data['name']}")
                
    finally:
        db.close()

def populate_hotel_data():
    """Poblar campos faltantes en hoteles existentes"""
    print("🔧 Poblando datos faltantes en hoteles...")
    
    db = next(get_db())
    
    try:
        # Obtener todos los hoteles
        hoteles = db.query(Hotel).order_by(Hotel.id).all()
        
        if not hoteles:
            print("❌ No se encontraron hoteles en la base de datos")
            return
        
        print(f"📋 Encontrados {len(hoteles)} hoteles")
        
        codigo_contador = 1
        hoteles_actualizados = 0
        
        for hotel in hoteles:
            actualizado = False
            
            # Actualizar cuenta contable si está vacía
            if not hotel.cuenta_contable:
                hotel.cuenta_contable = f"HOTEL-{codigo_contador:03d}"
                codigo_contador += 1
                actualizado = True
            
            # Actualizar presupuesto si está vacío o es 0
            if not hotel.presupuesto or hotel.presupuesto == 0:
                hotel.presupuesto = random.choice(PRESUPUESTOS_EJEMPLO)
                actualizado = True
            
            if actualizado:
                hoteles_actualizados += 1
                print(f"   ✅ Actualizado: {hotel.name}")
        
        if hoteles_actualizados > 0:
            db.commit()
            print(f"✅ {hoteles_actualizados} hoteles actualizados")
        else:
            print("ℹ️  No se requirieron actualizaciones")
            
    finally:
        db.close()

def main():
    """Función principal del script"""
    parser = argparse.ArgumentParser(
        description="Script consolidado para configuración de base de datos Talbot Hotels"
    )
    parser.add_argument(
        "--mode",
        choices=["init", "seed", "populate", "full"],
        default="init",
        help="Modo de ejecución (default: init)"
    )
    
    args = parser.parse_args()
    
    print("🏨 TALBOT HOTELS - Configuración de Base de Datos")
    print("=" * 50)
    
    if args.mode in ["init", "full"]:
        init_database()
        print()
    
    if args.mode in ["seed", "full"]:
        seed_data()
        print()
    
    if args.mode in ["populate", "full"]:
        populate_hotel_data()
        print()
    
    print("🎉 Configuración completada")
    print(f"🚀 Ejecuta 'python main.py' para iniciar la aplicación")
    print(f"📖 Documentación disponible en: http://localhost:{settings.port}/docs")

if __name__ == "__main__":
    main()