#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar las credenciales del usuario administrador
"""

import os
import sys
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.core.security import verify_password
from app.core.config import settings

def verify_admin_credentials():
    """Verificar las credenciales del usuario administrador"""
    try:
        print("🔍 Verificando credenciales del administrador...")
        print(f"📊 Conectando a: {settings.database_url[:50]}...")
        
        # Obtener conexión a la base de datos
        db = next(get_db())
        user_repo = UserRepository(db)
        auth_service = AuthService(db)
        
        # Buscar usuario admin
        print("\n👤 Buscando usuario 'admin'...")
        admin_user = user_repo.get_by_username("admin")
        
        if not admin_user:
            print("❌ Usuario 'admin' no encontrado en la base de datos")
            
            # Listar todos los usuarios
            print("\n📋 Usuarios existentes en la base de datos:")
            all_users = db.query(user_repo.model).all()
            if all_users:
                for user in all_users:
                    print(f"   - Username: {user.username}, Email: {user.email}, Role: {user.role}")
            else:
                print("   No hay usuarios en la base de datos")
            return
        
        print(f"✅ Usuario 'admin' encontrado:")
        print(f"   - ID: {admin_user.id}")
        print(f"   - Username: {admin_user.username}")
        print(f"   - Email: {admin_user.email}")
        print(f"   - Full Name: {admin_user.full_name}")
        print(f"   - Role: {admin_user.role}")
        print(f"   - Is Active: {admin_user.is_active}")
        print(f"   - Is Superuser: {admin_user.is_superuser}")
        print(f"   - Created At: {admin_user.created_at}")
        
        # Verificar contraseñas
        print("\n🔐 Verificando contraseñas...")
        
        # Contraseña por defecto
        default_password = "admin123"
        print(f"   Probando contraseña por defecto: '{default_password}'")
        
        # Verificar directamente con el hash
        is_valid_direct = verify_password(default_password, admin_user.hashed_password)
        print(f"   ✓ Verificación directa: {'✅ VÁLIDA' if is_valid_direct else '❌ INVÁLIDA'}")
        
        # Verificar con el servicio de autenticación
        authenticated_user = auth_service.authenticate_user("admin", default_password)
        print(f"   ✓ Autenticación con servicio: {'✅ EXITOSA' if authenticated_user else '❌ FALLIDA'}")
        
        # Verificar con variable de entorno
        env_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
        if env_password != default_password:
            print(f"\n   Probando contraseña de variable de entorno: '{env_password}'")
            is_valid_env = verify_password(env_password, admin_user.hashed_password)
            print(f"   ✓ Verificación con env: {'✅ VÁLIDA' if is_valid_env else '❌ INVÁLIDA'}")
            
            authenticated_user_env = auth_service.authenticate_user("admin", env_password)
            print(f"   ✓ Autenticación con env: {'✅ EXITOSA' if authenticated_user_env else '❌ FALLIDA'}")
        
        # Mostrar información del hash
        print(f"\n🔒 Hash de contraseña: {admin_user.hashed_password[:50]}...")
        
        print("\n📝 Resumen:")
        if is_valid_direct:
            print(f"   ✅ Las credenciales admin/{default_password} son CORRECTAS")
        else:
            print(f"   ❌ Las credenciales admin/{default_password} son INCORRECTAS")
            print(f"   💡 Posibles causas:")
            print(f"      - La contraseña fue cambiada después de la creación")
            print(f"      - Hay un problema con el hash de la contraseña")
            print(f"      - Se usó una contraseña diferente durante la creación")
        
    except Exception as e:
        print(f"❌ Error al verificar credenciales: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_admin_credentials()