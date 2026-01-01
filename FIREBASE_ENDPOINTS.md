# 🔥 ENDPOINTS FIREBASE - Guía de Uso

Tu API ahora está integrada con Firebase. Aquí están los nuevos endpoints:

## 📋 Endpoints Firebase

### 1️⃣ Obtener Todos los Usuarios
```
GET /api/v2/firebase/usuarios
```

**Respuesta:**
```json
{
  "status": "success",
  "total": 3,
  "data": [
    {
      "id": "user123",
      "email": "usuario@gmail.com",
      "nombre": "Juan"
    }
  ]
}
```

---

### 2️⃣ Obtener Usuario Específico
```
GET /api/v2/firebase/usuarios/{usuario_id}
```

**Ejemplo:**
```
GET https://api-google-colab.onrender.com/api/v2/firebase/usuarios/BCc7NaZ4KQTqFY3dUxgStWH62dh2
```

**Respuesta:**
```json
{
  "status": "success",
  "data": {
    "id": "BCc7NaZ4KQTqFY3dUxgStWH62dh2",
    "email": "usuario@gmail.com",
    "nombre": "Yordan"
  }
}
```

---

### 3️⃣ Obtener Gastos de un Usuario
```
GET /api/v2/firebase/gastos/{usuario_id}
```

**Ejemplo:**
```
GET https://api-google-colab.onrender.com/api/v2/firebase/gastos/BCc7NaZ4KQTqFY3dUxgStWH62dh2
```

**Respuesta:**
```json
{
  "status": "success",
  "usuario_id": "BCc7NaZ4KQTqFY3dUxgStWH62dh2",
  "total_gastos": 5,
  "data": [
    {
      "id": "5ZivLl6foLLSbfs5IU79",
      "cantidad": 18.67,
      "categoria": "Transporte",
      "descripcion": "taxi temprano",
      "fecha": "2025-12-30"
    }
  ]
}
```

---

### 4️⃣ Obtener Gastos Procesados con IA
```
GET /api/v2/firebase/gastos-procesados/{usuario_id}
Headers:
  Authorization: Bearer {tu_token}
```

**Ejemplo:**
```
GET https://api-google-colab.onrender.com/api/v2/firebase/gastos-procesados/BCc7NaZ4KQTqFY3dUxgStWH62dh2
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Respuesta:**
```json
{
  "status": "success",
  "usuario_id": "BCc7NaZ4KQTqFY3dUxgStWH62dh2",
  "total_gastos": 5,
  "gasto_total": 250.50,
  "promedio_gasto": 50.10,
  "resumen_por_categoria": {
    "Transporte": {
      "sum": 150,
      "count": 3,
      "mean": 50
    },
    "Comida": {
      "sum": 100.50,
      "count": 2,
      "mean": 50.25
    }
  },
  "data": [...]
}
```

---

### 5️⃣ Crear Nuevo Gasto
```
POST /api/v2/firebase/crear-gasto/{usuario_id}
Headers:
  Authorization: Bearer {tu_token}
  Content-Type: application/json

Body:
{
  "cantidad": 75.50,
  "categoria": "Comida",
  "descripcion": "Cena en restaurante",
  "fecha": "2024-12-30"
}
```

**Ejemplo completo:**
```
POST https://api-google-colab.onrender.com/api/v2/firebase/crear-gasto/BCc7NaZ4KQTqFY3dUxgStWH62dh2
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
  Content-Type: application/json

Body:
{
  "cantidad": 45,
  "categoria": "Transporte",
  "descripcion": "Uber",
  "fecha": "2024-12-30"
}
```

**Respuesta:**
```json
{
  "status": "success",
  "mensaje": "Gasto creado correctamente",
  "gasto_id": "nuevo_gasto_id_123",
  "data": {
    "cantidad": 45,
    "categoria": "Transporte",
    "descripcion": "Uber",
    "fecha": "2024-12-30",
    "createdAt": "2024-12-30T15:45:00"
  }
}
```

---

## 🔄 Flujo Completo en Postman

### Paso 1: Obtener Token
```
POST https://api-google-colab.onrender.com/api/v2/auth/token
Body: {"user_id": "BCc7NaZ4KQTqFY3dUxgStWH62dh2"}
```

### Paso 2: Obtener Gastos sin IA (sin token)
```
GET https://api-google-colab.onrender.com/api/v2/firebase/gastos/BCc7NaZ4KQTqFY3dUxgStWH62dh2
```

### Paso 3: Obtener Gastos con Análisis IA (requiere token)
```
GET https://api-google-colab.onrender.com/api/v2/firebase/gastos-procesados/BCc7NaZ4KQTqFY3dUxgStWH62dh2
Headers:
  Authorization: Bearer {token_del_paso_1}
