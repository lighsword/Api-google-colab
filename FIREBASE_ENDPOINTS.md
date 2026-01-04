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

> Nota: si envías los endpoints de análisis sin `expenses`, la API ahora cargará automáticamente los gastos del usuario autenticado desde Firebase (`users/{userId}/gastos`). Asegúrate de enviar el header `Authorization: Bearer {token}` para que se identifique tu `user_id`.

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
| `/api/v2/firebase/debug` | ❌ No | *(no aplica)* |
| `/api/v2/firebase/usuarios` | ❌ No | *(no aplica)* |
| `/api/v2/firebase/usuarios/{id}` | ❌ No | *(no aplica)* |
| `/api/v2/firebase/users/{id}/gastos` GET | ❌ No | *(no aplica)* |
| `/api/v2/firebase/users/{id}/gastos-ids` | ❌ No | *(no aplica)* |
| `/api/v2/firebase/users/{id}/gastos-procesados` | ✅ Sí | *(no aplica)* |
| `/api/v2/firebase/users/{id}/gastos` POST | ✅ Sí | `{"cantidad":..., "categoria":...}` |

---

## 🔐 Notas de Seguridad

- ✅ Base de datos: **gestofin** (no default)
- ✅ Path de gastos: `users/{userId}/gastos`
- ✅ Campo de monto: **`cantidad`** (no `monto`)
- ✅ Endpoints GET de lectura NO requieren token
- ✅ Endpoints POST/PUT/DELETE SÍ requieren token JWT
- ✅ Las credenciales Firebase están en variables de entorno en Render

---

# 🤖 ASESOR FINANCIERO IA - Endpoints Avanzados

Estos endpoints proporcionan análisis inteligente basado en los gastos registrados en Firebase.

---

## 🎯 Endpoint Principal: Asesor Financiero Completo

```
GET /api/v2/firebase/users/{usuario_id}/asesor-financiero
Headers:
  Authorization: Bearer {tu_token}
```

