# 🔔 Ejemplos cURL - Notificaciones Push

## 1. Enviar Notificación a Dispositivo Específico (Sin autenticación)

### Ejemplo Básico
```bash
curl -X POST https://api-google-colab.onrender.com/api/Firebase/sendnotificacion \
  -H "Content-Type: application/json" \
  -d '{
    "strToken": "e7sJ2xK9nP3lQ5mR8vT2xZ1cA4dE6fG9hI0jK3lM5n",
    "strTitle": "Gasto Detectado",
    "strMessage": "Detectamos un gasto de $100 en Comida"
  }'
```

### Ejemplo con Datos Adicionales
```bash
curl -X POST https://api-google-colab.onrender.com/api/Firebase/sendnotificacion \
  -H "Content-Type: application/json" \
  -d '{
    "strToken": "e7sJ2xK9nP3lQ5mR8vT2xZ1cA4dE6fG9hI0jK3lM5n",
    "strTitle": "⚠️ Gasto Anómalo",
    "strMessage": "Gasto de $500 en Transporte (muy alto para ti)",
    "mapData": {
      "categoria": "Transporte",
      "monto": "500",
      "tipo_alerta": "gasto_anomalico",
      "id_transaccion": "txn_abc123",
      "accion": "revisar"
    }
  }'
```

### Ejemplo - Alerta de Sobregasto
```bash
curl -X POST https://api-google-colab.onrender.com/api/Firebase/sendnotificacion \
  -H "Content-Type: application/json" \
  -d '{
    "strToken": "token_dispositivo_aqui",
    "strTitle": "💰 Presupuesto Excedido",
    "strMessage": "Ya gastaste 120% de tu presupuesto de Comida",
    "mapData": {
      "tipo": "sobregasto",
      "categoria": "Comida",
      "presupuesto": "400",
      "gastado": "480",
      "exceso": "80",
      "accion": "reducir_gastos"
    }
  }'
```

### Ejemplo - Oportunidad de Ahorro
```bash
curl -X POST https://api-google-colab.onrender.com/api/Firebase/sendnotificacion \
  -H "Content-Type: application/json" \
  -d '{
    "strToken": "token_dispositivo_aqui",
    "strTitle": "🎯 Oportunidad de Ahorro",
    "strMessage": "Podrías ahorrar $50 este mes con pequeños cambios",
    "mapData": {
      "tipo": "oportunidad_ahorro",
      "ahorro_potencial": "50",
      "sugerencia": "Cambiar de plan telefonico",
      "accion": "ver_detalles"
    }
  }'
```

---

## 2. Enviar Notificación a Todos los Dispositivos del Usuario (Con autenticación)

### Primero: Obtener Token JWT
```bash
curl -X POST https://api-google-colab.onrender.com/api/v2/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "usuario123"
  }'

# Respuesta:
# {
#   "status": "success",
#   "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "expires_in": 86400
# }

# Copiar el token para los siguientes ejemplos
```

### Ejemplo - Meta Alcanzada
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
USUARIO_ID="usuario123"

curl -X POST https://api-google-colab.onrender.com/api/v2/users/${USUARIO_ID}/send-notification \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "🎉 ¡Felicidades!",
    "cuerpo": "Alcanzaste tu meta de ahorro: $1,000",
    "datos_extra": {
      "tipo": "meta_alcanzada",
      "meta_nombre": "Fondo de Emergencia",
      "monto_alcanzado": "1000",
      "accion": "celebrar"
    }
  }'
```

### Ejemplo - Recordatorio de Presupuesto
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
USUARIO_ID="usuario123"

curl -X POST https://api-google-colab.onrender.com/api/v2/users/${USUARIO_ID}/send-notification \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "⏰ Recordatorio",
    "cuerpo": "Hoy es el último día para revisar tus gastos de este mes",
    "datos_extra": {
      "tipo": "recordatorio",
      "seccion": "resumen_mes",
      "accion": "ver_resumen"
    }
  }'
```

### Ejemplo - Consejo Personalizado
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
USUARIO_ID="usuario123"

curl -X POST https://api-google-colab.onrender.com/api/v2/users/${USUARIO_ID}/send-notification \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "💡 Consejo de Ahorro",
    "cuerpo": "Notamos que gastas mucho en Entretenimiento. ¿Reducimos? Ahorrarías $200/mes",
    "datos_extra": {
      "tipo": "consejo_personalizado",
      "categoria": "Entretenimiento",
      "gasto_actual": "400",
      "gasto_recomendado": "200",
      "ahorro_mensual": "200",
      "accion": "ver_plan"
    }
  }'
```

### Ejemplo - Análisis Completado
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
USUARIO_ID="usuario123"

curl -X POST https://api-google-colab.onrender.com/api/v2/users/${USUARIO_ID}/send-notification \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "📊 Análisis Disponible",
    "cuerpo": "Tu análisis financiero semanal está listo",
    "datos_extra": {
      "tipo": "analisis_completado",
      "periodo": "semanal",
      "fecha_inicio": "2026-01-29",
      "fecha_fin": "2026-02-05",
      "accion": "ver_analisis"
    }
  }'
```

### Ejemplo - Promoción/Noticia Importante
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
USUARIO_ID="usuario123"

curl -X POST https://api-google-colab.onrender.com/api/v2/users/${USUARIO_ID}/send-notification \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "📢 Importante",
    "cuerpo": "Ahora puedes conectar múltiples cuentas bancarias",
    "datos_extra": {
      "tipo": "noticia",
      "prioridad": "alta",
      "accion": "conectar_banco"
    }
  }'
