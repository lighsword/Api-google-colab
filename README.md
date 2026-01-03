# API Mejorada con 20+ Características de IA

API Flask con machine learning para análisis de gastos, predicciones y recomendaciones de ahorro. Integrada con Firebase Firestore.

## 🔥 Estructura Firebase (Firestore)

La API respeta las siguientes reglas de seguridad:

```
users/{userId}                    ← Documento del usuario
  └── gastos/{gastoId}           ← Subcolección de gastos
  └── presupuestos/{presupuestoId} ← Subcolección de presupuestos (futuro)
```

**Path principal usado:** `users/{userId}/gastos`

---

## 🚀 Instalación local

```bash
# 1. Clonar repositorio
git clone <tu-repo>
cd "Api google colab"

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Crear archivo .env
cp .env.example .env

# 6. Ejecutar la API
python API_MEJORADA.py
```

La API estará disponible en `http://localhost:5000`

---

## 🌐 Deploy en Render

1. Pushea el código a GitHub
2. Ve a [render.com](https://render.com)
3. Conecta tu repositorio
4. Crea un "Web Service":
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `gunicorn API_MEJORADA:app`
5. Configura variables de entorno en Render:
   - `SECRET_KEY`: Tu clave secreta
   - `FLASK_ENV`: `production`
   - `PORT`: `5000`
   - Variables Firebase (si usas credenciales por env)

---

## 📊 TODOS LOS ENDPOINTS PARA POSTMAN

### 🔐 Autenticación

#### 1. Obtener Token JWT
```
POST /api/v2/auth/token
```
**Headers:** `Content-Type: application/json`

**Body JSON:**
```json
{
  "user_id": "mi_usuario_123"
}
```

**Respuesta:**
```json
{
  "status": "success",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400
}
```

---

#### 2. Validar Token
```
POST /api/v2/auth/validate
```
**Headers:** 
- `Authorization: Bearer <tu_token>` o
- `X-API-Key: <tu_token>`

**Body:** *(vacío, no requiere JSON)*

**Respuesta:**
```json
{
  "valid": true,
  "message": "Token válido"
}
```

---

### 🏥 Health Check

#### 3. Estado del servidor
```
GET /api/v2/health
```
**Headers:** Ninguno requerido

**Body:** *(no aplica)*

**Respuesta:**
```json
{
  "status": "healthy",
  "firebase": true,
  "version": "2.0"
}
```

---

### 🔥 Firebase - Usuarios y Gastos

#### 4. Debug Firebase
```
GET /api/v2/firebase/debug
```
**Headers:** Ninguno

**Body:** *(no aplica)*

---

#### 5. Listar usuarios
```
GET /api/v2/firebase/usuarios
```
**Headers:** Ninguno

**Body:** *(no aplica)*

---

#### 6. Obtener usuario específico
```
GET /api/v2/firebase/usuarios/{usuario_id}
```
**Ejemplo:** `/api/v2/firebase/usuarios/abc123xyz`

**Headers:** Ninguno

**Body:** *(no aplica)*

---

#### 7. Obtener gastos de un usuario
```
GET /api/v2/firebase/users/{usuario_id}/gastos
```
**Ejemplo:** `/api/v2/firebase/users/abc123xyz/gastos`

**Query params opcionales:** `?ids_only=true`

**Headers:** Ninguno

**Body:** *(no aplica)*

**Respuesta:**
```json
{
  "status": "success",
  "usuario_id": "abc123xyz",
  "total_gastos": 5,
  "path_usado": "users/abc123xyz/gastos",
  "data": [
    {"id": "gasto1", "cantidad": 50, "categoria": "Comida", "fecha": "2025-12-01"}
  ]
}
```

---

#### 8. Obtener solo IDs de gastos
```
GET /api/v2/firebase/users/{usuario_id}/gastos-ids
```
**Headers:** Ninguno

**Body:** *(no aplica)*

**Respuesta:**
```json
{
  "status": "success",
  "ids": ["gasto1", "gasto2", "gasto3"]
}
```

---

#### 9. Obtener gastos procesados con IA
```
GET /api/v2/firebase/users/{usuario_id}/gastos-procesados
```
**Headers:** 
- `Authorization: Bearer <tu_token>`

**Body:** *(no aplica)*

**Respuesta:**
```json
{
  "status": "success",
  "total_gastos": 10,
  "gasto_total": 500.0,
  "promedio_gasto": 50.0,
  "resumen_por_categoria": {...}
}
```

---

#### 10. Crear nuevo gasto
```
POST /api/v2/firebase/users/{usuario_id}/gastos
```
**Headers:** 
- `Authorization: Bearer <tu_token>`
- `Content-Type: application/json`
- *(Opcional)* `X-Firebase-Id-Token: <firebase_id_token>`

**Body JSON:**
```json
{
  "cantidad": 150.50,
  "categoria": "Alimentación",
  "descripcion": "Compras del supermercado",
  "fecha": "2025-12-15"
}
```

**Respuesta:**
```json
{
  "status": "success",
  "mensaje": "Gasto creado correctamente",
  "gasto_id": "abc123def456",
  "path_usado": "users/abc123xyz/gastos/abc123def456"
}
```

---

### 📈 Predicciones (requieren token + expenses)

**Headers comunes para todos:**
- `Authorization: Bearer <tu_token>`
- `Content-Type: application/json`

**Body JSON común:**
```json
{
  "expenses": [
    {"fecha": "2025-11-01", "monto": 50, "categoria": "Comida"},
    {"fecha": "2025-11-02", "monto": 30, "categoria": "Transporte"},
    {"fecha": "2025-11-03", "monto": 100, "categoria": "Comida"},
    {"fecha": "2025-11-05", "monto": 25, "categoria": "Transporte"},
    {"fecha": "2025-11-10", "monto": 80, "categoria": "Entretenimiento"},
    {"fecha": "2025-11-15", "monto": 200, "categoria": "Comida"},
    {"fecha": "2025-11-20", "monto": 45, "categoria": "Transporte"}
  ]
}
```

#### 11. Predicción por categoría
```
POST /api/v2/predict-category
```

#### 12. Predicción mensual
```
POST /api/v2/predict-monthly
```

#### 13. Detección de anomalías
```
POST /api/v2/detect-anomalies
```

#### 14. Comparación de modelos
```
POST /api/v2/compare-models
```

#### 15. Análisis de estacionalidad
```
POST /api/v2/seasonality
```

#### 16. Análisis completo
```
POST /api/v2/analysis-complete
```

---

### 📊 Análisis Estadístico (requieren token + expenses)

**Headers:** `Authorization: Bearer <tu_token>`, `Content-Type: application/json`

**Body JSON:** (mismo formato de expenses que arriba)

#### 17. Correlaciones
```
POST /api/v2/stat/correlations
```

#### 18. Comparación temporal
```
POST /api/v2/stat/temporal-comparison
```

#### 19. Clustering (agrupamiento)
```
POST /api/v2/stat/clustering
```

#### 20. Tendencias
```
POST /api/v2/stat/trends
```

#### 21. Detección de outliers
```
POST /api/v2/stat/outliers
```

#### 22. Análisis estadístico completo
```
POST /api/v2/stat/complete
```

---

### 💰 Recomendaciones de Ahorro (requieren token + expenses)

**Headers:** `Authorization: Bearer <tu_token>`, `Content-Type: application/json`

**Body JSON:** (mismo formato de expenses)

#### 23. Metas de ahorro
```
POST /api/v2/savings/goals
```
**Body adicional opcional:**
```json
{
  "expenses": [...],
  "savings_goal": 500,
  "monthly_income": 3000
}
```

#### 24. Tips personalizados
```
POST /api/v2/savings/tips
```

#### 25. Alertas de presupuesto
```
POST /api/v2/savings/budget-alerts
```
**Body adicional opcional:**
```json
{
  "expenses": [...],
  "budget_limits": {
    "Comida": 300,
    "Transporte": 150,
    "Entretenimiento": 100
  }
}
```

#### 26. Puntuación de salud financiera
```
POST /api/v2/savings/health-score
```

#### 27. Reporte semanal
```
POST /api/v2/savings/weekly-report
```

#### 28. Análisis de ahorro completo
```
POST /api/v2/savings/complete
```

---

### 📉 Gráficos (requieren token + expenses)

**Headers:** `Authorization: Bearer <tu_token>`, `Content-Type: application/json`

**Body JSON:** (mismo formato de expenses)

#### 29. Mapa de calor
```
POST /api/v2/charts/heatmap
```

#### 30. Diagrama Sankey
```
POST /api/v2/charts/sankey
```

#### 31. Dashboard completo
```
POST /api/v2/charts/dashboard
```

#### 32. Gráficos comparativos
```
POST /api/v2/charts/comparison
```

#### 33. Exportar gráficos
```
POST /api/v2/charts/export
```
**Body adicional:**
```json
{
  "expenses": [...],
  "format": "png"
}
```

#### 34. Todos los gráficos
```
POST /api/v2/charts/complete
```

---

## 🔑 Resumen de Autenticación

| Endpoint | Token JWT | Body JSON |
|----------|-----------|-----------|
| `/auth/token` | ❌ No | `{"user_id": "..."}` |
| `/auth/validate` | ✅ Header | *(vacío)* |
| `/health` | ❌ No | *(no aplica)* |
| `/firebase/debug` | ❌ No | *(no aplica)* |
| `/firebase/usuarios` | ❌ No | *(no aplica)* |
| `/firebase/usuarios/{id}` | ❌ No | *(no aplica)* |
| `/firebase/users/{id}/gastos` GET | ❌ No | *(no aplica)* |
| `/firebase/users/{id}/gastos` POST | ✅ Header | `{"cantidad":..., "categoria":...}` |
| `/firebase/users/{id}/gastos-procesados` | ✅ Header | *(no aplica)* |
| Todos `/predict-*`, `/stat/*`, `/savings/*`, `/charts/*` | ✅ Header | `{"expenses": [...]}` |

---

## 📝 Ejemplo completo en Python

```python
import requests

BASE_URL = 'http://localhost:5000'

# 1. Obtener token
response = requests.post(f'{BASE_URL}/api/v2/auth/token', 
  json={'user_id': 'usuario1'})
token = response.json()['token']
headers = {'Authorization': f'Bearer {token}'}

# 2. Crear un gasto en Firebase
gasto = {
  'cantidad': 75.50,
  'categoria': 'Restaurante',
  'descripcion': 'Cena con amigos'
}
response = requests.post(
  f'{BASE_URL}/api/v2/firebase/users/usuario1/gastos',
  json=gasto, 
  headers=headers
)
print(response.json())

# 3. Obtener gastos
response = requests.get(
  f'{BASE_URL}/api/v2/firebase/users/usuario1/gastos'
)
print(response.json())

# 4. Hacer predicción con datos
data = {
  'expenses': [
    {'fecha': '2025-12-01', 'monto': 50, 'categoria': 'Comida'},
    {'fecha': '2025-12-02', 'monto': 30, 'categoria': 'Transporte'},
    {'fecha': '2025-12-03', 'monto': 100, 'categoria': 'Comida'}
  ]
}
response = requests.post(
  f'{BASE_URL}/api/v2/predict-category',
  json=data, 
  headers=headers
)
print(response.json())
```

---

## 📦 Dependencias

- Flask: Framework web
- pandas, numpy: Procesamiento de datos
- scikit-learn: Machine learning
- PyJWT: Autenticación JWT
- firebase-admin: Integración con Firebase
- gunicorn: Servidor WSGI para producción

## 📄 Licencia

MIT
