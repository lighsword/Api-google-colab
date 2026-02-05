# 🔔 FIX: Error "No hay dispositivos registrados"

## ❌ El Problema

El error ocurre cuando pasas el **JWT completo** como el `usuario_id` en la URL:

```
❌ INCORRECTO:
POST /api/v2/users/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.../send-notification
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                   ¡Aquí no va el JWT completo!
```

---

## ✅ La Solución

El `usuario_id` debe ser **solo el ID del usuario**, no el JWT.

### Paso 1: Obtener tu Usuario ID del JWT

Tu JWT contiene:
```json
{
  "user_id": "BCc7NaZ4KQTqFY3dUxgStWH62dh2",  ← ESTE ES TU USUARIO_ID
  "token_id": "44fe9e64-0b49-48c2-81a3-a87c1f6c0c66",
  "iat": 1770321315,
  "exp": 1770407715
}
```

### Paso 2: Usar la URL Correcta

```
✅ CORRECTO:
POST /api/v2/users/BCc7NaZ4KQTqFY3dUxgStWH62dh2/send-notification
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                   ¡Solo el ID del usuario!
```

### Paso 3: En el Header, Enviar el JWT

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                      ¡Aquí va el JWT!
```

---

## 📝 Ejemplo Correcto

### cURL
```bash
curl -X POST \
  'https://api-google-colab.onrender.com/api/v2/users/BCc7NaZ4KQTqFY3dUxgStWH62dh2/send-notification' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiQkNjN05hWjRLUVRxRlkzZFV4Z1N0V0g2MmRoMiIsInRva2VuX2lkIjoiNDRmZTllNjQtMGI0OS00OGMyLTgxYTMtYTg3YzFmNmMwYzY2IiwiaWF0IjoxNzcwMzIxMzE1LCJleHAiOjE3NzA0MDc3MTV9.gFo8k_ohYSWAYAqnqrGJ_J8sz1BD5sbWAfxYX9QI3Eo' \
  -H 'Content-Type: application/json' \
  -d '{
    "titulo": "¡Meta Alcanzada!",
    "cuerpo": "Felicidades, ahorraste $1,000 en alimentación",
    "datos_extra": {
      "tipo": "meta_alcanzada",
      "meta_id": "meta_123",
      "monto": "1000"
    }
  }'
```

### Python
```python
import requests
import jwt

# Tu JWT
jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Decodificar para obtener el usuario_id
decoded = jwt.decode(jwt_token, options={"verify_signature": False})
usuario_id = decoded['user_id']  # BCc7NaZ4KQTqFY3dUxgStWH62dh2

# Hacer la llamada
url = f"https://api-google-colab.onrender.com/api/v2/users/{usuario_id}/send-notification"

headers = {
    "Authorization": f"Bearer {jwt_token}",
    "Content-Type": "application/json"
}

payload = {
    "titulo": "¡Meta Alcanzada!",
    "cuerpo": "Felicidades, ahorraste $1,000",
    "datos_extra": {
        "tipo": "meta_alcanzada",
        "monto": "1000"
    }
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

### JavaScript
```javascript
// Tu JWT
const jwtToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";

// Decodificar para obtener usuario_id
const decoded = JSON.parse(atob(jwtToken.split('.')[1]));
const usuarioId = decoded.user_id;  // BCc7NaZ4KQTqFY3dUxgStWH62dh2

// Hacer la llamada
const url = `https://api-google-colab.onrender.com/api/v2/users/${usuarioId}/send-notification`;

const response = await fetch(url, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    titulo: '¡Meta Alcanzada!',
    cuerpo: 'Felicidades, ahorraste $1,000',
    datos_extra: {
      tipo: 'meta_alcanzada',
      monto: '1000'
    }
  })
});

const result = await response.json();
console.log(result);
```

---

## 🎯 Desglose Visual

```
JWT: eyJhbGciOi.eyJ1c2VyX2lk.gFo8k_ohYSWAYAq
     ^^^^^^^^^^^ ^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^
     HEADER      PAYLOAD          SIGNATURE
                 └─> Contiene "user_id"

URL: /api/v2/users/BCc7NaZ4KQTqFY3dUxgStWH62dh2/send-notification
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                    ↑ EXTRAER DE PAYLOAD ↑
                    {
                      "user_id": "BCc7NaZ4KQTqFY3dUxgStWH62dh2",
                      "token_id": "...",
                      ...
                    }

