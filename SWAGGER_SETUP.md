# 🚀 Gestor Financiero IA API - Instrucciones de Swagger

## 📋 Resumen

Tu API tiene **20 características de Inteligencia Artificial** documentadas en **Swagger UI**. Todos tus endpoints están disponibles en un panel interactivo.

---

## 🔧 Cómo Levantar la API con Swagger

### **Opción 1: Ejecución Directa (Windows)**

```bash
# 1. Abre PowerShell o CMD
# 2. Navega al directorio del proyecto
cd "d:\Projects\Api google colab"

# 3. Activa el entorno virtual
.venv\Scripts\activate

# 4. Instala las dependencias (si no lo hiciste)
pip install -r requirements.txt

# 5. Ejecuta la API
python API_MEJORADA.py
```

### **Opción 2: Desde VS Code**

1. Abre la carpeta del proyecto en VS Code
2. Abre la terminal integrada (`Ctrl + ñ`)
3. Ejecuta:
   ```bash
   python API_MEJORADA.py
   ```

---

## 📖 Acceder a Swagger UI

Una vez que la API esté corriendo, abre tu navegador y ve a:

### **🌐 http://localhost:5000/docs**

Verás un panel interactivo con:
- ✅ Todos los endpoints documentados
- ✅ Esquemas de request/response
- ✅ Botón "Try it out" para probar cada endpoint
- ✅ Ejemplos de uso
- ✅ Autenticación integrada

---

## 🔐 Cómo Usar la API desde Swagger

### **Paso 1: Generar un Token**

1. En Swagger, busca la sección **"Autenticación"**
2. Abre `POST /api/v2/auth/token`
3. Click en **"Try it out"**
4. En el body, ingresa:
   ```json
   {
     "user_id": "mi_usuario_123"
   }
   ```
5. Click en **"Execute"**
6. Copiar el `token` de la respuesta

### **Paso 2: Autenticar Requests Posteriores**

1. En Swagger, en la esquina superior derecha, haz click en **"Authorize"**
2. Pega el token en el campo de entrada
3. Click en **"Authorize"**
4. Ahora todos los endpoints protegidos funcionarán

### **Paso 3: Probar Endpoints**

1. Selecciona cualquier endpoint (ej: `/api/v2/predict-category`)
2. Click en **"Try it out"**
3. Modifica los parámetros si necesitas
4. Click en **"Execute"**
5. Verás la respuesta en JSON

---

## 📊 Categorías de Endpoints

### **1. 🔐 Autenticación**
- `POST /api/v2/auth/token` - Generar token
- `POST /api/v2/auth/validate` - Validar token

### **2. 📊 Predicción de Gastos (5 endpoints)**
- `POST /api/v2/predict-category` - Predicción por categoría
- `POST /api/v2/predict-monthly` - Predicción mensual (30 días)
- `POST /api/v2/detect-anomalies` - Detección de anomalías
- `POST /api/v2/compare-models` - Comparación de modelos ML
- `POST /api/v2/seasonality` - Análisis de estacionalidad

### **3. 📈 Análisis Estadístico (5 endpoints)**
- `POST /api/v2/stat/correlations` - Correlaciones entre categorías
- `POST /api/v2/stat/temporal-comparison` - Mes actual vs anterior
- `POST /api/v2/stat/clustering` - Clustering automático
- `POST /api/v2/stat/trends` - Detección de tendencias
- `POST /api/v2/stat/outliers` - Detección de outliers

### **4. 💡 Recomendaciones de Ahorro (5 endpoints)**
- `POST /api/v2/savings/goals` - Metas de ahorro
- `POST /api/v2/savings/tips` - Tips personalizados
- `POST /api/v2/savings/budget-alerts` - Alertas de presupuesto
- `POST /api/v2/savings/health-score` - Puntuación financiera
- `POST /api/v2/savings/weekly-report` - Reporte semanal

### **5. 📊 Gráficos y Visualización (5 endpoints)**
- `POST /api/v2/charts/heatmap` - Calendario de calor
- `POST /api/v2/charts/sankey` - Diagrama Sankey
- `POST /api/v2/charts/dashboard` - Dashboard interactivo
- `POST /api/v2/charts/comparison` - Comparativa mensual
- `POST /api/v2/charts/export` - Exportar como imagen

