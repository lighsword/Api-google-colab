# 🚀 GUÍA DE INTEGRACIÓN - CÓMO CONECTAR TU APP CON LA IA FINANCIERA

## 📋 ÍNDICE

1. [Introducción](#introducción)
2. [Configuración inicial](#configuración-inicial)
3. [Integración Web (React/Vue)](#integración-web)
4. [Integración Mobile (Flutter)](#integración-mobile)
5. [Integración Backend (Python)](#integración-backend)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Introducción

Tu API financiera ahora tiene **3 endpoints consolidados** que simplifican todo:

```
POST /api/v2/analysis/quick    → 1 request, múltiples análisis
POST /api/v2/analysis/full     → Análisis completo
POST /api/v2/analysis/queue    → Análisis asíncrono
```

**Beneficios:**
- ✅ 75% menos código en tu app
- ✅ 1 request en lugar de 21
- ✅ Manejo de errores centralizado
- ✅ Caché automático
- ✅ SDKs en múltiples lenguajes

---

## 🔧 Configuración inicial

### Paso 1: Obtener Token JWT

```bash
# Primero, obtén tu token de la API de autenticación
curl -X POST http://localhost:5000/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "tu_usuario",
    "contraseña": "tu_contraseña"
  }'

# Respuesta:
# {
#   "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
# }
```

### Paso 2: Guardar Token

**En el navegador (LocalStorage):**
```javascript
const response = await fetch('http://localhost:5000/api/v2/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    usuario: 'tu_usuario',
    contraseña: 'tu_contraseña'
  })
});

const { token } = await response.json();
localStorage.setItem('token', token);
```

**En mobile (Keystore/Keychain):**
```dart
// Flutter
final secureStorage = const FlutterSecureStorage();
await secureStorage.write(key: 'jwt_token', value: token);

// Luego recuperar:
final token = await secureStorage.read(key: 'jwt_token');
```

**En backend (Variables de entorno):**
```python
import os
TOKEN = os.getenv('API_TOKEN')
```

---

## 💻 INTEGRACIÓN WEB

### Opción A: React

#### Instalación

```bash
# Copiar el SDK a tu proyecto
cp financial_ai_sdk.ts src/lib/

# O instalar desde npm (cuando sea publicado)
npm install @financialai/sdk
```

#### Uso Básico

```jsx
// src/hooks/useFinancialAnalysis.js
import { FinancialAI } from '../lib/financial_ai_sdk';

export function useFinancialAnalysis() {
  const [analysis, setAnalysis] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const fetchAnalysis = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      const ai = new FinancialAI({
        apiUrl: 'http://localhost:5000',
        token: token
      });
      
      const result = await ai.fullAnalysis();
      setAnalysis(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  return { analysis, loading, error, fetchAnalysis };
}

// src/components/Dashboard.jsx
import { useFinancialAnalysis } from '../hooks/useFinancialAnalysis';

export function Dashboard() {
  const { analysis, loading, error, fetchAnalysis } = useFinancialAnalysis();

  React.useEffect(() => {
    fetchAnalysis();
  }, [fetchAnalysis]);

  if (loading) {
    return <div className="loader">Analizando tus gastos...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  if (!analysis?.data) {
    return <div>No hay datos</div>;
  }

  const { prediccion, ahorro, estadisticas, graficos } = analysis.data;

  return (
    <div className="dashboard">
      <section className="prediction">
        <h2>📊 Predicción</h2>
        <div className="grid">
          {Object.entries(prediccion?.categoria || {}).map(([cat, amount]) => (
            <div key={cat} className="card">
              <h3>{cat}</h3>
              <p className="amount">${amount.toFixed(2)}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="savings">
        <h2>💰 Oportunidades de Ahorro</h2>
        <div className="health-score">
          <div className="score">{ahorro?.health_score}%</div>
          <div className="label">Salud Financiera</div>
        </div>
        <ul className="tips">
          {ahorro?.tips?.map((tip, i) => (
            <li key={i}>✓ {tip}</li>
          ))}
        </ul>
      </section>

      <section className="stats">
        <p>⚡ Análisis completado en {analysis.meta.processing_time_ms}ms</p>
      </section>
    </div>
  );
}
```

#### Con Context API

```jsx
// src/context/FinancialContext.jsx
import React from 'react';
import { FinancialAI } from '../lib/financial_ai_sdk';

const FinancialContext = React.createContext();

export function FinancialProvider({ children }) {
  const [state, dispatch] = React.useReducer(financialReducer, initialState);
  
  const ai = React.useMemo(() => {
    return new FinancialAI({
      apiUrl: 'http://localhost:5000',
      token: localStorage.getItem('token')
    });
  }, []);

  const quickAnalysis = React.useCallback(async () => {
    dispatch({ type: 'LOADING' });
    try {
      const result = await ai.quickAnalysis();
      dispatch({ type: 'SUCCESS', payload: result });
    } catch (error) {
      dispatch({ type: 'ERROR', payload: error.message });
    }
  }, [ai]);

  const fullAnalysis = React.useCallback(async () => {
    dispatch({ type: 'LOADING' });
    try {
      const result = await ai.fullAnalysis();
      dispatch({ type: 'SUCCESS', payload: result });
    } catch (error) {
      dispatch({ type: 'ERROR', payload: error.message });
    }
  }, [ai]);

  return (
    <FinancialContext.Provider value={{ ...state, quickAnalysis, fullAnalysis }}>
      {children}
    </FinancialContext.Provider>
  );
}

export const useFinancial = () => React.useContext(FinancialContext);
```

#### Con Redux

```jsx
// src/redux/financialSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { FinancialAI } from '../lib/financial_ai_sdk';

const ai = new FinancialAI({
  apiUrl: process.env.REACT_APP_API_URL,
  token: localStorage.getItem('token')
});

export const fetchFullAnalysis = createAsyncThunk(
  'financial/fullAnalysis',
  async (_, { rejectWithValue }) => {
    try {
      return await ai.fullAnalysis();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const financialSlice = createSlice({
  name: 'financial',
  initialState: { data: null, loading: false, error: null },
  extraReducers: (builder) => {
    builder
      .addCase(fetchFullAnalysis.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchFullAnalysis.fulfilled, (state, action) => {
        state.data = action.payload;
        state.loading = false;
      })
      .addCase(fetchFullAnalysis.rejected, (state, action) => {
        state.error = action.payload;
        state.loading = false;
      });
  }
});

export default financialSlice.reducer;
```

---

### Opción B: Vue 3

```vue
<!-- src/components/FinancialDashboard.vue -->
<template>
  <div class="dashboard">
    <div v-if="loading" class="loader">
      Analizando tus datos financieros...
    </div>
    
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    
    <div v-else-if="analysis" class="content">
      <!-- Predicciones -->
      <section class="predictions">
        <h2>📊 Predicciones</h2>
        <div class="card-grid">
          <div 
            v-for="(amount, category) in analysis.data.prediccion.categoria"
            :key="category"
            class="card"
          >
            <h3>{{ category }}</h3>
            <p class="amount">${{ amount.toFixed(2) }}</p>
          </div>
        </div>
      </section>

      <!-- Ahorro -->
      <section class="savings">
        <h2>💰 Ahorro</h2>
        <div class="health-score">
          {{ analysis.data.ahorro.health_score }}%
        </div>
        <ul>
          <li v-for="tip in analysis.data.ahorro.tips" :key="tip">
            ✓ {{ tip }}
          </li>
        </ul>
      </section>
    </div>

    <button @click="handleAnalysis" :disabled="loading">
      Analizar
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { FinancialAI } from '@/lib/financial_ai_sdk';

const analysis = ref(null);
const loading = ref(false);
const error = ref(null);

const ai = new FinancialAI({
  apiUrl: import.meta.env.VITE_API_URL,
  token: localStorage.getItem('token')
});

async function handleAnalysis() {
  loading.value = true;
  error.value = null;
  
  try {
    analysis.value = await ai.fullAnalysis();
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.dashboard {
  padding: 2rem;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.card {
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.amount {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2ecc71;
}

button {
  padding: 0.5rem 1rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
```

---

## 📱 INTEGRACIÓN MOBILE

### Flutter/Dart

```dart
// lib/services/financial_ai_service.dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class FinancialAIClient {
  final String apiUrl;
  final String token;
  
  FinancialAIClient({
    required this.apiUrl,
    required this.token,
  });
  
  Map<String, String> get headers => {
    'Authorization': 'Bearer $token',
    'Content-Type': 'application/json',
  };
  
  Future<Map<String, dynamic>> fullAnalysis() async {
    final response = await http.post(
      Uri.parse('$apiUrl/api/v2/analysis/full'),
      headers: headers,
    ).timeout(const Duration(seconds: 30));
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to load analysis: ${response.statusCode}');
    }
  }
  
  Future<Map<String, dynamic>> quickAnalysis() async {
    final response = await http.post(
      Uri.parse('$apiUrl/api/v2/analysis/quick'),
      headers: headers,
    ).timeout(const Duration(seconds: 5));
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to load quick analysis');
    }
  }
}

// lib/screens/dashboard_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/financial_ai_service.dart';

class DashboardScreen extends StatefulWidget {
  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  late Future<Map<String, dynamic>> _analysisFuture;
  
  @override
  void initState() {
    super.initState();
    final token = /* obtener token */;
    final client = FinancialAIClient(
      apiUrl: 'http://localhost:5000',
      token: token,
    );
    _analysisFuture = client.fullAnalysis();
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Análisis Financiero')),
      body: FutureBuilder<Map<String, dynamic>>(
        future: _analysisFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return Center(child: CircularProgressIndicator());
          }
          
          if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          }
          
          final analysis = snapshot.data!;
          final data = analysis['data'] as Map<String, dynamic>;
          final ahorro = data['ahorro'] as Map<String, dynamic>;
          
          return ListView(
            children: [
              Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Salud Financiera',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      SizedBox(height: 8),
                      LinearProgressIndicator(
                        value: (ahorro['health_score'] as num).toDouble() / 100,
                      ),
                      SizedBox(height: 8),
                      Text('${ahorro['health_score']}%'),
                    ],
                  ),
                ),
              ),
              SizedBox(height: 16),
              Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Recomendaciones',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      SizedBox(height: 8),
                      ...(ahorro['tips'] as List<dynamic>)
                          .map((tip) => Padding(
                            padding: EdgeInsets.symmetric(vertical: 4),
                            child: Text('✓ $tip'),
                          )),
                    ],
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
```

---

## 🐍 INTEGRACIÓN BACKEND

### Python

```python
# main.py
from financial_ai_sdk import FinancialAI

# Configurar cliente
ai = FinancialAI(
    api_url='http://localhost:5000',
    token=os.getenv('API_TOKEN')
)

# Uso en endpoint Flask
@app.route('/dashboard')
def dashboard():
    try:
        # Obtener análisis completo
        analysis = ai.full_analysis()
        
        # Procesar datos
        prediction = analysis['data']['prediccion']
        savings = analysis['data']['ahorro']
        
        # Guardar en base de datos
        save_to_db({
            'usuario_id': analysis['data']['usuario_id'],
            'health_score': savings['health_score'],
            'timestamp': analysis['meta']['timestamp']
        })
        
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Procesamiento asíncrono
@app.route('/analysis/background')
def background_analysis():
    # Encolar análisis profundo
    result = ai.queue_analysis()
    job_id = result['data']['job_id']
    
    # Guardar job_id para seguimiento
    save_job_id(job_id)
    
    return jsonify({'job_id': job_id})

# Verificar estado del job
def check_analysis_status(job_id):
    result = ai.check_job(job_id)
    return result['data']
```

---

## 🧪 TESTING

### Jest (JavaScript)

```javascript
// __tests__/financial_ai_sdk.test.js
import { FinancialAI } from '../lib/financial_ai_sdk';

describe('FinancialAI SDK', () => {
  let ai;
  
  beforeEach(() => {
    ai = new FinancialAI({
      apiUrl: 'http://localhost:5000',
      token: 'test-token'
    });
  });
  
  test('should perform quick analysis', async () => {
    const result = await ai.quickAnalysis();
    expect(result.success).toBe(true);
    expect(result.data.prediccion).toBeDefined();
    expect(result.meta.nivel).toBe('quick');
  });
  
  test('should perform full analysis', async () => {
    const result = await ai.fullAnalysis();
    expect(result.success).toBe(true);
    expect(result.data.prediccion).toBeDefined();
    expect(result.data.ahorro).toBeDefined();
    expect(result.data.estadisticas).toBeDefined();
    expect(result.data.graficos).toBeDefined();
  });
});
```

### Pytest (Python)

```python
# tests/test_financial_ai.py
import pytest
from financial_ai_sdk import FinancialAI

@pytest.fixture
def ai_client():
    return FinancialAI(
        api_url='http://localhost:5000',
        token='test-token'
    )

def test_quick_analysis(ai_client):
    result = ai_client.quick_analysis()
    assert result['success'] == True
    assert 'data' in result
    assert result['meta']['nivel'] == 'quick'

def test_full_analysis(ai_client):
    result = ai_client.full_analysis()
    assert result['success'] == True
    assert 'prediccion' in result['data']
    assert 'ahorro' in result['data']
    assert 'estadisticas' in result['data']

def test_queue_analysis(ai_client):
    result = ai_client.queue_analysis()
    assert 'job_id' in result['data']
    job_id = result['data']['job_id']
    
    status = ai_client.check_job(job_id)
    assert status['data']['status'] in ['queued', 'processing', 'completed']
```

---

## 🆘 TROUBLESHOOTING

### Error: "401 Unauthorized"
```
Problema: Token inválido o expirado
Solución: Obtén un nuevo token
```

### Error: "Network error or API unreachable"
```
Problema: API no está disponible
Solución: Verifica que el servidor está corriendo
$ python app.py
```

### Error: "Timeout"
```
Problema: Análisis toma demasiado tiempo
Solución: Usa análisis asíncrono (queue)
```

### Error: "CORS issue"
```
Problema: Headers CORS no configurados
Solución: Verifica corsconfig.py
```

---

## 📊 CASOS DE USO

### 1. Dashboard en tiempo real
```javascript
setInterval(async () => {
  const analysis = await ai.quickAnalysis();
  updateDashboard(analysis.data);
}, 30000); // Cada 30 segundos
```

### 2. Análisis profundo en background
```javascript
const jobResult = await ai.queueAnalysis();
// Esperar sin bloquear la UI
ai.waitForJob(jobResult.data.job_id).then(result => {
  notifyUser('Análisis completado!', result);
});
```

### 3. Predicción personalizada
```javascript
const analysis = await ai.fullAnalysis();
const prediction = analysis.data.prediccion;
renderCharts(prediction);
```

---

## ✅ CHECKLIST

- [ ] API corriendo en http://localhost:5000
- [ ] Token JWT válido
- [ ] SDK copiado a tu proyecto
- [ ] Endpoint POST /api/v2/analysis/quick testeado
- [ ] Endpoint POST /api/v2/analysis/full testeado
- [ ] App conectando exitosamente
- [ ] Datos mostrándose en UI
- [ ] Errores siendo manejados
- [ ] Tests pasando
- [ ] Documentación actualizada

---

## 📞 SOPORTE

¿Problemas? Verifica:
1. Logs de la API: `python -u app.py`
2. Network tab en DevTools
3. Token en localStorage: `localStorage.getItem('token')`
4. CORS headers: `curl -i http://localhost:5000/api/v2/analysis/quick`

