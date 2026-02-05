# 🚀 Quick Reference: Comandos y Código Esencial

## ⚡ Comandos Rápidos

### Google Colab

```python
# 1️⃣ Instalar dependencias
!pip install firebase-admin requests google-cloud-firestore pandas

# 2️⃣ Subir credenciales
from google.colab import files
uploaded = files.upload()
credential_file = list(uploaded.keys())[0]

# 3️⃣ Inicializar Firebase
import firebase_admin
from firebase_admin import credentials, messaging, firestore
cred = credentials.Certificate(credential_file)
firebase_admin.initialize_app(cred)
db = firestore.client()

# 4️⃣ Enviar notificación simple
def send_notification(user_id, title, body):
    tokens_ref = db.collection('users').document(user_id).collection('fcmTokens')
    tokens = [doc.to_dict()['token'] for doc in tokens_ref.where('isActive', '==', True).stream()]
    if tokens:
        msg = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            tokens=tokens
        )
        response = messaging.send_multicast(msg)
        return response.success_count
    return 0

# 5️⃣ Usar
send_notification('user_id_aqui', '📊 Predicción', '$150 en Alimentación')
```

### Flutter

```dart
// 1️⃣ En LoginPage (después del login)
final notificationService = NotificationService();
await notificationService.saveTokenToDatabase(authProvider.user!.uid);

// 2️⃣ Acceder al token
final token = NotificationService().fcmToken;
print('Token: $token');

// 3️⃣ Obtener userId actual
final userId = FirebaseAuth.instance.currentUser!.uid;
print('User ID: $userId');
```

---

## 📋 Firestore Queries

### Obtener tokens de un usuario
```python
# En Colab
tokens = db.collection('users').document(user_id).collection('fcmTokens').stream()
tokens_list = [doc.to_dict() for doc in tokens]
```

### Obtener notificaciones guardadas
```python
# En Colab
logs = db.collection('notification_logs')\
    .where('user_id', '==', user_id)\
    .order_by('sent_at', direction='DESCENDING')\
    .limit(10)\
    .stream()
```

### Limpiar tokens viejos
```python
# En Colab
from datetime import datetime, timedelta
fecha_limite = datetime.now() - timedelta(days=30)
old_tokens = db.collection('users').document(user_id)\
    .collection('fcmTokens')\
    .where('lastUpdated', '<', fecha_limite)\
    .stream()

for doc in old_tokens:
    doc.reference.delete()
```

---

## 🎯 Casos de Uso - Código Minimal

### Predicción
```python
ml_service.notificar_prediccion_gasto('user_id', {
    'prediccion_id': 'pred_001',
    'gasto_predicho': 150.50,
    'categoria': 'Alimentación',
    'confianza': 0.85,
    'base_historica': 120.00
})
```

### Anomalía
```python
ml_service.notificar_anomalia('user_id', {
    'tipo': 'gasto_anormal',
    'monto': 500.00,
    'categoria': 'Entretenimiento',
    'promedio': 150.00,
    'razon': 'Exceede 3x el promedio'
})
```

### Recomendación
```python
ml_service.notificar_recomendacion('user_id', {
    'accion': 'Reducir gastos en Entretenimiento',
    'categoria': 'Entretenimiento',
    'ahorro_potencial': 300.00,
    'porcentaje': 0.35
})
```

### A múltiples usuarios
```python
usuarios = [
    {'user_id': 'user_1', 'titulo': 'Hola', 'cuerpo': 'Test 1'},
    {'user_id': 'user_2', 'titulo': 'Hola', 'cuerpo': 'Test 2'},
]
notif_manager.enviar_lote(usuarios)
```

---

## 🔗 URLs Importantes

| Recurso | URL |
|---------|-----|
| **Firebase Console** | https://console.firebase.google.com |
| **Google Colab** | https://colab.research.google.com |
| **FCM Documentation** | https://firebase.google.com/docs/cloud-messaging |
| **Firebase Admin SDK** | https://firebase.google.com/docs/reference/admin/python |
| **flutter_firebase_messaging** | https://pub.dev/packages/firebase_messaging |

---

## 📊 Estructura Firestore Minimal

```
users/{userId}/
  ├── email: string
  ├── displayName: string
  └── fcmTokens/{token}/
      ├── token: string
      ├── platform: string (android|ios)
      ├── isActive: boolean
      └── lastUpdated: timestamp
```

---

## 🔐 Reglas Firestore Minimal

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth.uid == userId;
      match /fcmTokens/{token} {
        allow read, write: if request.auth.uid == userId;
      }
    }
  }
}
```

---

## ❌ Errores Comunes y Soluciones Rápidas

| Error | Solución |
|-------|----------|
| `Token not found` | Verificar que usuario inició sesión y guardó token |
| `ModuleNotFoundError` | `!pip install firebase-admin` en Colab |
| `PermissionDenied` | Revisar reglas Firestore |
| `Invalid token` | Token expiró, usuario debe abrir app de nuevo |
| `No tokens returned` | Verificar `isActive: true` en Firestore |

---

## 📁 Archivos Clave

```
lib/config/services/
  ├── notification_service.dart ← Principal
  └── push_notifications_service.dart

