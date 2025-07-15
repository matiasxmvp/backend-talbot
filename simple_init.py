#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simplificado para inicialización de base de datos
Este script solo crea las tablas sin datos adicionales
"""

import os
import sys
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.db.database import create_tables, engine

def simple_init():
    """Inicialización simplificada - solo crear tablas"""
    print("🏗️  INICIALIZACIÓN SIMPLIFICADA")
    print("=" * 40)
    
    try:
        # Mostrar información de conexión
        print(f"📊 Conectando a: {settings.database_url[:50]}...")
        print(f"🌍 Entorno: {os.getenv('ENVIRONMENT', 'development')}")
        print()
        
        # Probar conexión básica
        print("🔗 Probando conexión...")
        with engine.connect() as connection:
            print("✅ Conexión exitosa")
            
        # Crear tablas
        print("🏗️  Creando tablas...")
        create_tables()
        print("✅ Tablas creadas exitosamente")
        
        # Verificar tablas creadas
        print("🔍 Verificando tablas creadas...")
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"📋 Tablas encontradas ({len(tables)}):")
        for table in tables:
            print(f"   - {table}")
            
        if 'users' in tables:
            print("✅ Tabla 'users' creada correctamente")
        else:
            print("❌ Tabla 'users' no encontrada")
            
        print("\n🎉 Inicialización simplificada completada")
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Error de SQLAlchemy: {str(e)}")
        print(f"🔍 Tipo de error: {type(e).__name__}")
        return False
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        print(f"🔍 Tipo de error: {type(e).__name__}")
        return False

def main():
    """Función principal"""
    print("🏨 TALBOT HOTELS - Inicialización Simplificada\n")
    
    success = simple_init()
    
    if success:
        print("\n✅ Proceso completado exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Proceso falló - Revisar errores arriba")
        sys.exit(1)

if __name__ == "__main__":
    main()