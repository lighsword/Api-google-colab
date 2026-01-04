# API Mejorada con 20+ Características de IA

API Flask con machine learning para análisis de gastos, predicciones y recomendaciones de ahorro. Integrada con Firebase Firestore.

---

## 📜 Swagger / OpenAPI

Esta API está documentada con OpenAPI 3.0 (Swagger) y organizada por módulos.

- Ver documentación completa: abre [swagger.yaml](swagger.yaml) en Swagger Editor (https://editor.swagger.io).
- Autenticación: muchas rutas requieren Bearer JWT. Primero consigue tu token.
- Módulos: Auth, Health, Firebase, Predictions, Statistics, Savings, Charts.

---

## 📘 Endpoints + Swagger (claros y breves)

A continuación, cada endpoint clave con su resumen y el fragmento Swagger que indica qué necesita y qué devuelve. La especificación completa está en [swagger.yaml](swagger.yaml).

### Auth

- Obtener token JWT: `POST /api/v2/auth/token`

```yaml
post:
  summary: Obtener token JWT
  tags: [Auth]
  requestBody:
    required: false
    content:
      application/json:
        schema:
          type: object
          properties:
            user_id:
              type: string
  responses:
    '200':
      description: Token generado
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/TokenResponse'
    '500':
      description: Error generando token
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
```

- Validar token: `POST /api/v2/auth/validate`

```yaml
post:
  summary: Validar token JWT
  tags: [Auth]
  responses:
    '200':
      description: Validación
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ValidateResponse'
```

### Firebase

- Listar gastos: `GET /api/v2/firebase/users/{usuario_id}/gastos`

```yaml
get:
  summary: Listar gastos de un usuario
  tags: [Firebase]
  parameters:
    - $ref: '#/components/parameters/UsuarioId'
    - in: query
      name: ids_only
      schema:
        type: string
        enum: [true, false]
  responses:
    '200': { description: Lista de gastos }
    '503': { description: Firebase no disponible }
```

- Crear gasto: `POST /api/v2/firebase/users/{usuario_id}/gastos` (requiere Bearer JWT)

```yaml
post:
  summary: Crear gasto para un usuario
  tags: [Firebase]
  security: [ { bearerAuth: [] } ]
  parameters:
    - $ref: '#/components/parameters/UsuarioId'
  requestBody:
    required: true
    content:
      application/json:
        schema:
          type: object
          required: [cantidad, categoria]
          properties:
            cantidad: { type: number }
            categoria: { type: string }
            descripcion: { type: string }
            fecha: { type: string }
  responses:
    '201':
      description: Gasto creado
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/StatusSuccess'
    '400': { description: Datos inválidos }
    '503': { description: Firebase no disponible }
```

### Predictions

- Predicción mensual: `GET /api/v2/firebase/users/{usuario_id}/predict-monthly` (Bearer JWT)

```yaml
get:
  summary: Predicción mensual (30 días)
  tags: [Predictions]
  security: [ { bearerAuth: [] } ]
  parameters:
    - $ref: '#/components/parameters/UsuarioId'
  responses:
    '200':
      description: OK
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/PredictionMonthly'
      examples:
        ejemplo:
          value:
            status: success
            data:
              diarias:
                - fecha: 2026-01-04
                  prediccion: 85.2
                  min: 70.0
                  max: 100.5
                  semana: 1
                  dia_semana: Monday
              total_mes: 2450.8
              promedio_diario: 81.7
              resumen_semanal:
                1: { total: 600.4, promedio_diario: 85.77 }
```

- Análisis completo: `GET /api/v2/firebase/users/{usuario_id}/analysis-complete` (Bearer JWT)

```yaml
get:
  summary: Análisis completo (predicciones)
  tags: [Predictions]
  security: [ { bearerAuth: [] } ]
  parameters:
    - $ref: '#/components/parameters/UsuarioId'
  responses:
    '200': { description: OK }
```

### Statistics

- Comparación temporal: `GET /api/v2/firebase/users/{usuario_id}/stat/temporal-comparison` (Bearer JWT)

```yaml
get:
  summary: Mes actual vs anterior
  tags: [Statistics]
  security: [ { bearerAuth: [] } ]
  parameters:
    - $ref: '#/components/parameters/UsuarioId'
  responses:
    '200': { description: OK }
```

- Outliers: `GET /api/v2/firebase/users/{usuario_id}/stat/outliers` (Bearer JWT)

```yaml
get:
  summary: Outliers (IQR + Z-Score)
  tags: [Statistics]
  security: [ { bearerAuth: [] } ]
  parameters:
    - $ref: '#/components/parameters/UsuarioId'
  responses:
    '200': { description: OK }
```

### Savings

- Ahorro completo: `GET /api/v2/firebase/users/{usuario_id}/savings/complete` (Bearer JWT)

```yaml
get:
  summary: Ahorro completo (todos módulos)
  tags: [Savings]
  security: [ { bearerAuth: [] } ]
  parameters:
    - $ref: '#/components/parameters/UsuarioId'
    - in: query
      name: goal_name
      schema: { type: string }
    - in: query
      name: target_amount
      schema: { type: number, default: 5000 }
    - in: query
      name: months
      schema: { type: integer, default: 12 }
    - in: query
      name: monthly_budget
      schema: { type: number, default: 3000 }
  responses:
    '200': { description: OK }
```

### Charts

- Exportar gráficos: `GET /api/v2/firebase/users/{usuario_id}/charts/export?format=json|base64` (Bearer JWT)

```yaml
get:
  summary: Exportar gráficos
  tags: [Charts]
  security: [ { bearerAuth: [] } ]
  parameters:
    - $ref: '#/components/parameters/UsuarioId'
    - in: query
      name: format
      schema: { type: string, enum: [json, base64], default: json }
  responses:
    '200':
      description: OK
      examples:
        json:
          value:
            formato: json
            graficos:
              - nombre: Pie Categorías
                json: '{...}'
        base64:
          value:
            formato: base64
            graficos:
              - nombre: Pie Categorías
                base64: iVBORw0KGgoAAA...
```

---

```yaml
openapi: 3.0.3
info:
  title: Gestor Financiero IA API
  version: "2.0"
  description: |
    API Flask con análisis de gastos, predicciones y recomendaciones de ahorro, integrada con Firebase Firestore.
    Autenticación vía JWT. Muchas rutas aceptan GET con query params para conveniencia.
servers:
  - url: http://localhost:5000
    description: Servidor local
  - url: https://your-render-service.onrender.com
    description: Producción (Render)
security:
  - bearerAuth: []
tags:
  - name: Auth
    description: Autenticación y validación de token JWT
  - name: Health
    description: Estado de la API
  - name: Firebase
    description: Lectura/escritura de datos en Firestore
  - name: Predictions
    description: Predicciones y análisis de gasto futuro
  - name: Statistics
    description: Análisis estadístico y detecciones
  - name: Savings
    description: Metas de ahorro, tips y salud financiera
  - name: Charts
    description: Gráficos y exportaciones
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  parameters:
    UsuarioId:
      in: path
      name: usuario_id
      required: true
      schema:
        type: string
      description: ID del usuario en Firestore (colección users)
paths:
  /api/v2/health:
    get:
      summary: Estado de la API
      tags: [Health]
      responses:
        '200':
          description: OK
  /api/v2/auth/token:
    post:
      summary: Obtener token JWT
      tags: [Auth]
      requestBody:
        required: false
        content:
          application/json:
            schema:
              type: object
              properties:
                user_id:
                  type: string
      responses:
        '200':
          description: Token generado
  /api/v2/auth/validate:
    post:
      summary: Validar token JWT
      tags: [Auth]
      responses:
        '200':
          description: Validación
  /api/v2/firebase/usuarios:
    get:
      summary: Listar usuarios (colección users)
      tags: [Firebase]
      responses:
        '200':
          description: Usuarios listados
  /api/v2/firebase/usuarios/{usuario_id}:
    get:
      summary: Obtener usuario con budget/current
      tags: [Firebase]
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      responses:
        '200':
          description: Usuario encontrado
  /api/v2/firebase/users/{usuario_id}/gastos:
    get:
      summary: Listar gastos de un usuario
      tags: [Firebase]
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
        - in: query
          name: ids_only
          schema:
            type: string
            enum: [true, false]
      responses:
        '200':
          description: Lista de gastos
    post:
      summary: Crear gasto para un usuario
      tags: [Firebase]
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [cantidad, categoria]
              properties:
                cantidad:
                  type: number
                categoria:
                  type: string
                descripcion:
                  type: string
                fecha:
                  type: string
      responses:
        '201':
          description: Gasto creado
  /api/v2/firebase/users/{usuario_id}/gastos-ids:
    get:
      summary: Listar solo IDs de gastos
      tags: [Firebase]
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      responses:
        '200':
          description: OK
  /api/v2/firebase/users/{usuario_id}/gastos-procesados:
    get:
      summary: Gastos + resumen IA (por categoría)
      tags: [Firebase]
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      responses:
        '200':
          description: OK

  # Predicción
  /api/v2/firebase/users/{usuario_id}/predict-category:
    get:
      summary: Predicción por categoría (30 días)
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      responses:
        '200':
          description: OK
  /api/v2/firebase/users/{usuario_id}/predict-monthly:
    get:
      summary: Predicción mensual (30 días)
      tags: [Predictions]
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      responses:
        '200':
          description: OK
          examples:
            ejemplo:
              value:
                status: success
                data:
                  diarias:
                    - fecha: 2026-01-04
                      prediccion: 85.2
                      min: 70.0
                      max: 100.5
                      semana: 1
                      dia_semana: Monday
                  total_mes: 2450.8
                  promedio_diario: 81.7
                  resumen_semanal:
                    1: { total: 600.4, promedio_diario: 85.77 }
  /api/v2/firebase/users/{usuario_id}/detect-anomalies:
    get:
      summary: Detección de anomalías
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      responses:
        '200':
          description: OK
  /api/v2/firebase/users/{usuario_id}/compare-models:
    get:
      summary: Comparación de modelos ML
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      responses:
        '200':
          description: OK
  /api/v2/firebase/users/{usuario_id}/seasonality:
    get:
      summary: Análisis de estacionalidad
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      responses:
        '200':
          description: OK
  /api/v2/firebase/users/{usuario_id}/analysis-complete:
    get:
      summary: Análisis completo (predicciones)
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      responses:
        '200':
          description: OK

  # Estadística
  /api/v2/firebase/users/{usuario_id}/stat/correlations:
    get:
      summary: Correlaciones entre categorías
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      responses:
        '200':
          description: OK
  /api/v2/firebase/users/{usuario_id}/stat/temporal-comparison:
    get:
      summary: Mes actual vs anterior
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      responses:
        '200':
          description: OK
  /api/v2/firebase/users/{usuario_id}/stat/clustering:
    get:
      summary: Clustering de gastos
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
        - in: query
          name: n_clusters
          schema:
            type: integer
            default: 3
      responses:
        '200':
          description: OK
  /api/v2/firebase/users/{usuario_id}/stat/trends:
    get:
      summary: Detección de tendencias
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      responses:
        '200':
          description: OK
  /api/v2/firebase/users/{usuario_id}/stat/outliers:
    get:
      summary: Outliers (IQR + Z-Score)
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      responses:
        '200':
          description: OK
  /api/v2/firebase/users/{usuario_id}/stat/complete:
    get:
      summary: Estadístico completo
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      responses:
        '200':
          description: OK

  # Ahorro y salud financiera
  /api/v2/firebase/users/{usuario_id}/savings/goals:
    get:
      summary: Metas de ahorro
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
        - in: query
          name: goal_name
          schema:
            type: string
        - in: query
          name: target_amount
          schema:
            type: number
            default: 1000
        - in: query
          name: months
          schema:
            type: integer
            default: 12
      responses:
        '200':
          description: OK
  /api/v2/firebase/users/{usuario_id}/savings/tips:
    get:
      summary: Tips personalizados
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      responses:
        '200':
          description: OK
  /api/v2/firebase/users/{usuario_id}/savings/budget-alerts:
    get:
      summary: Alertas de presupuesto
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
        - in: query
          name: monthly_budget
          schema:
            type: number
            default: 3000
      responses:
        '200':
          description: OK
  /api/v2/firebase/users/{usuario_id}/savings/health-score:
    get:
      summary: Puntuación financiera
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
        - in: query
          name: monthly_budget
          schema:
            type: number
            default: 3000
      responses:
        '200':
          description: OK
  /api/v2/firebase/users/{usuario_id}/savings/weekly-report:
    get:
      summary: Reporte semanal
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      responses:
        '200':
          description: OK
  /api/v2/firebase/users/{usuario_id}/savings/complete:
    get:
      summary: Ahorro completo (todos módulos)
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
        - in: query
          name: goal_name
          schema:
            type: string
        - in: query
          name: target_amount
          schema:
            type: number
            default: 5000
        - in: query
          name: months
          schema:
            type: integer
            default: 12
        - in: query
          name: monthly_budget
          schema:
            type: number
            default: 3000
      responses:
        '200':
          description: OK

  # Gráficos
  /api/v2/firebase/users/{usuario_id}/charts/heatmap:
    get:
      summary: Calendario de calor
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      responses:
        '200':
          description: OK (si Plotly disponible)
  /api/v2/firebase/users/{usuario_id}/charts/sankey:
    get:
      summary: Diagrama Sankey
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      responses:
        '200':
          description: OK
  /api/v2/firebase/users/{usuario_id}/charts/dashboard:
    get:
      summary: Dashboard interactivo
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      responses:
        '200':
          description: OK
  /api/v2/firebase/users/{usuario_id}/charts/comparison:
    get:
      summary: Comparativas mes vs mes
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      responses:
        '200':
          description: OK
  /api/v2/firebase/users/{usuario_id}/charts/export:
    get:
      summary: Exportar gráficos
      tags: [Charts]
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
        - in: query
          name: format
          schema:
            type: string
            enum: [json, base64]
            default: json
      responses:
        '200':
          description: OK
          examples:
            json:
              value:
                formato: json
                graficos:
                  - nombre: Pie Categorías
                    json: '{...}'
            base64:
              value:
                formato: base64
                graficos:
                  - nombre: Pie Categorías
                    base64: iVBORw0KGgoAAA...
  /api/v2/firebase/users/{usuario_id}/charts/complete:
    get:
      summary: Todos los gráficos
      security:
        - bearerAuth: []
      parameters:
        - $ref: '#/components/parameters/UsuarioId'
      responses:
        '200':
          description: OK
```

---

## 🔥 Estructura Firebase (Firestore)

```
users/{userId}                       ← Documento del usuario
  ├── gastos/{gastoId}              ← Subcolección de gastos
  └── budget/current                ← Documento con presupuesto/ingresos actuales
```

Base de datos utilizada por la API: `users/{userId}/gastos` y `users/{userId}/budget/current`.

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
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn API_MEJORADA:app`
5. Configura variables de entorno en Render:
   - `SECRET_KEY`: Tu clave secreta
   - `FLASK_ENV`: `production`
   - `PORT`: `5000`
   - Variables Firebase (si usas credenciales por env)

---

## 🔐 Autenticación

- Obtener token: `POST /api/v2/auth/token`
- Validar token: `POST /api/v2/auth/validate`
- Usa el token en: `Authorization: Bearer <token>` o `X-API-Key: <token>`

Ejemplo para obtener token:

```bash
curl -X POST http://localhost:5000/api/v2/auth/token \
  -H "Content-Type: application/json" \
  -d '{"user_id":"mi_usuario_123"}'
```

---

## 📚 Endpoints base: /api/v2/firebase/users

Todos los endpoints de usuario están conectados a la ruta base `/api/v2/firebase/users/{usuario_id}` y trabajan directamente con Firestore en `users/{usuario_id}`.

> Nota: Algunos endpoints requieren token JWT. Se indica en cada caso.

### 1) Gastos

- Listar gastos (sin token): `GET /api/v2/firebase/users/{usuario_id}/gastos`
  - Query opcional: `?ids_only=true` para devolver solo IDs

- Crear gasto (requiere token): `POST /api/v2/firebase/users/{usuario_id}/gastos`
  - Headers: `Authorization: Bearer <token>`, `Content-Type: application/json`
  - Body JSON:
    ```json
    { "cantidad": 150.50, "categoria": "Alimentación", "descripcion": "Compras", "fecha": "2025-12-15" }
    ```

- Listar solo IDs (sin token): `GET /api/v2/firebase/users/{usuario_id}/gastos-ids`

- Gastos procesados con IA (requiere token): `GET /api/v2/firebase/users/{usuario_id}/gastos-procesados`

### 2) Asesor financiero (suite completa)

- Asesor financiero completo (requiere token): `GET /api/v2/firebase/users/{usuario_id}/asesor-financiero`
  - Incluye: predicciones 30 días, análisis estadístico, recomendaciones y datos de gráficos.

### 3) Módulos por separado (todos requieren token)

- Predicciones: `GET /api/v2/firebase/users/{usuario_id}/predicciones`
- Análisis estadístico (con filtros): `GET /api/v2/firebase/users/{usuario_id}/analisis`
  - Query opcional:
    - `period=month&value=YYYY-MM`
    - `period=year&value=YYYY`
    - `period=quarter&value=YYYY-Qn`
- Recomendaciones de ahorro: `GET /api/v2/firebase/users/{usuario_id}/recomendaciones`
- Datos para gráficos: `GET /api/v2/firebase/users/{usuario_id}/graficos`
- Score financiero: `GET /api/v2/firebase/users/{usuario_id}/score`

### 4) Utilidades Firebase

- Debug conexión Firestore: `GET /api/v2/firebase/debug`
- Listar usuarios: `GET /api/v2/firebase/usuarios`
- Obtener usuario por ID: `GET /api/v2/firebase/usuarios/{usuario_id}`

---

## 📈 Endpoints de IA generales

Para evitar errores 405 y ser explícitos por usuario, usa las rutas bajo `/api/v2/firebase/users/{usuario_id}` para TODOS los módulos de IA. Todas requieren token.

### Predicción

- `GET /api/v2/firebase/users/{usuario_id}/predict-category`
- `GET /api/v2/firebase/users/{usuario_id}/predict-monthly`
- `GET /api/v2/firebase/users/{usuario_id}/detect-anomalies`
- `GET /api/v2/firebase/users/{usuario_id}/compare-models`
- `GET /api/v2/firebase/users/{usuario_id}/seasonality`
- `GET /api/v2/firebase/users/{usuario_id}/analysis-complete`

### Análisis estadístico

- `GET /api/v2/firebase/users/{usuario_id}/stat/correlations`
- `GET /api/v2/firebase/users/{usuario_id}/stat/temporal-comparison`
- `GET /api/v2/firebase/users/{usuario_id}/stat/clustering?n_clusters=3`
- `GET /api/v2/firebase/users/{usuario_id}/stat/trends`
- `GET /api/v2/firebase/users/{usuario_id}/stat/outliers`
- `GET /api/v2/firebase/users/{usuario_id}/stat/complete`

### Ahorro y salud financiera

- `GET /api/v2/firebase/users/{usuario_id}/savings/goals?goal_name=Viaje&target_amount=2500&months=6`
- `GET /api/v2/firebase/users/{usuario_id}/savings/tips`
- `GET /api/v2/firebase/users/{usuario_id}/savings/budget-alerts?monthly_budget=3000`
- `GET /api/v2/firebase/users/{usuario_id}/savings/health-score?monthly_budget=3000`
- `GET /api/v2/firebase/users/{usuario_id}/savings/weekly-report`
- `GET /api/v2/firebase/users/{usuario_id}/savings/complete?goal_name=Viaje&target_amount=2500&months=6&monthly_budget=3000`

### Gráficos

- `GET /api/v2/firebase/users/{usuario_id}/charts/heatmap`
- `GET /api/v2/firebase/users/{usuario_id}/charts/sankey`
- `GET /api/v2/firebase/users/{usuario_id}/charts/dashboard`
- `GET /api/v2/firebase/users/{usuario_id}/charts/comparison`
- `GET /api/v2/firebase/users/{usuario_id}/charts/export?format=json`
- `GET /api/v2/firebase/users/{usuario_id}/charts/complete`

---

## 🛠️ Troubleshooting

- Plotly missing: The charts endpoints return `{ "error": "Plotly no disponible. Instala: pip install plotly" }`. Install `plotly` to enable charts.
- Kaleido missing: Image export falls back to JSON. Install `kaleido` to enable `format=base64` in `/charts/export`.
- Firebase unavailable: Endpoints under `/firebase/*` return 503 if Firestore is not configured. Ensure env vars or service account JSON are set.
- JSON serialization: Weekly summaries in predictions are JSON-safe (no tuple keys). If you see unexpected 500s, update to the latest version and reinstall deps.

### Quick setup

```bash
pip install -r requirements.txt
gunicorn API_MEJORADA:app --bind 0.0.0.0:5000
```


## 🔑 Resumen rápido de autenticación

| Ruta | Requiere token |
|------|-----------------|
| `/api/v2/auth/token` | No |
| `/api/v2/auth/validate` | Sí (en header) |
| `/api/v2/health` | No |
| `/api/v2/firebase/debug` | No |
| `/api/v2/firebase/usuarios` | No |
| `/api/v2/firebase/usuarios/{id}` | No |
| `/api/v2/firebase/users/{id}/gastos` (GET) | No |
| `/api/v2/firebase/users/{id}/gastos` (POST) | Sí |
| `/api/v2/firebase/users/{id}/gastos-ids` | No |
| `/api/v2/firebase/users/{id}/gastos-procesados` | Sí |
| Resto de `/firebase/users/*` | Sí |
| Todos `/predict-*`, `/stat/*`, `/savings/*`, `/charts/*` | Sí |

---

## 📝 Ejemplo rápido (Python)

```python
import requests

BASE_URL = 'http://localhost:5000'

# 1) Token
tok = requests.post(f'{BASE_URL}/api/v2/auth/token', json={'user_id': 'usuario1'}).json()['token']
headers = {'Authorization': f'Bearer {tok}'}

# 2) Crear gasto
payload = { 'cantidad': 75.5, 'categoria': 'Restaurante', 'descripcion': 'Cena' }
r1 = requests.post(f'{BASE_URL}/api/v2/firebase/users/usuario1/gastos', json=payload, headers=headers)

# 3) Asesor financiero
r2 = requests.get(f'{BASE_URL}/api/v2/firebase/users/usuario1/asesor-financiero', headers=headers)
print(r1.json())
print(r2.json())
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
