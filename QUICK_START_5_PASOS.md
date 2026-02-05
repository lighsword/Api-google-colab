# 🚀 QUICK START - IMPLEMENTACIÓN EN 5 PASOS

## ⚡ TL;DR (Too Long; Didn't Read)

Tu API tiene **21 endpoints POST dispersos**. Ahora los consolidamos en **3 endpoints** que tu app usa así:

```javascript
// Antes: 21 requests
await fetch('/api/v2/predict-category');
await fetch('/api/v2/predict-monthly');
// ... 19 más

// Ahora: 1 request ✅
const analysis = await ai.fullAnalysis();
```

---

## 🎯 PASO 1: ENTIENDE LA ESTRUCTURA (5 min)

### Tu API ahora es así:

```
┌─────────────────────────────────────────────────┐
│  API FINANCIERA CONSOLIDADA                     │
├─────────────────────────────────────────────────┤
│                                                 │
│  POST /api/v2/analysis/quick        (< 2s)    │
│  ├─ Predicción básica               │         │
│  └─ Estadísticas rápidas            │ ← 1 REQ │
│                                      │         │
│  POST /api/v2/analysis/full         (2-5s)   │
│  ├─ Predicción completa             │         │
│  ├─ Estadísticas completas          │ ← 1 REQ │
│  ├─ Recomendaciones de ahorro       │         │
│  └─ Datos para gráficos             │         │
│                                      │         │
│  POST /api/v2/analysis/queue        (async)  │
│  ├─ Análisis profundo sin bloqueo   │         │
│  └─ Procesa en background           │ ← 1 REQ │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 📦 PASO 2: COPIAR LOS 3 ARCHIVOS (10 min)

### Descarga estos archivos del proyecto:

1. **financial_ai_sdk.py** - SDK Python
2. **financial_ai_sdk.ts** - SDK JavaScript/TypeScript
3. **API_MEJORADA.py** - Tu API actualizada

### O copia el código directamente:

```bash
# Posición en tu proyecto
tu-app/
├── backend/
│   ├── financial_ai_sdk.py          ← Copiar aquí
│   └── app.py
│
└── frontend/
    ├── src/
    │   ├── lib/
    │   │   └── financial_ai_sdk.ts  ← Copiar aquí
    │   └── App.jsx
    └── package.json
```

---

## 🔌 PASO 3: CONECTAR TU APP (15 min)

### React (Opción más común)

```jsx
// 1. Importar SDK
import { FinancialAI } from '@/lib/financial_ai_sdk';

// 2. Crear hook personalizado
function useAnalysis() {
  const [data, setData] = React.useState(null);
  const [loading, setLoading] = React.useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const ai = new FinancialAI({
        apiUrl: 'http://localhost:5000',
        token: localStorage.getItem('token')
      });
      const result = await ai.fullAnalysis();
      setData(result);
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, load };
}

// 3. Usar en tu componente
function Dashboard() {
  const { data, loading, load } = useAnalysis();

  React.useEffect(() => {
    load();
  }, []);

  if (loading) return <div>Cargando...</div>;
  if (!data) return null;

  const { prediccion, ahorro } = data.data;

  return (
    <div>
      <h1>Salud: {ahorro.health_score}%</h1>
      <p>Gastos: ${Object.values(prediccion.categoria).reduce((a, b) => a + b, 0)}</p>
    </div>
  );
}
```

### Flutter

```dart
// 1. Crear cliente
final ai = FinancialAIClient(
  apiUrl: 'http://localhost:5000',
  token: token
);

// 2. Usar en Widget
class Dashboard extends StatefulWidget {
  @override
  _DashboardState createState() => _DashboardState();
}

class _DashboardState extends State<Dashboard> {
  late Future<Map> analysis;

  @override
  void initState() {
    super.initState();
    analysis = ai.fullAnalysis();
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Map>(
      future: analysis,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return Center(child: CircularProgressIndicator());
        }
        final data = snapshot.data!['data'];
        return Column(
          children: [
            Text('Salud: ${data['ahorro']['health_score']}%'),
          ],
        );
      },
    );
  }
}
```

### Python

```python
from financial_ai_sdk import FinancialAI

ai = FinancialAI(
    api_url='http://localhost:5000',
    token='tu_token'
)

# Uso simple
result = ai.full_analysis()
print(result['data']['ahorro']['health_score'])
```

---

## 🧪 PASO 4: TESTEAR (10 min)

### Test con CURL

```bash
# Test 1: Quick analysis (rápido)
curl -X POST http://localhost:5000/api/v2/analysis/quick \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# Debería retornar en < 2 segundos
# Response:
# {
#   "success": true,
#   "data": {
#     "usuario_id": "user_123",
#     "prediccion": {...},
#     "estadisticas": {...}
#   },
#   "meta": {
#     "processing_time_ms": 1240,
#     "nivel": "quick"
#   }
# }

