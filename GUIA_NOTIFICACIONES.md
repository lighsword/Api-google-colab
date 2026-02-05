# 🔔 Guía de Notificaciones Push - API Financiera

## Endpoints Disponibles

### 1. **Enviar Notificación a Dispositivo Específico** (Sin autenticación)
```
POST /api/Firebase/sendnotificacion
```

**Cuándo usar:** 
- Alertas del servidor
- Notificaciones del sistema
- Alertas autogeneradas por reglas de negocio

**Body:**
```json
{
  "strToken": "token_del_dispositivo_fcm",
  "strTitle": "Gasto Detectado",
  "strMessage": "Detectamos un gasto de $100 en Comida",
  "mapData": {
    "categoria": "Comida",
    "monto": "100",
    "tipo_alerta": "gasto_detectado",
    "id_transaccion": "txn_12345"
  }
}
```

**Respuesta exitosa (200):**
```json
{
  "status": "success",
  "mensaje": "Notificación enviada exitosamente",
  "message_id": "0:1675849384938204%3a1234567",
  "timestamp": "2026-02-05T18:15:30.123456"
}
```

---

### 2. **Enviar Notificación a Todos los Dispositivos del Usuario** (Con autenticación)
```
POST /api/v2/users/{usuario_id}/send-notification
Headers:
  Authorization: Bearer {token_jwt}
  Content-Type: application/json
```

**Cuándo usar:**
- Notificaciones personalizadas
- Alertas para un usuario específico
- Recordatorios de metas

**Body:**
```json
{
  "titulo": "¡Meta Alcanzada!",
  "cuerpo": "Felicidades, ahorraste $1,000 en alimentación",
  "datos_extra": {
    "tipo": "meta_alcanzada",
    "meta_id": "meta_123",
    "monto": "1000"
  }
}
```

**Respuesta exitosa (200):**
```json
{
  "status": "success",
  "usuario_id": "user123",
  "mensajes_enviados": 2,
  "mensaje": "Notificación enviada a 2 dispositivos"
}
```

---

## 🚀 Ejemplos de Uso desde la APP

### **Ejemplo 1: Alerta de Gasto Detectado**
```javascript
// Cuando se detecta un gasto anómalo
async function alertarGastoAnomalico(token_dispositivo, monto, categoria) {
  const response = await fetch('https://api-google-colab.onrender.com/api/Firebase/sendnotificacion', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      strToken: token_dispositivo,
      strTitle: '⚠️ Gasto Anómalo Detectado',
      strMessage: `Gasto de $${monto} en ${categoria} (muy alto)`,
      mapData: {
        tipo_alerta: 'gasto_anomalico',
        monto: monto.toString(),
        categoria: categoria,
        accion: 'revisar'
      }
    })
  });
  return await response.json();
}
```

### **Ejemplo 2: Recordatorio de Presupuesto**
```javascript
// Cuando el usuario está a punto de exceder presupuesto
async function recordatorioPresupuesto(usuario_id, token_jwt, porcentaje_usado) {
  const response = await fetch(`https://api-google-colab.onrender.com/api/v2/users/${usuario_id}/send-notification`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token_jwt}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      titulo: '💰 Presupuesto Casi Agotado',
      cuerpo: `Ya gastaste el ${porcentaje_usado}% de tu presupuesto de este mes`,
      datos_extra: {
        tipo: 'recordatorio_presupuesto',
        porcentaje: porcentaje_usado.toString(),
        accion: 'ver_presupuesto'
      }
    })
  });
  return await response.json();
}
```

### **Ejemplo 3: Meta Alcanzada**
```javascript
// Cuando el usuario alcanza una meta de ahorro
async function notificarMetaAlcanzada(usuario_id, token_jwt, nombre_meta, monto) {
  const response = await fetch(`https://api-google-colab.onrender.com/api/v2/users/${usuario_id}/send-notification`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token_jwt}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      titulo: '🎉 ¡Felicidades!',
      cuerpo: `Alcanzaste tu meta de ${nombre_meta}: $${monto}`,
      datos_extra: {
        tipo: 'meta_alcanzada',
        meta_nombre: nombre_meta,
        monto_alcanzado: monto.toString(),
        accion: 'celebrar'
      }
    })
  });
  return await response.json();
}
```

### **Ejemplo 4: Consejo Personalizado**
```javascript
// Sugerencias basadas en análisis
async function enviarConsejoPersonalizado(usuario_id, token_jwt, consejo) {
  const response = await fetch(`https://api-google-colab.onrender.com/api/v2/users/${usuario_id}/send-notification`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token_jwt}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      titulo: '💡 Consejo de Ahorro',
      cuerpo: consejo,
      datos_extra: {
        tipo: 'consejo',
        accion: 'leer_consejo'
      }
    })
  });
  return await response.json();
}
```

---

## 🎯 Casos de Uso Automatizados

### **Flujo 1: Alertas por Anomalía**
```
1. Usuario realiza gasto
2. API analiza con predict-category
3. Si es anomalía → Enviar alerta
4. Usuario recibe notificación
5. Usuario puede revisar o ignorar
```

### **Flujo 2: Recordatorios de Presupuesto**
```
1. Cada día a las 8 PM
2. Calcular % de presupuesto usado
3. Si > 80% → Alerta
4. Si > 100% → Alerta crítica
5. Enviar notificación personalizada
```

### **Flujo 3: Logros y Motivación**
```
1. Usuario alcanza milestone (ej: $1,000 ahorrado)
2. Sistema detecta el logro
3. Enviar notificación celebratoria
4. Sumar puntos de gamificación
5. Desbloquear logro en app
```

---

## 📊 Flujo de Datos

```
APP (Frontend)
    ↓
