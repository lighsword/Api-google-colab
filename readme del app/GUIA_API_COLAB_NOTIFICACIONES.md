# 🚀 Guía: API de Google Colab Enviando Notificaciones a Flutter

## 📋 Descripción General

Esta guía explica cómo tu API de machine learning en Google Colab puede enviar notificaciones **de forma independiente** a tu app Flutter cuando está en producción. El sistema utiliza Firebase Cloud Messaging (FCM) como intermediario.

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Google Colab API (ML)                                      │
│  ├─ Análisis de gastos                                      │
│  ├─ Predicciones                                            │
│  └─ Detección de anomalías                                  │
│                         │                                    │
│                         ▼                                    │
│        ┌────────────────────────────────┐                   │
│        │   Firebase Realtime Database   │                   │
│        │   o Firestore                  │                   │
│        │   (Almacena tokens FCM)        │                   │
│        └────────────────────────────────┘                   │
│                         │                                    │
│                         ▼                                    │
│        ┌────────────────────────────────┐                   │
│        │  Firebase Cloud Messaging      │                   │
│        │  (Envía notificaciones)        │                   │
│        └────────────────────────────────┘                   │
│                         │                                    │
│                         ▼                                    │
│        ┌────────────────────────────────┐                   │
│        │   App Flutter (Usuario)        │                   │
│        │   ├─ Recibe notificación       │                   │
│        │   ├─ Muestra al usuario        │                   │
│        │   └─ Filtra por userId        │                   │
│        └────────────────────────────────┘                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 Conceptos Clave

### 1. **Token FCM (Firebase Cloud Messaging)**
- Identificador único generado por Firebase para cada dispositivo
- Necesario para enviar notificaciones push
- Varía por dispositivo y usuario

### 2. **User ID**
- ID único del usuario en Firebase Auth
- Se utiliza para filtrar qué notificaciones recibe cada usuario

### 3. **Firebase Service Account**
- Credenciales para que tu API en Colab acceda a Firebase
- Necesaria para enviar notificaciones desde el backend

---

## ⚙️ Paso 1: Configurar Firebase (Backend)

### 1.1 Crear Service Account

