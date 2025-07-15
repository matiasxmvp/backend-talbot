# seed_data.py - Script para poblar la base de datos con datos de ejemplo

from sqlalchemy.orm import Session
from app.db.database import get_db, create_tables
from app.repositories.user_repository import UserRepository
from app.repositories.hotel_repository import HotelRepository
from app.schemas.user import UserCreate
from app.schemas.hotel import HotelCreate
from app.models.user import UserRole
from app.core.security import get_password_hash

def seed_hotels(db: Session):
    """Crear hoteles de ejemplo"""
    hotel_repo = HotelRepository(db)
    
    hotels_data = [
        {
            "name": "Talbot Hotels Corporativo",
            "location": "Santiago",
            "address": "El Bosque Norte #0440",
            "rooms": 120,
            "manager": "Administrador",
            "phone": "+56 2 2345 6789",
            "description": "Hotel corporativo Talbot en Santiago",
            "status": "active"
        },
        {
            "name": "Hyatt Centric Las Condes Santiago",
            "location": "Santiago",
            "address": "Enrique Foster 30",
            "rooms": 85,
            "manager": "Administrador",
            "phone": "+56 2 2345 6790",
            "description": "Hotel Hyatt Centric en Las Condes",
            "status": "active"
        },
        {
            "name": "Holiday Inn Aeropuerto Terminal Santiago",
            "location": "Santiago",
            "address": "Armando Cortinez Norte #2150",
            "rooms": 95,
            "manager": "Administrador",
            "phone": "+56 2 2345 6791",
            "description": "Holiday Inn cerca del aeropuerto de Santiago",
            "status": "active"
        },
        {
            "name": "Holiday Inn Express Las Condes Santiago",
            "location": "Santiago",
            "address": "Av. Vitacura #2929",
            "rooms": 110,
            "manager": "Administrador",
            "phone": "+56 2 2345 6792",
            "description": "Holiday Inn Express en Las Condes",
            "status": "active"
        },
        {
            "name": "Holiday Inn Express Concepción",
            "location": "Concepción",
            "address": "San Andrés #38",
            "rooms": 75,
            "manager": "Administrador",
            "phone": "+56 41 224 0000",
            "description": "Holiday Inn Express en Concepción",
            "status": "active"
        },
        {
            "name": "Holiday Inn Express Temuco",
            "location": "Temuco",
            "address": "Av. Ortega #01800",
            "rooms": 90,
            "manager": "Administrador",
            "phone": "+56 45 221 2000",
            "description": "Holiday Inn Express en Temuco",
            "status": "active"
        },
        {
            "name": "Holiday Inn Express Iquique",
            "location": "Iquique",
            "address": "Av. Arturo Prat #1690",
            "rooms": 65,
            "manager": "Administrador",
            "phone": "+56 57 241 0000",
            "description": "Holiday Inn Express en Iquique",
            "status": "active"
        },
        {
            "name": "Holiday Inn Express Antofagasta",
            "location": "Antofagasta",
            "address": "Av. Grecia #1490",
            "rooms": 80,
            "manager": "Administrador",
            "phone": "+56 55 245 8000",
            "description": "Holiday Inn Express en Antofagasta",
            "status": "active"
        },
        {
            "name": "Holiday Inn Express Valparaíso",
            "location": "Valparaíso",
            "address": "Av. Brasil #1532",
            "rooms": 70,
            "manager": "Administrador",
            "phone": "+56 32 225 4000",
            "description": "Holiday Inn Express en el puerto de Valparaíso",
            "status": "active"
        },
        {
            "name": "Holiday Inn Express La Serena",
            "location": "La Serena",
            "address": "Av. Francisco de Aguirre #170",
            "rooms": 85,
            "manager": "Administrador",
            "phone": "+56 51 221 8000",
            "description": "Holiday Inn Express en La Serena, cerca de las playas",
            "status": "active"
        },
        {
            "name": "Holiday Inn Express Puerto Montt",
            "location": "Puerto Montt",
            "address": "Av. Presidente Ibáñez #1462",
            "rooms": 95,
            "manager": "Administrador",
            "phone": "+56 65 225 6000",
            "description": "Holiday Inn Express en Puerto Montt, puerta de entrada a la Patagonia",
            "status": "active"
        }
    ]
    
    for hotel_data in hotels_data:
        # Verificar si el hotel ya existe
        existing_hotel = hotel_repo.get_by_name(hotel_data["name"])
        if not existing_hotel:
            hotel_create = HotelCreate(**hotel_data)
            hotel_repo.create(hotel_create)
            print(f"✅ Hotel creado: {hotel_data['name']}")
        else:
            print(f"⚠️  Hotel ya existe: {hotel_data['name']}")

