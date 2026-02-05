#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ============================================
# 🧪 SCRIPT DE PRUEBA - NOTIFICACIONES
# ============================================
#
# Este script prueba todos los nuevos endpoints
# de notificaciones integrados en API_MEJORADA.py
#
# Uso:
#   python test_notificaciones_api.py
#
# Requisitos:
#   - requests
#   - API_MEJORADA.py ejecutándose en http://localhost:5000

import requests
import json
from datetime import datetime

# ============================================
# CONFIGURACIÓN
# ============================================

API_URL = "http://localhost:5000"
EMAIL = "test@example.com"
CONTRASEÑA = "password123"
USUARIO_ID = "test_user_notifications"

# Colores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# ============================================
# FUNCIONES AUXILIARES
# ============================================

def print_header(titulo):
    """Imprimir encabezado"""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{titulo}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

def print_success(mensaje):
    """Imprimir mensaje de éxito"""
    print(f"{GREEN}✅ {mensaje}{RESET}")

def print_error(mensaje):
    """Imprimir mensaje de error"""
    print(f"{RED}❌ {mensaje}{RESET}")

def print_info(mensaje):
    """Imprimir mensaje informativo"""
    print(f"{BLUE}ℹ️  {mensaje}{RESET}")

def print_warning(mensaje):
    """Imprimir advertencia"""
    print(f"{YELLOW}⚠️  {mensaje}{RESET}")