# Test 2: Full analysis (completo)
curl -X POST http://localhost:5000/api/v2/analysis/full \
  -H "Authorization: Bearer YOUR_TOKEN"

# Debería retornar en 2-5 segundos
# Response completo con predicción + ahorro + gráficos

# Test 3: Queue analysis (asíncrono)
curl -X POST http://localhost:5000/api/v2/analysis/queue \
  -H "Authorization: Bearer YOUR_TOKEN"

# Retorna job_id inmediatamente
# Response:
# {
#   "data": {
#     "job_id": "job_abc123",
#     "status": "queued"
#   }
# }

# Luego verificar estado
curl -X GET http://localhost:5000/api/v2/analysis/job/job_abc123 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test en JavaScript

```javascript
// test.js
const ai = new FinancialAI({
  apiUrl: 'http://localhost:5000',
  token: 'your_token'
});

// Test 1
console.log('Quick analysis...');
ai.quickAnalysis().then(result => {
  console.log('✅ Success:', result.meta.processing_time_ms, 'ms');
});

// Test 2
console.log('Full analysis...');
ai.fullAnalysis().then(result => {
  console.log('✅ Success:', result.data.ahorro.health_score, '%');
});

// Test 3
console.log('Queue analysis...');
ai.queueAnalysis().then(result => {
  const jobId = result.data.job_id;
  console.log('Job enqueued:', jobId);
  
  // Esperar a que termine
  ai.waitForJob(jobId).then(resultado => {
    console.log('✅ Completado:', resultado);
  });
});
```

---

## 📊 PASO 5: IMPLEMENTAR CASOS DE USO (Variable)

### Caso Simple: Dashboard (1 hora)

```jsx
// App.jsx
import { FinancialAI } from './lib/financial_ai_sdk';

export function App() {
  const [analysis, setAnalysis] = React.useState(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    const ai = new FinancialAI({
      apiUrl: 'http://localhost:5000',
      token: localStorage.getItem('token')
    });

    ai.quickAnalysis()
      .then(setAnalysis)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loader" />;
  if (!analysis?.data) return <div>Error</div>;

  const { data, meta } = analysis;

  return (
    <div className="app">
      <h1>💰 Tu Finanzas</h1>
      
      <div className="health-card">
        <h2>Salud Financiera</h2>
        <div className="score">{data.ahorro.health_score}%</div>
      </div>

      <div className="spending-grid">
        {Object.entries(data.prediccion.categoria || {}).map(([cat, amount]) => (
          <div key={cat} className="category-card">
            <h3>{cat}</h3>
            <p>${amount.toFixed(2)}</p>
          </div>
        ))}
      </div>

      <div className="tips">
        <h3>💡 Recomendaciones</h3>
        <ul>
          {data.ahorro.tips?.map((tip, i) => (
            <li key={i}>✓ {tip}</li>
          ))}
        </ul>
      </div>

      <p className="meta">Procesado en {meta.processing_time_ms}ms</p>
    </div>
  );
}
```

### Caso Intermedio: Alertas (2 horas)

```python
from financial_ai_sdk import FinancialAI
from apscheduler.schedulers.background import BackgroundScheduler

ai = FinancialAI(api_url='http://localhost:5000', token=TOKEN)

@app.route('/monitor/start', methods=['POST'])
def start_monitoring():
    """Iniciar monitoreo de anomalías"""
    scheduler = BackgroundScheduler()
    
    @scheduler.scheduled_job('interval', minutes=5)
    def check_anomalies():
        analysis = ai.quick_analysis()
        anomalies = analysis['data']['prediccion'].get('anomalias', {})
        
        if anomalies.get('detectadas', 0) > 0:
            send_notification(
                f"⚠️ {anomalies['detectadas']} gastos anómalos detectados"
            )
    
    scheduler.start()
    return {'status': 'monitoring_started'}
```

### Caso Avanzado: Análisis Profundo (4 horas)

```python
@app.route('/analysis/weekly', methods=['POST'])
def generate_weekly_report():
    """Generar reporte semanal profundo"""
    
    # Encolar análisis asíncrono
    job = ai.queue_analysis()
    job_id = job['data']['job_id']
    
    # Guardar en DB
    Report.create(
        job_id=job_id,
        tipo='weekly',
        estado='processing'
    )
    
    # En background, ejecutar cuando esté listo
    def send_report_when_ready():
        time.sleep(2)  # Esperar
        
        status = ai.check_job(job_id)
        if status['data']['status'] == 'completed':
            resultado = status['data']['resultado']
            
            # Generar PDF con matplotlib
            pdf = generate_report_pdf(resultado)
            
            # Enviar email
            send_email(
                to='user@email.com',
                subject='Reporte Financiero Semanal',
                attachment=pdf
            )
            
            # Actualizar DB
            Report.update({'job_id': job_id}, {'estado': 'completed'})
    
    # Ejecutar en background
    threading.Thread(target=send_report_when_ready).start()
    
    return {'job_id': job_id, 'status': 'processing'}
```

