#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test para verificar que obtener_paquetes_por_tipo_nodo funciona correctamente
"""

import sys
sys.path.insert(0, '.')

from paquetes import obtener_paquetes_por_tipo_nodo

def test_paquetes_la_paz():
    """Test obtener paquetes de La Paz"""
    print("\n=== Test La Paz ===")
    resultado = obtener_paquetes_por_tipo_nodo('lapaz')
    
    print(f"Paquetes Operativos: {len(resultado['operativos'])} registros")
    if resultado['operativos']:
        print(f"  Primer registro: {resultado['operativos'][0]}")
    
    print(f"Paquetes Financieros: {len(resultado['financieros'])} registros")
    if resultado['financieros']:
        print(f"  Primer registro: {resultado['financieros'][0]}")
    
    assert isinstance(resultado, dict), "Debe retornar un diccionario"
    assert 'operativos' in resultado, "Debe tener clave 'operativos'"
    assert 'financieros' in resultado, "Debe tener clave 'financieros'"
    print("✓ Test La Paz pasado")

def test_paquetes_santa_cruz():
    """Test obtener paquetes de Santa Cruz"""
    print("\n=== Test Santa Cruz ===")
    resultado = obtener_paquetes_por_tipo_nodo('scz')
    
    print(f"Paquetes Operativos: {len(resultado['operativos'])} registros")
    if resultado['operativos']:
        print(f"  Primer registro: {resultado['operativos'][0]}")
    
    print(f"Paquetes Financieros: {len(resultado['financieros'])} registros")
    if resultado['financieros']:
        print(f"  Primer registro: {resultado['financieros'][0]}")
    
    assert isinstance(resultado, dict), "Debe retornar un diccionario"
    assert 'operativos' in resultado, "Debe tener clave 'operativos'"
    assert 'financieros' in resultado, "Debe tener clave 'financieros'"
    print("✓ Test Santa Cruz pasado")

def test_estructura_respuesta():
    """Test que la estructura sea la correcta"""
    print("\n=== Test Estructura ===")
    resultado = obtener_paquetes_por_tipo_nodo('lapaz')
    
    # Validar que los valores son listas
    assert isinstance(resultado['operativos'], list), "operativos debe ser una lista"
    assert isinstance(resultado['financieros'], list), "financieros debe ser una lista"
    
    # Si hay registros, validar que sean diccionarios
    if resultado['operativos']:
        assert isinstance(resultado['operativos'][0], dict), "Registros operativos deben ser dicts"
    
    if resultado['financieros']:
        assert isinstance(resultado['financieros'][0], dict), "Registros financieros deben ser dicts"
    
    print("✓ Test Estructura pasado")

if __name__ == '__main__':
    try:
        test_estructura_respuesta()
        test_paquetes_la_paz()
        test_paquetes_santa_cruz()
        print("\n✅ Todos los tests pasaron correctamente")
    except AssertionError as e:
        print(f"\n❌ Test falló: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