```

---

## 3. PowerShell (Windows)

### Enviar Notificación Básica
```powershell
$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    strToken = "token_dispositivo_aqui"
    strTitle = "Gasto Detectado"
    strMessage = "Se registró un gasto de $50"
} | ConvertTo-Json

$response = Invoke-WebRequest `
    -Uri "https://api-google-colab.onrender.com/api/Firebase/sendnotificacion" `
    -Method POST `
    -Headers $headers `
    -Body $body

$response.Content | ConvertFrom-Json | Format-Table
```

### Enviar Notificación con Autenticación
```powershell
$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
$usuarioId = "usuario123"

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$body = @{
    titulo = "¡Meta Alcanzada!"
    cuerpo = "Ahorraste $1,000"
    datos_extra = @{
        tipo = "meta_alcanzada"
        monto = "1000"
    }
} | ConvertTo-Json

$response = Invoke-WebRequest `
    -Uri "https://api-google-colab.onrender.com/api/v2/users/$usuarioId/send-notification" `
    -Method POST `
    -Headers $headers `
    -Body $body

$response.Content | ConvertFrom-Json | Format-Table
```

---

## 4. Python (Requests)

### Enviar Notificación Básica
```python
import requests
import json

url = "https://api-google-colab.onrender.com/api/Firebase/sendnotificacion"

payload = {
    "strToken": "token_dispositivo_aqui",
    "strTitle": "Gasto Detectado",
    "strMessage": "Se registró un gasto de $50",
    "mapData": {
        "categoria": "Comida",
        "monto": "50"
    }
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

### Enviar Notificación con Autenticación
```python
import requests
import json

# Primero obtener token
auth_url = "https://api-google-colab.onrender.com/api/v2/auth/token"
auth_payload = {"user_id": "usuario123"}
auth_response = requests.post(auth_url, json=auth_payload)
token = auth_response.json()["token"]

# Luego enviar notificación
notification_url = "https://api-google-colab.onrender.com/api/v2/users/usuario123/send-notification"

payload = {
    "titulo": "¡Meta Alcanzada!",
    "cuerpo": "Ahorraste $1,000 en alimentación",
    "datos_extra": {
        "tipo": "meta_alcanzada",
        "monto": "1000"
    }
}

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

response = requests.post(notification_url, json=payload, headers=headers)
print(response.json())
```

### Loop - Enviar a Múltiples Usuarios
```python
import requests

usuarios = ["user1", "user2", "user3"]
token = "tu_token_jwt"

for usuario_id in usuarios:
    url = f"https://api-google-colab.onrender.com/api/v2/users/{usuario_id}/send-notification"
    
    payload = {
        "titulo": "📊 Análisis Disponible",
        "cuerpo": "Tu reporte semanal está listo",
        "datos_extra": {
            "tipo": "reporte",
            "accion": "ver_reporte"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    print(f"{usuario_id}: {response.json()['status']}")
```

---

## 5. JavaScript (Fetch API)

### Enviar Notificación Básica
```javascript
async function sendNotification(deviceToken, title, message) {
  const response = await fetch(
    'https://api-google-colab.onrender.com/api/Firebase/sendnotificacion',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        strToken: deviceToken,
        strTitle: title,
        strMessage: message
      })
    }
  );
  
  return await response.json();
}

// Usar
sendNotification('token_aqui', 'Gasto Detectado', 'Se registró un gasto de $50')
  .then(result => console.log(result));
```

### Enviar Notificación con Autenticación
```javascript
async function sendAuthenticatedNotification(usuarioId, jwtToken, titulo, cuerpo) {
  const response = await fetch(
    `https://api-google-colab.onrender.com/api/v2/users/${usuarioId}/send-notification`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${jwtToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        titulo: titulo,
        cuerpo: cuerpo,
        datos_extra: {
          accion: 'ver_detalles'
        }
      })
    }
  );
  
  return await response.json();
}

// Usar
sendAuthenticatedNotification(
  'usuario123',
  'eyJhbGciOi...',
  '¡Meta Alcanzada!',
  'Ahorraste $1,000'
).then(result => console.log(result));
```

---

## Respuestas de Ejemplo

### Exitosa (200)
```json
{
  "status": "success",
  "mensaje": "Notificación enviada exitosamente",
  "message_id": "0:1675849384938204%3a1234567",
  "timestamp": "2026-02-05T18:15:30.123456"
}
```

### Error - Faltan Campos (400)
```json
{
  "status": "error",
  "mensaje": "Faltan campos requeridos: strToken, strTitle, strMessage",
  "code": "MISSING_FIELDS"
}
```

### Error - Token Inválido (401)
```json
{
  "status": "error",
  "mensaje": "Token requerido o inválido",
  "code": "UNAUTHORIZED"
}
```

### Error - Firebase No Disponible (503)
```json
{
  "status": "error",
  "mensaje": "Firebase no disponible",
  "code": "FIREBASE_NOT_AVAILABLE"
}
```

---

## ✅ Checklist Antes de Probar

- [ ] ¿Tienes un token FCM válido?
- [ ] ¿Firebase está configurado correctamente?
- [ ] ¿El credentials.json está en el servidor?
- [ ] ¿La app tiene permisos de notificaciones?
- [ ] ¿Estás usando HTTPS en producción?
- [ ] ¿El usuario tiene al menos un dispositivo registrado?
