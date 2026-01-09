# 📖 Guía de Ejemplos - API Gestor Financiero IA

Esta guía proporciona ejemplos claros y detallados para usar todos los endpoints de la API.

## 🔐 1. Autenticación

### 1.1 Obtener Token JWT

**Endpoint:** `POST /api/v2/auth/token`

**No requiere autenticación**

```bash
# Ejemplo con curl
curl -X POST https://api-google-colab.onrender.com/api/v2/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "abc123xyz789"
  }'
```

**Request Body:**
```json
{
  "user_id": "abc123xyz789"
}
```

**Response:**
```json
{
  "status": "success",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expires_in": 86400,
  "message": "Token generado para abc123xyz789. Válido por 24 horas",
  "instrucciones": "Usar en headers: Authorization: Bearer <token> o X-API-Key: <token>",
  "user_id": "abc123xyz789"
}
```

### 1.2 Usar el Token

Una vez obtenido el token, inclúyelo en TODOS los requests posteriores:

```bash
# Opción 1: Authorization header (Recomendado)
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

# Opción 2: X-API-Key header
X-API-Key: eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## 📊 2. Predicción de Gastos

### 2.1 Predicción por Categoría

**Endpoint:** `POST /api/v2/predict-category`

Predice gastos separados para cada categoría para los próximos 30 días.

#### Opción A: Usar datos de Firebase (Recomendado)

```bash
curl -X POST https://api-google-colab.onrender.com/api/v2/predict-category \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{}'
```

La API automáticamente obtiene los gastos del usuario autenticado desde Firebase.

#### Opción B: Enviar gastos manualmente

```bash
curl -X POST https://api-google-colab.onrender.com/api/v2/predict-category \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "expenses": [
      {"fecha": "2026-01-08", "monto": 95.50, "categoria": "Comida"},
      {"fecha": "2026-01-08", "monto": 42.00, "categoria": "Transporte"},
      {"fecha": "2026-01-07", "monto": 180.00, "categoria": "Comida"},
      {"fecha": "2026-01-07", "monto": 35.00, "categoria": "Transporte"},
      {"fecha": "2026-01-06", "monto": 250.00, "categoria": "Entretenimiento"}
    ]
  }'
```

**Formato del Array `expenses`:**
- **fecha** (string, requerido): Formato "YYYY-MM-DD" (ej: "2026-01-08")
- **monto** (number, requerido): Número positivo (ej: 150.50)
- **categoria** (string, requerido): Nombre de la categoría (ej: "Comida", "Transporte")
- **descripcion** (string, opcional): Descripción del gasto

**Response:**
```json
{
  "status": "success",
  "message": "Predicción por categoría generada exitosamente para los próximos 30 días",
  "data": {
    "Comida": {
      "predicciones": [
        {"fecha": "2026-01-10", "monto": 85.50, "dia_semana": "Viernes"},
        {"fecha": "2026-01-11", "monto": 92.30, "dia_semana": "Sábado"}
      ],
      "total": 2556.00,
      "promedio_diario": 85.20,
      "dias": 30
    },
    "Transporte": {
      "predicciones": [
        {"fecha": "2026-01-10", "monto": 35.00, "dia_semana": "Viernes"}
      ],
      "total": 945.00,
      "promedio_diario": 31.50,
      "dias": 30
    }
  }
}
```

### 2.2 Detección de Anomalías

**Endpoint:** `POST /api/v2/detect-anomalies`

Detecta gastos anómalos usando Z-Score e Isolation Forest.

```bash
curl -X POST https://api-google-colab.onrender.com/api/v2/detect-anomalies \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "status": "success",
  "message": "Análisis de anomalías completado usando Z-Score e Isolation Forest",
  "data": {
    "cantidad": 4,
    "total_gastos": 76,
    "porcentaje": 5.26,
    "anomalias": [
      {
        "fecha": "2026-01-05",
        "monto": 850.00,
        "categoria": "Compras",
        "descripcion": "Compra de electrodoméstico",
        "metodo": "Z-Score",
        "razon": "Desviación 3.45σ del promedio (promedio: 145.50, desv: 204.35)",
        "z_score": 3.45
      },
      {
        "fecha": "2025-12-28",
        "monto": 1250.00,
        "categoria": "Salud",
        "descripcion": "Consulta médica especializada",
        "metodo": "Isolation Forest",
        "razon": "Gasto atípico detectado por ML",
        "anomaly_score": -0.42
      }
    ],
    "estadisticas": {
      "promedio_general": 145.50,
      "mediana": 89.30,
      "desviacion_estandar": 204.35
    }
  }
}
```

---

## 📈 3. Análisis Estadístico

### 3.1 Clustering de Gastos

**Endpoint:** `POST /api/v2/stat/clustering`

Agrupa automáticamente gastos similares usando K-Means.

```bash
curl -X POST https://api-google-colab.onrender.com/api/v2/stat/clustering \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "n_clusters": 3
  }'
