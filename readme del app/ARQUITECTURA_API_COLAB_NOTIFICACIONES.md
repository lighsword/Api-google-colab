# 🏗️ Arquitectura Completa: Sistema de Notificaciones API Colab → Flutter

## 📊 Diagrama General

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        SISTEMA COMPLETO DE NOTIFICACIONES                     │
│                                                                               │
│  ┌──────────────────┐         ┌─────────────────────┐      ┌──────────────┐ │
│  │   USUARIO APP    │         │  GOOGLE COLAB API   │      │   FIREBASE   │ │
│  │   (Flutter)      │◄────────┤  (Python ML)        │──────►  CONSOLE     │ │
│  │                  │         │                     │      │              │ │
│  │ ┌──────────────┐ │         │ ┌──────────────────┐│      │ ┌──────────┐ │ │
│  │ │ Recibe notif │ │         │ │ Análisis de datos││      │ │Firestore │ │ │
│  │ │ FCM Handler  │ │         │ │ ML predictions   ││      │ │Database  │ │ │
│  │ └──────────────┘ │         │ │ Anomalías        ││      │ └──────────┘ │ │
│  │                  │         │ └──────────────────┘│      │              │ │
│  │ ┌──────────────┐ │         │ ┌──────────────────┐│      │ ┌──────────┐ │ │
│  │ │ Muestra al   │ │         │ │ Envía mensaje a  ││      │ │Cloud MSG │ │ │
│  │ │ usuario      │ │         │ │ FCM              ││      │ │(FCM)     │ │ │
│  │ └──────────────┘ │         │ └──────────────────┘│      │ └──────────┘ │ │
│  └──────────────────┘         └─────────────────────┘      └──────────────┘ │
│          ▲                             │                           ▲         │
│          │                             │                           │         │
│          └─────────────────────────────┴───────────────────────────┘         │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flujo de Datos Completo

```
FASE 1: INICIALIZACIÓN (App abierta por primera vez)
═══════════════════════════════════════════════════════

┌─────────────────────┐
│  Usuario abre app   │
│  e inicia sesión    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ NotificationService.initialize()        │
│  ├─ Solicitar permisos                  │
│  ├─ Obtener token FCM                   │
│  └─ Configurar handlers                 │
└──────────┬──────────────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Guardar Token en Firestore       │
│ /users/{userId}/fcmTokens/       │
│   {token}/                       │
│   ├─ token: "cJ3EHfN..."        │
│   ├─ deviceName: "Samsung"      │
│   ├─ platform: "android"        │
│   ├─ createdAt: timestamp       │
│   └─ isActive: true             │
└──────────┬───────────────────────┘
           │
           ▼
       ✅ TOKEN LISTO


FASE 2: ANÁLISIS EN COLAB (ML API analiza gastos)
════════════════════════════════════════════════

┌──────────────────────┐
│ Ejecutar Análisis ML │
│  ├─ Obtener gastos   │
│  ├─ Hacer predic.    │
│  ├─ Detectar anomalía│
│  └─ Generar recom.   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────┐
│ NotificationManager obtiene       │
│ tokens del usuario desde          │
│ Firestore                         │
│                                  │
│ tokens = [                        │
│   {token: "cJ3EHfN...",          │
│    deviceName: "Samsung",        │
│    isActive: true},              │
│   ...                            │
│ ]                                │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Crear Mensaje FCM               │
│ {                               │
│   "notification": {             │
│     "title": "Predicción",      │
│     "body": "$150 en Aliment."  │
│   },                            │
│   "data": {                     │
│     "userId": "usuario_123",    │
│     "tipo": "prediccion",       │
│     "gasto": "150.50",          │
│     "timestamp": "2025-02-05"   │
│   },                            │
│   "tokens": ["cJ3EHfN...", ...] │
│ }                               │
└──────────┬───────────────────────┘
           │
           ▼


FASE 3: ENVÍO A FCM (Firebase Cloud Messaging)
═══════════════════════════════════════════════

┌─────────────────────────────────┐
│ messaging.send_multicast()      │
│ (envía a múltiples tokens)      │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ Firebase Cloud Messaging procesa        │
│  ├─ Valida tokens                       │
│  ├─ Encola mensajes                     │
│  ├─ Espera conexión de app              │
│  └─ Entrega a dispositivos disponibles  │
└──────────┬──────────────────────────────┘
           │
           ▼


FASE 4: RECEPCIÓN EN APP FLUTTER
════════════════════════════════════

     ┌──────────────────────────┐
     │   Notificación llega a   │
     │   Firebase Messaging     │
     └──────────┬───────────────┘
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
   ┌─────────┐   ┌──────────────────┐
   │  Primer │   │  App en segundo  │
   │ plano   │   │ plano (handler)  │
   │(onMsg)  │   │ (background)     │
   └────┬────┘   └────┬─────────────┘
        │             │
        ▼             ▼
   ┌────────────────────────────┐
   │ NotificationService._      │
   │ handleNotification()        │
   │                            │
   │ • Validar userId           │
   │ • Procesar datos           │
   │ • Actualizar UI            │
   │ • Mostrar local notif      │
   └────┬───────────────────────┘
        │
        ▼
   ┌────────────────────────────┐
   │ Mostrar Notificación Local │
   │                            │
   │ [📊 Predicción             │
   │  Se predice $150 en        │
   │  Alimentación]             │
   └────────────────────────────┘
        │
        ▼
     ✅ USUARIO VE NOTIFICACIÓN


FASE 5: INTERACCIÓN DEL USUARIO
═════════════════════════════════

┌─────────────────────────┐
│ Usuario toca notificación│
└──────────┬──────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ onMessageOpenedApp listener      │
│ dispara con los datos            │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ _handleNotificationTap()         │
│ analiza tipo de notificación     │
│                                  │
│ switch(tipo) {                   │
│   'prediccion' → ir a predic.    │
│   'anomalia' → ir a alertas      │
│   'recomendacion' → mostrar      │
│   'resumen' → ir a estadísticas  │
│ }                                │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Navegar a pantalla correspondiente│
│ y pasar datos de la notificación │
│ (contexto completo)              │
└──────────────────────────────────┘
        │
        ▼
     ✅ USUARIO VE DETALLES
```

