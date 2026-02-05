# 🐛 Troubleshooting y FAQs: Sistema de Notificaciones API Colab

## ❓ Preguntas Frecuentes (FAQs)

### 1. "¿Cómo obtengo el userId del usuario?"

**Respuesta:** El `userId` es el UID que genera Firebase Auth automáticamente:

```dart
// En Flutter
final userId = FirebaseAuth.instance.currentUser!.uid;

// Copiar y pegar en Colab:
user_id = "ABC123xyz789..."  // Este UUID

// O desde Firestore Console:
// Authentication → Usuarios → Copiar el UID
```

### 2. "¿Qué pasa si el usuario tiene múltiples dispositivos?"

**Respuesta:** Cada dispositivo tiene un token diferente. El sistema:
- Guarda todos los tokens bajo `fcmTokens/{token}`
- Envía la notificación a TODOS los dispositivos activos
- El usuario la recibe en todos sus dispositivos

```
Dispositivo 1 (Samsung): token_1 ✅
Dispositivo 2 (iPhone):  token_2 ✅
Dispositivo 3 (Tablet):  token_3 ✅
         ↓
    Notificación → Todos reciben
```

### 3. "¿Puedo enviar notificaciones a múltiples usuarios a la vez?"

**Respuesta:** Sí, usa `enviar_lote()`:

```python
usuarios_para_notificar = [
    {
        'user_id': 'usuario_1',
        'titulo': 'Nuevo análisis',
        'cuerpo': 'Tus predicciones están listas'
    },
    {
        'user_id': 'usuario_2',
        'titulo': 'Nuevo análisis',
        'cuerpo': 'Tus predicciones están listas'
    }
]

resultado = notif_manager.enviar_lote(usuarios_para_notificar)
print(f"Enviadas a {resultado['usuarios_exitosos']} usuarios")
```

### 4. "¿Cuánto tiempo tarda en llegar la notificación?"

**Respuesta:** Normalmente **menos de 1 segundo** si:
- El dispositivo está conectado a internet ✅
- El usuario está autenticado ✅
- El token es válido ✅