1. Ve a [Firebase Console](https://console.firebase.google.com)
2. Selecciona tu proyecto `gestor-financiero-28ac2`
3. Ve a **Configuración** → **Cuentas de Servicio**
4. Haz clic en **Generar nueva clave privada**
5. Se descargará un archivo JSON con tus credenciales

**Este archivo es SENSIBLE. No lo compartas ni lo subas a GitHub.**

### 1.2 Estructura de la Colección en Firestore

Crea o verifica que exista esta estructura:

```
/users/{userId}/
  ├── email: "usuario@example.com"
  ├── displayName: "Juan Pérez"
  ├── fcmTokens: {
  │   ├── "device_token_1": {
  │   │   ├── token: "cJ3EHfNEfQ1K4..."
  │   │   ├── deviceName: "Samsung Galaxy S21"
  │   │   ├── createdAt: timestamp
  │   │   └── isActive: true
  │   ├── "device_token_2": {...}
  │   └── ...
  ├── lastNotificationReceived: timestamp
  └── notificationPreferences: {
      ├── mlRecommendations: true
      ├── alerts: true
      └── summaries: true
    }
```

---

## 📱 Paso 2: Guardar Token FCM en Flutter

La app ya tiene implementado esto, pero aquí está el código completo:

### 2.1 En `lib/config/services/notification_service.dart`

```dart
/// Guardar token FCM en Firestore asociado al usuario
Future<void> saveTokenToDatabase(String userId) async {
  try {
    final token = _fcmToken;
    if (token == null) {
      print('❌ Token FCM no disponible');
      return;
    }

    // Obtener nombre del dispositivo
    final deviceInfo = await _getDeviceInfo();
    
    final tokenData = {
      'token': token,
      'deviceName': deviceInfo,
      'createdAt': FieldValue.serverTimestamp(),
      'isActive': true,
      'platform': Platform.isAndroid ? 'android' : 'ios',
      'lastUpdated': FieldValue.serverTimestamp(),
    };

    // Guardar en Firestore bajo /users/{userId}/fcmTokens/
    await _firestore
        .collection('users')
        .doc(userId)
        .collection('fcmTokens')
        .doc(token)
        .set(tokenData, SetOptions(merge: true));

    print('✅ Token FCM guardado en Firestore: $token');
  } catch (e) {
    print('❌ Error guardando token FCM: $e');
  }
}

/// Obtener información del dispositivo
Future<String> _getDeviceInfo() async {
  try {
    if (Platform.isAndroid) {
      return 'Android Device';
    } else if (Platform.isIOS) {
      return 'iOS Device';
    }
    return 'Unknown Device';
  } catch (e) {
    return 'Unknown Device';
  }
}

/// Escuchar cambios de token FCM (cuando expira o se genera uno nuevo)
void _setupTokenRefreshListener() {
  _firebaseMessaging.onTokenRefresh.listen((newToken) async {
    print('🔄 Token FCM renovado: $newToken');
    _fcmToken = newToken;
    
    // Actualizar en Firestore para el usuario actual
    final userId = _getCurrentUserId(); // Implementar según tu app
    if (userId != null) {
      await saveTokenToDatabase(userId);
    }
  });
}
```

### 2.2 Llamar al Iniciar Sesión

En tu `AuthProvider` o en el `LoginPage`:

```dart
// Después del login exitoso
await authProvider.signIn(email: email, password: password);

if (authProvider.isAuthenticated) {
  final userId = authProvider.user!.uid;
  
  // Guardar token FCM
  final notificationService = NotificationService();
  await notificationService.saveTokenToDatabase(userId);
  
  print('✅ Usuario autenticado y token FCM guardado');
}
```

---

## 🐍 Paso 3: Crear la API en Google Colab

### 3.1 Instalar Dependencias en Colab

```python
# En la primera celda de tu notebook Colab
!pip install firebase-admin
!pip install requests
!pip install google-cloud-firestore
```

### 3.2 Autenticarse con Firebase

```python
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from firebase_admin import firestore
import json

# Opción 1: Subir el archivo JSON descargado en Colab
from google.colab import files
uploaded = files.upload()

# El nombre del archivo debe ser tu archivo JSON de Service Account
credential_file = 'gestor-financiero-28ac2-xxxxx.json'

# Inicializar Firebase
cred = credentials.Certificate(credential_file)
firebase_admin.initialize_app(cred)

# Obtener referencias
db = firestore.client()
```

### 3.3 Funciones para Enviar Notificaciones

```python
def obtener_tokens_fcm_usuario(user_id):
    """
    Obtiene todos los tokens FCM asociados a un usuario
    
    Args:
        user_id (str): ID del usuario en Firebase
    
    Returns:
        list: Lista de tokens FCM activos
    """
    try:
        # Acceder a la subcolección de tokens
        tokens_ref = db.collection('users').document(user_id).collection('fcmTokens')
        docs = tokens_ref.where('isActive', '==', True).stream()
        
        tokens = []
        for doc in docs:
            token_data = doc.to_dict()
            tokens.append({
                'token': token_data.get('token'),
                'deviceName': token_data.get('deviceName'),
                'platform': token_data.get('platform')
            })
        
        print(f"✅ {len(tokens)} tokens encontrados para usuario {user_id}")
        return tokens
    
    except Exception as e:
        print(f"❌ Error obteniendo tokens FCM: {e}")
        return []


def enviar_notificacion(user_id, titulo, cuerpo, datos=None):
    """
    Envía una notificación a todos los dispositivos de un usuario
    
    Args:
        user_id (str): ID del usuario en Firebase
        titulo (str): Título de la notificación
        cuerpo (str): Cuerpo/contenido de la notificación
        datos (dict): Datos adicionales opcionales
    
    Returns:
        dict: Resultado del envío (tokens exitosos y fallidos)
    """
    try:
        # Obtener tokens
        tokens = obtener_tokens_fcm_usuario(user_id)
        
        if not tokens:
            print(f"⚠️  No hay dispositivos registrados para {user_id}")
            return {
                'exitosos': 0,
                'fallidos': 0,
                'tokens': []
            }
        
        # Preparar datos adicionales
        notif_data = datos or {}
        notif_data['userId'] = user_id  # Incluir userId en datos
        notif_data['timestamp'] = str(datetime.now().isoformat())
        
        # Crear mensaje
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=titulo,
                body=cuerpo,
            ),
            data=notif_data,
            tokens=[t['token'] for t in tokens]
        )
        
        # Enviar
        response = messaging.send_multicast(message)
        
        # Procesar respuesta
        resultado = {
            'exitosos': response.success_count,
            'fallidos': response.failure_count,
            'tokens_enviados': len(tokens),
            'mensaje': f"Notificación enviada a {response.success_count} dispositivos"
        }
        
        print(f"✅ {resultado['exitosos']} notificaciones enviadas exitosamente")
        print(f"❌ {resultado['fallidos']} notificaciones fallaron")
        
        return resultado
    
    except Exception as e:
        print(f"❌ Error enviando notificación: {e}")
        return {
            'exitosos': 0,
            'fallidos': 0,
            'error': str(e)
        }


def enviar_notificacion_a_multiples_usuarios(user_ids, titulo, cuerpo, datos=None):
    """
    Envía una notificación a múltiples usuarios
    
    Args:
        user_ids (list): Lista de IDs de usuarios
        titulo (str): Título de la notificación
        cuerpo (str): Cuerpo de la notificación
        datos (dict): Datos adicionales
    
    Returns:
        dict: Resumen de los envíos
    """
    resumen = {
        'usuarios_totales': len(user_ids),
        'usuarios_exitosos': 0,
        'usuarios_fallidos': 0,
        'notificaciones_enviadas': 0,
        'detalles': []
    }
    
    for user_id in user_ids:
        resultado = enviar_notificacion(user_id, titulo, cuerpo, datos)
        resumen['notificaciones_enviadas'] += resultado.get('exitosos', 0)
        
        if resultado.get('exitosos', 0) > 0:
            resumen['usuarios_exitosos'] += 1
        else:
            resumen['usuarios_fallidos'] += 1
        
        resumen['detalles'].append({
            'user_id': user_id,
            'exitosas': resultado.get('exitosos', 0),
            'fallidas': resultado.get('fallidos', 0)
        })
    
    return resumen
```

---

## 📊 Paso 4: Casos de Uso de la API

### 4.1 Notificación de Predicción ML

```python
from datetime import datetime

def notificar_prediccion(user_id, prediccion_data):
    """
    Envía notificación cuando hay una nueva predicción del modelo ML
    
    Args:
        user_id (str): ID del usuario
        prediccion_data (dict): Datos de la predicción
    """
    
    titulo = "📊 Nueva Predicción Disponible"
    
    # Crear cuerpo según el tipo de predicción
    gasto_predicho = prediccion_data.get('gasto_predicho', 0)
    categoria = prediccion_data.get('categoria', 'General')
    confianza = prediccion_data.get('confianza', 0)
    
    cuerpo = f"Se predice un gasto de ${gasto_predicho:.2f} en {categoria} (Confianza: {confianza:.0%})"
    
    datos = {
        'tipo': 'prediccion',
        'prediccion_id': prediccion_data.get('id'),
        'gasto_predicho': str(gasto_predicho),
        'categoria': categoria,
        'confianza': str(confianza),
        'timestamp': datetime.now().isoformat()
    }
    
    return enviar_notificacion(user_id, titulo, cuerpo, datos)


# Usar:
resultado = notificar_prediccion('usuario123', {
    'id': 'pred_001',
    'gasto_predicho': 150.50,
    'categoria': 'Alimentación',
    'confianza': 0.85
})
```

### 4.2 Notificación de Anomalía Detectada

```python
def notificar_anomalia(user_id, anomalia_data):
    """
    Envía notificación cuando se detecta una anomalía en gastos
    
    Args:
        user_id (str): ID del usuario
        anomalia_data (dict): Datos de la anomalía
    """
    
    titulo = "⚠️ Anomalía Detectada"
    
    tipo_anomalia = anomalia_data.get('tipo', 'gasto inusual')
    monto = anomalia_data.get('monto', 0)
    razon = anomalia_data.get('razon', 'Excede el promedio')
    
    cuerpo = f"{tipo_anomalia}: ${monto:.2f} - {razon}"
    
    datos = {
        'tipo': 'anomalia',
        'anomalia_id': anomalia_data.get('id'),
        'monto': str(monto),
        'tipo_anomalia': tipo_anomalia,
        'razon': razon
    }
    
    return enviar_notificacion(user_id, titulo, cuerpo, datos)


# Usar:
resultado = notificar_anomalia('usuario123', {
    'id': 'anom_001',
    'tipo': 'Gasto Anormal',
    'monto': 500.00,
    'razon': 'El gasto es 300% superior al promedio'
})
```

### 4.3 Notificación de Recomendación

```python
def notificar_recomendacion(user_id, recomendacion_data):
    """
    Envía notificación con recomendación personalizada del modelo ML
    
    Args:
        user_id (str): ID del usuario
        recomendacion_data (dict): Datos de la recomendación
    """
    
    titulo = "💡 Recomendación Personalizada"
    
    accion = recomendacion_data.get('accion', 'Revisar gastos')
    ahorro_potencial = recomendacion_data.get('ahorro_potencial', 0)
    categoria = recomendacion_data.get('categoria', 'General')
    
    cuerpo = f"{accion} en {categoria}. Ahorro potencial: ${ahorro_potencial:.2f}"
    
    datos = {
        'tipo': 'recomendacion',
        'recomendacion_id': recomendacion_data.get('id'),
        'accion': accion,
        'ahorro_potencial': str(ahorro_potencial),
        'categoria': categoria
    }
    
    return enviar_notificacion(user_id, titulo, cuerpo, datos)
```

### 4.4 Análisis Diario

```python
def enviar_analisis_diario(user_id):
    """
    Envía un resumen de análisis diario del usuario
    
    Args:
        user_id (str): ID del usuario
    """
    
    # Aquí iría tu lógica de análisis de ML
    # Por ejemplo, obtener datos del usuario, calcular métricas, etc.
    
    titulo = "📈 Resumen Diario de Gastos"
    
    # Datos simulados - reemplaza con cálculos reales
    gasto_total = 125.50
    categoria_mayor = "Alimentación"
    tendencia = "↓ 15% menos que ayer"
    
    cuerpo = f"Gastaste ${gasto_total:.2f}. Mayor gasto: {categoria_mayor}. {tendencia}"
    
    datos = {
        'tipo': 'resumen_diario',
        'gasto_total': str(gasto_total),
        'categoria_mayor': categoria_mayor,
        'fecha': datetime.now().strftime('%Y-%m-%d')
    }
    
    return enviar_notificacion(user_id, titulo, cuerpo, datos)
```

---

## 📱 Paso 5: Procesar Notificaciones en Flutter

### 5.1 Escuchar Notificaciones FCM

```dart
// En notification_service.dart - Este código ya existe pero lo muestro completo

/// Configurar handlers de FCM
void _setupFCMHandlers() {
  // Notificaciones mientras la app está en primer plano
  FirebaseMessaging.onMessage.listen((RemoteMessage message) {
    print('📬 Notificación en primer plano: ${message.messageId}');
    _handleNotification(message);
  });

  // Notificaciones cuando el usuario toca la notificación
  FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
    print('👆 Usuario tocó notificación: ${message.messageId}');
    _handleNotificationTap(message);
  });

  // Notificaciones en segundo plano (background handler)
  FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);

  // Escuchar renovación de token
  _setupTokenRefreshListener();
}

/// Procesar notificación que llega mientras la app está abierta
Future<void> _handleNotification(RemoteMessage message) async {
  final notificacion = message.notification;
  final datos = message.data;
  
  // Filtrar por userId si es necesario
  final userId = _getCurrentUserId(); // Implementar
  final notifUserId = datos['userId'];
  
  if (notifUserId != userId) {
    print('⚠️ Notificación para otro usuario, ignorando');
    return;
  }

  // Mostrar notificación local
  if (notificacion != null) {
    await _showLocalNotification(
      title: notificacion.title ?? 'Notificación',
      body: notificacion.body ?? '',
      payload: _encodePayload(datos),
    );
  }
  
  // Aquí puedes actualizar tu interfaz o guardar datos
  _processNotificationData(datos);
}

/// Procesar cuando el usuario toca la notificación
Future<void> _handleNotificationTap(RemoteMessage message) async {
  final datos = message.data;
  
  // Navegar según el tipo de notificación
  final tipo = datos['tipo'];
  
  switch (tipo) {
    case 'prediccion':
      // Navegar a pantalla de predicciones
      _navigateTo('predicciones', datos);
      break;
    
    case 'anomalia':
      // Navegar a pantalla de alertas
      _navigateTo('alertas', datos);
      break;
    
    case 'recomendacion':
      // Mostrar modal con recomendación
      _navigateTo('recomendaciones', datos);
      break;
    
    case 'resumen_diario':
      // Ir a estadísticas
      _navigateTo('estadisticas', datos);
      break;
    
    default:
      _navigateTo('home', datos);
  }
}

/// Procesar datos de la notificación
void _processNotificationData(Map<String, dynamic> datos) {
  final tipo = datos['tipo'];
  
  print('📊 Procesando notificación tipo: $tipo');
  
  // Guardar en provider o base de datos local si es necesario
  // Actualizar UI
  // Triggerar acciones
}

/// Mostrar notificación local
Future<void> _showLocalNotification({
  required String title,
  required String body,
  String? payload,
}) async {
  const androidDetails = AndroidNotificationDetails(
    'high_importance_channel',
    'High Importance Notifications',
    channelDescription: 'Notificaciones importantes de ML',
    importance: Importance.max,
    priority: Priority.high,
    showWhen: true,
  );

  const iosDetails = DarwinNotificationDetails(
    presentAlert: true,
    presentBadge: true,
    presentSound: true,
  );

  const details = NotificationDetails(
    android: androidDetails,
    iOS: iosDetails,
  );

  await _localNotifications.show(
    DateTime.now().millisecondsSinceEpoch ~/ 1000,
    title,
    body,
    details,
    payload: payload,
  );
}
```

### 5.2 Filtrar Notificaciones por userId

```dart
// En cualquier service o provider donde manejes notificaciones:

class NotificationFilterService {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  
  /// Verificar si una notificación es para el usuario actual
  bool isNotificationForCurrentUser(Map<String, dynamic> notificationData) {
    final currentUserId = _auth.currentUser?.uid;
    final notifUserId = notificationData['userId'];
    
    if (currentUserId == null) {
      print('⚠️ Usuario no autenticado');
      return false;
    }
    
    if (notifUserId != currentUserId) {
      print('⚠️ Notificación para otro usuario');
      return false;
    }
    
    return true;
  }
  
  /// Procesar solo notificaciones del usuario actual
  Future<void> processNotificationIfForCurrentUser(
    Map<String, dynamic> notificationData
  ) async {
    if (isNotificationForCurrentUser(notificationData)) {
      // Procesar notificación
      print('✅ Procesando notificación para usuario actual');
      // Tu lógica aquí
    }
  }
}
```

---

## 🔐 Paso 6: Seguridad y Mejores Prácticas

### 6.1 Reglas de Firestore

Actualiza `firestore.rules` para proteger los tokens:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Usuarios solo pueden ver/modificar sus propios datos
    match /users/{userId} {
      allow read, write: if request.auth.uid == userId;
      
      // Los tokens solo el usuario propietario puede leer/escribir
      match /fcmTokens/{tokenId} {
        allow read, write: if request.auth.uid == userId;
      }
    }
    
    // La API (Service Account) puede leer tokens para enviar notificaciones
    // Esta regla debe estar disponible para tu backend
    match /{document=**} {
      allow read, write: if request.auth.token.firebase.sign_in_provider == 'custom'
                         || request.auth.token.iss == 'https://securetoken.google.com/gestor-financiero-28ac2';
    }
  }
}
```

### 6.2 Variables de Entorno en Colab

Nunca hardcodees el JSON de Service Account. Usa variables de entorno:

```python
import os
from google.colab import userdata

