# ============================================
# 📚 EJEMPLOS DE USO - Controlador de Notificaciones
# ============================================
#
# Este archivo muestra cómo usar el NotificationsController
# desde Google Colab, Flask API o cualquier entorno Python
#
# Autor: API Google Colab
# Versión: 2.1
# Fecha: 2026-02-05

# ============================================
# IMPORTS
# ============================================

from notifications_controller import (
    NotificationsController,
    NotificationType,
    AlertLevel,
    inicializar_controlador
)
import firebase_admin
from firebase_admin import credentials, firestore
import logging

logging.basicConfig(level=logging.INFO)

# ============================================
# EJEMPLO 1: INICIALIZACIÓN BÁSICA
# ============================================

def ejemplo_1_inicializacion_basica():
    """
    Ejemplo 1: Inicializar el controlador
    """
    print("\n" + "="*60)
    print("EJEMPLO 1: Inicialización Básica")
    print("="*60)
    
    # Obtener cliente de Firestore (ya debe estar inicializado en API_MEJORADA.py)
    try:
        db = firestore.client()
        controller = NotificationsController(db_instance=db)
        print("✅ Controlador inicializado correctamente")
        return controller
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# ============================================
# EJEMPLO 2: ENVIAR NOTIFICACIÓN DE GASTO
# ============================================

def ejemplo_2_notificacion_gasto(controller, usuario_id="user_demo_123"):
    """
    Ejemplo 2: Enviar notificación de gasto registrado
    
    Caso de uso: El usuario registra un gasto en la app
    """
    print("\n" + "="*60)
    print("EJEMPLO 2: Notificación de Gasto Registrado")
    print("="*60)
    
    resultado = controller.enviar_notificacion_gasto(
        usuario_id=usuario_id,
        monto=50.0,
        categoria="Comida",
        descripcion="Almuerzo en restaurante"
    )
    
    print(f"\n📊 Resultado:")
    print(f"   Exitoso: {resultado.exitoso}")
    print(f"   Usuario: {resultado.usuario_id}")
    print(f"   Dispositivos: {resultado.total_dispositivos}")
    print(f"   Envíos exitosos: {resultado.tokens_exitosos}")
    print(f"   Mensaje: {resultado.mensaje}")
    
    return resultado


# ============================================
# EJEMPLO 3: ALERTA DE PRESUPUESTO
# ============================================

def ejemplo_3_alerta_presupuesto(controller, usuario_id="user_demo_123"):
    """
    Ejemplo 3: Enviar alerta de presupuesto
    
    Caso de uso: El usuario va a exceder su presupuesto en una categoría
    """
    print("\n" + "="*60)
    print("EJEMPLO 3: Alerta de Presupuesto")
    print("="*60)
    
    # Caso 1: Presupuesto casi agotado (80%)
    resultado1 = controller.enviar_alerta_presupuesto(
        usuario_id=usuario_id,
        categoria="Entretenimiento",
        gastado=80.0,
        presupuesto=100.0
    )
    
    print(f"\n📊 Alerta 1 (80%): {resultado1.mensaje}")
    
    # Caso 2: Presupuesto excedido (110%)
    resultado2 = controller.enviar_alerta_presupuesto(
        usuario_id=usuario_id,
        categoria="Transporte",
        gastado=110.0,
        presupuesto=100.0
    )
    
    print(f"📊 Alerta 2 (110%): {resultado2.mensaje}")
    
    return resultado1, resultado2


# ============================================
# EJEMPLO 4: RECOMENDACIÓN DE ML (DESDE COLAB)
# ============================================

def ejemplo_4_recomendacion_ml(controller, usuario_id="user_demo_123"):
    """
    Ejemplo 4: Enviar recomendación de ML
    
    Caso de uso: Google Colab detecta un patrón en los gastos
    y envía una recomendación al usuario
    """
    print("\n" + "="*60)
    print("EJEMPLO 4: Recomendación de Machine Learning")
    print("="*60)
    
    # Simular análisis de ML
    print("\n🤖 Analizando patrones de gasto...")
    print("   - Gastos en Comida: Incremento del 35%")
    print("   - Gastos en Entretenimiento: Aumento sostenido")
    print("   - Patrón detectado: Aumento de gasto en entretenimiento")
    
    resultado = controller.enviar_recomendacion_ml(
        usuario_id=usuario_id,
        recomendacion="Notamos que has incrementado tus gastos en entretenimiento. "
                     "Considera establecer un presupuesto para esta categoría.",
        categoria="Entretenimiento",
        confianza=0.87,
        accion="ver_detalles"
    )
    
    print(f"\n📊 Recomendación enviada:")
    print(f"   Confianza: 87%")
    print(f"   Dispositivos: {resultado.total_dispositivos}")
    print(f"   Mensaje: {resultado.mensaje}")
    
    return resultado


# ============================================
# EJEMPLO 5: ALERTA DE ANOMALÍA
# ============================================

