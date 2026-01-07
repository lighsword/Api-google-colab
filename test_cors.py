#!/usr/bin/env python3
"""
Script para diagnosticar problemas de CORS en la API
"""
import requests
import json

def test_cors():
    """Test CORS configuration"""
    
    api_url = "http://localhost:5000"
    endpoints = [
        "/api/v2/health",
        "/api/v2/auth/token",
        "/docs",
    ]
    
    print("\n" + "="*80)
    print("🔍 DIAGNÓSTICO DE CORS")
    print("="*80 + "\n")
    
    print("📋 Verificando headers CORS en cada endpoint...\n")
    
    for endpoint in endpoints:
        url = api_url + endpoint
        print(f"🔗 Endpoint: {endpoint}")
        print(f"   URL: {url}")
        
        try:
            # Hacer request OPTIONS primero (preflight)
            print("   ⏳ Verificando preflight (OPTIONS)...")
            options_response = requests.options(
                url,
                headers={
                    'Origin': 'http://localhost:3000',
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'Content-Type, Authorization'
                },
                timeout=5
            )
            
            print(f"   Status: {options_response.status_code}")
            print(f"   Headers CORS:")
            
            cors_headers = {
                'Access-Control-Allow-Origin': options_response.headers.get('Access-Control-Allow-Origin', '❌ NO ENCONTRADO'),
                'Access-Control-Allow-Methods': options_response.headers.get('Access-Control-Allow-Methods', '❌ NO ENCONTRADO'),
                'Access-Control-Allow-Headers': options_response.headers.get('Access-Control-Allow-Headers', '❌ NO ENCONTRADO'),
            }
            
            for header, value in cors_headers.items():
                status = "✅" if value != "❌ NO ENCONTRADO" else "❌"
                print(f"      {status} {header}: {value}")
            
            # Hacer GET request
            print("   ⏳ Verificando GET...")
            get_response = requests.get(
                url,
                headers={'Origin': 'http://localhost:3000'},
                timeout=5
            )
            
            print(f"   Status: {get_response.status_code}")
            
            if get_response.status_code == 200:
                print("   ✅ GET exitoso")
            else:
                print(f"   ⚠️ GET retornó {get_response.status_code}")
            
            print()
            
        except requests.exceptions.ConnectionError:
            print(f"   ❌ No se pudo conectar")
            print(f"   Asegúrate de que la API está corriendo en {api_url}\n")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}\n")
    
    print("="*80)
    print("✨ TEST COMPLETADO")
    print("="*80)
    print("\n📌 Resultados esperados:")
    print("   - Access-Control-Allow-Origin: *")
    print("   - Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD")
    print("   - Access-Control-Allow-Headers: Content-Type, Authorization, X-API-Key, Accept, Origin")
    print("\n💡 Si todos muestran ✅, CORS está funcionando correctamente")
    print("   Si alguno muestra ❌, hay un problema de configuración\n")

if __name__ == "__main__":
    test_cors()
