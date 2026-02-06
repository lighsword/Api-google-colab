# 🔔 Notificaciones Push - Solución al Usuario ID

## ❌ El Problema

```
POST /api/Firebase/sendnotificacion
{
  "strToken": "e7sJ2xK9nP3lQ5mR8vT2xZ1cA4dE6fG9hI0jK3lM5n"
  "strTitle": "Gasto Detectado",
  "strMessage": "Se registró un gasto"
}

RESPUESTA: ❌ 500 Error
{
  "status": "error",
  "mensaje": "The registration token is not a valid FCM registration token",
  "code": "SEND_NOTIFICATION_ERROR"
}
```

**¿Por qué falla?** 
- ❌ El token es inválido o no está registrado
- ❌ El usuario no sabe qué token enviar
- ❌ No hay forma de obtener el token correcto

---

## ✅ La Solución

### Nuevo Enfoque: Usar `usuario_id`

```bash
POST /api/Firebase/sendnotificacion-usuario
Content-Type: application/json

{
  "usuario_id": "7niAh4AIH4dyNDiXnAb86jiZVEj2",
  "strTitle": "Gasto Detectado",
  "strMessage": "Se registró un gasto de $100",
  "mapData": {
    "categoria": "Comida",
    "monto": "100"
  }
}
```

**RESPUESTA:**
```json
{
  "status": "success",
  "mensaje": "Notificación enviada a 2 dispositivo(s)",
  "timestamp": "2026-02-05T21:15:30.123456",
  "tokens_enviados": 2,
  "tokens_fallidos": 0,
  "usuario_id": "7niAh4AIH4dyNDiXnAb86jiZVEj2"
}
```

---

## 🎯 ¿Qué Hace?

```
Tu código
   ↓
   ├─ Envías: usuario_id
   ├─ API busca en Firestore
   │  └─ usuarios/{usuario_id}/device_tokens
   │     ├─ Token del teléfono
   │     ├─ Token de tablet
   │     └─ Token de web
   ├─ API envía a TODOS
   └─ ✅ Retorna cuántos se enviaron
```

---

## 🚀 Uso Rápido (3 pasos)

### 1️⃣ Obtener usuario_id
```bash
curl -X POST https://api-google-colab.onrender.com/api/v2/auth/token \
  -d '{"usuario":"email@example.com","contrasena":"pass"}'

# Respuesta: { "usuario_id": "7niAh4AIH4dyNDiXnAb86jiZVEj2", ... }
```

### 2️⃣ Registrar dispositivo (primera vez)
```bash
curl -X POST https://api-google-colab.onrender.com/api/v2/notifications/register-device \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -d '{"dispositivo_token":"fcm_token_device"}'
```

### 3️⃣ Enviar notificación
```bash
curl -X POST https://api-google-colab.onrender.com/api/Firebase/sendnotificacion-usuario \
  -d '{
    "usuario_id": "7niAh4AIH4dyNDiXnAb86jiZVEj2",
    "strTitle": "Título",
    "strMessage": "Mensaje"
  }'

# ✅ Listo! Se envió a todos los dispositivos del usuario
```

---

## 📊 Antes vs Después

```
ANTES (❌ NO FUNCIONA)                  DESPUÉS (✅ FUNCIONA)
═════════════════════════════════════════════════════════════════
POST /api/Firebase/sendnotificacion     POST /api/Firebase/sendnotificacion-usuario
{                                       {
  "strToken": "???"  ← ¿Cuál token?       "usuario_id": "7niAh4AIH4dy..."
  "strTitle": "..."                       "strTitle": "..."
}                                       }
↓                                       ↓
Error: Token inválido                   Busca automáticamente
500 FAIL                                Envía a todos los dispositivos
                                        200 SUCCESS
```

---

## 🎁 ¿Qué Cambió?

### Endpoints Nuevos/Mejorados

| Endpoint | Nuevo | Cambio |
|----------|-------|--------|
| `/api/Firebase/sendnotificacion-usuario` | ✨ NUEVO | Envía por usuario_id (RECOMENDADO) |
| `/api/Firebase/sendnotificacion` | 🔧 MEJORADO | Ahora soporta usuario_id también |

### Características

- ✅ Busca automáticamente tokens en Firestore
- ✅ Envía a múltiples dispositivos
- ✅ Mejor manejo de errores
- ✅ Respuestas detalladas
- ✅ Historial automático

---

## 📚 Documentación Rápida

