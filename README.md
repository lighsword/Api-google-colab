# 🚀 Gestor Financiero IA - API REST

API avanzada con **20 características de Inteligencia Artificial** para gestión financiera personal.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Firebase](https://img.shields.io/badge/Firebase-Ready-orange.svg)](https://firebase.google.com/)
[![Machine Learning](https://img.shields.io/badge/ML-Enabled-red.svg)](https://scikit-learn.org/)

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Instalación](#-instalación)
- [Autenticación](#-autenticación)
- [Endpoints](#-endpoints)
  - [🔐 Autenticación](#-autenticación-1)
  - [📊 Predicción de Gastos](#-predicción-de-gastos-5-endpoints)
  - [📈 Análisis Estadístico](#-análisis-estadístico-6-endpoints)
  - [💡 Recomendaciones de Ahorro](#-recomendaciones-de-ahorro-6-endpoints)
  - [📊 Gráficos y Visualización](#-gráficos-y-visualización-6-endpoints)
  - [🔥 Firebase Integration](#-firebase-integration)
  - [🤖 Asesor Financiero IA](#-asesor-financiero-ia)
- [Ejemplos de Uso](#-ejemplos-de-uso)
- [Modelos de Datos](#-modelos-de-datos)

---

## 🎯 Características

### 📊 PREDICCIÓN DE GASTOS (5 mejoras)
1. **Predicción por categoría** - Predicciones separadas para cada categoría de gasto
2. **Predicción mensual** - Proyección de gastos para los próximos 30 días con intervalos de confianza
3. **Detección de anomalías** - Identificación automática de gastos inusuales usando Z-Score e Isolation Forest
4. **Múltiples modelos ML** - Comparación entre RandomForest, ARIMA, Prophet y LSTM
5. **Análisis de estacionalidad** - Detección de patrones semanales y mensuales

### 📈 ANÁLISIS ESTADÍSTICO (5 mejoras)
6. **Correlaciones entre categorías** - Análisis de relaciones entre diferentes tipos de gastos
7. **Análisis temporal** - Comparación mes actual vs mes anterior
8. **Clustering automático** - Agrupamiento inteligente de gastos similares
9. **Detección de tendencias** - Identificación de patrones ascendentes o descendentes
10. **Identificación de outliers** - Detección de gastos atípicos usando IQR + Z-Score

### 💡 RECOMENDACIONES DE AHORRO (5 mejoras)
11. **Metas de ahorro** - Objetivos específicos con planes de ahorro personalizados
12. **Tips personalizados** - Recomendaciones basadas en patrones de comportamiento
13. **Alertas de presupuesto** - Notificaciones cuando se acerca o supera límites mensuales
14. **Gamificación** - Puntuación de salud financiera (0-100 puntos)
15. **Reportes automáticos** - Resúmenes semanales de actividad financiera

### 📊 GRÁFICOS Y VISUALIZACIÓN (5 mejoras)
16. **Calendario de calor** - Heatmap de gastos diarios
17. **Gráfico Sankey** - Visualización del flujo de dinero entre categorías
18. **Dashboard interactivo** - Panel con múltiples métricas y filtros
19. **Comparativas** - Gráficos de mes vs mes anterior
20. **Exportar como imagen** - Descarga de gráficos en PNG/PDF

---

## 🛠️ Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Firebase Admin SDK (opcional, para integración con Firebase)

### Pasos de Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/tu-usuario/api-gestor-financiero.git
cd api-gestor-financiero
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno:**

Crear archivo `.env` en la raíz del proyecto:
```env
SECRET_KEY=tu_clave_secreta_super_segura_2024
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=tu-proyecto-firebase
FIREBASE_PRIVATE_KEY_ID=tu_private_key_id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nTU_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@tu-proyecto.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=tu_client_id
FIRESTORE_DATABASE_ID=gestofin
```

4. **Ejecutar la API:**
```bash
python API_MEJORADA.py
```

La API estará disponible en: `http://localhost:5000`

---

## 🔐 Autenticación

Todos los endpoints (excepto `/auth/token` y `/health`) requieren autenticación mediante JWT.

### Paso 1: Obtener Token

**Endpoint:** `POST https://tu-api.com/api/v2/auth/token`

**Request:**
```json
{
  "user_id": "usuario123"
}
```

**Response:**
```json
{
  "status": "success",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expires_in": 86400,
  "message": "Token generado para usuario123. Válido por 24 horas",
  "instrucciones": "Usar en headers: Authorization: Bearer <token> o X-API-Key: <token>"
}
```

### Paso 2: Usar Token en Requests

Incluir en los headers de todas las peticiones:

**Opción 1 (Recomendada):**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Opción 2:**
```
X-API-Key: eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## 📡 Endpoints

### 🔐 Autenticación

#### 1. Generar Token JWT

**Endpoint:** `POST https://tu-api.com/api/v2/auth/token`

**Requiere autenticación:** ❌ No

**Parámetros:**
- `user_id` (string, opcional): ID del usuario. Default: "default_user"

**Respuesta:**
```json
{
  "status": "success",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "expires_in": 86400,
  "message": "Token generado para usuario123. Válido por 24 horas"
}
```

---

#### 2. Validar Token

**Endpoint:** `POST https://tu-api.com/api/v2/auth/validate`

**Requiere autenticación:** ❌ No (pero requiere token en headers)

**Respuesta:**
```json
{
  "valid": true,
  "message": "Token válido"
}
```

---

#### 3. Estado de la API

**Endpoint:** `GET https://tu-api.com/api/v2/health`

**Requiere autenticación:** ❌ No

**Respuesta:**
```json
{
  "status": "ok",
  "timestamp": "2024-12-15T10:30:00",
  "firebase": true,
  "modelos_disponibles": {
    "arima": true,
    "prophet": true,
    "lstm": false
  }
}
```

---

### 📊 Predicción de Gastos (5 endpoints)

#### 1. Predicción por Categoría

**Endpoint:** `POST https://tu-api.com/api/v2/predict-category`

**Requiere autenticación:** ✅ Sí

**Parámetros:**
- `expenses` (array, opcional): Lista de gastos. Si se omite, se obtienen de Firebase.

**Ejemplo Request:**
```json
{
  "expenses": [
    {"fecha": "2024-12-01", "monto": 50, "categoria": "Comida"},
    {"fecha": "2024-12-02", "monto": 30, "categoria": "Transporte"},
    {"fecha": "2024-12-03", "monto": 100, "categoria": "Comida"}
  ]
}
```

**Ejemplo Response:**
```json
{
  "status": "success",
  "data": {
    "Comida": {
      "predicciones": [
        {"fecha": "2024-12-16", "monto": 85.50},
        {"fecha": "2024-12-17", "monto": 92.30}
      ],
      "total": 2556.00,
      "promedio_diario": 85.20
    },
    "Transporte": {
      "predicciones": [
        {"fecha": "2024-12-16", "monto": 35.00}
      ],
      "total": 1050.00,
      "promedio_diario": 35.00
    }
  }
}
```

---

#### 2. Predicción Mensual (30 días)

**Endpoint:** `POST https://tu-api.com/api/v2/predict-monthly`

**Requiere autenticación:** ✅ Sí

**Parámetros:**
- `expenses` (array, opcional): Lista de gastos

**Ejemplo Response:**
```json
{
  "status": "success",
  "data": {
    "diarias": [
      {
        "fecha": "2024-12-16",
        "dia_semana": "Monday",
        "semana": 1,
        "prediccion": 120.50,
        "min": 80.30,
        "max": 160.70
      }
    ],
    "total_mes": 3615.00,
    "promedio_diario": 120.50,
    "resumen_semanal": {
      "1": {
        "total": 843.50,
        "promedio_diario": 120.50
      }
    }
  }
}
```

---

#### 3. Detección de Anomalías

**Endpoint:** `POST https://tu-api.com/api/v2/detect-anomalies`

**Requiere autenticación:** ✅ Sí

**Parámetros:**
- `expenses` (array, opcional): Lista de gastos

**Ejemplo Response:**
```json
{
  "status": "success",
  "data": {
    "cantidad": 3,
    "anomalias": [
      {
        "fecha": "2024-12-10",
        "monto": 850.00,
        "categoria": "Compras",
        "metodo": "Z-Score",
        "razon": "Desviación 3.45σ del promedio"
      }
    ],
    "porcentaje": 5.26
  }
}
```

---

#### 4. Comparación de Modelos ML

**Endpoint:** `POST https://tu-api.com/api/v2/compare-models`

**Requiere autenticación:** ✅ Sí

**Parámetros:**
- `expenses` (array, opcional): Lista de gastos

**Ejemplo Response:**
```json
{
  "status": "success",
  "data": {
    "modelos": ["RandomForest", "ARIMA", "ExponentialSmoothing"],
    "resultados": {
      "RandomForest": {
        "mae": 15.32,
        "r2": 0.8756,
        "modelo": "RandomForest"
      },
      "ARIMA": {
        "mae": 18.45,
        "r2": 0.8234,
        "modelo": "ARIMA"
      }
    },
    "mejor": "RandomForest",
    "mejor_r2": 0.8756
  }
}
```

---

#### 5. Análisis de Estacionalidad

**Endpoint:** `POST https://tu-api.com/api/v2/seasonality`

**Requiere autenticación:** ✅ Sí

**Parámetros:**
- `expenses` (array, opcional): Lista de gastos

**Descripción:** Detecta patrones semanales y mensuales en los gastos.

---

#### 6. Análisis Completo de Predicción

**Endpoint:** `POST https://tu-api.com/api/v2/analysis-complete`

**Requiere autenticación:** ✅ Sí

**Descripción:** Ejecuta todas las 5 funcionalidades de predicción en un solo endpoint.

**Parámetros:**
- `expenses` (array, opcional): Lista de gastos

**Respuesta:** Objeto con todos los análisis de predicción combinados.

---

### 📈 Análisis Estadístico (6 endpoints)

#### 1. Correlaciones entre Categorías

**Endpoint:** `POST https://tu-api.com/api/v2/stat/correlations`

**Requiere autenticación:** ✅ Sí

**Descripción:** Analiza las correlaciones entre diferentes categorías de gastos.

---

#### 2. Comparación Temporal

**Endpoint:** `POST https://tu-api.com/api/v2/stat/temporal-comparison`

**Requiere autenticación:** ✅ Sí

**Descripción:** Compara gastos del mes actual vs mes anterior.

---

#### 3. Clustering de Gastos

**Endpoint:** `POST https://tu-api.com/api/v2/stat/clustering`

**Requiere autenticación:** ✅ Sí

**Parámetros:**
- `n_clusters` (integer, opcional): Número de clusters. Default: 3
- `expenses` (array, opcional): Lista de gastos

**Descripción:** Agrupa automáticamente gastos similares usando K-Means.

---

#### 4. Detección de Tendencias

**Endpoint:** `POST https://tu-api.com/api/v2/stat/trends`

**Requiere autenticación:** ✅ Sí

**Descripción:** Detecta tendencias en los patrones de gasto.

---

#### 5. Detección de Outliers

**Endpoint:** `POST https://tu-api.com/api/v2/stat/outliers`

**Requiere autenticación:** ✅ Sí

**Descripción:** Detecta gastos atípicos usando IQR y Z-Score.

---

#### 6. Análisis Estadístico Completo

**Endpoint:** `POST https://tu-api.com/api/v2/stat/complete`

**Requiere autenticación:** ✅ Sí

**Descripción:** Ejecuta todas las 5 funcionalidades de análisis estadístico en un solo endpoint.

---

### 💡 Recomendaciones de Ahorro (6 endpoints)

#### 1. Metas de Ahorro

**Endpoint:** `POST https://tu-api.com/api/v2/savings/goals`

**Requiere autenticación:** ✅ Sí

**Parámetros:**
- `goal_name` (string, opcional): Nombre de la meta. Default: "Meta general"
- `target_amount` (number, opcional): Monto objetivo. Default: 5000
- `months` (integer, opcional): Meses para alcanzar la meta. Default: 12
- `expenses` (array, opcional): Lista de gastos

**Ejemplo Request:**
```json
{
  "goal_name": "Vacaciones",
  "target_amount": 5000,
  "months": 12
}
```

---

#### 2. Tips Personalizados

**Endpoint:** `POST https://tu-api.com/api/v2/savings/tips`

**Requiere autenticación:** ✅ Sí

**Descripción:** Genera tips de ahorro personalizados basados en patrones de gasto.

---

#### 3. Alertas de Presupuesto

**Endpoint:** `POST https://tu-api.com/api/v2/savings/budget-alerts`

**Requiere autenticación:** ✅ Sí

**Parámetros:**
- `monthly_budget` (number, opcional): Presupuesto mensual. Default: 3000
- `expenses` (array, opcional): Lista de gastos

**Descripción:** Genera alertas cuando se acerca o supera el presupuesto mensual.

---

#### 4. Puntuación de Salud Financiera

**Endpoint:** `POST https://tu-api.com/api/v2/savings/health-score`

**Requiere autenticación:** ✅ Sí

**Parámetros:**
- `monthly_budget` (number, opcional): Presupuesto mensual. Default: 3000
- `expenses` (array, opcional): Lista de gastos

**Descripción:** Calcula una puntuación de salud financiera (0-100 puntos).

---

#### 5. Reporte Semanal

**Endpoint:** `POST https://tu-api.com/api/v2/savings/weekly-report`

**Requiere autenticación:** ✅ Sí

**Descripción:** Genera un resumen automático de gastos de la última semana.

---

#### 6. Análisis Completo de Ahorro

**Endpoint:** `POST https://tu-api.com/api/v2/savings/complete`

**Requiere autenticación:** ✅ Sí

**Parámetros:**
- `goal_name`, `target_amount`, `months`, `monthly_budget`
- `expenses` (array, opcional): Lista de gastos

**Descripción:** Ejecuta todas las 5 funcionalidades de recomendaciones en un solo endpoint.

---

### 📊 Gráficos y Visualización (6 endpoints)

#### 1. Calendario de Calor (Heatmap)

**Endpoint:** `POST https://tu-api.com/api/v2/charts/heatmap`

**Requiere autenticación:** ✅ Sí

**Descripción:** Genera un calendario de calor de gastos diarios.

---

#### 2. Diagrama Sankey

**Endpoint:** `POST https://tu-api.com/api/v2/charts/sankey`

**Requiere autenticación:** ✅ Sí

**Descripción:** Genera un diagrama Sankey del flujo de dinero entre categorías.

---

#### 3. Dashboard Interactivo

**Endpoint:** `POST https://tu-api.com/api/v2/charts/dashboard`

**Requiere autenticación:** ✅ Sí

**Descripción:** Genera un dashboard interactivo con múltiples gráficos y métricas.

---

#### 4. Comparación Mensual

**Endpoint:** `POST https://tu-api.com/api/v2/charts/comparison`

**Requiere autenticación:** ✅ Sí

**Descripción:** Genera gráficos comparativos mes vs mes anterior.

---

#### 5. Exportar Gráficos

**Endpoint:** `POST https://tu-api.com/api/v2/charts/export`

**Requiere autenticación:** ✅ Sí

**Parámetros:**
- `format` (string, opcional): "json" o "base64". Default: "json"
- `expenses` (array, opcional): Lista de gastos

**Descripción:** Exporta gráficos como imágenes en formato JSON o BASE64.

---

#### 6. Todos los Gráficos

**Endpoint:** `POST https://tu-api.com/api/v2/charts/complete`

**Requiere autenticación:** ✅ Sí

**Descripción:** Genera todos los 5 tipos de gráficos en un solo endpoint.

---

### 🔥 Firebase Integration

#### 1. Obtener Gastos del Usuario

**Endpoint:** `GET https://tu-api.com/api/v2/firebase/users/{usuario_id}/gastos`

**Requiere autenticación:** ✅ Sí

**Parámetros:**
- `usuario_id` (path): ID del usuario en Firebase

**Descripción:** Obtiene todos los gastos registrados de un usuario desde Firebase.

---

#### 2. Crear Nuevo Gasto

**Endpoint:** `POST https://tu-api.com/api/v2/firebase/users/{usuario_id}/gastos`

**Requiere autenticación:** ✅ Sí

**Parámetros:**
- `usuario_id` (path): ID del usuario en Firebase

**Request Body:**
```json
{
  "categoria": "Comida",
  "cantidad": 150.50,
  "descripcion": "Almuerzo",
  "fecha": "2024-12-15T12:00:00"
}
```

**Descripción:** Crea un nuevo gasto en Firebase para el usuario especificado.

---

#### 3. Obtener Todos los Usuarios

**Endpoint:** `GET https://tu-api.com/api/v2/firebase/usuarios`

**Requiere autenticación:** ✅ Sí

**Descripción:** Obtiene todos los usuarios registrados en Firebase.

---

#### 4. Obtener Usuario Específico

**Endpoint:** `GET https://tu-api.com/api/v2/firebase/usuarios/{usuario_id}`

**Requiere autenticación:** ✅ Sí

**Parámetros:**
- `usuario_id` (path): ID del usuario en Firebase

**Descripción:** Obtiene información de un usuario específico.

---

### 🤖 Asesor Financiero IA

#### 1. Análisis Completo con IA

**Endpoint:** `GET https://tu-api.com/api/v2/firebase/users/{usuario_id}/asesor-financiero`

**Requiere autenticación:** ✅ Sí

**Parámetros:**
- `usuario_id` (path): ID del usuario en Firebase

**Descripción:** Devuelve análisis integral del usuario con IA incluyendo:
- Predicciones de gastos futuros (30 días)
- Análisis estadístico completo
- Recomendaciones personalizadas de ahorro
- Datos para gráficos

---

#### 2. Predicciones para Usuario

**Endpoint:** `GET https://tu-api.com/api/v2/firebase/users/{usuario_id}/predicciones`

**Requiere autenticación:** ✅ Sí

**Descripción:** Obtiene todas las predicciones de gastos para un usuario específico.

---

#### 3. Análisis Estadístico para Usuario

**Endpoint:** `GET https://tu-api.com/api/v2/firebase/users/{usuario_id}/analisis`

**Requiere autenticación:** ✅ Sí

**Descripción:** Obtiene análisis estadístico completo para un usuario específico.

---

#### 4. Recomendaciones para Usuario

**Endpoint:** `GET https://tu-api.com/api/v2/firebase/users/{usuario_id}/recomendaciones`

**Requiere autenticación:** ✅ Sí

**Descripción:** Obtiene recomendaciones personalizadas de ahorro para un usuario.

---

#### 5. Gráficos para Usuario

**Endpoint:** `GET https://tu-api.com/api/v2/firebase/users/{usuario_id}/graficos`

**Requiere autenticación:** ✅ Sí

**Descripción:** Genera todos los gráficos para un usuario específico.

---

#### 6. Puntuación Financiera del Usuario

**Endpoint:** `GET https://tu-api.com/api/v2/firebase/users/{usuario_id}/score`

**Requiere autenticación:** ✅ Sí

**Descripción:** Calcula la puntuación de salud financiera del usuario (0-100).

---

## 💻 Ejemplos de Uso

### Ejemplo 1: Flujo Completo con Postman

#### Paso 1: Obtener Token
```http
POST http://localhost:5000/api/v2/auth/token
Content-Type: application/json

{
  "user_id": "usuario123"
}
```

#### Paso 2: Usar Token para Predicciones
```http
POST http://localhost:5000/api/v2/predict-category
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "expenses": [
    {"fecha": "2024-12-01", "monto": 50, "categoria": "Comida"},
    {"fecha": "2024-12-02", "monto": 30, "categoria": "Transporte"},
    {"fecha": "2024-12-03", "monto": 100, "categoria": "Comida"}
  ]
}
```

---

### Ejemplo 2: Usar con cURL

```bash
# Obtener token
curl -X POST http://localhost:5000/api/v2/auth/token \
  -H "Content-Type: application/json" \
  -d '{"user_id": "usuario123"}'

# Usar token para obtener predicciones
curl -X POST http://localhost:5000/api/v2/predict-monthly \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"expenses": [...]}'
```

---

### Ejemplo 3: Usar con Python

```python
import requests

# Base URL
BASE_URL = "http://localhost:5000/api/v2"

# 1. Obtener token
response = requests.post(f"{BASE_URL}/auth/token", 
                        json={"user_id": "usuario123"})
token = response.json()["token"]

# 2. Headers con autenticación
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 3. Realizar predicciones
expenses_data = {
    "expenses": [
        {"fecha": "2024-12-01", "monto": 50, "categoria": "Comida"},
        {"fecha": "2024-12-02", "monto": 30, "categoria": "Transporte"}
    ]
}

response = requests.post(f"{BASE_URL}/predict-category", 
                        json=expenses_data, 
                        headers=headers)
predictions = response.json()
print(predictions)
```

---

### Ejemplo 4: Usar con JavaScript/Fetch

```javascript
// Base URL
const BASE_URL = 'http://localhost:5000/api/v2';

// 1. Obtener token
async function getToken() {
  const response = await fetch(`${BASE_URL}/auth/token`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({user_id: 'usuario123'})
  });
  const data = await response.json();
  return data.token;
}

// 2. Obtener predicciones
async function getPredictions() {
  const token = await getToken();
  
  const response = await fetch(`${BASE_URL}/predict-category`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      expenses: [
        {fecha: '2024-12-01', monto: 50, categoria: 'Comida'},
        {fecha: '2024-12-02', monto: 30, categoria: 'Transporte'}
      ]
    })
  });
  
  const predictions = await response.json();
  console.log(predictions);
}

getPredictions();
```

---

## 📦 Modelos de Datos

### Expense Object
```json
{
  "fecha": "2024-12-15",
  "monto": 150.50,
  "categoria": "Comida"
}
```

### Categorías Sugeridas
- Comida
- Transporte
- Entretenimiento
- Salud
- Educación
- Compras
- Servicios
- Vivienda
- Otros

---

## 🔧 Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `SECRET_KEY` | Clave secreta para JWT | ✅ |
| `FIREBASE_PROJECT_ID` | ID del proyecto Firebase | ⚠️ Si usas Firebase |
| `FIREBASE_PRIVATE_KEY` | Clave privada de Firebase | ⚠️ Si usas Firebase |
| `FIREBASE_CLIENT_EMAIL` | Email del service account | ⚠️ Si usas Firebase |
| `FIRESTORE_DATABASE_ID` | ID de la base de datos Firestore | ⚠️ Si usas Firebase |

---

## 📊 Swagger UI

La API incluye documentación interactiva Swagger UI disponible en:

```
http://localhost:5000/docs
```

Aquí puedes:
- Ver todos los endpoints
- Probar requests directamente desde el navegador
- Ver ejemplos de request/response
- Descargar la especificación OpenAPI

---

## 🚀 Deployment

### Deploy en Render

1. Crear cuenta en [Render](https://render.com)
2. Conectar tu repositorio de GitHub
3. Configurar variables de entorno
4. Deploy automático

### Deploy en Heroku

```bash
heroku create tu-api-financiera
git push heroku main
heroku config:set SECRET_KEY=tu_clave_secreta
```

---

## 📝 Notas Importantes

- **Tokens JWT:** Válidos por 24 horas. Generar nuevo token si expira.
- **Firebase:** Opcional. Si no se usa Firebase, enviar datos en el body de cada request.
- **Rate Limiting:** Se recomienda implementar rate limiting en producción.
- **HTTPS:** Usar siempre HTTPS en producción para proteger tokens.

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

---

## 📞 Soporte

Para preguntas o soporte:
- Email: soporte@gestor-financiero.com
- Issues: [GitHub Issues](https://github.com/tu-usuario/api-gestor-financiero/issues)

---

**Desarrollado con ❤️ usando Flask y Machine Learning**