def seed_users(db: Session):
    """Crear usuarios de ejemplo"""
    user_repo = UserRepository(db)
    
    users_data = [
        {
            "username": "maria.gonzalez",
            "email": "maria.gonzalez@talbothotels.com",
            "full_name": "María González",
            "password": "password123",
            "role": UserRole.HOUSEKEEPER,
            "is_active": True
        },
        {
            "username": "carlos.ruiz",
            "email": "carlos.ruiz@talbothotels.com",
            "full_name": "Carlos Ruiz",
            "password": "password123",
            "role": UserRole.JEFE_RECEPCION,
            "is_active": True
        },
        {
            "username": "ana.morales",
            "email": "ana.morales@talbothotels.com",
            "full_name": "Ana Morales",
            "password": "password123",
            "role": UserRole.GERENTE,
            "is_active": True
        },
        {
            "username": "pedro.silva",
            "email": "pedro.silva@talbothotels.com",
            "full_name": "Pedro Silva",
            "password": "password123",
            "role": UserRole.CONTROLLER,
            "is_active": True
        },
        {
            "username": "laura.diaz",
            "email": "laura.diaz@talbothotels.com",
            "full_name": "Laura Díaz",
            "password": "password123",
            "role": UserRole.ADMIN_BODEGA,
            "is_active": True
        },
        {
            "username": "roberto.vega",
            "email": "roberto.vega@talbothotels.com",
            "full_name": "Roberto Vega",
            "password": "password123",
            "role": UserRole.HOUSEKEEPER,
            "is_active": True
        },
        {
            "username": "jose.ramirez",
            "email": "jose.ramirez@talbothotels.com",
            "full_name": "José Ramírez",
            "password": "password123",
            "role": UserRole.GERENTE,
            "is_active": True
        },
        {
            "username": "carmen.torres",
            "email": "carmen.torres@talbothotels.com",
            "full_name": "Carmen Torres",
            "password": "password123",
            "role": UserRole.JEFE_RECEPCION,
            "is_active": True
        },
        {
            "username": "francisco.lopez",
            "email": "francisco.lopez@talbothotels.com",
            "full_name": "Francisco López",
            "password": "password123",
            "role": UserRole.ADMIN_BODEGA,
            "is_active": True
        },
        {
            "username": "monica.herrera",
            "email": "monica.herrera@talbothotels.com",
            "full_name": "Mónica Herrera",
            "password": "password123",
            "role": UserRole.HOUSEKEEPER,
            "is_active": True
        }
    ]
    
    for user_data in users_data:
        # Verificar si el usuario ya existe
        existing_user = user_repo.get_by_username(user_data["username"])
        if not existing_user:
            # Crear el usuario
            hashed_password = get_password_hash(user_data["password"])
            user_create_data = {
                "username": user_data["username"],
                "email": user_data["email"],
                "full_name": user_data["full_name"],
                "hashed_password": hashed_password,
                "role": user_data["role"],
                "is_active": user_data["is_active"]
            }
            
            from app.models.user import User
            db_user = User(**user_create_data)
            db.add(db_user)
            db.commit()
            print(f"✅ Usuario creado: {user_data['username']} ({user_data['role'].value})")
        else:
            print(f"⚠️  Usuario ya existe: {user_data['username']}")

def main():
    """Función principal para poblar la base de datos"""
    print("🌱 Iniciando población de la base de datos...")
    
    # Asegurar que las tablas existen
    create_tables()
    
    # Obtener sesión de base de datos
    db = next(get_db())
    
    try:
        # Poblar hoteles
        print("\n📍 Creando hoteles...")
        seed_hotels(db)
        
        # Poblar usuarios
        print("\n👥 Creando usuarios...")
        seed_users(db)
        
        print("\n✅ Base de datos poblada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error al poblar la base de datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()