| Necesitas | Archivo | Tiempo |
|-----------|---------|--------|
| **Empezar AHORA** | [QUICK_START_NOTIFICACIONES.md](QUICK_START_NOTIFICACIONES.md) | 2 min ⚡ |
| **Entender TODO** | [GUIA_NOTIFICACIONES_USUARIO_ID.md](GUIA_NOTIFICACIONES_USUARIO_ID.md) | 10 min 📖 |
| **Resumen ejecutivo** | [RESUMEN_FIX_NOTIFICACIONES_USUARIO_ID.md](RESUMEN_FIX_NOTIFICACIONES_USUARIO_ID.md) | 5 min 📊 |
| **Cambios técnicos** | [CAMBIOS_IMPLEMENTADOS_NOTIFICACIONES.md](CAMBIOS_IMPLEMENTADOS_NOTIFICACIONES.md) | 7 min 🔧 |
| **Probar todo** | [test_notificaciones_usuario_id.ps1](test_notificaciones_usuario_id.ps1) | 5 min ✅ |

---

## 💻 Ejemplo en Código

### JavaScript/TypeScript

```javascript
// Enviar notificación
const response = await fetch(
  'https://api-google-colab.onrender.com/api/Firebase/sendnotificacion-usuario',
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      usuario_id: 'usuario123',
      strTitle: 'Nuevo gasto',
      strMessage: 'Se registró un gasto de $100',
      mapData: { categoria: 'Comida', monto: '100' }
    })
  }
);

const result = await response.json();
console.log(`✅ Enviado a ${result.tokens_enviados} dispositivos`);
```

### Python

```python
# Enviar notificación
import requests

response = requests.post(
  'https://api-google-colab.onrender.com/api/Firebase/sendnotificacion-usuario',
  json={
    'usuario_id': 'usuario123',
    'strTitle': 'Nuevo gasto',
    'strMessage': 'Se registró un gasto de $100',
    'mapData': {'categoria': 'Comida', 'monto': '100'}
  }
)

print(f"✅ Enviado a {response.json()['tokens_enviados']} dispositivos")
```

### cURL

```bash
curl -X POST 'https://api-google-colab.onrender.com/api/Firebase/sendnotificacion-usuario' \
  -H 'Content-Type: application/json' \
  -d '{
    "usuario_id": "usuario123",
    "strTitle": "Nuevo gasto",
    "strMessage": "Se registró un gasto de $100",
    "mapData": {"categoria": "Comida", "monto": "100"}
  }'
```

---

## ✨ Ventajas

| Antes | Después |
|-------|---------|
| ❌ Un solo dispositivo | ✅ Múltiples dispositivos |
| ❌ Token obligatorio | ✅ usuario_id automático |
| ❌ Token puede expirar | ✅ Se busca automáticamente |
| ❌ Error 500 | ✅ Error descriptivo |
| ❌ Sin historial | ✅ Historial guardado |
| ❌ Difícil de debuggear | ✅ Fácil de trackear |

---

## 🧪 Probar Ahora

### Windows PowerShell
```powershell
.\test_notificaciones_usuario_id.ps1
```

### Linux/Mac Bash
```bash
bash test_notificaciones_usuario_id.sh
```

---

## 📞 ¿Errores?

### "No hay dispositivos registrados"
**Solución**: Primero registra un dispositivo:
```bash
curl -X POST /api/v2/notifications/register-device \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{"dispositivo_token":"..."}'
```

### "Faltan campos requeridos"
**Solución**: Asegúrate de enviar:
- `usuario_id` ✓
- `strTitle` ✓
- `strMessage` ✓

### "The registration token is invalid"
**Solución**: Usa `/api/Firebase/sendnotificacion-usuario` con `usuario_id`

---

## 🎯 Resumen

| Aspecto | Detalle |
|--------|---------|
| **Problema** | Token FCM inválido o desconocido |
| **Solución** | Usar usuario_id, API busca automáticamente |
| **Endpoint** | `/api/Firebase/sendnotificacion-usuario` |
| **Entrada** | usuario_id, strTitle, strMessage |
| **Salida** | Notificación enviada a todos los dispositivos |
| **Tiempo** | 5 minutos para implementar |

---

## 📚 Índice Completo

👉 **[Ver documentación completa](INDICE_NOTIFICACIONES.md)**

---

## ✅ Estado

- ✅ Endpoint nuevo creado
- ✅ Endpoint anterior mejorado
- ✅ Documentación completa
- ✅ Scripts de prueba incluidos
- ✅ Listo para producción

**🎉 ¡Problema resuelto!**
