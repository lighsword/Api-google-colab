# 📱 Guía Completa: Enviar Notificaciones al Usuario ID

## Problema Solucionado ✅

El error `The registration token is not a valid FCM registration token` ocurría porque:

1. **Problema original**: El endpoint esperaba un token FCM válido directamente
2. **Causa**: El token que se estaba enviando no era un token FCM válido registrado en la base de datos
3. **Solución**: Se ha creado un nuevo flujo que:
   - Acepta el `usuario_id` en lugar del token directo
   - Automáticamente obtiene TODOS los tokens registrados del usuario desde Firestore
   - Envía la notificación a todos los dispositivos del usuario

---

## 🎯 Flujo Correcto de 3 Pasos

### Paso 1: El cliente registra su dispositivo (una sola vez)

El cliente debe registrar su dispositivo FCM la primera vez que instala la app:

```bash
POST /api/v2/notifications/register-device
Content-Type: application/json

{
    "dispositivo_token": "e7sJ2xK9nP3lQ5mR8vT2xZ1cA4dE6fG9hI0jK3lM5n",
    "dispositivo_info": {
        "tipo": "android",
        "modelo": "Pixel 6",
        "os": "Android 13"
    }
}

HEADERS REQUERIDOS:
Authorization: Bearer {JWT_TOKEN}
```

**Respuesta:**
```json
{
    "status": "success",
    "mensaje": "Dispositivo registrado exitosamente",
    "usuario_id": "7niAh4AIH4dyNDiXnAb86jiZVEj2",
    "tokens_activos": 1
}
```

---

### Paso 2: Obtener el JWT Token (si es necesario)

Si necesitas autenticarte:

```bash
POST /api/v2/auth/token
Content-Type: application/json

{
    "usuario": "usuario@email.com",
    "contrasena": "password123"
}
```

**Respuesta:**
```json
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "usuario_id": "7niAh4AIH4dyNDiXnAb86jiZVEj2",
    "expira_en": 86400
}
```

---

### Paso 3: Enviar notificación al usuario_id ✅

**ENDPOINT RECOMENDADO (El nuevo):**

```bash
POST /api/Firebase/sendnotificacion-usuario
Content-Type: application/json

{
    "usuario_id": "7niAh4AIH4dyNDiXnAb86jiZVEj2",
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

**Respuesta Exitosa (200):**
```json
{
    "status": "success",
    "mensaje": "Notificación enviada a 2 dispositivo(s)",
    "timestamp": "2026-02-05T21:15:30.123456",
    "tokens_enviados": 2,
    "tokens_fallidos": 0,
    "usuario_id": "7niAh4AIH4dyNDiXnAb86jiZVEj2",
    "detalles": [
        {
            "token": "e7sJ2xK9nP3lQ5mR8vT2x...",
            "estado": "enviado",
            "message_id": "0:1675849384938204%3a1234567"
        }
    ]
}
```

---

## 📊 Comparación: Antes vs Después

### ❌ ANTES (Producía Error)

```bash
POST /api/Firebase/sendnotificacion
{
    "strToken": "invalid_token_or_unregistered",  # ← Error: Token no registrado
    "strTitle": "Gasto Detectado",
    "strMessage": "Detectamos un gasto de $100"
}

RESPUESTA: 500 Error - "The registration token is not a valid FCM registration token"
```

### ✅ DESPUÉS (Funciona Correctamente)

```bash
POST /api/Firebase/sendnotificacion-usuario
{
    "usuario_id": "7niAh4AIH4dyNDiXnAb86jiZVEj2",  # ← La API obtiene automáticamente los tokens
    "strTitle": "Gasto Detectado",
    "strMessage": "Detectamos un gasto de $100"
}

RESPUESTA: 200 Success - Notificación enviada a todos los dispositivos del usuario
```

---

## 🔄 Dos Formas de Enviar Notificaciones

### Opción A: Usando usuario_id (RECOMENDADO) ⭐

```bash
POST /api/Firebase/sendnotificacion-usuario
Content-Type: application/json

{
    "usuario_id": "ID_del_usuario",
    "strTitle": "Título",
    "strMessage": "Mensaje",
    "mapData": {
        "clave": "valor"
    }
}
```

**Ventajas:**
- ✅ No necesitas saber el token FCM
- ✅ Envía a TODOS los dispositivos del usuario automáticamente
- ✅ Si el usuario registra más dispositivos, se envían a todos
- ✅ Más seguro (no expones tokens individuales)

---

### Opción B: Usando token directo (Casos Especiales)

Si necesitas enviar a un token específico (avanzado):

```bash
POST /api/Firebase/sendnotificacion
Content-Type: application/json

