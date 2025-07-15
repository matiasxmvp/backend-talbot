# init_db.py - Script para inicializar la base de datos

"""Script para crear las tablas de la base de datos y un usuario administrador inicial"""

from app.db.database import create_tables, get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.core.config import settings

def init_database():
    """Inicializar la base de datos y crear un usuario administrador"""
    print("Creando tablas de la base de datos...")
    create_tables()
    print("✅ Tablas creadas exitosamente")
    
    # Crear usuario administrador por defecto
    db = next(get_db())
    user_repo = UserRepository(db)
    
    # Verificar si ya existe un usuario admin
    admin_user = user_repo.get_by_username("admin")
    if not admin_user:
        print("Creando usuario administrador por defecto...")
        admin_create = UserCreate(
            username="admin",
            email="admin@talbothotels.cl",
            password="admin123",
            full_name="Administrador",
            role="administrador",
            is_active=True
        )
        
        admin_user = user_repo.create(admin_create)
        # Hacer que sea superusuario
        admin_user.is_superuser = True
        db.commit()
        
        print("✅ Usuario administrador creado:")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print(f"   Email: admin@talbothotels.cl")
        print("   ⚠️  Cambia la contraseña después del primer login")
    else:
        print("ℹ️  Usuario administrador ya existe")
    
    db.close()
    print("\n🎉 Base de datos inicializada correctamente")
    print(f"🚀 Ejecuta 'python main.py' para iniciar la aplicación")
    print(f"📖 Documentación disponible en: http://localhost:{settings.port}/docs")

if __name__ == "__main__":
    init_database()