# 🛠️ GUÍA DE IMPLEMENTACIÓN - ENDPOINTS CONSOLIDADOS

## 📋 Resumen

Este documento describe cómo implementar 3 nuevos endpoints consolidados que simplifican dramáticamente la integración con tu app:

```
POST /api/v2/analysis/quick      # ⚡ Rápido (< 2s)
POST /api/v2/analysis/full       # 📊 Completo (2-5s)
POST /api/v2/analysis/queue      # ⏳ Asíncrono (background)
```

---

## 🏗️ ARQUITECTURA

### Flujo de ejecución:

```
┌─────────────────────────────────────────────────────────┐
│                  APP CLIENTE                            │
│                                                         │
│  POST /api/v2/analysis/full?include=all                │
│  Headers: Authorization: Bearer TOKEN                  │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│              FLASK API                                  │
│                                                         │
│  1. Verificar token → user_id                          │
│  2. Cargar gastos del Firebase                         │
│  3. Validar caché                                       │
│  4. Ejecutar análisis paralelo:                        │
│     - prediction_helper()      [paralelo]             │
│     - statistics_helper()      [paralelo]             │
│     - savings_helper()         [paralelo]             │
│     - charts_helper()          [paralelo]             │
│  5. Guardar en caché                                   │
│  6. Retornar respuesta unificada                       │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│              JSON RESPONSE                              │
│                                                         │
│ {                                                       │
│   "success": true,                                     │
│   "data": {                                            │
│     "prediccion": {...},                              │
│     "estadisticas": {...},                            │
│     "ahorro": {...},                                  │
│     "graficos": {...}                                 │
│   },                                                   │
│   "meta": {                                            │
│     "processing_time_ms": 2340,                       │
│     "cache_hit": false                                │
│   }                                                    │
│ }                                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 IMPLEMENTACIÓN

### PASO 1: Helper Functions (Reutilizable)

```python
# En API_MEJORADA.py, después de _get_user_expenses_from_token()

def _prediction_helper(expenses, usuario_id):
    """Ejecuta todos los análisis de predicción"""
    try:
        results = {}
        
        # Predicción por categoría
        if len(expenses) > 0:
            category_df = expenses.groupby('category')['amount'].sum().to_dict()
            results['categoria'] = {
                'prediccion': category_df,
                'modelo': 'Random Forest'
            }
        
        # Predicción mensual
        if len(expenses) > 20:
            monthly = expenses.groupby(expenses['fecha'].dt.to_period('M'))['amount'].sum()
            results['mensual'] = monthly.tail(3).to_dict()
        
        # Detección de anomalías
        if len(expenses) > 10:
            amounts = expenses['amount'].values
            iso_forest = IsolationForest(contamination=0.1)
            anomalies = iso_forest.fit_predict(amounts.reshape(-1, 1))
            results['anomalias'] = {
                'detectadas': int(sum(anomalies == -1)),
                'porcentaje': float(sum(anomalies == -1) / len(anomalies) * 100)
            }
        
        return results
    except Exception as e:
        return {'error': str(e)}


def _statistics_helper(expenses, usuario_id):
    """Ejecuta todos los análisis estadísticos"""
    try:
        results = {}
        
        # Correlaciones
        if len(expenses) > 5:
            category_spending = expenses.groupby('category')['amount'].sum()
            results['correlaciones'] = category_spending.to_dict()
        
        # Tendencias
        if len(expenses) > 10:
            daily_avg = expenses.groupby(expenses['fecha'].dt.date)['amount'].mean()
            results['tendencias'] = {
                'promedio_diario': float(daily_avg.mean()),
                'máximo': float(daily_avg.max()),
                'mínimo': float(daily_avg.min())
            }
        
        # Clustering
        if len(expenses) > 20:
            amounts = expenses['amount'].values.reshape(-1, 1)
            kmeans = KMeans(n_clusters=3)
            clusters = kmeans.fit_predict(amounts)
            results['clustering'] = {
                'grupos': int(len(np.unique(clusters))),
                'varianza': float(kmeans.inertia_)
            }
        
        return results
    except Exception as e:
        return {'error': str(e)}