{
    "strToken": "token_fcm_válido_y_registrado",
    "strTitle": "Título",
    "strMessage": "Mensaje",
    "mapData": {...}
}
```

**Cuándo usarlo:**
- Envíos a dispositivos específicos
- Tokens ya registrados en Firestore
- Casos muy específicos

---

## 🚨 Solucionar Errores Comunes

### Error 404: No hay dispositivos registrados

```json
{
    "status": "error",
    "mensaje": "No hay dispositivos registrados para el usuario...",
    "code": "NO_DEVICES_FOUND"
}
```

**Solución:**
1. El usuario debe instalar la app mobile
2. La app debe llamar a `/api/v2/notifications/register-device`
3. Luego intentar enviar notificación nuevamente

---

### Error 400: Faltan campos requeridos

```json
{
    "status": "error",
    "mensaje": "Faltan campos requeridos: strTitle, strMessage",
    "code": "MISSING_FIELDS"
}
```

**Solución:** Verifica que envíes:
- `usuario_id` ✓
- `strTitle` ✓
- `strMessage` ✓
- `mapData` (opcional)

---

### Error 500: Token inválido

```json
{
    "status": "error",
    "mensaje": "The registration token is not a valid FCM registration token",
    "code": "SEND_NOTIFICATION_ERROR"
}
```

**Soluciones:**
1. Usa `/api/Firebase/sendnotificacion-usuario` en lugar del endpoint antiguo
2. Verifica que el usuario_id sea correcto
3. Asegúrate que el dispositivo esté registrado primero

---

## 📚 Endpoints Relacionados

### Registrar Dispositivo
```bash
POST /api/v2/notifications/register-device
Authorization: Bearer {JWT_TOKEN}
```

### Obtener Historial de Notificaciones
```bash
GET /api/v2/notifications/history
Authorization: Bearer {JWT_TOKEN}
```

### Enviar a Usuario Autenticado (Requiere JWT)
```bash
POST /api/v2/me/send-notification
Authorization: Bearer {JWT_TOKEN}
```

### Enviar a Múltiples Usuarios
```bash
POST /api/v2/notifications/send-bulk
Authorization: Bearer {JWT_TOKEN}
```

---

## 🧪 Ejemplo Completo con cURL

### Paso 1: Obtener Token
```bash
curl -X POST http://localhost:5000/api/v2/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "user@example.com",
    "contrasena": "pass123"
  }'
```

### Paso 2: Registrar Dispositivo
```bash
curl -X POST http://localhost:5000/api/v2/notifications/register-device \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "dispositivo_token": "e7sJ2xK9nP3lQ5mR8vT2xZ1cA4dE6fG9hI0jK3lM5n",
    "dispositivo_info": {
      "tipo": "android",
      "modelo": "Pixel 6"
    }
  }'
```

### Paso 3: Enviar Notificación
```bash
curl -X POST http://localhost:5000/api/Firebase/sendnotificacion-usuario \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": "7niAh4AIH4dyNDiXnAb86jiZVEj2",
    "strTitle": "¡Gasto Detectado!",
    "strMessage": "Detectamos un gasto de $100 en Comida",
    "mapData": {
      "categoria": "Comida",
      "monto": "100",
      "tipo_alerta": "gasto_detectado",
      "id_transaccion": "txn_12345"
    }
  }'
```

---

## 📝 Notas Importantes

1. **Usuario ID**: Obtén el `usuario_id` del JWT token después de autenticarse
2. **Tokens de Dispositivo**: Se almacenan automáticamente en `usuarios/{usuario_id}/device_tokens`
3. **Limite de datos**: La sección `mapData` tiene límite de 4KB
4. **Títulos y mensajes**: Máximo 100 y 240 caracteres respectivamente
5. **Historial**: Las notificaciones se guardan en `usuarios/{usuario_id}/notificaciones_historial`

---

## ✅ Checklist de Configuración

- [ ] La app mobile tiene configurada Firebase Cloud Messaging
- [ ] El usuario instaló la app y aceptó permisos de notificación
- [ ] El dispositivo está registrado vía `/api/v2/notifications/register-device`
- [ ] Tienes el `usuario_id` del usuario
- [ ] Estás usando `/api/Firebase/sendnotificacion-usuario` (no el endpoint antiguo)
- [ ] Los campos `strTitle`, `strMessage`, `usuario_id` están presentes

¡Ahora las notificaciones deberían funcionar perfectamente! 🎉