---

## 🗄️ Estructura de Datos en Firestore

```
┌─────────────────────────────────────────────────┐
│ Firebase Realtime Database / Firestore          │
└─────────────────────────────────────────────────┘

users/
├── usuario_123/
│   ├── email: "juan@example.com"
│   ├── displayName: "Juan Pérez"
│   ├── createdAt: timestamp(2024-01-15)
│   ├── lastLogin: timestamp(2025-02-05)
│   │
│   ├── fcmTokens/ (SUBCOLLECTION)
│   │   ├── cJ3EHfNEfQ1K4.../
│   │   │   ├── token: "cJ3EHfNEfQ1K4..."
│   │   │   ├── deviceName: "Samsung Galaxy S21"
│   │   │   ├── platform: "android"
│   │   │   ├── createdAt: timestamp(2025-02-01)
│   │   │   ├── lastUpdated: timestamp(2025-02-05 10:30:45)
│   │   │   └── isActive: true
│   │   │
│   │   └── eF5KjHoPxQ9L2.../
│   │       ├── token: "eF5KjHoPxQ9L2..."
│   │       ├── deviceName: "iPhone 14"
│   │       ├── platform: "ios"
│   │       ├── createdAt: timestamp(2025-01-20)
│   │       ├── lastUpdated: timestamp(2025-02-03 15:22:10)
│   │       └── isActive: false
│   │
│   ├── notificationPreferences/
│   │   ├── mlRecommendations: true
│   │   ├── alerts: true
│   │   ├── summaries: true
│   │   └── dailySummaryTime: "20:00"
│   │
│   └── notificationLogs/ (SUBCOLLECTION)
│       ├── notif_001/
│       │   ├── type: "prediccion"
│       │   ├── title: "Predicción: Alimentación"
│       │   ├── body: "$150 (Confianza: 85%)"
│       │   ├── sentAt: timestamp(2025-02-05 10:15:30)
│       │   ├── delivered: true
│       │   ├── opened: true
│       │   └── openedAt: timestamp(2025-02-05 10:16:45)
│       │
│       └── notif_002/
│           ├── type: "anomalia"
│           ├── title: "Gasto Inusual"
│           ├── body: "$500 en Entretenimiento"
│           ├── sentAt: timestamp(2025-02-05 14:20:15)
│           ├── delivered: true
│           └── opened: false
│
├── usuario_456/
│   └── ... (estructura similar)
│
└── usuario_789/
    └── ... (estructura similar)
```

---

## 🐍 Estructura de Código en Google Colab