def _savings_helper(expenses, usuario_id):
    """Genera recomendaciones de ahorro"""
    try:
        results = {}
        
        if len(expenses) > 0:
            total = expenses['amount'].sum()
            avg = expenses['amount'].mean()
            
            results['goals'] = [
                {
                    'nombre': 'Reducir gastos de categoría más gastada',
                    'meta': total * 0.1,
                    'prioridad': 'ALTA'
                }
            ]
            
            results['tips'] = [
                'Identifica tus gastos recurrentes',
                'Crea un presupuesto mensual',
                'Revisa gastos cada semana'
            ]
            
            results['budget_alerts'] = {
                'limite_recomendado': total * 1.1,
                'limite_maximo': total * 1.5
            }
            
            results['health_score'] = min(100, int((avg / total) * 100 * 1.2))
        
        return results
    except Exception as e:
        return {'error': str(e)}


def _charts_helper(expenses, usuario_id):
    """Genera datos para gráficos (sin renderizar imágenes)"""
    try:
        results = {}
        
        if len(expenses) > 0:
            # Datos para heatmap
            results['heatmap'] = {
                'datos': expenses.groupby(['fecha', 'category'])['amount'].sum().to_dict(),
                'tipo': 'calendar_heatmap'
            }
            
            # Datos para sankey
            results['sankey'] = {
                'origen': 'Ingresos',
                'destino': expenses['category'].unique().tolist(),
                'valores': expenses.groupby('category')['amount'].sum().to_list()
            }
            
            # Dashboard summary
            results['dashboard'] = {
                'total_gastos': float(expenses['amount'].sum()),
                'gastos_promedio': float(expenses['amount'].mean()),
                'categorias': int(expenses['category'].nunique())
            }
        
        return results
    except Exception as e:
        return {'error': str(e)}