def ejemplo_5_alerta_anomalia(controller, usuario_id="user_demo_123"):
    """
    Ejemplo 5: Enviar alerta de anomalía
    
    Caso de uso: Se detecta un gasto muy inusual
    """
    print("\n" + "="*60)
    print("EJEMPLO 5: Alerta de Anomalía")
    print("="*60)
    
    # Simular detección de anomalía
    print("\n🔍 Analizando transacción...")
    print("   - Monto: $500")
    print("   - Categoría: Compras Online")
    print("   - Desviación: 5σ (muy inusual)")
    
    resultado = controller.enviar_alerta_anomalia(
        usuario_id=usuario_id,
        tipo_anomalia="gasto_inusual",
        monto=500.0,
        descripcion="Detectamos un gasto muy superior a tu promedio. "
                   "¿Fue una compra planeada?",
        categoria="Compras Online"
    )
    
    print(f"\n⚠️ Alerta enviada:")
    print(f"   Tipo: Gasto Inusual")
    print(f"   Monto: $500")
    print(f"   Dispositivos notificados: {resultado.tokens_exitosos}")
    
    return resultado


# ============================================
# EJEMPLO 6: TIP FINANCIERO
# ============================================

def ejemplo_6_tip_financiero(controller, usuario_id="user_demo_123"):
    """
    Ejemplo 6: Enviar tips financieros
    
    Caso de uso: Enviar consejos personalizados basados en análisis
    """
    print("\n" + "="*60)
    print("EJEMPLO 6: Tips Financieros Personalizados")
    print("="*60)
    
    tips = [
        {
            'tip': 'Podrías ahorrar $200/mes si reduces gastos en entretenimiento',
            'categoria': 'Entretenimiento'
        },
        {
            'tip': 'Tu gasto promedio en comida es $400/mes. Considera un presupuesto',
            'categoria': 'Comida'
        },
        {
            'tip': 'Has ahorrado $50 este mes. ¡Sigue así!',
            'categoria': 'Ahorros'
        }
    ]
    
    resultados = []
    for tip_data in tips:
        resultado = controller.enviar_tip_financiero(
            usuario_id=usuario_id,
            tip=tip_data['tip'],
            categoria=tip_data['categoria'],
            fuente="Machine Learning"
        )
        resultados.append(resultado)
        print(f"✅ Tip enviado: {tip_data['tip'][:50]}...")
    
    return resultados


# ============================================
# EJEMPLO 7: ENVIAR LOTE DE NOTIFICACIONES
# ============================================

def ejemplo_7_lote_notificaciones(controller):
    """
    Ejemplo 7: Enviar notificaciones a múltiples usuarios
    
    Caso de uso: Análisis masivo en Google Colab para múltiples usuarios
    """
    print("\n" + "="*60)
    print("EJEMPLO 7: Lote de Notificaciones (Múltiples Usuarios)")
    print("="*60)
    
    # Simular análisis masivo
    usuarios_a_notificar = [
        {
            'usuario_id': 'user_001',
            'titulo': '💰 Gasto Registrado',
            'cuerpo': 'Registraste un gasto de $25',
            'tipo': NotificationType.GASTO_REGISTRADO,
            'datos_extra': {
                'monto': 25,
                'categoria': 'Comida'
            }
        },
        {
            'usuario_id': 'user_002',
            'titulo': '🤖 Recomendación',
            'cuerpo': 'Ahorrarías más si reduces gastos de viaje',
            'tipo': NotificationType.RECOMENDACION_ML,
            'datos_extra': {
                'categoria': 'Transporte',
                'confianza': 0.92
            }
        },
        {
            'usuario_id': 'user_003',
            'titulo': '⚠️ Presupuesto',
            'cuerpo': 'Te quedan $50 de tu presupuesto de entretenimiento',
            'tipo': NotificationType.ALERTA_PRESUPUESTO,
            'datos_extra': {
                'categoria': 'Entretenimiento',
                'gastado': 75,
                'presupuesto': 125
            }
        },
    ]
    
    print(f"\n📤 Enviando {len(usuarios_a_notificar)} notificaciones...")
    resumen = controller.enviar_lote(usuarios_a_notificar)
    
    print(f"\n📊 Resumen:")
    print(f"   Total usuarios: {resumen['total_usuarios']}")
    print(f"   Exitosos: {resumen['usuarios_exitosos']}")
    print(f"   Fallidos: {resumen['usuarios_fallidos']}")
    print(f"   Notificaciones totales: {resumen['notificaciones_totales']}")
    
    return resumen


# ============================================
# EJEMPLO 8: OBTENER HISTORIAL
# ============================================

def ejemplo_8_historial(controller, usuario_id="user_demo_123"):
    """
    Ejemplo 8: Obtener historial de notificaciones
    """
    print("\n" + "="*60)
    print("EJEMPLO 8: Historial de Notificaciones")
    print("="*60)
    
    historial = controller.obtener_historial(usuario_id, limite=10)
    
    print(f"\n📋 Últimas {len(historial)} notificaciones:")
    for i, notif in enumerate(historial, 1):
        print(f"\n   {i}. {notif.get('titulo')}")
        print(f"      Tipo: {notif.get('tipo')}")
        print(f"      Exitoso: {notif.get('exitoso')}")
        print(f"      Tokens exitosos: {notif.get('tokens_exitosos')}")
    
    return historial


