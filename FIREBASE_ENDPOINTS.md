# 🔥 ENDPOINTS FIREBASE - Guía de Uso

Tu API está integrada con Firebase Firestore (base de datos: **gestofin**).

## ✅ Estructura Firebase Confirmada

```
Base de datos: gestofin
└── users/                              ← Colección de usuarios
    ├── BCc7NaZ4KQTqFY3dUxgStWH62dh2/  ← Documento usuario
    │   ├── accountType: "user"
    │   ├── displayName: "yordan..."
    │   ├── email: "yordan03224@hotmail.com"
    │   ├── uid: "BCc7NaZ4KQTqFY3dUxgStWH62dh2"
    │   ├── budget/                     ← Subcolección
    │   │   └── current/
    │   └── gastos/                     ← Subcolección de gastos
    │       ├── 5ZivLl6foLLSbfs5IU79/
    │       │   ├── cantidad: 18.67
    │       │   ├── categoria: "Transporte"
    │       │   ├── descripcion: "taxi temprano"
    │       │   ├── fecha: "2025-12-30T00:00:00.000"
    │       │   └── userId: "BCc7NaZ4KQTqFY3dUxgStWH62dh2"
    │       └── ... más gastos
    ├── qn6FfGYZboNB48n26hjyYPEt8L43/
    └── sdyUylJAItaxjjVJEThKbhxeJFz2/
```

---

## 📋 Endpoints Firebase

### 🔧 Debug - Verificar Conexión
```
GET /api/v2/firebase/debug
```
**Ejemplo:** `https://api-google-colab.onrender.com/api/v2/firebase/debug`

**Respuesta:**
```json
{
  "status": "success",
  "data": {
    "firebase_available": true,
    "database_id": "gestofin",
    "projectId": "gestor-financiero-28ac2",
    "collections": ["ml_models", "users"],
    "users_count": 3,
    "users_ids": ["BCc7NaZ4KQTqFY3dUxgStWH62dh2", "..."]
  }
}
```

---

### 1️⃣ Obtener Todos los Usuarios
```
GET /api/v2/firebase/usuarios
```
**Ejemplo:** `https://api-google-colab.onrender.com/api/v2/firebase/usuarios`

**Respuesta:**
```json
{
  "status": "success",
  "total": 3,
  "data": [
    {
      "id": "BCc7NaZ4KQTqFY3dUxgStWH62dh2",
      "email": "yordan03224@hotmail.com",
      "displayName": "yordan alberto rojas de la cruz",
      "accountType": "user"
    }
  ]
}
```

---

### 2️⃣ Obtener Usuario Específico
```
GET /api/v2/firebase/usuarios/{usuario_id}
```
**Ejemplo:** `https://api-google-colab.onrender.com/api/v2/firebase/usuarios/BCc7NaZ4KQTqFY3dUxgStWH62dh2`

**Respuesta:**
```json
{
  "status": "success",
  "data": {
    "id": "BCc7NaZ4KQTqFY3dUxgStWH62dh2",
    "email": "yordan03224@hotmail.com",
    "displayName": "yordan alberto rojas de la cruz",
    "accountType": "user",
    "budget": {...}
  }
}
```

---

### 3️⃣ Obtener Gastos de un Usuario
```
GET /api/v2/firebase/users/{usuario_id}/gastos
```
**Ejemplo:** `https://api-google-colab.onrender.com/api/v2/firebase/users/BCc7NaZ4KQTqFY3dUxgStWH62dh2/gastos`

**Query params opcionales:** `?ids_only=true`

**Respuesta:**
```json
{
  "status": "success",
  "usuario_id": "BCc7NaZ4KQTqFY3dUxgStWH62dh2",
  "total_gastos": 11,
  "path_usado": "users/BCc7NaZ4KQTqFY3dUxgStWH62dh2/gastos",
  "data": [
    {
      "id": "5ZivLl6foLLSbfs5IU79",
      "cantidad": 18.67,
      "categoria": "Transporte",
      "descripcion": "taxi temprano",
      "fecha": "2025-12-30T00:00:00.000",
      "createdAt": "2025-12-30T20:27:14.844",
      "userId": "BCc7NaZ4KQTqFY3dUxgStWH62dh2"
    }
  ]
}
```

---

### 4️⃣ Obtener Solo IDs de Gastos
```
GET /api/v2/firebase/users/{usuario_id}/gastos-ids
```
**Ejemplo:** `https://api-google-colab.onrender.com/api/v2/firebase/users/BCc7NaZ4KQTqFY3dUxgStWH62dh2/gastos-ids`

**Respuesta:**
```json
{
  "status": "success",
  "usuario_id": "BCc7NaZ4KQTqFY3dUxgStWH62dh2",
  "total_gastos": 11,
  "path_usado": "users/BCc7NaZ4KQTqFY3dUxgStWH62dh2/gastos",
  "ids": [
    "5ZivLl6foLLSbfs5IU79",
    "7cGlk6Z1kDWVSmfwmNdi",
    "HcW2VX9kb9dN22G704Ue"
  ]
}
```