```
NOTEBOOK ESTRUCTURA
═══════════════════

Celda 1: INSTALACIÓN
├─ !pip install firebase-admin
├─ !pip install requests
└─ !pip install pandas

Celda 2: IMPORTACIONES
├─ import firebase_admin
├─ from firebase_admin import credentials, messaging, firestore
├─ from datetime import datetime
└─ import json

Celda 3: CONFIGURACIÓN FIREBASE
├─ files.upload() → subir JSON
├─ cred = credentials.Certificate(...)
├─ firebase_admin.initialize_app(cred)
└─ db = firestore.client()

Celda 4: CLASE NotificationManager
├─ obtener_tokens_usuario(user_id)
├─ enviar_notificacion(user_id, titulo, cuerpo, datos)
└─ enviar_lote(usuarios_datos)

Celda 5: CLASE MLNotificationService
├─ notificar_prediccion_gasto(user_id, prediccion)
├─ notificar_anomalia(user_id, anomalia)
└─ notificar_recomendacion(user_id, recomendacion)

Celda 6: CLASE ExpenseAnalyzer
├─ analizar_usuario_y_notificar(user_id)
├─ _obtener_gastos_mes_actual(user_id)
├─ _detectar_anomalias(gastos)
├─ _generar_predicciones(gastos)
└─ _generar_recomendaciones(gastos)

Celda 7: FUNCIONES ADICIONALES
├─ enviar_resumen_diario(user_id)
├─ enviar_resumenes_diarios_todos_usuarios()
└─ probar_configuracion()

Celda 8: SCHEDULER (OPCIONAL)
├─ @scheduler.scheduled_job('interval', hours=6)
├─ @scheduler.scheduled_job(CronTrigger(hour=22))
└─ scheduler.start()

Celda 9: PRUEBAS
├─ probar_configuracion()
└─ enviar_notificacion('test_user', 'Test', 'Test')
```

---

## 📱 Estructura de Código en Flutter

```
lib/
├── config/
│   └── services/
│       ├── notification_service.dart
│       │   ├── initialize()
│       │   ├── saveTokenToDatabase(userId)
│       │   ├── _setupFCMHandlers()
│       │   ├── _setupTokenRefreshListener()
│       │   ├── _handleNotification(message)
│       │   ├── _handleNotificationTap(message)
│       │   └── _processNotificationData(datos)
│       │
│       └── push_notifications_service.dart
│           └── (handlers específicos)
│
├── modules/
│   └── auth/
│       └── auth_provider.dart
│           └── signIn() ← Llama a saveTokenToDatabase()
│
└── widgets/
    └── notification_helper.dart
        ├── onNotificationTapped()
        └── displayNotification()
```

---

## 🔐 Flujo de Seguridad

```
┌─────────────────────────────────────────────────────┐
│         VALIDACIÓN Y SEGURIDAD DE DATOS             │
└─────────────────────────────────────────────────────┘

CLIENTE (Flutter)
═════════════════
┌──────────────────────────┐
│ Usuario inicia sesión    │
│ ✅ Autenticado por Firebase
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────────┐
│ Guardar token en Firestore   │
│ /users/{userId}/fcmTokens/   │
│ ✅ Solo ese usuario puede leer
└────────────┬─────────────────┘
             │
             ▼
      ✅ TOKEN SEGURO


SERVIDOR (Google Colab)
═══════════════════════
┌──────────────────────────────────┐
│ Service Account (credenciales)   │
│ ✅ Almacenadas en variable env   │
│ ❌ Nunca en código fuente        │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ Obtener tokens de Firestore      │
│ ✅ Acceso validado por SA        │
│ ✅ Solo tokens del usuario       │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ Crear mensaje FCM                │
│ ✅ Incluir userId en datos       │
│ ✅ Validar estructura             │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ Enviar a Firebase Cloud Messaging│
│ ✅ Solo a tokens del usuario     │
│ ✅ Datos validados               │
└────────────┬─────────────────────┘
             │
             ▼
      ✅ MENSAJE SEGURO


CLIENTE (Flutter - Recibe)
═══════════════════════════
┌──────────────────────────────┐
│ FCM recibe notificación       │
│ ✅ Firebase valida sender     │
│ ✅ Solo para este dispositivo │
└────────────┬─────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ _handleNotification()            │
│ ✅ Validar que userId == auth   │
│ ✅ Procesar solo si corresponde  │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ Mostrar al usuario               │
│ ✅ Datos ya validados            │
│ ✅ Navegación segura             │
└──────────────────────────────────┘
```

---

## 🔄 Flujo de Casos de Uso