Si tarda más o no llega:
- Ver sección de [Troubleshooting](#troubleshooting-problems)

### 5. "¿Las notificaciones se guardan en la base de datos?"

**Respuesta:** Por defecto NO. Pero puedes guardarlas:

```python
# Después de enviar
resultado = notif_manager.enviar_notificacion(...)

# Guardar log
db.collection('notification_logs').document().set({
    'user_id': user_id,
    'type': 'prediccion',
    'title': titulo,
    'body': cuerpo,
    'sent_at': datetime.now(),
    'success': resultado['exitosas'] > 0
})
```

### 6. "¿Qué ocurre si un token expira?"

**Respuesta:** Firebase maneja esto automáticamente:
- Flutter regenera automáticamente tokens expirados
- El nuevo token se guarda en Firestore
- Las notificaciones se envían al token activo

Limpia tokens inactivos regularmente:

```python
# En Colab - eliminar tokens de hace 30 días
fecha_limite = datetime.now() - timedelta(days=30)
docs = db.collection('users').document(user_id).collection('fcmTokens')\
    .where('lastUpdated', '<', fecha_limite).stream()

for doc in docs:
    doc.reference.delete()
```

### 7. "¿Necesito configurar algo especial en iOS?"

**Respuesta:** Casi nada, ya está configurado:
- Flutter + firebase_messaging lo maneja
- Solo asegúrate de que los permisos estén activados
- En iOS 15+, usuario debe otorgar permiso para notificaciones

### 8. "¿Las notificaciones funcionan cuando la app está cerrada?"

**Respuesta:** Sí. Firebase usa el `background handler`:

```dart
@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  // Se ejecuta incluso si app está cerrada
  print('Notificación en background: ${message.notification?.title}');
}
```

### 9. "¿Cuál es el costo de usar FCM?"

**Respuesta:** 
- Notificaciones de FCM: **GRATIS para primeras 20,000/mes**
- Firestore: **125,000 escrituras/mes GRATIS**
- Después: ~$0.10 por 100,000 notificaciones

Muy económico incluso en escala.

### 10. "¿Puedo personalizar el sonido/vibración de la notificación?"

**Respuesta:** Sí, en el cliente (Flutter):

```dart
// En notification_service.dart
const androidDetails = AndroidNotificationDetails(
  'channel_id',
  'Channel Name',
  sound: RawResourceAndroidNotificationSound('notification_sound'),
  vibrationPattern: Int64List.fromList([0, 250, 250, 250]),
  importance: Importance.max,
);
```

---

## 🐛 Troubleshooting: Problemas y Soluciones

### Problema 1: "Token no encontrado en Firestore"

**Síntomas:**
```
Error: No tokens found for user usuario_123
```

**Causas posibles:**

1. ❌ Usuario no inició sesión correctamente
   ```dart
   // ✅ DEBE haber esto en el login:
   await notificationService.saveTokenToDatabase(authProvider.user!.uid);
   ```

2. ❌ El usuario cerró la app sin permitir permisos
   ```dart
   // Verificar en Android/iOS settings que permisos estén ON
   ```

3. ❌ Firestore colección no existe aún
   - Es normal, se crea cuando se intenta guardrar el primer documento

**Solución:**

```dart
// En main.dart o login_page.dart
final notificationService = NotificationService();
final userId = authProvider.user!.uid;

try {
  await notificationService.saveTokenToDatabase(userId);
  print('✅ Token guardado: $userId');
} catch (e) {
  print('❌ Error: $e');
}
```

**Verificar en Firestore Console:**
```
users → usuario_123 → fcmTokens → {token} → Debe existir
```

---

### Problema 2: "Notificación no llega a la app"

**Síntomas:**
- Ejecuté `enviar_notificacion()` en Colab
- No recibí nada en la app ❌

**Diagnóstico paso a paso:**

1️⃣ **Verificar token en Firestore**
```python
# En Colab
tokens = notif_manager.obtener_tokens_usuario('usuario_123')
print(tokens)

# Debe retornar lista NO VACÍA con estructura:
# [{'token': 'cJ3EHfN...', 'isActive': True, ...}]

# Si está vacía → El usuario no tiene tokens guardados
```

2️⃣ **Verificar conectividad del dispositivo**
- Abrir app Flutter
- Verificar que está conectada a internet
- Notar en logs: "FCM Token: ..."

3️⃣ **Verificar que isActive == true**
```python
# En Colab
db.collection('users').document('usuario_123')\
  .collection('fcmTokens').stream()

# Todos deben tener isActive: True
```

4️⃣ **Verificar en Firebase Console**
```
Cloud Messaging → Envíos (mira estadísticas)
¿Se muestra la notificación que enviaste?
```

5️⃣ **Revisar logs de Android Studio**
```
Android Studio → Logcat → Filtro: "FCM"
Buscar mensajes del sistema
```

**Soluciones comunes:**

```python
# Solución 1: Token inactivo
db.collection('users').document(user_id)\
  .collection('fcmTokens').document(token).update({
    'isActive': True
  })

# Solución 2: Regenerar token en Flutter
# Desinstalar app y reinstalar
# Notificaciones de Firebase se inicializan de nuevo

# Solución 3: Verificar permisos Android
# Ir a Settings → Apps → Tu App → Notifications → ON
```

---

### Problema 3: "Error: 'Token es inválido o expirado'"

**Síntomas:**
```
messaging.exceptions.InvalidArgumentError: Invalid token
```

**Causa:** El token en Firestore ya no es válido

**Solución:**

```python
# Opción 1: Limpiar tokens viejos
tokens_inactivos = db.collection('users').document(user_id)\
  .collection('fcmTokens').where('isActive', '==', False).stream()

for doc in tokens_inactivos:
    doc.reference.delete()

# Opción 2: Pedirle al usuario que abra la app
# (Flutter regenerará el token automáticamente)

# Opción 3: Implementar retry
def enviar_con_reintentos(user_id, titulo, cuerpo, max_intentos=3):
    for intento in range(max_intentos):
        try:
            return notif_manager.enviar_notificacion(user_id, titulo, cuerpo)
        except Exception as e:
            if intento == max_intentos - 1:
                raise e
            time.sleep(2 ** intento)  # Backoff exponencial
```

---

### Problema 4: "Module 'firebase_admin' no encontrado"

**Síntomas:**
```
ModuleNotFoundError: No module named 'firebase_admin'
```

**Solución (en Colab):**

```python
# Primera celda SIEMPRE:
!pip install firebase-admin

# Luego ejecutar el resto del código
import firebase_admin
```

---

### Problema 5: "TypeError: Object of type Timestamp is not JSON serializable"

**Síntomas:**
```python
TypeError cuando intento guardar datos con timestamp
```

**Causa:** Firebase Timestamp no es serializable a JSON

**Solución:**

```python
# Opción 1: Convertir a string
datos = {
    'timestamp': datetime.now().isoformat()  # String, no Timestamp
}

# Opción 2: Cuando lees de Firestore
doc_data = doc.to_dict()
doc_data['timestamp'] = str(doc_data['timestamp'])

# Opción 3: Usar solo FieldValue.serverTimestamp()
db.collection('notificaciones').document().set({
    'sent_at': firestore.firestore.FieldValue.server_timestamp(),
    'user_id': user_id
})
```

---

### Problema 6: "Firestore rechaza la escritura (Permission denied)"

**Síntomas:**
```
google.api_core.exceptions.PermissionDenied: 403 Permission denied
```

**Causa:** Las reglas de Firestore no permiten la operación

**Solución:**

1. Verificar que Service Account tiene permisos
2. Revisar reglas de Firestore:

```firestore
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Permitir leer/escribir si está autenticado
    match /users/{userId} {
      allow read, write: if request.auth != null;
    }
  }
}
```

---

### Problema 7: "¿Cómo puedo probar sin un usuario real?"

**Solución:** Crear usuario de prueba en Firebase:

```dart
// En Flutter (durante desarrollo)
final authProvider = context.read<AuthProvider>();

// Registrar usuario de prueba
await authProvider.register(
  email: 'test@example.com',
  password: 'Test123456!',
  displayName: 'Usuario Test'
);

// Abrir app y guardar token
final notificationService = NotificationService();
await notificationService.saveTokenToDatabase(authProvider.user!.uid);

// Copiar el UID
print('UID de prueba: ${authProvider.user!.uid}');
```

```python
# En Colab - usar el UID de prueba
user_id_test = 'ABC123xyz789...'  # El UID que copiaste

# Enviar notificación de prueba
resultado = notif_manager.enviar_notificacion(
    user_id_test,
    '🧪 Notificación de Prueba',
    'Si ves esto, ¡todo funciona!'
)
```

---

### Problema 8: "Las notificaciones llegan pero no se muestran"

**Síntomas:**
- En Firestore Console veo que se "enviaron"
- Pero el usuario no ve nada ❌

**Diagnóstico:**

1. ¿Están los handlers de FCM configurados?
```dart
// En NotificationService, debe estar:
FirebaseMessaging.onMessage.listen((RemoteMessage message) {
  _handleNotification(message);
});
```

2. ¿Está la app en segundo plano?
```dart
// Verificar background handler en main.dart
@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  print('Notificación en background');
}
```

3. ¿Tiene permisos en Android/iOS?
- Android: Settings → Apps → Tu App → Notifications → ON
- iOS: Settings → Tu App → Notifications → ON

**Solución:**

```dart
// En NotificationService, verifica que esto está:
void _setupFCMHandlers() {
  // Cuando app está abierta
  FirebaseMessaging.onMessage.listen((RemoteMessage message) {
    print('📬 Mensaje: ${message.notification?.title}');
    _handleNotification(message);
  });

  // Cuando usuario toca la notificación
  FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
    print('👆 Usuario tocó: ${message.messageId}');
    _handleNotificationTap(message);
  });

  // En segundo plano
  FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);
}
```

---

### Problema 9: "Error de autenticación en Service Account"

**Síntomas:**
```
google.auth.exceptions.DefaultCredentialsError: Could not automatically determine credentials
```

**Causa:** El archivo JSON no está donde se espera

**Solución:**

```python
# ✅ CORRECTO en Colab:
from google.colab import files
uploaded = files.upload()  # Sube el JSON

credential_file = list(uploaded.keys())[0]  # Obtén el nombre
cred = credentials.Certificate(credential_file)

# ✅ CORRECTO en servidor:
import os
credential_json = os.environ.get('FIREBASE_CREDENTIALS')
cred = credentials.Certificate(json.loads(credential_json))
```

---

### Problema 10: "Notificación llega pero userId no coincide"

**Síntomas:**
- Usuario A recibe notificación destinada a Usuario B ❌

**Causa:** No se está filtrando por userId

**Solución:**

```dart
// En Flutter - SIEMPRE verificar:
void _handleNotification(RemoteMessage message) {
  final currentUserId = FirebaseAuth.instance.currentUser?.uid;
  final notificationUserId = message.data['userId'];
  
  // ✅ IMPORTANTE: Filtrar por userId
  if (currentUserId != notificationUserId) {
    print('⚠️ Notificación para otro usuario, ignorando');
    return;
  }
  
  // Procesar si es para el usuario actual
  _processNotificationData(message.data);
}
```

```python
# En Colab - verificar al enviar:
datos = {
    'userId': user_id,  # ✅ SIEMPRE incluir
    'tipo': 'prediccion',
    'timestamp': datetime.now().isoformat()
}

message = messaging.MulticastMessage(
    notification=messaging.Notification(...),
    data=datos,
    tokens=tokens
)
```

---

## 📊 Checklist de Debugging

Cuando algo no funciona, revisar en orden:

1. **Firebase Console**
   - [ ] Project existe y está activo
   - [ ] Firestore Database OK
   - [ ] Authentication habilitado
   - [ ] Cloud Messaging activo

2. **Firestore**
   - [ ] Usuarios colección existe
   - [ ] Tokens están guardados
   - [ ] isActive = true
   - [ ] Reglas de seguridad permiten

3. **Flutter App**
   - [ ] notification_service inicializado
   - [ ] Token se guarda en login
   - [ ] Permisos otorgados (Android/iOS)
   - [ ] Handlers de FCM registrados

4. **Google Colab**
   - [ ] firebase-admin instalado
   - [ ] Credenciales subidas
   - [ ] Conexión a Firestore OK
   - [ ] No hay errores en ejecución

5. **Notificaciones**
   - [ ] `obtener_tokens_usuario()` retorna tokens
   - [ ] `enviar_notificacion()` no da error
   - [ ] Firebase Console muestra envío
   - [ ] App recibe la notificación

---

## 🆘 Cuando Todo Falla

Si nada funciona, intenta esto:

```python
# 1. Verificar setup COMPLETAMENTE
probar_configuracion()

# 2. Si el problema persiste, hacer reset:

# En Firebase Console:
# - Eliminar colección users
# - Desinstalar app
# - Limpiar cache de Android Studio

# En Colab:
# - Reiniciar runtime
# - Reinstalar dependencias
# - Subir credenciales de nuevo

# En la app:
# - Desinstalar completamente
# - Reinstalar desde cero
# - Volver a iniciar sesión
```

```python
# 3. Si aún no funciona, verificar logs:

# Opción A: Firebase Console
# Cloud Messaging → Envíos
# Ver estadísticas de entrega

# Opción B: Android Studio Logcat
# Buscar: "FCM" o "firebase"
# Ver qué dice

# Opción C: Colab
# Activar print statements
# Ver qué se ejecuta
```

---

## 📞 Recursos de Ayuda

1. **Documentación oficial:**
   - [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging)
   - [Firebase Admin SDK Python](https://firebase.google.com/docs/reference/admin/python)
   - [Flutter firebase_messaging](https://pub.dev/packages/firebase_messaging)

2. **Foros y comunidades:**
   - Stack Overflow: tag `firebase` + `flutter`
   - Firebase Community: https://firebase.google.com/community
   - GitHub Issues: firebase/firebase-admin-python

3. **Contactos del proyecto:**
   - Revisar documentación en `docs/`
   - Contactar al equipo de desarrollo

---

**Última actualización:** Febrero 2025
**Versión:** 1.0 ✅