# En Colab, guardar el JSON como secreto
# Luego acceder:
credential_json = userdata.get('FIREBASE_CREDENTIALS')

# En producción (servidor)
credential_json = os.environ.get('FIREBASE_CREDENTIALS')
```

### 6.3 Validación de Datos

```python
def validar_datos_notificacion(datos):
    """
    Validar que los datos sean correctos antes de enviar
    """
    campos_requeridos = ['user_id', 'titulo', 'cuerpo']
    
    for campo in campos_requeridos:
        if campo not in datos or not datos[campo]:
            raise ValueError(f"Campo requerido faltante: {campo}")
    
    # Validar longitud
    if len(datos['titulo']) > 65:
        raise ValueError("Título muy largo (máx 65 caracteres)")
    
    if len(datos['cuerpo']) > 240:
        raise ValueError("Cuerpo muy largo (máx 240 caracteres)")
    
    return True
```

---

## ✅ Checklist de Implementación

- [ ] Descargar Service Account JSON desde Firebase Console
- [ ] Crear estructura de colecciones en Firestore
- [ ] Implementar `saveTokenToDatabase()` en Flutter
- [ ] Guardar token FCM cuando el usuario inicia sesión
- [ ] Instalar `firebase-admin` en Google Colab
- [ ] Crear funciones de envío de notificaciones en Colab
- [ ] Configurar handlers de FCM en Flutter
- [ ] Implementar filtrado por userId
- [ ] Actualizar reglas de seguridad en Firestore
- [ ] Probar enviando notificaciones de prueba
- [ ] Documentar endpoints y casos de uso
- [ ] Implementar retry logic para fallos
- [ ] Monitorear en Firebase Console

---

## 🧪 Pruebas

### Prueba desde Colab

```python
# Prueba simple de envío
user_id = 'TEST_USER_ID'  # Reemplaza con un usuario real