```

**Parámetros:**
- **n_clusters** (integer, opcional): Número de grupos a identificar
  - Default: 3
  - Recomendado: 3-5 clusters
  - Más clusters = patrones más específicos

**Ejemplos de uso:**

```json
// 3 clusters (default) - Grupos generales
{"n_clusters": 3}

// 5 clusters - Patrones más específicos
{"n_clusters": 5}

// Con expenses manual
{
  "n_clusters": 4,
  "expenses": [
    {"fecha": "2026-01-08", "monto": 45.00, "categoria": "Comida"},
    {"fecha": "2026-01-08", "monto": 35.00, "categoria": "Transporte"}
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Clustering completado. Se identificaron 3 grupos de gastos con patrones similares",
  "data": {
    "n_clusters": 3,
    "clusters": {
      "0": {
        "nombre": "Gastos Pequeños Diarios",
        "descripcion": "Gastos frecuentes de bajo monto",
        "cantidad": 28,
        "promedio_monto": 45.30,
        "categorias_principales": ["Comida", "Transporte"],
        "ejemplos": [
          {"fecha": "2026-01-08", "monto": 42.50, "categoria": "Comida"}
        ]
      },
      "1": {
        "nombre": "Gastos Medianos Semanales",
        "cantidad": 15,
        "promedio_monto": 185.60
      }
    }
  }
}
```

---

## 💡 4. Recomendaciones de Ahorro

### 4.1 Metas de Ahorro

**Endpoint:** `POST /api/v2/savings/goals`

Calcula metas de ahorro personalizadas basadas en objetivos específicos.

```bash
curl -X POST https://api-google-colab.onrender.com/api/v2/savings/goals \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "goal_name": "Vacaciones en Europa",
    "target_amount": 8000,
    "months": 12
  }'
```

**Parámetros:**
- **goal_name** (string, opcional): Nombre de la meta
  - Default: "Meta general"
  - Ejemplos: "Vacaciones", "Auto usado", "Fondo emergencia"
- **target_amount** (number, opcional): Monto objetivo a ahorrar
  - Default: 5000
  - Debe ser número positivo
- **months** (integer, opcional): Plazo en meses para alcanzar la meta
  - Default: 12
  - Rango recomendado: 1-36 meses

**Ejemplos de Metas Comunes:**

```json
// Vacaciones
{
  "goal_name": "Vacaciones en Europa",
  "target_amount": 8000,
  "months": 12
}

// Compra de auto usado
{
  "goal_name": "Auto usado",
  "target_amount": 50000,
  "months": 24
}

// Fondo de emergencia (3 meses de gastos)
{
  "goal_name": "Fondo de emergencia",
  "target_amount": 15000,
  "months": 10
}

// Curso de capacitación
{
  "goal_name": "Curso online de programación",
  "target_amount": 1500,
  "months": 3
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Meta de ahorro calculada exitosamente",
  "data": {
    "meta": {
      "nombre": "Vacaciones en Europa",
      "monto_objetivo": 8000.00,
      "meses": 12,
      "ahorro_mensual_requerido": 666.67,
      "ahorro_semanal_requerido": 153.85,
      "ahorro_diario_requerido": 21.98
    },
    "analisis_actual": {
      "gasto_promedio_mensual": 4815.00,
      "capacidad_ahorro_actual": 1185.00
    },
    "viabilidad": {
      "es_alcanzable": true,
      "confianza": "Alta",
      "mensaje": "Tu meta es alcanzable. Necesitas ahorrar $666.67 mensuales"
    },
    "plan_accion": [
      {
        "accion": "Reducir gastos en Entretenimiento en 15%",
        "ahorro_estimado": 112.50
      }
    ]
  }
}
```

### 4.2 Alertas de Presupuesto

**Endpoint:** `POST /api/v2/savings/budget-alerts`

Genera alertas cuando se acerca o supera el presupuesto mensual.

```bash
curl -X POST https://api-google-colab.onrender.com/api/v2/savings/budget-alerts \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "monthly_budget": 5000
  }'