# ============================================
# EJEMPLO 9: ESTADÍSTICAS
# ============================================

def ejemplo_9_estadisticas(controller, usuario_id="user_demo_123"):
    """
    Ejemplo 9: Obtener estadísticas de notificaciones
    """
    print("\n" + "="*60)
    print("EJEMPLO 9: Estadísticas de Notificaciones")
    print("="*60)
    
    stats = controller.obtener_estadisticas(usuario_id)
    
    print(f"\n📊 Estadísticas para {usuario_id}:")
    print(f"   Total de notificaciones: {stats.get('total_notificaciones')}")
    print(f"   Exitosas: {stats.get('exitosas')}")
    print(f"   Fallidas: {stats.get('fallidas')}")
    print(f"   Tasa de éxito: {stats.get('tasa_exito', 0):.1f}%")
    print(f"   Por tipo:")
    for tipo, cantidad in stats.get('por_tipo', {}).items():
        print(f"      - {tipo}: {cantidad}")
    
    return stats


# ============================================
# EJEMPLO 10: SCRIPT COMPLETO EN GOOGLE COLAB
# ============================================

def ejemplo_10_colab_script_completo():
    """
    Ejemplo 10: Script completo para ejecutar en Google Colab
    
    Este script se ejecutaría en una celda de Colab
    """
    print("\n" + "="*60)
    print("EJEMPLO 10: Script Completo para Google Colab")
    print("="*60)
    
    script = '''
# ============================================
# GOOGLE COLAB - Script de Notificaciones
# ============================================

# Celda 1: Instalar dependencias
!pip install firebase-admin requests google-cloud-firestore

# Celda 2: Importes y configuración
from google.colab import files
import firebase_admin
from firebase_admin import credentials, firestore
from notifications_controller import NotificationsController, NotificationType

# Celda 3: Cargar credenciales
print("Sube tu archivo de Service Account (JSON)")
uploaded = files.upload()
credential_file = list(uploaded.keys())[0]

cred = credentials.Certificate(credential_file)
firebase_admin.initialize_app(cred)
print("✅ Firebase inicializado")

# Celda 4: Crear controlador
db = firestore.client()
controller = NotificationsController(db_instance=db)
print("✅ Controlador de notificaciones listo")

# Celda 5: Analizar datos y enviar notificaciones
import pandas as pd
import numpy as np

# Simular análisis de datos
print("🔍 Analizando datos de gastos...")

# Obtener datos de usuarios (ejemplo)
usuarios = ["user_1", "user_2", "user_3"]

for usuario_id in usuarios:
    # Análisis de presupuesto
    categoria = "Comida"
    gastado = np.random.uniform(40, 120)
    presupuesto = 100
    
    if gastado > presupuesto * 0.8:
        controller.enviar_alerta_presupuesto(
            usuario_id=usuario_id,
            categoria=categoria,
            gastado=gastado,
            presupuesto=presupuesto
        )
        print(f"✅ Alerta presupuesto enviada a {usuario_id}")
    
    # Enviar recomendación de ML
    controller.enviar_recomendacion_ml(
        usuario_id=usuario_id,
        recomendacion="Podrías optimizar tu presupuesto",
        confianza=0.88
    )
    print(f"✅ Recomendación ML enviada a {usuario_id}")

# Celda 6: Obtener estadísticas
print("\\n📊 Estadísticas de envío:")
for usuario_id in usuarios:
    stats = controller.obtener_estadisticas(usuario_id)
    print(f"{usuario_id}: {stats.get('total_notificaciones')} notificaciones, "
          f"Tasa de éxito: {stats.get('tasa_exito', 0):.1f}%")

print("✅ ¡Notificaciones enviadas exitosamente!")
    '''
    
    print("\n" + script)
    return script


# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

def main():
    """
    Ejecutar todos los ejemplos
    """
    print("\n" + "="*60)
    print("EJEMPLOS - Controlador de Notificaciones")
    print("="*60)
    print("Este archivo muestra cómo usar el NotificationsController")
    print("desde Python, Google Colab o la API Flask")
    
    try:
        # Inicializar
        controller = ejemplo_1_inicializacion_basica()
        if not controller:
            print("❌ No se pudo inicializar. Verifica que Firebase esté configurado.")
            return
        
        usuario_demo = "user_demo_123"
        
        # Ejecutar ejemplos
        print("\n📚 Ejecutando ejemplos...")
        
        ejemplo_2_notificacion_gasto(controller, usuario_demo)
        ejemplo_3_alerta_presupuesto(controller, usuario_demo)
        ejemplo_4_recomendacion_ml(controller, usuario_demo)
        ejemplo_5_alerta_anomalia(controller, usuario_demo)
        ejemplo_6_tip_financiero(controller, usuario_demo)
        ejemplo_7_lote_notificaciones(controller)
        ejemplo_8_historial(controller, usuario_demo)
        ejemplo_9_estadisticas(controller, usuario_demo)
        ejemplo_10_colab_script_completo()
        
        print("\n" + "="*60)
        print("✅ EJEMPLOS COMPLETADOS")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