---

## ✅ CHECKLIST FINAL

- [ ] Entendí que ahora hay 3 endpoints en lugar de 21
- [ ] Copié los SDK a mi proyecto
- [ ] Testeé con curl - todos retornan datos correctos
- [ ] Conecté mi app (React/Flutter/Python)
- [ ] Dashboard funciona y muestra datos
- [ ] Puedo ver cambios en tiempo real
- [ ] El tiempo de respuesta es < 5 segundos
- [ ] Los errores se manejan correctamente
- [ ] Documentación está clara

---

## 🎁 BONUS: OPTIMIZACIONES

### Caché Local

```javascript
// Guardar resultado en localStorage por 5 minutos
const cacheAnalysis = (result) => {
  localStorage.setItem('analysis', JSON.stringify({
    data: result,
    timestamp: Date.now()
  }));
};

const getCachedAnalysis = () => {
  const cached = localStorage.getItem('analysis');
  if (!cached) return null;
  
  const { data, timestamp } = JSON.parse(cached);
  const isExpired = Date.now() - timestamp > 5 * 60 * 1000;
  
  return isExpired ? null : data;
};

// Uso
const cached = getCachedAnalysis();
if (cached) {
  setAnalysis(cached);
} else {
  ai.fullAnalysis().then(result => {
    cacheAnalysis(result);
    setAnalysis(result);
  });
}
```

### Refresh Automático

```javascript
// Actualizar cada 30 segundos
setInterval(() => {
  ai.quickAnalysis().then(setAnalysis);
}, 30000);

// O solo cuando gasta el usuario
document.addEventListener('expense-added', async () => {
  const analysis = await ai.quickAnalysis();
  updateUI(analysis);
});
```

### Error Handling

```javascript
async function robustAnalysis() {
  const maxRetries = 3;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await ai.fullAnalysis();
    } catch (error) {
      console.warn(`Attempt ${i + 1} failed:`, error.message);
      
      if (i === maxRetries - 1) throw error;
      
      // Esperar exponencial
      await new Promise(r => 
        setTimeout(r, Math.pow(2, i) * 1000)
      );
    }
  }
}
```

---

## 📞 SOPORTE

| Problema | Solución |
|----------|----------|
| "401 Unauthorized" | Token expirado, obtén uno nuevo |
| "Network error" | API no está corriendo, ejecuta `python app.py` |
| "Timeout" | Análisis toma mucho, usa `queue_analysis()` |
| "CORS error" | Verifica CORS config en API |
| "Empty response" | Verifica que el usuario tiene gastos |

---

## 🚀 PRÓXIMOS PASOS

1. ✅ Lee esta guía (5 min)
2. ✅ Copia los SDKs (5 min)
3. ✅ Testea con curl (10 min)
4. ✅ Conecta tu app (15 min)
5. ✅ Implementa un caso de uso (1-4 horas)

**Tiempo total: 2 horas para un dashboard funcional**

---

## 📚 DOCUMENTACIÓN COMPLETA

Para más detalles, consulta:
- [ARQUITECTURA_ENDPOINTS_PRACTICA.md](ARQUITECTURA_ENDPOINTS_PRACTICA.md)
- [GUIA_IMPLEMENTACION_ENDPOINTS.md](GUIA_IMPLEMENTACION_ENDPOINTS.md)
- [GUIA_INTEGRACION_APP.md](GUIA_INTEGRACION_APP.md)
- [CASOS_PRACTICOS_USO.md](CASOS_PRACTICOS_USO.md)

---

## 🎯 ¿QUÉ QUIERES HACER?

**Opción A:** Dashboard web bonito (React)
→ Sigue [GUIA_INTEGRACION_APP.md](GUIA_INTEGRACION_APP.md) - Sección React

**Opción B:** App móvil (Flutter)
→ Sigue [GUIA_INTEGRACION_APP.md](GUIA_INTEGRACION_APP.md) - Sección Flutter

**Opción C:** Backend Python (Django/FastAPI)
→ Sigue [GUIA_INTEGRACION_APP.md](GUIA_INTEGRACION_APP.md) - Sección Python

**Opción D:** Alertas en tiempo real
→ Sigue [CASOS_PRACTICOS_USO.md](CASOS_PRACTICOS_USO.md) - Caso 3

**Opción E:** Análisis profundo nocturno
→ Sigue [CASOS_PRACTICOS_USO.md](CASOS_PRACTICOS_USO.md) - Caso 2

---

**¡Listo para empezar? Elige tu opción arriba y comienza en 2 horas!** ⚡

