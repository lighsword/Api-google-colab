# 🚀 Resumen: Solución de Notificaciones al Usuario ID

**Fecha**: 05 de Febrero de 2026  
**Estado**: ✅ COMPLETADO

---

## El Problema

El endpoint `POST /api/Firebase/sendnotificacion` producía error:

```
500 Error: The registration token is not a valid FCM registration token
```

**Causa raíz**: El endpoint esperaba un token FCM válido, pero los usuarios no sabían qué token enviar.

---

## La Solución Implementada

Se han creado **2 nuevos enfoques**:

### ✅ 1. Endpoint Recomendado: `/api/Firebase/sendnotificacion-usuario`

**Usa el `usuario_id` en lugar del token directo**

```bash
POST /api/Firebase/sendnotificacion-usuario
Content-Type: application/json

{
    "usuario_id": "7niAh4AIH4dyNDiXnAb86jiZVEj2",
    "strTitle": "Gasto Detectado",
    "strMessage": "Detectamos un gasto de $100",
    "mapData": {
        "categoria": "Comida",
        "monto": "100"
    }
}
```

**Ventajas:**
- ✅ No necesitas saber el token FCM
- ✅ Busca automáticamente TODOS los tokens del usuario
- ✅ Envía a múltiples dispositivos del mismo usuario
- ✅ Más seguro y escalable

---

### ✅ 2. Endpoint Mejorado: `/api/Firebase/sendnotificacion`

**Se mejoró el endpoint existente** para soportar ambas opciones:

```bash
# Opción A: Con usuario_id (NUEVO)
{
    "usuario_id": "7niAh4AIH4dyNDiXnAb86jiZVEj2",
    "strTitle": "Título",
    "strMessage": "Mensaje"
}

# Opción B: Con token directo (antiguo)
{
    "strToken": "token_fcm_válido",
    "strTitle": "Título",
    "strMessage": "Mensaje"
}
```

---

## Flujo Correcto (3 Pasos)

### 1️⃣ Cliente registra dispositivo (primera vez)

```bash
POST /api/v2/notifications/register-device
Authorization: Bearer {JWT_TOKEN}

{
    "dispositivo_token": "fcm_token_del_dispositivo"
}
```

### 2️⃣ Sistema backend obtiene usuario_id

Después de autenticar, tienes el `usuario_id` del JWT token:

```bash
POST /api/v2/auth/token
{
    "usuario": "email@example.com",
    "contrasena": "password"
}

RESPUESTA: {
    "usuario_id": "7niAh4AIH4dyNDiXnAb86jiZVEj2",
    ...
}
```

### 3️⃣ Enviar notificación al usuario_id

```bash
POST /api/Firebase/sendnotificacion-usuario
{
    "usuario_id": "7niAh4AIH4dyNDiXnAb86jiZVEj2",
    "strTitle": "Notificación",
    "strMessage": "Tu mensaje aquí"
}
```

**La API automáticamente:**
1. Busca en Firestore: `usuarios/{usuario_id}/device_tokens`
2. Obtiene todos los tokens activos
3. Envía la notificación a TODOS los dispositivos

---

## Archivos Modificados

### 1. [API_MEJORADA.py](API_MEJORADA.py)

**Cambios:**

- ✅ Mejorado endpoint `/api/Firebase/sendnotificacion` (línea 2184)
  - Ahora acepta `usuario_id` O `strToken`
  - Busca automáticamente tokens en Firestore
  - Mejor manejo de errores

- ✅ Nuevo endpoint `/api/Firebase/sendnotificacion-usuario` (línea 2403)
  - Específicamente diseñado para usuario_id
  - Documentación clara
  - Respuestas detalladas con detalles por dispositivo

---

## Archivos de Documentación Nuevos

### 2. [GUIA_NOTIFICACIONES_USUARIO_ID.md](GUIA_NOTIFICACIONES_USUARIO_ID.md)

Guía completa con:
- 🎯 Flujo correcto de 3 pasos
- 📊 Comparación Antes vs Después
- 🔄 Dos opciones de envío
- 🚨 Solución de errores comunes
- 📚 Todos los endpoints relacionados
- 🧪 Ejemplo completo con cURL