```

**Parámetros:**
- **monthly_budget** (number, opcional): Presupuesto mensual total
  - Default: 3000
  - La API compara tus gastos actuales contra este límite

**Ejemplos por Nivel de Presupuesto:**

```json
// Presupuesto ajustado
{"monthly_budget": 3000}

// Presupuesto medio
{"monthly_budget": 5000}

// Presupuesto holgado
{"monthly_budget": 8000}
```

**Response:**
```json
{
  "status": "success",
  "message": "Análisis de presupuesto completado",
  "data": {
    "presupuesto_mensual": 5000.00,
    "gasto_actual": 4815.00,
    "gasto_porcentaje": 96.30,
    "presupuesto_restante": 185.00,
    "dias_restantes_mes": 22,
    "alerta": {
      "nivel": "Crítico",
      "mensaje": "¡ALERTA! Has gastado el 96.3% de tu presupuesto",
      "recomendacion": "Reduce gastos inmediatamente"
    },
    "alertas_categoria": [
      {
        "categoria": "Comida",
        "presupuesto": 1500.00,
        "gastado": 2556.00,
        "porcentaje": 170.40,
        "estado": "Excedido",
        "exceso": 1056.00
      }
    ]
  }
}
```

---

## 🔥 5. Firebase Integration

### 5.1 Obtener Gastos del Usuario

**Endpoint:** `GET /api/v2/firebase/users/{usuario_id}/gastos`

```bash
curl -X GET https://api-google-colab.onrender.com/api/v2/firebase/users/abc123xyz789/gastos \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

**Response:**
```json
{
  "status": "success",
  "usuario_id": "abc123xyz789",
  "total": 47,
  "data": [
    {
      "id": "gasto_001",
      "fecha": "2026-01-08T14:30:00Z",
      "cantidad": 150.50,
      "categoria": "Comida",
      "descripcion": "Almuerzo restaurante"
    }
  ]
}
```

### 5.2 Crear Nuevo Gasto

**Endpoint:** `POST /api/v2/firebase/users/{usuario_id}/gastos`

```bash
curl -X POST https://api-google-colab.onrender.com/api/v2/firebase/users/abc123xyz789/gastos \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "categoria": "Comida",
    "cantidad": 150.50,
    "descripcion": "Almuerzo en restaurante italiano",
    "fecha": "2026-01-09T14:30:00Z"
  }'
```

**Campos del Request Body:**
- **categoria** (string, **REQUERIDO**): Categoría del gasto
  - Valores válidos: "Comida", "Transporte", "Entretenimiento", "Servicios", "Salud", "Educación", "Compras", "Vivienda", "Otros"
- **cantidad** (number, **REQUERIDO**): Monto del gasto
  - Debe ser un número positivo mayor a 0
- **descripcion** (string, opcional): Descripción detallada
  - Recomendado para mejor análisis
- **fecha** (string, opcional): Fecha y hora del gasto
  - Formato ISO 8601: "2026-01-09T14:30:00Z"
  - Si no se proporciona, se usa la fecha actual

**Ejemplos de Gastos:**

```json
// Gasto de comida
{
  "categoria": "Comida",
  "cantidad": 150.50,
  "descripcion": "Almuerzo en restaurante italiano",
  "fecha": "2026-01-09T14:30:00Z"
}

// Gasto de transporte
{
  "categoria": "Transporte",
  "cantidad": 35.00,
  "descripcion": "Uber del trabajo a casa",
  "fecha": "2026-01-09T19:15:00Z"
}

// Gasto de entretenimiento
{
  "categoria": "Entretenimiento",
  "cantidad": 280.00,
  "descripcion": "Cine IMAX con palomitas y bebidas",
  "fecha": "2026-01-08T21:00:00Z"
}

// Gasto mínimo (solo campos requeridos)
{
  "categoria": "Comida",
  "cantidad": 45.00
}
```

