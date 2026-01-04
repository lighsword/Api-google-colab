# API Mejorada con 20+ Características de IA

API Flask con machine learning para análisis de gastos, predicciones y recomendaciones de ahorro. Integrada con Firebase Firestore.

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

Estos endpoints también pueden usar datos de Firebase automáticamente si no envías `expenses` y tu token incluye `user_id`. Alternativamente, puedes enviar `expenses` en el body.

Headers comunes: `Authorization: Bearer <token>`, `Content-Type: application/json`

Body común (si no usas Firebase implícito):
```json
{
  "expenses": [
    {"fecha": "2025-11-01", "monto": 50, "categoria": "Comida"},
    {"fecha": "2025-11-02", "monto": 30, "categoria": "Transporte"}
  ]
}
```

- Predicción por categoría: `POST /api/v2/predict-category`
- Predicción mensual: `POST /api/v2/predict-monthly`
- Detección de anomalías: `POST /api/v2/detect-anomalies`
- Comparación de modelos: `POST /api/v2/compare-models`
- Estacionalidad: `POST /api/v2/seasonality`
- Análisis completo (predicción): `POST /api/v2/analysis-complete`

### Análisis estadístico

- Correlaciones: `POST /api/v2/stat/correlations`
- Mes actual vs anterior: `POST /api/v2/stat/temporal-comparison`
- Clustering: `POST /api/v2/stat/clustering`
- Tendencias: `POST /api/v2/stat/trends`
- Outliers (IQR + Z-Score): `POST /api/v2/stat/outliers`
- Análisis estadístico completo: `POST /api/v2/stat/complete`

### Ahorro y salud financiera

- Metas de ahorro: `POST /api/v2/savings/goals`
- Tips personalizados: `POST /api/v2/savings/tips`
- Alertas de presupuesto: `POST /api/v2/savings/budget-alerts`
- Puntuación financiera: `POST /api/v2/savings/health-score`
- Reporte semanal: `POST /api/v2/savings/weekly-report`
- Análisis de ahorro completo: `POST /api/v2/savings/complete`

### Gráficos

- Heatmap: `POST /api/v2/charts/heatmap`
- Sankey: `POST /api/v2/charts/sankey`
- Dashboard: `POST /api/v2/charts/dashboard`
- Comparación meses: `POST /api/v2/charts/comparison`
- Exportar gráficos: `POST /api/v2/charts/export` (campo `format`: `json` o `base64`)
- Paquete completo de gráficos: `POST /api/v2/charts/complete`

---

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