lib/modules/auth/
  └── auth_provider.dart ← Guardar token aquí

docs/
  ├── INDICE_API_COLAB_NOTIFICACIONES.md ← EMPIEZA AQUÍ
  ├── INICIO_RAPIDO_COLAB_NOTIFICACIONES.md
  ├── GUIA_API_COLAB_NOTIFICACIONES.md
  ├── EJEMPLOS_API_COLAB_NOTIFICACIONES.md
  ├── CHECKLIST_API_COLAB_NOTIFICACIONES.md
  ├── ARQUITECTURA_API_COLAB_NOTIFICACIONES.md
  └── TROUBLESHOOTING_API_COLAB_NOTIFICACIONES.md
```

---

## ⏱️ Tiempos Típicos

| Actividad | Tiempo |
|-----------|--------|
| Setup inicial | 5 min |
| Primera notificación | 2 min |
| Guardar tokens en Flutter | 5 min |
| Crear NotificationManager | 10 min |
| Implementar casos de uso | 15 min |
| Testing completo | 20 min |
| **Total** | **~1 hora** |

---

## 🎓 Recursos por Nivel

### Principiante
- INICIO_RAPIDO_COLAB_NOTIFICACIONES.md
- EJEMPLOS_API_COLAB_NOTIFICACIONES.md (ej 1-2)

### Intermedio
- GUIA_API_COLAB_NOTIFICACIONES.md (completa)
- EJEMPLOS_API_COLAB_NOTIFICACIONES.md (ej 3-5)

### Avanzado
- ARQUITECTURA_API_COLAB_NOTIFICACIONES.md
- CHECKLIST_API_COLAB_NOTIFICACIONES.md (fase 9)

### Debugging
- TROUBLESHOOTING_API_COLAB_NOTIFICACIONES.md

---

## 🔄 Flujo Rápido de Desarrollo

```
1. Descargar credenciales (Firebase)
   ↓
2. Crear proyecto Colab
   ↓
3. Guardar token en Flutter
   ↓
4. Crear NotificationManager
   ↓
5. Enviar notificación test
   ↓
6. Verificar en app
   ↓
7. Implementar casos de uso ML
   ↓
8. Testing completo
   ↓
9. Deploy a producción
```

---

## 📞 Líneas de Soporte

### Si necesitas...

**Empezar rápido**
→ INICIO_RAPIDO_COLAB_NOTIFICACIONES.md

**Entender cómo funciona**
→ ARQUITECTURA_API_COLAB_NOTIFICACIONES.md

**Código para copiar**
→ EJEMPLOS_API_COLAB_NOTIFICACIONES.md

**Guía paso a paso**
→ GUIA_API_COLAB_NOTIFICACIONES.md

**Resolver un problema**
→ TROUBLESHOOTING_API_COLAB_NOTIFICACIONES.md

**Verificación de completitud**
→ CHECKLIST_API_COLAB_NOTIFICACIONES.md

**Índice de todo**
→ INDICE_API_COLAB_NOTIFICACIONES.md

---

## ✨ Pro Tips

1. **Guardar tokens con metadata:**
   ```dart
   // Incluir info del dispositivo
   await notificationService.saveTokenToDatabase(userId);
   // Automáticamente incluye: platform, deviceName, timestamp
   ```

2. **Validar antes de enviar:**
   ```python
   tokens = notif_manager.obtener_tokens_usuario(user_id)
   if tokens:
       enviar_notificacion(...)
   else:
       print("⚠️ No hay tokens para este usuario")
   ```

3. **Usar timestamps UTC:**
   ```python
   from datetime import datetime, timezone
   timestamp = datetime.now(timezone.utc)
   ```

4. **Implementar retry automático:**
   ```python
   import time
   for intento in range(3):
       try:
           return enviar_notificacion(...)
       except:
           time.sleep(2 ** intento)
   ```

5. **Loguear todo:**
   ```python
   print(f"✅ Enviadas: {resultado['exitosas']}")
   print(f"❌ Fallidas: {resultado['fallidas']}")
   print(f"📊 Total dispositivos: {resultado['total_dispositivos']}")
   ```

---

## 🎯 Checklist de los 5 Primeros Pasos

- [ ] Descargar JSON de Service Account
- [ ] Copiar código setup en Colab
- [ ] Actualizar login en Flutter
- [ ] Abrir app y verificar token se guardó
- [ ] Enviar notificación de prueba desde Colab
- [ ] ✅ App recibe notificación

---

## 📚 Documentación Relacionada Existente

- `GUIA_NOTIFICACIONES.md` - Sistema de notificaciones (existente)
- `GUIA_API_ML.md` - Integración API ML (existente)
- `CHECKLIST_FIREBASE_EMAIL.md` - Firebase setup (existente)
- `IMPLEMENTACION_NOTIFICACIONES_PUSH.md` - Push notifications (existente)

---

**Sistema de Notificaciones API Colab → Flutter**  
**Quick Reference Card** 🚀  
**Última actualización:** Febrero 2025  