### **6. 🔥 Firebase Integration**
- `GET /api/v2/firebase/usuarios` - Obtener todos los usuarios
- `GET /api/v2/firebase/usuarios/{usuario_id}` - Obtener usuario específico
- `GET /api/v2/firebase/users/{usuario_id}/gastos` - Obtener gastos
- `POST /api/v2/firebase/users/{usuario_id}/gastos` - Crear gasto
- `GET /api/v2/firebase/users/{usuario_id}/gastos-procesados` - Gastos procesados
- `GET /api/v2/firebase/users/{usuario_id}/gastos-ids` - IDs de gastos

### **7. 🤖 Asesor Financiero IA**
- `GET /api/v2/firebase/users/{usuario_id}/asesor-financiero` - Análisis completo
- `GET /api/v2/firebase/users/{usuario_id}/predicciones` - Predicciones
- `GET /api/v2/firebase/users/{usuario_id}/analisis` - Análisis estadístico
- `GET /api/v2/firebase/users/{usuario_id}/recomendaciones` - Recomendaciones
- `GET /api/v2/firebase/users/{usuario_id}/graficos` - Gráficos
- `GET /api/v2/firebase/users/{usuario_id}/score` - Puntuación

### **8. 🔧 Utilidades**
- `GET /api/v2/health` - Estado de la API
- `GET /api/v2/firebase/debug` - Debug de Firebase
- `GET /api/v2/swagger.yaml` - Especificación OpenAPI

---

## 🧪 Probar la API Localmente

### **Script de Testing**

Se incluye un script `test_swagger.py` que verifica que todo está corriendo:

```bash
# En otra terminal (mientras la API está corriendo)
python test_swagger.py
```

Esto verificará:
- ✅ Health check
- ✅ Acceso a swagger.yaml
- ✅ Disponibilidad de Swagger UI
- ✅ Generación de tokens

---

## 🐛 Troubleshooting

### **Problema: "No se puede conectar a localhost:5000"**
- Verifica que la API esté corriendo con `python API_MEJORADA.py`
- Abre http://localhost:5000/api/v2/health en el navegador
- Si no funciona, el servidor no está corriendo

### **Problema: "Swagger UI en /docs no carga"**
- Verifica que `flask-swagger-ui` esté instalado: `pip install flask-swagger-ui`
- Reinicia el servidor

### **Problema: "Token inválido o expirado"**
- Genera un nuevo token en `/api/v2/auth/token`
- Copia el nuevo token y úsalo para autenticar

### **Problema: "No puedo conectar con Firebase"**
- Verifica que tengas el archivo JSON de credenciales o variables de entorno configuradas
- Abre `/api/v2/firebase/debug` para ver el estado

---

## 📱 Usar la API desde Postman/cURL

### **Generar Token**
```bash
curl -X POST http://localhost:5000/api/v2/auth/token \
  -H "Content-Type: application/json" \
  -d '{"user_id":"mi_usuario"}'
```

### **Usar Token en Request**
```bash
curl -X POST http://localhost:5000/api/v2/predict-category \
  -H "Authorization: Bearer TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"expenses":[{"fecha":"2024-12-15","monto":100,"categoria":"Comida"}]}'
```

---

## 🚀 Despliegue en Producción

Para desplegar en **Render.com** (recomendado):

1. Configura el `Procfile` (ya incluido):
   ```
   web: gunicorn API_MEJORADA:app
   ```

2. Configura las variables de entorno en Render:
   ```
   PORT=5000
   FLASK_ENV=production
   SECRET_KEY=tu_clave_secreta
   FIREBASE_PROJECT_ID=...
   ```

3. Despliega: Tu API estará en `https://tu-app.onrender.com`

4. Accede a Swagger: `https://tu-app.onrender.com/docs`

---

## 📞 Soporte

Si tienes problemas:
1. Verifica que todos los paquetes estén instalados: `pip install -r requirements.txt`
2. Revisa los logs del servidor
3. Abre `/api/v2/health` en el navegador para ver el estado
4. Abre `/api/v2/firebase/debug` para ver estado de Firebase

---

## ✨ Próximos Pasos

1. ✅ **Levanta la API**: `python API_MEJORADA.py`
2. ✅ **Abre Swagger**: http://localhost:5000/docs
3. ✅ **Genera un token**: En `/api/v2/auth/token`
4. ✅ **Prueba tus endpoints**: Usa el botón "Try it out"
5. ✅ **Integra en tu aplicación**: Usa los endpoints que necesites

---

¡Disfruta de tu API con 20 características de IA! 🎉
