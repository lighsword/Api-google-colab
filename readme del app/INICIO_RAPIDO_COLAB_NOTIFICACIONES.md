# ⚡ Guía Rápida: 5 Minutos para Empezar

## 🎯 Objetivo
Hacer que tu API de Google Colab envíe notificaciones a tu app Flutter en 5 pasos simples.

---

## Paso 1: Descargar Credenciales de Firebase (1 min)

```
1. Ve a: https://console.firebase.google.com
2. Selecciona proyecto: gestor-financiero-28ac2
3. Ve a: ⚙️ Configuración → Cuentas de Servicio
4. Haz clic: "Generar nueva clave privada"
5. Se descarga: gestor-financiero-28ac2-xxxxx.json
```

**IMPORTANTE**: Este archivo es como una contraseña. ¡No lo compartas!

---

## Paso 2: Preparar Firebase (1 min)

En Firebase Console, verifica que exista esta estructura:

```
users/
  └── userId123/
      ├── email
      ├── displayName  
      └── fcmTokens/ ← IMPORTANTE: Esta colección
          └── {token}/
              ├── token
              ├── deviceName
              ├── platform
              └── isActive: true
```

Si no existe, Firestore la creará automáticamente cuando guarde el primer token.

---

## Paso 3: Actualizar tu App Flutter (1 min)

En tu pantalla de login, después de autenticar, añade:

```dart
// Después del login exitoso
final notificationService = NotificationService();
await notificationService.saveTokenToDatabase(authProvider.user!.uid);
```

**Eso es todo en Flutter.** La app ya tiene todo configurado en `notification_service.dart`.

---

## Paso 4: Copiar Código en Google Colab (1 min)

En un nuevo Notebook de Colab:

```python
# Celda 1: Instalar dependencias
!pip install firebase-admin

# Celda 2: Subir credenciales
from google.colab import files
uploaded = files.upload()
credential_file = list(uploaded.keys())[0]

# Celda 3: Inicializar Firebase
import firebase_admin
from firebase_admin import credentials, messaging, firestore

cred = credentials.Certificate(credential_file)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Celda 4: Función simple para enviar
def enviar_notificacion(user_id, titulo, cuerpo):
    """Envía una notificación simple a un usuario"""
    try:
        # Obtener tokens del usuario
        tokens_ref = db.collection('users').document(user_id).collection('fcmTokens')
        docs = tokens_ref.where('isActive', '==', True).stream()
        
        tokens = [doc.to_dict()['token'] for doc in docs]
        
        if not tokens:
            print(f"❌ No hay dispositivos para {user_id}")
            return False
        
        # Enviar notificación
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=titulo,
                body=cuerpo
            ),
            tokens=tokens
        )
        
        response = messaging.send_multicast(message)
        print(f"✅ Enviadas: {response.success_count}")
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
```

---

## Paso 5: Enviar tu Primera Notificación (1 min)

En una nueva celda de Colab:

```python
# Cambiar estos valores:
user_id = "UID_DEL_USUARIO"  # Obtén esto de Firebase Console → Authentication
titulo = "Hola desde Colab! 👋"
cuerpo = "¡Si ves esto, todo funciona!"

# ¡Enviar!
enviar_notificacion(user_id, titulo, cuerpo)
```

**Abre tu app Flutter y verás la notificación llegar instantáneamente** 🎉

---

## 📊 Así de Simple es la Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  Google Colab                                       │
│  └─ enviar_notificacion(user_id, titulo, cuerpo)  │
│                    ↓                                │
│  Firebase Cloud Messaging                          │
│  (envía la notificación)                           │
│                    ↓                                │
│  App Flutter                                        │
│  └─ La recibe y la muestra al usuario ✅           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔄 Ahora: Casos de Uso del ML

Una vez que funciona lo básico, puedes:

### 1. Notificación de Predicción
```python
def notificar_prediccion(user_id, gasto_predicho, categoria, confianza):
    titulo = f"📊 Predicción: {categoria}"
    cuerpo = f"Se predice ${gasto_predicho:.2f} (Confianza: {confianza:.0%})"
    enviar_notificacion(user_id, titulo, cuerpo)

# Usar:
notificar_prediccion('usuario_123', 150.50, 'Alimentación', 0.85)
```

### 2. Notificación de Anomalía
```python
def notificar_anomalia(user_id, monto, categoria):
    titulo = "⚠️ Gasto Inusual"
    cuerpo = f"${monto:.2f} en {categoria} - Exceede el promedio"
    enviar_notificacion(user_id, titulo, cuerpo)

# Usar:
notificar_anomalia('usuario_123', 500.00, 'Entretenimiento')
```

### 3. Notificación de Recomendación
```python
def notificar_recomendacion(user_id, accion, ahorro):
    titulo = "💡 Recomendación"
    cuerpo = f"{accion} - Ahorro potencial: ${ahorro:.2f}"
    enviar_notificacion(user_id, titulo, cuerpo)

# Usar:
notificar_recomendacion('usuario_123', 'Reducir Entretenimiento', 300.00)
```

---

## 🚨 Problemas Comunes

| Problema | Solución |
|----------|----------|
| "Token no encontrado" | Asegúrate que el usuario inició sesión en la app |
| "Error de autenticación" | Verifica que el JSON es válido |
| "Notificación no llega" | Revisa que isActive: true en Firestore |
| "ModuleNotFoundError" | Ejecuta `!pip install firebase-admin` primero |

---

## 📖 Documentación Completa

Para más detalles, consulta:
- [GUIA_API_COLAB_NOTIFICACIONES.md](GUIA_API_COLAB_NOTIFICACIONES.md) - Guía completa
- [EJEMPLOS_API_COLAB_NOTIFICACIONES.md](EJEMPLOS_API_COLAB_NOTIFICACIONES.md) - Más ejemplos
- [CHECKLIST_API_COLAB_NOTIFICACIONES.md](CHECKLIST_API_COLAB_NOTIFICACIONES.md) - Implementación paso a paso

---

## ✅ Checklist Rápido

- [ ] Descargué el JSON de Service Account
- [ ] Actualicé el login en Flutter
- [ ] Abrí la app y verifiqué que el token se guardó en Firestore
- [ ] Copié el código en Colab
- [ ] Envié una notificación de prueba
- [ ] La app la recibió ✅

**¡Listo! Ahora puedes enviar notificaciones desde Colab cuando lo necesites.**

---

## 🎓 Próximo Paso

Integra tu modelo ML:

1. Tu modelo hace predicción/detección
2. Llama a `notificar_prediccion()` o similar
3. La app muestra la notificación al usuario
4. El usuario toma acción

**¡Así de simple es tener un ML backend enviando notificaciones en tiempo real!**
