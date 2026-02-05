# 🔧 Solución: Error "Message.data must not contain non-string values"

## El Problema

```
Error: 400 Bad Request
{
  "exito": false,
  "mensaje": "Notificación enviada a 0 dispositivo(s)",
  "resultados": {
    "error": "Message.data must not contain non-string values.",
    "estado": "error"
  }
}
```

**Causa**: Firebase Cloud Messaging (FCM) requiere que **TODOS los valores** en el campo `data` sean strings, pero estabas enviando números:

```json
{
  "datos": {
    "monto": 50,        // ❌ Número (incorrecto)
    "categoria": "Comida"
  }
}
```

---

## ✅ La Solución

### Opción 1: Envía TODO como Strings (RECOMENDADO)

```bash
curl -X POST https://api-google-colab.onrender.com/api/v2/notifications/send \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": "BCc7NaZ4KQTqFY3dUxgStWH62dh2",
    "titulo": "¡Gasto detectado!",
    "cuerpo": "Registramos un gasto de $50 en Comida",
    "datos": {
      "monto": "50",              // ✅ String (correcto)
      "categoria": "Comida",      // ✅ String (correcto)
      "tipo_alerta": "gasto_detectado"
    }
  }'
```

### Opción 2: La API lo Convierte Automáticamente (NUEVO)

¡Buena noticia! Hemos actualizado la API para que **convierta automáticamente** todos los valores a strings:

```bash
curl -X POST https://api-google-colab.onrender.com/api/v2/notifications/send \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": "BCc7NaZ4KQTqFY3dUxgStWH62dh2",
    "titulo": "¡Gasto detectado!",
    "cuerpo": "Registramos un gasto de $50 en Comida",
    "datos": {
      "monto": 50,                // ✅ Ahora acepta números
      "categoria": "Comida",
      "porcentaje": 25.5,         // ✅ También decimales
      "activo": true              // ✅ Y booleans
    }
  }'
```

**La API automáticamente convierte:**
- `50` → `"50"`
- `25.5` → `"25.5"`
- `true` → `"true"`
- `"text"` → `"text"`

---

## 📱 Integración con Flutter (Control de Gastos)

Para la app Flutter, aquí está el código correcto:

### Paso 1: Obtener JWT Token

```dart
Future<String?> obtenerToken(String usuario, String contrasena) async {
  final response = await http.post(
    Uri.parse('https://api-google-colab.onrender.com/api/v2/auth/token'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'usuario': usuario,
      'contrasena': contrasena,
    }),
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    return data['token']; // Guardar este token
  }
  return null;
}
```

### Paso 2: Registrar Dispositivo (Una sola vez)

```dart
Future<void> registrarDispositivo(String token, String usuarioId) async {
  // Obtener token FCM del dispositivo
  final String? fcmToken = await FirebaseMessaging.instance.getToken();

  if (fcmToken != null) {
    final response = await http.post(
      Uri.parse('https://api-google-colab.onrender.com/api/v2/notifications/register-device'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'dispositivo_token': fcmToken,
        'dispositivo_info': {
          'tipo': 'flutter',
          'modelo': 'Control de Gastos',
          'os': 'iOS/Android',
        }
      }),
    );

    print('Dispositivo registrado: ${response.statusCode}');
  }
}
```

### Paso 3: Enviar Notificación de Gasto

```dart
Future<void> enviarNotificacionGasto({
  required String token,
  required String usuarioId,
  required String titulo,
  required String cuerpo,
  required double monto,
  required String categoria,
  String? tipoAlerta,
}) async {
  final response = await http.post(
    Uri.parse('https://api-google-colab.onrender.com/api/v2/notifications/send'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'usuario_id': usuarioId,
      'titulo': titulo,
      'cuerpo': cuerpo,
      'datos': {
        'monto': monto.toString(),        // ✅ Convertir a string
        'categoria': categoria,
        'tipo_alerta': tipoAlerta ?? 'gasto_registrado',
        'timestamp': DateTime.now().toString(),
      }
    }),
  );

  if (response.statusCode == 200) {
    print('✅ Notificación enviada correctamente');
  } else {
    print('❌ Error: ${response.body}');
  }
}
```

### Paso 4: Uso en tu App Flutter

```dart
// Cuando el usuario registra un gasto
onGastoRegistrado(Gasto gasto) async {
  await enviarNotificacionGasto(
    token: jwtToken,
    usuarioId: usuarioId,
    titulo: '💰 ${gasto.categoria}',
    cuerpo: '\$${gasto.monto.toStringAsFixed(2)} en ${gasto.descripcion}',
    monto: gasto.monto,
    categoria: gasto.categoria,
    tipoAlerta: 'gasto_registrado',
  );
}
```