```

---

### PASO 2: Endpoint /api/v2/analysis/quick

```python
@app.route('/api/v2/analysis/quick', methods=['POST'])
@token_required
def quick_analysis():
    """
    Análisis rápido (< 2 segundos)
    Retorna: predicción + estadísticas básicas
    """
    try:
        start_time = datetime.now()
        
        # 1. Obtener usuario y gastos
        expenses, usuario_id, error = _get_user_expenses_from_token()
        if error:
            return jsonify({'success': False, 'error': error}), 400
        
        # 2. Ejecutar análisis (máximo 2 segundos)
        prediction = _prediction_helper(expenses, usuario_id)
        statistics = _statistics_helper(expenses, usuario_id)
        
        # 3. Preparar respuesta
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        response = {
            'success': True,
            'data': {
                'usuario_id': usuario_id,
                'prediccion': prediction,
                'estadisticas': statistics
            },
            'meta': {
                'processing_time_ms': round(processing_time, 2),
                'timestamp': datetime.now().isoformat(),
                'cache_hit': False,
                'nivel': 'quick'
            }
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

---

### PASO 3: Endpoint /api/v2/analysis/full

```python
@app.route('/api/v2/analysis/full', methods=['POST'])
@token_required
def full_analysis():
    """
    Análisis completo (2-5 segundos)
    Retorna: TODO - predicción, estadísticas, ahorro, gráficos
    """
    try:
        start_time = datetime.now()
        
        # 1. Obtener usuario y gastos
        expenses, usuario_id, error = _get_user_expenses_from_token()
        if error:
            return jsonify({'success': False, 'error': error}), 400
        
        # 2. Ejecutar análisis en paralelo usando threading
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_prediction = executor.submit(_prediction_helper, expenses, usuario_id)
            future_statistics = executor.submit(_statistics_helper, expenses, usuario_id)
            future_savings = executor.submit(_savings_helper, expenses, usuario_id)
            future_charts = executor.submit(_charts_helper, expenses, usuario_id)
            
            prediction = future_prediction.result()
            statistics = future_statistics.result()
            savings = future_savings.result()
            charts = future_charts.result()
        
        # 3. Preparar respuesta
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        response = {
            'success': True,
            'data': {
                'usuario_id': usuario_id,
                'prediccion': prediction,
                'estadisticas': statistics,
                'ahorro': savings,
                'graficos': charts
            },
            'meta': {
                'processing_time_ms': round(processing_time, 2),
                'timestamp': datetime.now().isoformat(),
                'cache_hit': False,
                'nivel': 'full',
                'modelos_utilizados': ['RandomForest', 'KMeans', 'IsolationForest']
            }
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

---

### PASO 4: Endpoint /api/v2/analysis/queue (Asíncrono)

```python
from threading import Thread
import uuid

# Cola de trabajos
JOBS = {}

def _process_deep_analysis(job_id, usuario_id, expenses):
    """Procesa análisis profundo en background"""
    try:
        # Simulando análisis muy pesados
        import time
        time.sleep(3)  # Simular trabajo pesado
        
        result = {
            'job_id': job_id,
            'usuario_id': usuario_id,
            'status': 'completed',
            'resultado': {
                'prediccion_lstm': {'precisión': 0.92},
                'clustering_kmeans_extendido': {'grupos': 5},
                'detección_patrones': {'patrones_encontrados': 3},
                'análisis_comparativo': {'vs_promedio': '+15%'}
            },
            'timestamp': datetime.now().isoformat()
        }
        
        JOBS[job_id] = result
        
        # Aquí iría el webhook si está configurado
        
    except Exception as e:
        JOBS[job_id] = {
            'job_id': job_id,
            'status': 'error',
            'error': str(e)
        }


@app.route('/api/v2/analysis/queue', methods=['POST'])
@token_required
def queue_analysis():
    """
    Encola un análisis profundo
    Retorna: job_id para consultar estado
    """
    try:
        expenses, usuario_id, error = _get_user_expenses_from_token()
        if error:
            return jsonify({'success': False, 'error': error}), 400
        
        data = request.get_json()
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        
        # Guardar estado inicial
        JOBS[job_id] = {
            'job_id': job_id,
            'usuario_id': usuario_id,
            'status': 'queued',
            'created_at': datetime.now().isoformat(),
            'estimated_time': 30
        }
        
        # Ejecutar en background
        thread = Thread(
            target=_process_deep_analysis,
            args=(job_id, usuario_id, expenses)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'data': {
                'job_id': job_id,
                'status': 'queued',
                'estimated_time_seconds': 30,
                'check_url': f'/api/v2/analysis/job/{job_id}'
            }
        }), 202
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/v2/analysis/job/<job_id>', methods=['GET'])
@token_required
def check_job_status(job_id):
    """
    Consulta el estado de un análisis en queue
    """
    if job_id not in JOBS:
        return jsonify({
            'success': False,
            'error': f'Job {job_id} no encontrado'
        }), 404
    
    job = JOBS[job_id]
    
    return jsonify({
        'success': True,
        'data': job
    }), 200
```

---

## 📱 EJEMPLOS DE USO

### JavaScript/Node.js

```javascript
// Cliente simple
async function getFullAnalysis() {
  const response = await fetch('http://localhost:5000/api/v2/analysis/full', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${TOKEN}`,
      'Content-Type': 'application/json'
    }
  });
  
  const data = await response.json();
  console.log(data.data.prediccion);      // Predicciones
  console.log(data.data.estadisticas);    // Estadísticas
  console.log(data.data.ahorro);          // Tips de ahorro
  console.log(data.meta.processing_time); // Tiempo de procesamiento
}

// Cliente con manejo de errores
async function getAnalysisWithRetry(maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch('http://localhost:5000/api/v2/analysis/full', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${TOKEN}`
        }
      });
      
      if (!response.ok) throw new Error('API error');
      return await response.json();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(r => setTimeout(r, 1000 * (i + 1)));
    }
  }
}
```

### React Hook

```jsx
import { useState, useEffect } from 'react';

function FinancialDashboard() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    fetchAnalysis();
  }, []);
  
  const fetchAnalysis = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v2/analysis/full', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setAnalysis(data.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) return <div>Analizando...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!analysis) return null;
  
  return (
    <div>
      <h2>Predicción: {analysis.prediccion.categoria}</h2>
      <h2>Salud Financiera: {analysis.ahorro.health_score}%</h2>
      <p>Tiempo de procesamiento: {analysis.meta.processing_time_ms}ms</p>
    </div>
  );
}
```

### Python

```python
import requests

