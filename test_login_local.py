#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el login localmente
"""

import os
import sys
import requests
import json
from app.core.config import settings

def test_login_local():
    """Probar el login del administrador localmente"""
    try:
        # URL del endpoint de login
        base_url = "http://localhost:8000"  # Cambia esto si tu servidor local usa otro puerto
        login_url = f"{base_url}/api/auth/login"
        
        print("🔐 Probando login del administrador...")
        print(f"📍 URL: {login_url}")
        
        # Credenciales a probar
        credentials_to_test = [
            {"username": "admin", "password": "admin123"},
            {"username": "admin", "password": os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")},
        ]
        
        for i, creds in enumerate(credentials_to_test, 1):
            print(f"\n🧪 Prueba {i}: {creds['username']}/{creds['password']}")
            
            try:
                # Hacer petición POST al endpoint de login
                response = requests.post(
                    login_url,
                    data={
                        "username": creds["username"],
                        "password": creds["password"]
                    },
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    timeout=10
                )
                
                print(f"   📊 Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ LOGIN EXITOSO")
                    try:
                        data = response.json()
                        print(f"   🎫 Token recibido: {data.get('access_token', 'N/A')[:50]}...")
                        print(f"   👤 Usuario: {data.get('user', {}).get('username', 'N/A')}")
                        print(f"   🏷️  Rol: {data.get('user', {}).get('role', 'N/A')}")
                    except:
                        print("   📄 Respuesta no es JSON válido")
                        print(f"   📝 Respuesta: {response.text[:200]}")
                elif response.status_code == 401:
                    print("   ❌ CREDENCIALES INCORRECTAS")
                    try:
                        error_data = response.json()
                        print(f"   💬 Mensaje: {error_data.get('detail', 'Sin mensaje')}")
                    except:
                        print(f"   📝 Respuesta: {response.text}")
                else:
                    print(f"   ⚠️  Error inesperado: {response.status_code}")
                    print(f"   📝 Respuesta: {response.text[:200]}")
                    
            except requests.exceptions.ConnectionError:
                print("   ❌ No se pudo conectar al servidor")
                print("   💡 Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
            except requests.exceptions.Timeout:
                print("   ⏰ Timeout - El servidor tardó demasiado en responder")
            except Exception as e:
                print(f"   ❌ Error inesperado: {str(e)}")
        
        print("\n📋 Instrucciones:")
        print("   1. Si el login es exitoso, las credenciales están correctas")
        print("   2. Si falla con 401, verifica que el usuario admin existe en la BD")
        print("   3. Si falla la conexión, inicia el servidor con: python application.py")
        
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        import traceback
        traceback.print_exc()

def test_with_production_url():
    """Probar con la URL de producción de Elastic Beanstalk"""
    production_url = input("\n🌐 Ingresa la URL de tu aplicación en Elastic Beanstalk (ej: http://tu-app.elasticbeanstalk.com): ").strip()
    
    if not production_url:
        print("❌ URL no proporcionada")
        return
    
    if not production_url.startswith("http"):
        production_url = f"http://{production_url}"
    
    login_url = f"{production_url}/api/auth/login"
    
    print(f"\n🔐 Probando login en producción...")
    print(f"📍 URL: {login_url}")
    
    creds = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post(
            login_url,
            data=creds,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ LOGIN EXITOSO EN PRODUCCIÓN")
            data = response.json()
            print(f"👤 Usuario: {data.get('user', {}).get('username', 'N/A')}")
        elif response.status_code == 401:
            print("❌ CREDENCIALES INCORRECTAS EN PRODUCCIÓN")
            print("💡 Revisa los logs de Elastic Beanstalk para más detalles")
        else:
            print(f"⚠️  Error: {response.status_code}")
            print(f"📝 Respuesta: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error al conectar con producción: {str(e)}")

if __name__ == "__main__":
    print("🧪 Test de Login - Talbot Hotels")
    print("=" * 40)
    
    choice = input("\n¿Dónde quieres probar el login?\n1. Local (localhost:8000)\n2. Producción (Elastic Beanstalk)\n3. Ambos\nElige (1/2/3): ").strip()
    
    if choice in ["1", "3"]:
        test_login_local()
    
    if choice in ["2", "3"]:
        test_with_production_url()
    
    if choice not in ["1", "2", "3"]:
        print("❌ Opción inválida")