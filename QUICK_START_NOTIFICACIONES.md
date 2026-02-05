# ⚡ Quick Start: Notificaciones al Usuario ID

## El Problema Está Resuelto ✅

**Error anterior:** `The registration token is not a valid FCM registration token`

**Solución:** Usa el `usuario_id` en lugar del token directo

---

## 🚀 Uso Inmediato

### Opción 1: Endpoint Nuevo y Recomendado

```bash
curl -X POST https://api-google-colab.onrender.com/api/Firebase/sendnotificacion-usuario \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": "7niAh4AIH4dyNDiXnAb86jiZVEj2",
    "strTitle": "Gasto Detectado",
    "strMessage": "Detectamos un gasto de $100 en Comida",
    "mapData": {
      "categoria": "Comida",
      "monto": "100",
      "tipo_alerta": "gasto_detectado"
    }
  }'
```

**Respuesta:** 200 OK
```json
{
  "status": "success",
  "mensaje": "Notificación enviada a 2 dispositivo(s)",
  "tokens_enviados": 2
}
```

---

### Opción 2: Endpoint Mejorado (también funciona)

```bash
curl -X POST https://api-google-colab.onrender.com/api/Firebase/sendnotificacion \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": "7niAh4AIH4dyNDiXnAb86jiZVEj2",
    "strTitle": "Gasto Detectado",
    "strMessage": "Detectamos un gasto de $100"
  }'
```

---

## 📋 Pasos Previos (Una sola vez)

### 1. Obtener JWT Token

```bash
curl -X POST https://api-google-colab.onrender.com/api/v2/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "email@example.com",
    "contrasena": "password"
  }'
```

Guardar:
- `token`: JWT
- `usuario_id`: ID del usuario

### 2. Registrar Dispositivo (app mobile lo hace automáticamente)

```bash
curl -X POST https://api-google-colab.onrender.com/api/v2/notifications/register-device \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "dispositivo_token": "token_fcm_del_dispositivo"
  }'
```

---

## 🎯 Flujo Completo

```
┌─────────────────────────────────────────┐
│ 1. Usuario se autentica                 │
│    POST /api/v2/auth/token              │
│    ↓ Obtiene: usuario_id, JWT token     │
├─────────────────────────────────────────┤
│ 2. App registra dispositivo (automático)│
│    POST /api/v2/notifications/...       │
│    ↓ Se guarda en: usuarios/{id}/...    │
├─────────────────────────────────────────┤
│ 3. Backend envía notificación           │
│    POST /api/Firebase/sendnotificacion-usuario
│    Input: usuario_id                    │
│    ↓ Busca automáticamente los tokens   │
│    ↓ Envía a TODOS los dispositivos     │
└─────────────────────────────────────────┘
```

---

## ✨ Parámetros

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `usuario_id` | string | ✅ | ID del usuario en Firebase |
| `strTitle` | string | ✅ | Título (máx 100 chars) |
| `strMessage` | string | ✅ | Mensaje (máx 240 chars) |
| `mapData` | object | ❌ | Datos adicionales (máx 4KB) |

---

## 📊 Respuestas

### ✅ Éxito (200)
```json
{
  "status": "success",
  "mensaje": "Notificación enviada a X dispositivo(s)",
  "tokens_enviados": 2,
  "tokens_fallidos": 0
}
```

### ❌ Error: Sin dispositivos (404)
```json
{
  "status": "error",
  "mensaje": "No hay dispositivos registrados...",
  "code": "NO_DEVICES_FOUND"
}
→ Solución: Registra un dispositivo primero
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

## 🔥 Diferencia Clave

### ❌ ANTES (Error)
```bash
POST /api/Firebase/sendnotificacion
{
  "strToken": "invalid_or_unregistered_token"  # ← Aquí estaba el problema
}
→ 500 Error: Invalid FCM token
```

### ✅ DESPUÉS (Funciona)
```bash
POST /api/Firebase/sendnotificacion-usuario
{
  "usuario_id": "7niAh4AIH4dyNDiXnAb86jiZVEj2"  # ← La API busca automáticamente los tokens
}
→ 200 Success: Notificación enviada
```

---

## 💡 Claves del Éxito

1. **Usa `usuario_id`** en lugar de token directo
2. **El usuario debe registrar** su dispositivo primero
3. **La app busca automáticamente** los tokens en Firestore
4. **Envía a todos** los dispositivos del usuario

---

## 📚 Documentación Completa

- [GUIA_NOTIFICACIONES_USUARIO_ID.md](GUIA_NOTIFICACIONES_USUARIO_ID.md) - Guía completa
- [RESUMEN_FIX_NOTIFICACIONES_USUARIO_ID.md](RESUMEN_FIX_NOTIFICACIONES_USUARIO_ID.md) - Resumen del cambio
- [test_notificaciones_usuario_id.ps1](test_notificaciones_usuario_id.ps1) - Script PowerShell
- [test_notificaciones_usuario_id.sh](test_notificaciones_usuario_id.sh) - Script Bash

---

## 🧪 Probar Ahora

**Windows PowerShell:**
```powershell
.\test_notificaciones_usuario_id.ps1
```

**Linux/Mac Bash:**
```bash
bash test_notificaciones_usuario_id.sh
```

---

¡Ya está todo listo! 🎉 Las notificaciones funcionan correctamente ahora.