### 3. [test_notificaciones_usuario_id.sh](test_notificaciones_usuario_id.sh)

Script bash para probar todos los endpoints en Linux/Mac

### 4. [test_notificaciones_usuario_id.ps1](test_notificaciones_usuario_id.ps1)

Script PowerShell para probar todos los endpoints en Windows

---

## Respuestas Esperadas

### ✅ Exitosa (200)

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

### ❌ Error: Sin dispositivos (404)

```json
{
    "status": "error",
    "mensaje": "No hay dispositivos registrados para el usuario...",
    "code": "NO_DEVICES_FOUND",
    "instruccion": "Usa POST /api/v2/notifications/register-device"
}
```

### ❌ Error: Campos faltantes (400)

```json
{
    "status": "error",
    "mensaje": "Faltan campos requeridos: strTitle, strMessage",
    "code": "MISSING_FIELDS"
}
```

---

## Cómo Usar Ahora

### Para frontend/mobile app:

```javascript
// 1. Obtener token JWT
const tokenResponse = await fetch('/api/v2/auth/token', {
    method: 'POST',
    body: JSON.stringify({
        usuario: 'email@example.com',
        contrasena: 'password'
    })
});
const { usuario_id, token } = await tokenResponse.json();

// 2. Registrar dispositivo (una sola vez)
await fetch('/api/v2/notifications/register-device', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: JSON.stringify({
        dispositivo_token: 'fcm_token'
    })
});

// 3. Enviar notificación
await fetch('/api/Firebase/sendnotificacion-usuario', {
    method: 'POST',
    body: JSON.stringify({
        usuario_id: usuario_id,
        strTitle: "Gasto Detectado",
        strMessage: "Nuevo gasto registrado",
        mapData: { categoria: "Comida" }
    })
});
```

### Para backend/scripts:

```python
# Usa la función existente
from API_MEJORADA import send_push_notification

resultado = send_push_notification(
    usuario_id='7niAh4AIH4dyNDiXnAb86jiZVEj2',
    titulo='Gasto Detectado',
    cuerpo='Se registró un nuevo gasto',
    datos_extra={
        'categoria': 'Comida',
        'monto': '100'
    }
)

print(resultado)
```

---

## Checklist de Verificación

- ✅ Nuevo endpoint `/api/Firebase/sendnotificacion-usuario` creado
- ✅ Endpoint anterior `/api/Firebase/sendnotificacion` mejorado
- ✅ Soporta buscar tokens automáticamente en Firestore
- ✅ Mejor manejo de errores con mensajes descriptivos
- ✅ Documentación completa en GUIA_NOTIFICACIONES_USUARIO_ID.md
- ✅ Scripts de prueba en bash y PowerShell
- ✅ Respuestas detalladas con información por dispositivo
- ✅ Historial de notificaciones se guarda automáticamente

---

## Próximos Pasos Recomendados

1. **Probar localmente** con `test_notificaciones_usuario_id.ps1` o `.sh`
2. **Verificar** que Firestore tiene la colección `device_tokens` por usuario
3. **Actualizar** la app mobile para llamar a `/api/v2/notifications/register-device`
4. **Usar** `/api/Firebase/sendnotificacion-usuario` en lugar del endpoint antiguo
5. **Monitorear** el historial en `usuarios/{usuario_id}/notificaciones_historial`

---

## Tabla de Endpoints

| Endpoint | Método | Requiere Auth | Función |
|----------|--------|---------------|---------|
| `/api/Firebase/sendnotificacion-usuario` | POST | No | ✅ Enviar a usuario_id (RECOMENDADO) |
| `/api/Firebase/sendnotificacion` | POST | No | Enviar a token directo |
| `/api/v2/notifications/register-device` | POST | Sí | Registrar dispositivo |
| `/api/v2/me/send-notification` | POST | Sí | Enviar al usuario autenticado |
| `/api/v2/notifications/history` | GET | Sí | Ver historial |

---

**¡Problema Resuelto! 🎉**

Las notificaciones ahora se pueden enviar fácilmente al `usuario_id` sin necesidad de conocer los tokens FCM individuales.
