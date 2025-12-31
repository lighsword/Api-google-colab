# API Mejorada con 20 Características de IA

API Flask con machine learning para análisis de gastos, predicciones y recomendaciones de ahorro.

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

## 📊 Endpoints

### Autenticación
- `POST /api/v2/auth/token` - Obtener token JWT
- `POST /api/v2/auth/validate` - Validar token

### Predicciones (5 endpoints)
- `POST /api/v2/predict-category` - Predicción por categoría
- `POST /api/v2/predict-monthly` - Predicción mensual
- `POST /api/v2/anomalies` - Detección de anomalías
- `POST /api/v2/models-comparison` - Comparación de modelos
- `POST /api/v2/seasonality` - Análisis de estacionalidad

### Análisis Estadístico (5 endpoints)
- `POST /api/v2/stat/correlations` - Correlaciones
- `POST /api/v2/stat/temporal-comparison` - Comparación temporal
- `POST /api/v2/stat/clustering` - Agrupamiento
- `POST /api/v2/stat/trends` - Tendencias
- `POST /api/v2/stat/outliers` - Detección de outliers

### Recomendaciones (5 endpoints)
- `POST /api/v2/savings/goals` - Metas de ahorro
- `POST /api/v2/savings/tips` - Tips personalizados
- `POST /api/v2/savings/budget-alerts` - Alertas
- `POST /api/v2/savings/health-score` - Puntuación financiera
- `POST /api/v2/savings/weekly-report` - Reportes

### Gráficos (5 endpoints)
- `POST /api/v2/charts/heatmap` - Calendario de calor
- `POST /api/v2/charts/sankey` - Diagrama Sankey
- `POST /api/v2/charts/dashboard` - Dashboard
- `POST /api/v2/charts/comparison` - Comparativas
- `POST /api/v2/charts/export` - Exportar gráficos

## 🔐 Autenticación

Todos los endpoints (excepto `/auth/token`) requieren un token JWT.

**Obtener token**:
```bash
curl -X POST http://localhost:5000/api/v2/auth/token \
  -H "Content-Type: application/json" \
  -d '{"user_id": "mi_usuario"}'
```

**Usar token**:
```bash
curl -X POST http://localhost:5000/api/v2/predict-category \
  -H "Authorization: Bearer <tu_token>" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

## 📝 Ejemplo de uso

```python
import requests

# 1. Obtener token
response = requests.post('http://localhost:5000/api/v2/auth/token', 
  json={'user_id': 'usuario1'})
token = response.json()['token']

# 2. Hacer predicción
headers = {'Authorization': f'Bearer {token}'}
data = {
  'expenses': [
    {'fecha': '2024-12-01', 'monto': 50, 'categoria': 'Comida'},
    {'fecha': '2024-12-02', 'monto': 30, 'categoria': 'Transporte'}
  ]
}
response = requests.post('http://localhost:5000/api/v2/predict-category',
  json=data, headers=headers)
print(response.json())
```

## 📦 Dependencias

- Flask: Framework web
- pandas, numpy: Procesamiento de datos
- scikit-learn: Machine learning
- PyJWT: Autenticación JWT
- gunicorn: Servidor WSGI para producción

## 📄 Licencia

MIT