Usuario realiza acción
    ↓
API (/api/v2/users/{id}/predict-category, etc)
    ↓
Genera predicción/alerta
    ↓
POST a /api/Firebase/sendnotificacion
    ↓
Firebase Cloud Messaging (FCM)
    ↓
Dispositivo del usuario
    ↓
Notificación Push (Android/iOS/Web)
```

---

## ⚙️ Configuración Necesaria en la APP

### **Android (Flutter/React Native)**

```dart
// Configurar FCM
FirebaseMessaging messaging = FirebaseMessaging.instance;

// Obtener token
String? token = await messaging.getToken();
// Enviar este token al servidor para guardarlo

// Escuchar notificaciones
FirebaseMessaging.onMessage.listen((RemoteMessage message) {
  print('Notificación recibida: ${message.notification?.title}');
  // Mostrar notificación en el app
});
```

### **iOS (Flutter/React Native)**

```dart
// Solicitar permisos
NotificationSettings settings = await messaging.requestPermission(
  alert: true,
  announcement: false,
  badge: true,
  carefullyConsiderations: false,
  criticalAlert: false,
  provisional: false,
  sound: true,
);
```

### **Web (JavaScript)**

```javascript
// Registrar service worker
navigator.serviceWorker.register('/firebase-messaging-sw.js');

// Obtener token
const messaging = firebase.messaging();
const token = await messaging.getToken({
  vapidKey: 'YOUR_VAPID_KEY'
});

// Escuchar notificaciones en foreground
messaging.onMessage((payload) => {
  console.log('Notificación:', payload);
});
```

---

## 🔐 Seguridad

- ✅ Endpoint `/api/Firebase/sendnotificacion` **NO requiere autenticación** (solo el token FCM válido)
- ✅ Endpoint `/api/v2/users/{id}/send-notification` **REQUIERE JWT** (previene spam)
- ✅ Todos los tokens FCM son únicos por dispositivo
- ✅ Las notificaciones se envían sobre HTTPS
- ✅ Firebase Cloud Messaging maneja el cifrado

---

## 🛠️ Troubleshooting

| Error | Causa | Solución |
|-------|-------|----------|
| `Firebase no disponible` | Firebase no está configurado | Verificar `credentials.json` |
| `Faltan campos requeridos` | Body incompleto | Verificar strToken, strTitle, strMessage |
| `Token requerido o inválido` | No hay JWT o está expirado | Generar nuevo token en `/api/v2/auth/token` |
| `No hay dispositivos registrados` | Usuario sin dispositivos | Solicitar permiso de notificaciones en app |
| `Notificación no llega` | Token FCM inválido/expirado | Refrescar token en app |

---

## 📚 Documentación Adicional

- [Firebase Cloud Messaging Docs](https://firebase.google.com/docs/cloud-messaging)
- [OpenAPI Swagger UI](https://api-google-colab.onrender.com/swagger-ui.html)
- [Ejemplos de Código](./EJEMPLOS_CODIGO_API.md)