---

## 🔄 Flujo Completo: Flutter → API → Notificación

```
┌──────────────────────────────────────┐
│ 1. Usuario abre app Flutter          │
│    Obtiene JWT token                 │
│    Registra su dispositivo (1x)      │
└──────────────────────────────────────┘
                ↓
┌──────────────────────────────────────┐
│ 2. Usuario registra un gasto         │
│    Presiona botón "Guardar gasto"    │
└──────────────────────────────────────┘
                ↓
┌──────────────────────────────────────┐
│ 3. App envía notificación            │
│    POST /api/v2/notifications/send   │
│    Payload: {usuario_id, datos,...}  │
└──────────────────────────────────────┘
                ↓
┌──────────────────────────────────────┐
│ 4. API convierte datos a strings     │
│    Busca tokens del usuario          │
│    Envía vía Firebase Cloud Messaging│
└──────────────────────────────────────┘
                ↓
┌──────────────────────────────────────┐
│ 5. ✅ Notificación llega al celular  │
│    "💰 Comida: $50"                  │
└──────────────────────────────────────┘
```

---

## 📋 Endpoints de Notificaciones

### 1. Registrar Dispositivo (Una sola vez)

```bash
POST /api/v2/notifications/register-device
Authorization: Bearer {JWT_TOKEN}

{
  "dispositivo_token": "fcm_token_del_dispositivo",
  "dispositivo_info": {
    "tipo": "flutter",
    "modelo": "Pixel 6"
  }
}
```

### 2. Enviar Notificación

```bash
POST /api/v2/notifications/send
Authorization: Bearer {JWT_TOKEN}

{
  "usuario_id": "usuario123",
  "titulo": "Título",
  "cuerpo": "Mensaje",
  "datos": {
    "clave1": "valor1",
    "monto": "100",
    "activo": "true"
  }
}
```

### 3. Enviar por Usuario ID (Sin JWT)

```bash
POST /api/Firebase/sendnotificacion-usuario

{
  "usuario_id": "usuario123",
  "strTitle": "Título",
  "strMessage": "Mensaje",
  "mapData": {
    "monto": "100",
    "categoria": "Comida"
  }
}
```

### 4. Enviar Alerta de Presupuesto

```bash
POST /api/v2/notifications/send-alert/{usuario_id}
Authorization: Bearer {JWT_TOKEN}

{
  "presupuesto_mensual": 1000
}
```

### 5. Enviar Tips Personalizados

```bash
POST /api/v2/notifications/send-tips/{usuario_id}
Authorization: Bearer {JWT_TOKEN}
```

---

## ✅ Checklist

- ✅ Todos los valores en `datos` son strings
- ✅ Números convertidos: `50` → `"50"`
- ✅ Booleanos convertidos: `true` → `"true"`
- ✅ Decimales convertidos: `25.5` → `"25.5"`
- ✅ Token JWT es válido
- ✅ usuario_id es correcto
- ✅ Dispositivo está registrado
- ✅ Firebase Cloud Messaging está configurado

---

## 🚨 Errores Comunes

### Error 400: "Message.data must not contain non-string values"

**Solución**: Convierte todos los valores a strings

```json
// ❌ Incorrecto
"datos": {
  "monto": 50,
  "activo": true
}

// ✅ Correcto
"datos": {
  "monto": "50",
  "activo": "true"
}
```

### Error 401: Token inválido

**Solución**: Obtén un nuevo JWT token

```bash
POST /api/v2/auth/token
{
  "usuario": "email@example.com",
  "contrasena": "password"
}
```

### Error 404: No hay dispositivos registrados

**Solución**: Registra el dispositivo primero

```bash
POST /api/v2/notifications/register-device
Authorization: Bearer {JWT_TOKEN}
```

---

## 📊 Cambios en la API

**Actualización**: La API ahora convierte automáticamente todos los valores en `datos` a strings. No necesitas hacer el casting en tu código, pero es buena práctica hacerlo igualmente.

**Versión**: 1.1  
**Fecha**: 05 de Febrero de 2026

---

## 🎯 Próximo Paso

Prueba con este comando:

```bash
curl -X POST https://api-google-colab.onrender.com/api/v2/notifications/send \
  -H "Authorization: Bearer {Tu_JWT_Token}" \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": "BCc7NaZ4KQTqFY3dUxgStWH62dh2",
    "titulo": "Test",
    "cuerpo": "¡Funciona!",
    "datos": {
      "monto": "50",
      "categoria": "Prueba"
    }
  }'
```

**Debe responder:**
```json
{
  "exito": true,
  "mensaje": "Notificación enviada a 1 dispositivo(s)"
}
```

¡Listo! 🎉