HEADER: Authorization: Bearer eyJhbGciOi.eyJ1c2VyX2lk.gFo8k_ohYSWAYAq
                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                               ↑ JWT COMPLETO ↑
```

---

## ✅ Después de la Fix

Ahora el endpoint:

✅ Verifica que `usuario_id` en la URL coincida con el JWT  
✅ Previene que usuarios envíen notificaciones a otros usuarios  
✅ Retorna 200 si no hay dispositivos (con mensaje informativo)  
✅ Retorna 403 si intentas enviar a otro usuario  

---

## 🧪 Respuestas Posibles

### Éxito (200)
```json
{
  "status": "success",
  "usuario_id": "BCc7NaZ4KQTqFY3dUxgStWH62dh2",
  "mensajes_enviados": 2,
  "mensaje": "Notificación enviada a 2 dispositivos",
  "exitosos": 2,
  "fallidos": 0
}
```

### Sin dispositivos registrados (200)
```json
{
  "status": "info",
  "usuario_id": "BCc7NaZ4KQTqFY3dUxgStWH62dh2",
  "mensajes_enviados": 0,
  "mensaje": "El usuario no tiene dispositivos registrados. Asegúrate de que la app está configurada para recibir notificaciones."
}
```

### Error - Usuario no autorizado (403)
```json
{
  "status": "error",
  "mensaje": "No tienes permiso para enviar notificaciones a este usuario"
}
```

### Error - JWT inválido (401)
```json
{
  "status": "error",
  "mensaje": "Token requerido o inválido"
}
```

---

## 📚 Cómo Extraer usuario_id de tu JWT

### Online (https://jwt.io)
1. Copiar tu JWT completo
2. Pegarlo en jwt.io
3. Ver el PAYLOAD
4. Copiar el valor de "user_id"

### En Python
```python
import jwt

token = "tu_jwt_aqui"
decoded = jwt.decode(token, options={"verify_signature": False})
print(decoded['user_id'])
```

### En JavaScript
```javascript
const token = "tu_jwt_aqui";
const payload = JSON.parse(atob(token.split('.')[1]));
console.log(payload.user_id);
```

### En PowerShell
```powershell
$token = "tu_jwt_aqui"
$parts = $token.Split('.')
$payload = [System.Convert]::FromBase64String($parts[1])
$json = [System.Text.Encoding]::UTF8.GetString($payload)
$obj = $json | ConvertFrom-Json
$obj.user_id
```

---

## 🔐 Seguridad Mejorada

El endpoint ahora:

1. **Verifica que el usuario_id en la URL coincida con el JWT**
   ```python
   jwt_usuario_id = g.get('user_id')
   if jwt_usuario_id != usuario_id:
       return error 403
   ```

2. **Previene que se envíen notificaciones entre usuarios**
   - Solo el propietario de la cuenta puede enviar notificaciones a su propia cuenta

3. **Valida campos requeridos**
   - Titulo y cuerpo son obligatorios

---

## ❓ FAQ

**P: ¿Por qué dice "No hay dispositivos registrados"?**
R: Porque:
   1. Pasaste el JWT completo en la URL (ya arreglado)
   2. O el usuario no tiene dispositivos en Firebase
   
   Asegúrate que tu app registra tokens FCM en:
   `usuarios/{usuario_id}/device_tokens`

**P: ¿Cómo registrar dispositivos en Firebase?**
R: Desde tu app:
   ```javascript
   // Obtener token FCM
   const token = await messaging.getToken();
   
   // Guardar en Firebase
   await firebase.firestore()
     .collection('usuarios')
     .doc(usuarioId)
     .collection('device_tokens')
     .add({
       token: token,
       activo: true,
       createdAt: new Date()
     });
   ```

**P: ¿Puedo enviar a múltiples usuarios?**
R: No con este endpoint. Use el endpoint sin autenticación `/api/Firebase/sendnotificacion` para eso (pero requiere token FCM).

---

✅ **¡Problema Resuelto!**

Ahora el endpoint debería funcionar correctamente. Recuerda:
- **URL**: Usuario ID real
- **Header**: JWT completo

Prueba nuevamente y debería funcionar.