---

### 5️⃣ Obtener Gastos Procesados con IA (requiere token)
```
GET /api/v2/firebase/users/{usuario_id}/gastos-procesados
Headers:
  Authorization: Bearer {tu_token}
```
**Ejemplo:** `https://api-google-colab.onrender.com/api/v2/firebase/users/BCc7NaZ4KQTqFY3dUxgStWH62dh2/gastos-procesados`

**Respuesta:**
```json
{
  "status": "success",
  "usuario_id": "BCc7NaZ4KQTqFY3dUxgStWH62dh2",
  "total_gastos": 11,
  "path_usado": "users/BCc7NaZ4KQTqFY3dUxgStWH62dh2/gastos",
  "gasto_total": 302.92,
  "promedio_gasto": 27.54,
  "resumen_por_categoria": {
    "Transporte": {"sum": 150.0, "count": 5, "mean": 30.0},
    "Comida": {"sum": 100.50, "count": 4, "mean": 25.13}
  },
  "data": [...]
}
```

---

### 6️⃣ Crear Nuevo Gasto (requiere token)
```
POST /api/v2/firebase/users/{usuario_id}/gastos
Headers:
  Authorization: Bearer {tu_token}
  Content-Type: application/json

Body:
{
  "cantidad": 75.50,
  "categoria": "Comida",
  "descripcion": "Cena en restaurante",
  "fecha": "2026-01-02"
}
```

**Ejemplo completo:**
```
POST https://api-google-colab.onrender.com/api/v2/firebase/users/BCc7NaZ4KQTqFY3dUxgStWH62dh2/gastos
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
  Content-Type: application/json

Body:
{
  "cantidad": 45,
  "categoria": "Transporte",
  "descripcion": "Uber al trabajo"
}
```

**Respuesta:**
```json
{
  "status": "success",
  "mensaje": "Gasto creado correctamente",
  "gasto_id": "nuevo_id_generado",
  "path_usado": "users/BCc7NaZ4KQTqFY3dUxgStWH62dh2/gastos/nuevo_id_generado",
  "data": {
    "cantidad": 45,
    "categoria": "Transporte",
    "descripcion": "Uber al trabajo",
    "fecha": "2026-01-02T...",
    "createdAt": "2026-01-02T..."
  }
}
```

---

## 🔄 Flujo Completo en Postman

### Paso 1: Verificar conexión Firebase
```
GET https://api-google-colab.onrender.com/api/v2/firebase/debug
```

### Paso 2: Obtener Token JWT
```
POST https://api-google-colab.onrender.com/api/v2/auth/token
Content-Type: application/json

Body: {"user_id": "BCc7NaZ4KQTqFY3dUxgStWH62dh2"}
```

### Paso 3: Obtener Gastos (sin token)
```
GET https://api-google-colab.onrender.com/api/v2/firebase/users/BCc7NaZ4KQTqFY3dUxgStWH62dh2/gastos
```

### Paso 4: Obtener Gastos con Análisis IA (requiere token)
```
GET https://api-google-colab.onrender.com/api/v2/firebase/users/BCc7NaZ4KQTqFY3dUxgStWH62dh2/gastos-procesados
Headers:
  Authorization: Bearer {token_del_paso_2}
```

### Paso 5: Crear un Nuevo Gasto
```
POST https://api-google-colab.onrender.com/api/v2/firebase/users/BCc7NaZ4KQTqFY3dUxgStWH62dh2/gastos
Headers:
  Authorization: Bearer {token_del_paso_2}
  Content-Type: application/json

Body:
{
  "cantidad": 50,
  "categoria": "Comida",
  "descripcion": "Desayuno"
}
```

---

## 🔑 Resumen de Autenticación

| Endpoint | Token JWT | Body JSON |
|----------|-----------|-----------|
| `/firebase/debug` | ❌ No | *(no aplica)* |
| `/firebase/usuarios` | ❌ No | *(no aplica)* |
| `/firebase/usuarios/{id}` | ❌ No | *(no aplica)* |
| `/firebase/users/{id}/gastos` GET | ❌ No | *(no aplica)* |
| `/firebase/users/{id}/gastos-ids` | ❌ No | *(no aplica)* |
| `/firebase/users/{id}/gastos-procesados` | ✅ Sí | *(no aplica)* |
| `/firebase/users/{id}/gastos` POST | ✅ Sí | `{"cantidad":..., "categoria":...}` |

---

## 🔐 Notas de Seguridad

- ✅ Base de datos: **gestofin** (no default)
- ✅ Path de gastos: `users/{userId}/gastos`
- ✅ Campo de monto: **`cantidad`** (no `monto`)
- ✅ Endpoints GET de lectura NO requieren token
- ✅ Endpoints POST/PUT/DELETE SÍ requieren token JWT
- ✅ Las credenciales Firebase están en variables de entorno en Render