resultado = enviar_notificacion(
    user_id=user_id,
    titulo="🧪 Notificación de Prueba",
    cuerpo="Si ves esto, ¡todo está funcionando!",
    datos={
        'tipo': 'prueba',
        'timestamp': datetime.now().isoformat()
    }
)

print(f"Resultado: {resultado}")
```

### Prueba desde Flutter

```dart
// En tu app, cuando quieras probar:
import 'package:firebase_messaging/firebase_messaging.dart';

// Simular llegada de notificación
await FirebaseMessaging.instance.sendMessage(
  to: 'tu_token_fcm_aqui',
);
```

---

## 🐛 Solución de Problemas

| Problema | Solución |
|----------|----------|
| "Token no encontrado" | Asegurar que el usuario inició sesión y guardó su token |
| "Notificación no llega" | Verificar que el token esté activo en Firestore |
| "Notificación llega a usuario incorrecto" | Verificar que userId sea correcto en datos |
| "Error de permisos en Colab" | Revisar que Service Account tenga permisos de FCM |
| "Token expirado" | Implementar refresh automático (ya está en el código) |

---

## 📚 Referencias

- [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging)
- [Firebase Admin SDK Python](https://firebase.google.com/docs/reference/admin/python)
- [Flutter firebase_messaging](https://pub.dev/packages/firebase_messaging)
- [Google Colab + Firebase](https://colab.research.google.com/github/firebase/firebase-admin-python/blob/master/docs/source/firebaseadmin.md)

---

## 📞 Soporte

Si tienes dudas:
1. Revisa la documentación de Firebase
2. Consulta los ejemplos de código en este documento
3. Verifica los logs en Firebase Console
4. Revisa la consola de Colab para errores