### Caso 1: Predicción de Gasto

```
ML Model (Colab)
    │
    ├─ Analiza histórico de usuario
    │
    ├─ Genera predicción:
    │  • Categoría: "Alimentación"
    │  • Monto predicho: $150.50
    │  • Confianza: 85%
    │
    └─ Llama a ml_service.notificar_prediccion_gasto()
           │
           ├─ Obtiene token FCM del usuario
           │
           ├─ Crea mensaje:
           │  • Título: "📊 Predicción: Alimentación"
           │  • Cuerpo: "$150.50 (Confianza: 85%)"
           │
           └─ Envía a FCM
                  │
                  └─► App Flutter recibe
                      │
                      ├─ Muestra notificación
                      │
                      └─ Usuario toca
                         │
                         └─ Abre pantalla de predicciones
                            con contexto completo
```

### Caso 2: Anomalía Detectada

```
ML Model (Colab)
    │
    ├─ Calcula estadísticas de gasto
    │
    ├─ Detecta: gasto de $500 en "Entretenimiento"
    │           promedio: $150, z-score: 2.8
    │
    └─ Llama a ml_service.notificar_anomalia()
           │
           ├─ Obtiene tokens FCM
           │
           ├─ Crea mensaje con contexto:
           │  • Título: "⚠️ Gasto Inusual Detectado"
           │  • Cuerpo: "$500 en Entretenimiento (3.3x promedio)"
           │  • Datos: monto, promedio, razón
           │
           └─ Envía
                  │
                  └─► App Flutter
                      │
                      ├─ Notificación en tiempo real
                      │
                      └─ Usuario puede:
                         • Ver detalles
                         • Editar/eliminar gasto
                         • Ver análisis
```

### Caso 3: Recomendación Personalizada

```
ML Model (Colab)
    │
    ├─ Análisis completo:
    │  • Categoría mayor: "Entretenimiento"
    │  • Gasto: $800/mes
    │  • Promedio histórico: $500/mes
    │  • Oportunidad de ahorro: $300
    │
    └─ Llama a ml_service.notificar_recomendacion()
           │
           ├─ Crea recomendación personalizada
           │
           ├─ Mensaje:
           │  • Título: "💡 Recomendación Personalizada"
           │  • Cuerpo: "Reducir Entretenimiento - Ahorro: $300"
           │  • Datos: acción, % ahorro, reasoning
           │
           └─ Envía
                  │
                  └─► App Flutter
                      │
                      ├─ Notificación destacada
                      │
                      └─ Usuario:
                         • Lee recomendación
                         • Ve análisis detallado
                         • Toma acción
```

---

## 📈 Escalabilidad

```
PEQUEÑA ESCALA (1-100 usuarios)
════════════════════════════════
• 1-2 análisis/usuario/día
• ~50-100 notificaciones/día
• Colab notebook es suficiente
• Firestore free tier OK


MEDIANA ESCALA (100-1000 usuarios)
═══════════════════════════════════
• Análisis programados
• Scheduler en Colab
• ~500-2000 notificaciones/día
• Considerar Cloud Functions


GRAN ESCALA (1000+ usuarios)
════════════════════════════
• Análisis en Cloud Run
• Pub/Sub para notificaciones
• Dataflow para procesamiento
• Firestore pago
• Monitoreo en Cloud Monitoring
```

---

## ✅ Checklist de Implementación

```
FIREBASE SETUP
══════════════
☐ Service Account JSON descargado
☐ Firestore collections creadas
☐ FCM habilitado
☐ Reglas de seguridad actualizadas

FLUTTER APP
═══════════
☐ notification_service.dart OK
☐ saveTokenToDatabase() en login
☐ FCM handlers implementados
☐ notificationPreferences creadas
☐ Tests en emulador pasados

GOOGLE COLAB
════════════
☐ firebase-admin instalado
☐ Credenciales subidas
☐ NotificationManager creada
☐ MLNotificationService creada
☐ Funciones de prueba trabajando

INTEGRACIÓN ML
═══════════════
☐ Predicciones funcionan
☐ Anomalías detectadas
☐ Recomendaciones generadas
☐ Notificaciones enviadas
☐ Datos correctos en app

PRODUCCIÓN
══════════
☐ Seguridad validada
☐ Performance optimizada
☐ Monitoreo activado
☐ Logs implementados
☐ Rollback plan listo
```

---

**Última actualización**: Febrero 2025
**Versión**: 1.0 - Listo para Producción ✅
