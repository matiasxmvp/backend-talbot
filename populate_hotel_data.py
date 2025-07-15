#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para poblar los campos cuenta_contable y presupuesto de los hoteles existentes

Este script actualiza los hoteles que no tienen datos en los campos:
- cuenta_contable: Genera códigos únicos secuenciales
- presupuesto: Asigna presupuestos aleatorios realistas
"""

import random
from app.db.database import SessionLocal
from app.models.hotel import Hotel
from sqlalchemy.orm import Session

# Presupuestos de ejemplo para diferentes tipos de hoteles (en pesos chilenos)
PRESUPUESTOS_EJEMPLO = [
    15000000,   # 15 millones
    25000000,   # 25 millones
    35000000,   # 35 millones
    45000000,   # 45 millones
    55000000,   # 55 millones
    75000000,   # 75 millones
    100000000,  # 100 millones
    150000000,  # 150 millones
]

def poblar_datos_hoteles():
    """
    Pobla los campos cuenta_contable y presupuesto de los hoteles existentes
    """
    print("🏨 Iniciando población de datos de hoteles...")
    
    # Crear sesión de base de datos
    session = SessionLocal()
    
    try:
        # Obtener todos los hoteles
        hoteles = session.query(Hotel).order_by(Hotel.id).all()
        
        if not hoteles:
            print("❌ No se encontraron hoteles en la base de datos")
            return
        
        print(f"📋 Encontrados {len(hoteles)} hoteles")
        
        # Contador para códigos contables
        codigo_contador = 1
        hoteles_actualizados = 0
        
        for hotel in hoteles:
            actualizado = False
            
            # Generar cuenta_contable si no existe
            if not hotel.cuenta_contable:
                # Generar código único con formato "H001", "H002", etc.
                while True:
                    nuevo_codigo = f"H{codigo_contador:03d}"
                    
                    # Verificar que el código no exista
                    existe = session.query(Hotel).filter(Hotel.cuenta_contable == nuevo_codigo).first()
                    if not existe:
                        hotel.cuenta_contable = nuevo_codigo
                        actualizado = True
                        break
                    codigo_contador += 1
                
                codigo_contador += 1
            
            # Asignar presupuesto si no existe o es 0
            if not hotel.presupuesto or hotel.presupuesto == 0:
                # Asignar un presupuesto aleatorio de la lista
                hotel.presupuesto = random.choice(PRESUPUESTOS_EJEMPLO)
                actualizado = True
            
            if actualizado:
                hoteles_actualizados += 1
                print(f"✅ Hotel '{hotel.name}' actualizado:")
                print(f"   - Cuenta contable: {hotel.cuenta_contable}")
                print(f"   - Presupuesto: ${hotel.presupuesto:,}")
        
        # Guardar cambios
        if hoteles_actualizados > 0:
            session.commit()
            print(f"\n🎉 ¡Población completada! {hoteles_actualizados} hoteles actualizados")
        else:
            print("\n✨ Todos los hoteles ya tienen datos completos")
            
    except Exception as e:
        session.rollback()
        print(f"❌ Error durante la población: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Ejecutando script de población de datos de hoteles...")
    poblar_datos_hoteles()
    print("✅ Script completado")