def obtener_token():
    """Obtener JWT token"""
    print_info("Obteniendo token...")
    
    try:
        response = requests.post(
            f"{API_URL}/api/v2/auth/token",
            json={
                "usuario": EMAIL,
                "contraseña": CONTRASEÑA
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            if token:
                print_success(f"Token obtenido: {token[:20]}...")
                return token
            else:
                print_error("No se encontró token en la respuesta")
                return None
        else:
            print_error(f"Error obteniendo token: {response.status_code}")
            print_info(f"Respuesta: {response.text}")
            return None
    except Exception as e:
        print_error(f"Excepción obteniendo token: {e}")
        return None

# ============================================
# PRUEBAS
# ============================================

def test_enviar_gasto(token):
    """Prueba: Enviar notificación de gasto"""
    print_header("TEST 1: Enviar Notificación de Gasto")
    
    payload = {
        "usuario_id": USUARIO_ID,
        "monto": 50.0,
        "categoria": "Comida",
        "descripcion": "Almuerzo en restaurante"
    }
    
    print_info(f"Enviando: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{API_URL}/api/notificaciones/gasto",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"Notificación enviada exitosamente")
            print_info(f"Respuesta: {json.dumps(data, indent=2)}")
            return True
        else:
            print_error(f"Error: {response.status_code}")
            print_info(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción: {e}")
        return False

def test_alerta_presupuesto(token):
    """Prueba: Enviar alerta de presupuesto"""
    print_header("TEST 2: Enviar Alerta de Presupuesto")
    
    payload = {
        "usuario_id": USUARIO_ID,
        "categoria": "Comida",
        "gastado": 80.0,
        "presupuesto": 100.0
    }
    
    print_info(f"Enviando: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{API_URL}/api/notificaciones/alerta-presupuesto",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"Alerta enviada exitosamente")
            print_info(f"Respuesta: {json.dumps(data, indent=2)}")
            return True
        else:
            print_error(f"Error: {response.status_code}")
            print_info(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción: {e}")
        return False

def test_recomendacion_ml(token):
    """Prueba: Enviar recomendación de ML"""
    print_header("TEST 3: Enviar Recomendación de ML")
    
    payload = {
        "usuario_id": USUARIO_ID,
        "recomendacion": "Podrías ahorrar más si reduces gastos de entretenimiento",
        "categoria": "Entretenimiento",
        "confianza": 0.87
    }
    
    print_info(f"Enviando: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{API_URL}/api/notificaciones/recomendacion-ml",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"Recomendación enviada exitosamente")
            print_info(f"Respuesta: {json.dumps(data, indent=2)}")
            return True
        else:
            print_error(f"Error: {response.status_code}")
            print_info(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción: {e}")
        return False

def test_alerta_anomalia(token):
    """Prueba: Enviar alerta de anomalía"""
    print_header("TEST 4: Enviar Alerta de Anomalía")
    
    payload = {
        "usuario_id": USUARIO_ID,
        "tipo_anomalia": "gasto_inusual",
        "monto": 150.0,
        "descripcion": "Gasto muy superior a tu promedio",
        "categoria": "Compras Online"
    }
    
    print_info(f"Enviando: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{API_URL}/api/notificaciones/anomalia",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"Alerta de anomalía enviada exitosamente")
            print_info(f"Respuesta: {json.dumps(data, indent=2)}")
            return True
        else:
            print_error(f"Error: {response.status_code}")
            print_info(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción: {e}")
        return False

def test_tip_financiero(token):
    """Prueba: Enviar tip financiero"""
    print_header("TEST 5: Enviar Tip Financiero")
    
    payload = {
        "usuario_id": USUARIO_ID,
        "tip": "Podrías ahorrar $200/mes si reduces gastos de entretenimiento",
        "categoria": "Entretenimiento",
        "fuente": "Machine Learning"
    }
    
    print_info(f"Enviando: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{API_URL}/api/notificaciones/tip",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"Tip enviado exitosamente")
            print_info(f"Respuesta: {json.dumps(data, indent=2)}")
            return True
        else:
            print_error(f"Error: {response.status_code}")
            print_info(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción: {e}")
        return False

def test_notificacion_personalizada(token):
    """Prueba: Enviar notificación personalizada"""
    print_header("TEST 6: Enviar Notificación Personalizada")
    
    payload = {
        "usuario_id": USUARIO_ID,
        "titulo": "🎉 ¡Test Exitoso!",
        "cuerpo": "Las notificaciones están funcionando correctamente",
        "tipo": "general",
        "datos": {
            "test": "true",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    print_info(f"Enviando: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{API_URL}/api/notificaciones/enviar",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"Notificación personalizada enviada")
            print_info(f"Respuesta: {json.dumps(data, indent=2)}")
            return True
        else:
            print_error(f"Error: {response.status_code}")
            print_info(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción: {e}")
        return False

def test_obtener_historial(token):
    """Prueba: Obtener historial de notificaciones"""
    print_header("TEST 7: Obtener Historial")
    
    print_info(f"Obteniendo historial para usuario: {USUARIO_ID}")
    
    try:
        response = requests.get(
            f"{API_URL}/api/notificaciones/historial/{USUARIO_ID}?limit=5",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Historial obtenido exitosamente")
            total = data.get('total', 0)
            print_info(f"Total de notificaciones: {total}")
            
            if total > 0:
                notificaciones = data.get('notificaciones', [])
                print_info(f"Mostrando primeras {len(notificaciones)} notificaciones:")
                for i, notif in enumerate(notificaciones, 1):
                    print(f"  {i}. {notif.get('titulo')}")
                    print(f"     Tipo: {notif.get('tipo')}")
                    print(f"     Exitoso: {notif.get('exitoso')}")
            
            return True
        else:
            print_error(f"Error: {response.status_code}")
            print_info(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción: {e}")
        return False

def test_obtener_estadisticas(token):
    """Prueba: Obtener estadísticas"""
    print_header("TEST 8: Obtener Estadísticas")
    
    print_info(f"Obteniendo estadísticas para usuario: {USUARIO_ID}")
    
    try:
        response = requests.get(
            f"{API_URL}/api/notificaciones/estadisticas/{USUARIO_ID}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Estadísticas obtenidas exitosamente")
            
            stats = data.get('estadisticas', {})
            print_info(f"Total de notificaciones: {stats.get('total_notificaciones')}")
            print_info(f"Exitosas: {stats.get('exitosas')}")
            print_info(f"Fallidas: {stats.get('fallidas')}")
            print_info(f"Tasa de éxito: {stats.get('tasa_exito', 0):.1f}%")
            
            por_tipo = stats.get('por_tipo', {})
            if por_tipo:
                print_info("Por tipo:")
                for tipo, cantidad in por_tipo.items():
                    print(f"  - {tipo}: {cantidad}")
            
            return True
        else:
            print_error(f"Error: {response.status_code}")
            print_info(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción: {e}")
        return False

# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

def main():
    """Ejecutar todas las pruebas"""
    print(f"\n{BOLD}{BLUE}🧪 PRUEBAS DE NOTIFICACIONES - API_MEJORADA.py{RESET}")
    print(f"{BOLD}{BLUE}Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    
    # Verificar que la API está disponible
    print_info(f"Verificando API en {API_URL}...")
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 404:
            print_warning("API está disponible (respuesta 404 esperada)")
        elif response.status_code == 200:
            print_success("API está disponible")
    except Exception as e:
        print_error(f"No se puede conectar a la API: {e}")
        print_info("Asegúrate de ejecutar: python API_MEJORADA.py")
        return
    
    # Obtener token
    token = obtener_token()
    if not token:
        print_error("No se pudo obtener el token. Abortando pruebas.")
        return
    
    # Ejecutar pruebas
    resultados = []
    
    resultados.append(("Enviar Gasto", test_enviar_gasto(token)))
    resultados.append(("Alerta Presupuesto", test_alerta_presupuesto(token)))
    resultados.append(("Recomendación ML", test_recomendacion_ml(token)))
    resultados.append(("Alerta Anomalía", test_alerta_anomalia(token)))
    resultados.append(("Tip Financiero", test_tip_financiero(token)))
    resultados.append(("Notificación Personalizada", test_notificacion_personalizada(token)))
    resultados.append(("Obtener Historial", test_obtener_historial(token)))
    resultados.append(("Obtener Estadísticas", test_obtener_estadisticas(token)))
    
    # Resumen
    print_header("RESUMEN DE PRUEBAS")
    
    exitosas = sum(1 for _, resultado in resultados if resultado)
    fallidas = len(resultados) - exitosas
    
    for nombre, resultado in resultados:
        if resultado:
            print_success(f"{nombre}")
        else:
            print_error(f"{nombre}")
    
    print()
    print_info(f"Total: {len(resultados)} pruebas")
    print_success(f"Exitosas: {exitosas}")
    if fallidas > 0:
        print_error(f"Fallidas: {fallidas}")
    
    if fallidas == 0:
        print(f"\n{GREEN}{BOLD}🎉 ¡TODAS LAS PRUEBAS PASARON!{RESET}")
    else:
        print(f"\n{RED}{BOLD}⚠️ Algunas pruebas fallaron{RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Pruebas canceladas por el usuario{RESET}")
    except Exception as e:
        print_error(f"Error fatal: {e}")
        import traceback
        traceback.print_exc()