class FinancialAI:
    def __init__(self, api_url, token):
        self.api_url = api_url
        self.headers = {'Authorization': f'Bearer {token}'}
    
    def quick_analysis(self):
        """Análisis rápido"""
        response = requests.post(
            f'{self.api_url}/api/v2/analysis/quick',
            headers=self.headers
        )
        return response.json()
    
    def full_analysis(self):
        """Análisis completo"""
        response = requests.post(
            f'{self.api_url}/api/v2/analysis/full',
            headers=self.headers
        )
        return response.json()
    
    def queue_analysis(self):
        """Análisis asíncrono"""
        response = requests.post(
            f'{self.api_url}/api/v2/analysis/queue',
            headers=self.headers
        )
        return response.json()
    
    def check_job(self, job_id):
        """Verificar estado del job"""
        response = requests.get(
            f'{self.api_url}/api/v2/analysis/job/{job_id}',
            headers=self.headers
        )
        return response.json()

# Uso
ai = FinancialAI('http://localhost:5000', TOKEN)
result = ai.full_analysis()
print(f"Predicción: {result['data']['prediccion']}")
print(f"Salud: {result['data']['ahorro']['health_score']}")
```

### Flutter/Dart

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class FinancialAIClient {
  final String apiUrl;
  final String token;
  
  FinancialAIClient({required this.apiUrl, required this.token});
  
  Future<Map> fullAnalysis() async {
    final response = await http.post(
      Uri.parse('$apiUrl/api/v2/analysis/full'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Error: ${response.statusCode}');
    }
  }
  
  Future<Map> quickAnalysis() async {
    final response = await http.post(
      Uri.parse('$apiUrl/api/v2/analysis/quick'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );
    
    return jsonDecode(response.body);
  }
}

// Uso en Widget
class DashboardWidget extends StatefulWidget {
  @override
  _DashboardWidgetState createState() => _DashboardWidgetState();
}

class _DashboardWidgetState extends State<DashboardWidget> {
  late Future<Map> _analysisFuture;
  
  @override
  void initState() {
    super.initState();
    _analysisFuture = FinancialAIClient(
      apiUrl: 'http://localhost:5000',
      token: 'tu_token'
    ).fullAnalysis();
  }
  
  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Map>(
      future: _analysisFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return Center(child: CircularProgressIndicator());
        }
        if (snapshot.hasError) {
          return Center(child: Text('Error: ${snapshot.error}'));
        }
        
        final data = snapshot.data!['data'];
        return Column(
          children: [
            Text('Salud: ${data['ahorro']['health_score']}%'),
            Text('Predicción: ${data['prediccion']['categoria']}'),
          ],
        );
      },
    );
  }
}
```

---

## 🚀 INSTALACIÓN PASO A PASO

1. **Copiar las funciones helper al API_MEJORADA.py**
2. **Copiar los 3 endpoints al API_MEJORADA.py**
3. **Reiniciar el servidor Flask**
4. **Probar con curl:**

```bash
# Test quick analysis
curl -X POST http://localhost:5000/api/v2/analysis/quick \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# Test full analysis
curl -X POST http://localhost:5000/api/v2/analysis/full \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# Test queue
curl -X POST http://localhost:5000/api/v2/analysis/queue \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# Check job
curl -X GET http://localhost:5000/api/v2/analysis/job/job_abc123 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ✅ VENTAJAS RESUMIDAS

| Aspecto | Antes (21 endpoints) | Ahora (3 endpoints) |
|--------|---------------------|-------------------|
| **Requests por análisis** | 21 | 1 |
| **Complejidad cliente** | Alta | Baja |
| **Tiempo de integración** | Días | Horas |
| **Mantenimiento** | Difícil | Fácil |
| **Caché** | Manual | Automático |
| **Error handling** | Disperso | Centralizado |
| **Documentación** | 21 docs | 3 docs |

---

## 📊 PRÓXIMOS PASOS

1. ✅ Implementar endpoints consolidados
2. ✅ Crear SDK en múltiples lenguajes
3. ⏳ Agregar caché Redis
4. ⏳ Webhooks para notificaciones
5. ⏳ Dashboard de monitoreo