**Response Exitosa:**
```json
{
  "status": "success",
  "message": "Gasto registrado exitosamente en Firebase",
  "gasto_id": "gasto_abc123xyz789_20260109_143000",
  "data": {
    "id": "gasto_abc123xyz789_20260109_143000",
    "categoria": "Comida",
    "cantidad": 150.50,
    "descripcion": "Almuerzo en restaurante italiano",
    "fecha": "2026-01-09T14:30:00Z",
    "usuario_id": "abc123xyz789",
    "timestamp": "2026-01-09T14:30:15.234Z"
  }
}
```

**Response Error:**
```json
{
  "status": "error",
  "error": "La cantidad debe ser un número positivo mayor a 0"
}
```

### 5.3 Asesor Financiero IA (Análisis Completo)

**Endpoint:** `GET /api/v2/firebase/users/{usuario_id}/asesor-financiero`

Devuelve análisis integral del usuario con IA.

```bash
curl -X GET https://api-google-colab.onrender.com/api/v2/firebase/users/abc123xyz789/asesor-financiero \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

**Response:**
```json
{
  "status": "success",
  "usuario_id": "abc123xyz789",
  "data": {
    "predicciones": { /* Predicciones de gastos futuros */ },
    "analisis": { /* Análisis estadístico completo */ },
    "recomendaciones": { /* Recomendaciones personalizadas */ },
    "graficos": { /* Datos para visualización */ },
    "score": { /* Puntuación de salud financiera */ }
  }
}
```

---

## 📝 Notas Importantes

### Formato de Arrays `expenses`

Cuando envíes un array de gastos manualmente, asegúrate de:

1. **Formato correcto de fecha**: "YYYY-MM-DD" (ej: "2026-01-08")
2. **Monto como número**: No uses comillas (correcto: 150.50, incorrecto: "150.50")
3. **Categorías consistentes**: Usa nombres consistentes (ej: "Comida", no "comida" o "COMIDA")
4. **Mínimo de datos**: Para análisis preciso, envía al menos 30 gastos
5. **Descripción opcional**: Ayuda al análisis pero no es obligatoria

### Ejemplo de Array Completo

```json
{
  "expenses": [
    {"fecha": "2026-01-08", "monto": 95.50, "categoria": "Comida", "descripcion": "Desayuno"},
    {"fecha": "2026-01-08", "monto": 42.00, "categoria": "Transporte", "descripcion": "Metro"},
    {"fecha": "2026-01-07", "monto": 180.00, "categoria": "Comida", "descripcion": "Cena"},
    {"fecha": "2026-01-07", "monto": 35.00, "categoria": "Transporte", "descripcion": "Uber"},
    {"fecha": "2026-01-06", "monto": 250.00, "categoria": "Entretenimiento", "descripcion": "Cine"},
    {"fecha": "2026-01-06", "monto": 68.50, "categoria": "Comida", "descripcion": "Almuerzo"},
    {"fecha": "2026-01-05", "monto": 850.00, "categoria": "Compras", "descripcion": "Electrodoméstico"},
    {"fecha": "2026-01-05", "monto": 125.00, "categoria": "Comida", "descripcion": "Supermercado"}
  ]
}
```

### Códigos de Error Comunes

- **401 Unauthorized**: Token inválido o expirado - Obtén un nuevo token
- **400 Bad Request**: Datos inválidos - Verifica el formato del request
- **404 Not Found**: Usuario no encontrado en Firebase
- **500 Internal Server Error**: Error del servidor - Contacta soporte

---

## 🚀 Flujo de Trabajo Recomendado

1. **Obtener token** → `POST /api/v2/auth/token`
2. **Verificar conexión** → `GET /api/v2/health`
3. **Crear/obtener gastos** → `POST /api/v2/firebase/users/{id}/gastos`
4. **Análisis completo** → `GET /api/v2/firebase/users/{id}/asesor-financiero`
5. **Análisis específicos** según necesidad

---

Para más información, visita la documentación interactiva en:
**https://api-google-colab.onrender.com/docs**
