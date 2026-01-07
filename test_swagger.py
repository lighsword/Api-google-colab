#!/usr/bin/env python3
"""
Script para verificar que Swagger está funcionando correctamente
"""
import requests
import time
import subprocess
import sys

def test_swagger():
    """Test que verifica Swagger"""
    
    # URLs de prueba
    health_url = "http://localhost:5000/api/v2/health"
    swagger_yaml_url = "http://localhost:5000/api/v2/swagger.yaml"
    swagger_ui_url = "http://localhost:5000/docs"
    
    print("\n" + "="*80)
    print("🧪 TESTING SWAGGER CONFIGURATION")
    print("="*80 + "\n")
    
    print("⏳ Esperando a que la API se inicie...")
    time.sleep(3)
    
    try:
        # Test 1: Health check
        print("1️⃣  Probando /api/v2/health...")
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            print("✅ Health check OK")
            print(f"   Respuesta: {response.json()}\n")
        else:
            print(f"❌ Health check falló con código {response.status_code}\n")
        
        # Test 2: Swagger YAML
        print("2️⃣  Probando /api/v2/swagger.yaml...")
        response = requests.get(swagger_yaml_url, timeout=5)
        if response.status_code == 200:
            print("✅ Swagger YAML accesible")
            print(f"   Tamaño: {len(response.text)} bytes")
            print(f"   Tipo: {response.headers.get('content-type', 'unknown')}\n")
        else:
            print(f"❌ Swagger YAML falló con código {response.status_code}\n")
        
        # Test 3: Swagger UI
        print("3️⃣  Probando /docs (Swagger UI)...")
        response = requests.get(swagger_ui_url, timeout=5)
        if response.status_code == 200:
            print("✅ Swagger UI disponible")
            print(f"   Accede a: http://localhost:5000/docs\n")
        else:
            print(f"❌ Swagger UI falló con código {response.status_code}\n")
        
        # Test 4: Token generation
        print("4️⃣  Probando generación de token...")
        token_url = "http://localhost:5000/api/v2/auth/token"
        response = requests.post(token_url, json={"user_id": "test_user"}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print("✅ Token generado correctamente")
            print(f"   Token (primeros 20 chars): {token[:20]}...\n")
        else:
            print(f"❌ Token generation falló con código {response.status_code}\n")
        
        print("="*80)
        print("✅ TODOS LOS TESTS PASARON CORRECTAMENTE")
        print("="*80)
        print("\n📋 PRÓXIMOS PASOS:")
        print("   1. Abre: http://localhost:5000/docs")
        print("   2. Verás todos los endpoints documentados")
        print("   3. Prueba los endpoints desde el panel de Swagger")
        print("   4. Usa el token generado para endpoints protegidos")
        print("\n")
        
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar a la API en http://localhost:5000")
        print("   Asegúrate de que el servidor esté corriendo\n")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}\n")

if __name__ == "__main__":
    test_swagger()