**Ejemplo:** 
```
GET https://api-google-colab.onrender.com/api/v2/firebase/users/BCc7NaZ4KQTqFY3dUxgStWH62dh2/asesor-financiero
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Respuesta completa:**
```json
{
  "status": "success",
  "usuario_id": "BCc7NaZ4KQTqFY3dUxgStWH62dh2",
  "fecha_analisis": "2026-01-02T15:30:00",
  "resumen": {
    "total_gastos_registrados": 11,
    "gasto_total": 302.92,
    "gasto_promedio": 27.54,
    "periodo_analizado": {
      "desde": "2025-12-01",
      "hasta": "2025-12-30",
      "dias": 29
    }
  },
  "score_financiero": {
    "score": 75,
    "nivel": "BUENO",
    "emoji": "👍",
    "mensaje": "Buen control, con margen de mejora",
    "detalles": ["-10: Transporte supera el 40% de gastos"]
  },
  "predicciones": {
    "proximo_mes": {
      "estimacion_base": 310.50,
      "estimacion_ajustada": 341.55,
      "gasto_diario_promedio": 10.35,
      "confianza": "MEDIA"
    },
    "tendencia": "AUMENTANDO",
    "por_categoria": {
      "Transporte": {"prediccion_30_dias": 150.00, "promedio_por_gasto": 25.00},
      "Comida": {"prediccion_30_dias": 120.00, "promedio_por_gasto": 20.00}
    },
    "alerta_gastos": []
  },
  "analisis_estadistico": {
    "por_categoria": {
      "Transporte": {
        "total": 150.00,
        "promedio": 25.00,
        "maximo": 50.00,
        "minimo": 10.00,
        "porcentaje_total": 49.5
      }
    },
    "por_mes": {
      "Diciembre": {"total": 302.92, "promedio": 27.54, "categoria_top": "Transporte"}
    },
    "por_dia_semana": {
      "Lunes": {"total": 80.00, "promedio": 20.00},
      "Viernes": {"total": 100.00, "promedio": 33.33}
    },
    "comparativas": {
      "mes_actual_vs_anterior": {
        "mes_actual": {"nombre": "Enero", "total": 50.00},
        "mes_anterior": {"nombre": "Diciembre", "total": 302.92},
        "variacion_porcentaje": -83.5,
        "tendencia": "DISMINUCIÓN"
      }
    },
    "outliers": [
      {"categoria": "Comida", "cantidad": 100.00, "fecha": "2025-12-15", "motivo": "Gasto atípico"}
    ],
    "patrones": {
      "dia_mas_gastos": "Viernes",
      "categoria_mas_frecuente": "Transporte",
      "gasto_promedio_general": 27.54
    }
  },
  "recomendaciones": {
    "ahorro": [
      {
        "categoria": "Transporte",
        "ahorro_potencial": 30.00,
        "estrategia": "Reducir gastos en Transporte un 20%",
        "prioridad": "ALTA"
      }
    ],
    "alertas": [
      {
        "tipo": "GASTO_EXCESIVO",
        "categoria": "Transporte",
        "mensaje": "⚠️ Transporte representa el 49.5% de tus gastos",
        "porcentaje": 49.5
      }
    ],
    "metas_sugeridas": [
      {"tipo": "EVITAR_NUMEROS_ROJOS", "meta": 42.10, "descripcion": "Ahorro necesario para cerrar el mes sin déficit", "base": {"prediccion_mes": 341.55, "presupuesto": 300.00, "ingreso": null}, "dificultad": "MEDIA"},
      {"tipo": "BUFFER_PREVENTIVO", "meta": 34.15, "descripcion": "Crear un colchón del 10% de la proyección para imprevistos", "dificultad": "MEDIA"}
    ],
    "tips_personalizados": [
      {"icono": "📅", "titulo": "Patrón: Viernes", "mensaje": "Los Viernes son tu día de mayor gasto"},
      {"icono": "💡", "titulo": "Regla 50/30/20", "mensaje": "Destina 50% necesidades, 30% deseos, 20% ahorro"}
    ]
  },
  "graficos": {
    "pie_categorias": {
      "tipo": "pie",
      "titulo": "Distribución por Categoría",
      "labels": ["Transporte", "Comida", "Entretenimiento"],
      "values": [150.00, 100.50, 52.42]
    },
    "bar_meses": {
      "tipo": "bar",
      "titulo": "Gastos por Mes",
      "labels": ["Nov", "Dic"],
      "values": [200.00, 302.92]
    },
    "line_tendencia": {
      "tipo": "line",
      "titulo": "Tendencia Últimos 30 días",
      "labels": ["2025-12-01", "2025-12-02", "..."],
      "values": [10.00, 25.00, "..."]
    }
  }
}
```

---

## 📊 Endpoints Individuales (Componentes Separados)

### 1️⃣ Solo Predicciones
```
GET /api/v2/firebase/users/{usuario_id}/predicciones
Headers: Authorization: Bearer {token}
```

### 2️⃣ Solo Análisis Estadístico
```
GET /api/v2/firebase/users/{usuario_id}/analisis
Headers: Authorization: Bearer {token}
```

### 3️⃣ Solo Recomendaciones
```
GET /api/v2/firebase/users/{usuario_id}/recomendaciones
Headers: Authorization: Bearer {token}
```

### 4️⃣ Solo Datos para Gráficos
```
GET /api/v2/firebase/users/{usuario_id}/graficos
Headers: Authorization: Bearer {token}
```

### 5️⃣ Solo Score Financiero
```
GET /api/v2/firebase/users/{usuario_id}/score
Headers: Authorization: Bearer {token}
```

---

## 🎮 Score Financiero (Gamificación)

El score va de 0 a 100 y evalúa:

| Score | Nivel | Emoji | Significado |
|-------|-------|-------|-------------|
| 80-100 | EXCELENTE | 🌟 | Excelente manejo financiero |
| 60-79 | BUENO | 👍 | Buen control con margen de mejora |
| 40-59 | REGULAR | ⚠️ | Áreas que necesitan atención |
| 0-39 | CRÍTICO | 🚨 | Requiere atención inmediata |

**Factores que afectan el score:**
- ❌ Categoría con >50% de gastos: -15 puntos
- ❌ Categoría con >40% de gastos: -10 puntos
- ❌ Muchos gastos atípicos: -5 a -10 puntos
- ❌ Aumento de gastos >30%: -15 puntos
- ✅ Reducción de gastos >10%: +10 puntos
- ✅ Buen historial de registros: +5 puntos

---

## 📈 Tipos de Gráficos Disponibles

| Gráfico | Tipo | Descripción |
|---------|------|-------------|
| `pie_categorias` | Pastel | Distribución de gastos por categoría |
| `bar_meses` | Barras | Gastos totales por mes |
| `line_tendencia` | Línea | Tendencia de gastos últimos 30 días |
| `bar_dias_semana` | Barras | Gastos por día de la semana |
| `heatmap_calendario` | Heatmap | Calendario de calor de gastos |
| `stacked_categorias_mes` | Barras apiladas | Categorías por mes |
| `top_gastos` | Lista | Top 5 gastos más grandes |

---

## 🔄 Flujo Completo para App Flutter

### Paso 1: Obtener Token
```
POST /api/v2/auth/token
Body: {"user_id": "BCc7NaZ4KQTqFY3dUxgStWH62dh2"}
```

### Paso 2: Llamar al Asesor Financiero
```
GET /api/v2/firebase/users/BCc7NaZ4KQTqFY3dUxgStWH62dh2/asesor-financiero
Headers: Authorization: Bearer {token}
```

### Paso 3: Usar los datos en Flutter
```dart
// Ejemplo en Flutter
final response = await http.get(
  Uri.parse('$baseUrl/api/v2/firebase/users/$userId/asesor-financiero'),
  headers: {'Authorization': 'Bearer $token'},
);

final data = jsonDecode(response.body);
final score = data['score_financiero']['score'];
final prediccion = data['predicciones']['proximo_mes']['estimacion_ajustada'];
final tips = data['recomendaciones']['tips_personalizados'];
```

---

## ⚡ Resumen de Todos los Endpoints Firebase

| Endpoint | Método | Token | Descripción |
|----------|--------|-------|-------------|
| `/api/v2/firebase/debug` | GET | ❌ | Verificar conexión |
| `/api/v2/firebase/usuarios` | GET | ❌ | Listar usuarios |
| `/api/v2/firebase/usuarios/{id}` | GET | ❌ | Ver usuario |
| `/api/v2/firebase/users/{id}/gastos` | GET | ❌ | Ver gastos |
| `/api/v2/firebase/users/{id}/gastos` | POST | ✅ | Crear gasto |
| `/api/v2/firebase/users/{id}/gastos-ids` | GET | ❌ | Solo IDs |
| `/api/v2/firebase/users/{id}/gastos-procesados` | GET | ✅ | Análisis básico |
| `/api/v2/firebase/users/{id}/asesor-financiero` | GET | ✅ | **🤖 ASESOR COMPLETO** |
| `/api/v2/firebase/users/{id}/predicciones` | GET | ✅ | Solo predicciones |
| `/api/v2/firebase/users/{id}/analisis` | GET | ✅ | Solo estadísticas |
| `/api/v2/firebase/users/{id}/recomendaciones` | GET | ✅ | Solo consejos |
| `/api/v2/firebase/users/{id}/graficos` | GET | ✅ | Solo gráficos |
| `/api/v2/firebase/users/{id}/score` | GET | ✅ | Solo score |