```

### Paso 4: Crear un Nuevo Gasto
```
POST https://api-google-colab.onrender.com/api/v2/firebase/crear-gasto/BCc7NaZ4KQTqFY3dUxgStWH62dh2
Headers:
  Authorization: Bearer {token_del_paso_1}
  Content-Type: application/json
Body:
{
  "cantidad": 50,
  "categoria": "Comida",
  "descripcion": "Desayuno",
  "fecha": "2024-12-31"
}
```

---

## 💡 Casos de Uso

### Caso 1: Ver gastos del usuario actual
```
1. Obtén el token del usuario
2. GET /api/v2/firebase/gastos-procesados/{usuario_id}
3. Verás resumen automático por categoría
```

### Caso 2: Registrar nuevo gasto desde la app
```
1. Usuario ingresa gasto en Flutter
2. POST /api/v2/firebase/crear-gasto/{usuario_id}
3. Se guarda en Firebase y es accesible en la API
```

### Caso 3: Análisis histórico
```
1. GET /api/v2/firebase/gastos-procesados/{usuario_id}
2. Luego POST /api/v2/predict-category con esos gastos
3. Obtienes predicciones automáticas
```

---

## ✅ Estructura Firebase Actual

Tu Firebase tiene esta estructura:

```
gestofin/
  └── users/
      ├── BCc7NaZ4KQTqFY3dUxgStWH62dh2/  (userId autogenerado)
      │   ├── budget/
      │   │   ├── ahorroRecomendado: 90
      │   │   ├── gastosTotales: 302.92
      │   │   ├── metaAhorro: 400
      │   │   ├── presupuesoGeneral: 600
      │   │   └── updatedAt: timestamp
      │   └── gastos/ (Subcolección)
      │       ├── 5ZivLl6foLLSbfs5IU79/
      │       │   ├── cantidad: 18.67
      │       │   ├── categoria: "Transporte"
      │       │   ├── descripcion: "taxi temprano"
      │       │   └── fecha: "2025-12-30"
      │       └── {otro_gastoId}/
      │           ├── cantidad: 50
      │           ├── categoria: "Comida"
      │           └── fecha: "2025-12-31"
      ├── qn6FfGYZboNB48n26hjyYPEt8L43/
      │   └── gastos/ (Subcolección)
      └── sdyUylJAItaxjjVJEThKbhxeJFz2/
          └── gastos/ (Subcolección)
```

**Campos importantes:**
- Colección raíz: **`gestofin`**
- Colección de usuarios: **`gestofin/users`**
- IDs de usuarios: Auto-generados (hashes como BCc7NaZ4KQTqFY3dUxgStWH62dh2)
- Campo de monto: **`cantidad`** (no `monto`)
- Subcollección de gastos: **`gestofin/users/{userId}/gastos`**
- IDs de gastos: Auto-generados (hashes como 5ZivLl6foLLSbfs5IU79)

---

## 🔐 Notas de Seguridad

- ✅ Endpoints GET de Firebase NO requieren token
- ✅ Endpoints POST/PUT/DELETE SÍ requieren token JWT
- ✅ El archivo `gestor-financiero-28ac2-firebase-adminsdk-fbsvc-6efa11cbf8.json` está protegido
- ✅ En Render, las credenciales se guardan como variables de entorno

---

## 🚀 Próximos Pasos

1. Sube los cambios a GitHub
2. En Render, dispara un redeploy
3. Prueba los endpoints en Postman
4. La app Flutter ahora sincroniza con la API automáticamente
