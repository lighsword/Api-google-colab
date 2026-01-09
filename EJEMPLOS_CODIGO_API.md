# 💻 Ejemplos de Código - API Gestor Financiero IA

Ejemplos de integración en diferentes lenguajes de programación.

---

## 🐍 Python

### Instalación
```bash
pip install requests
```

### 1. Obtener Token y Hacer Request

```python
import requests
import json

# Configuración base
BASE_URL = "https://api-google-colab.onrender.com"
USER_ID = "abc123xyz789"

# 1. Obtener token
def obtener_token(user_id):
    url = f"{BASE_URL}/api/v2/auth/token"
    payload = {"user_id": user_id}
    
    response = requests.post(url, json=payload)
    data = response.json()
    
    if data["status"] == "success":
        print(f"✅ Token obtenido: {data['token'][:50]}...")
        return data["token"]
    else:
        print(f"❌ Error: {data.get('error')}")
        return None

# 2. Obtener predicción por categoría
def obtener_prediccion_categoria(token):
    url = f"{BASE_URL}/api/v2/predict-category"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Usar datos de Firebase (body vacío)
    response = requests.post(url, headers=headers, json={})
    data = response.json()
    
    if data["status"] == "success":
        print(f"✅ Predicción obtenida")
        print(f"Categorías encontradas: {list(data['data'].keys())}")
        
        # Mostrar predicción de Comida
        if "Comida" in data["data"]:
            comida = data["data"]["Comida"]
            print(f"Total predicho en Comida: ${comida['total']:.2f}")
            print(f"Promedio diario: ${comida['promedio_diario']:.2f}")
    else:
        print(f"❌ Error: {data.get('error')}")
    
    return data

# 3. Crear un nuevo gasto
def crear_gasto(token, usuario_id, categoria, cantidad, descripcion):
    url = f"{BASE_URL}/api/v2/firebase/users/{usuario_id}/gastos"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "categoria": categoria,
        "cantidad": cantidad,
        "descripcion": descripcion
    }
    
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    
    if data["status"] == "success":
        print(f"✅ Gasto creado: ID {data['gasto_id']}")
    else:
        print(f"❌ Error: {data.get('error')}")
    
    return data

# 4. Obtener análisis completo
def obtener_analisis_completo(token, usuario_id):
    url = f"{BASE_URL}/api/v2/firebase/users/{usuario_id}/asesor-financiero"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    if data["status"] == "success":
        print(f"✅ Análisis completo obtenido")
        # Procesar datos según necesidad
    else:
        print(f"❌ Error: {data.get('error')}")
    
    return data

# Uso
if __name__ == "__main__":
    # 1. Obtener token
    token = obtener_token(USER_ID)
    
    if token:
        # 2. Crear un gasto
        crear_gasto(token, USER_ID, "Comida", 150.50, "Almuerzo italiano")
        
        # 3. Obtener predicciones
        obtener_prediccion_categoria(token)
        
        # 4. Obtener análisis completo
        obtener_analisis_completo(token, USER_ID)
```

### 2. Enviar Array de Gastos Manual

```python
def analizar_gastos_manual(token, gastos):
    """
    Analiza un array de gastos enviado manualmente
    
    Args:
        token: JWT token de autenticación
        gastos: Lista de diccionarios con gastos
                [{"fecha": "2026-01-08", "monto": 150.50, "categoria": "Comida"}, ...]
    """
    url = f"{BASE_URL}/api/v2/predict-category"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {"expenses": gastos}
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Ejemplo de uso
gastos_ejemplo = [
    {"fecha": "2026-01-08", "monto": 95.50, "categoria": "Comida", "descripcion": "Desayuno"},
    {"fecha": "2026-01-08", "monto": 42.00, "categoria": "Transporte", "descripcion": "Metro"},
    {"fecha": "2026-01-07", "monto": 180.00, "categoria": "Comida", "descripcion": "Cena"},
    {"fecha": "2026-01-07", "monto": 35.00, "categoria": "Transporte", "descripcion": "Uber"},
    {"fecha": "2026-01-06", "monto": 250.00, "categoria": "Entretenimiento", "descripcion": "Cine"},
]

token = obtener_token(USER_ID)
resultado = analizar_gastos_manual(token, gastos_ejemplo)
print(json.dumps(resultado, indent=2))
```

### 3. Establecer Meta de Ahorro

```python
def crear_meta_ahorro(token, nombre, monto, meses):
    """
    Crea una meta de ahorro personalizada
    
    Args:
        token: JWT token
        nombre: Nombre de la meta (ej: "Vacaciones")
        monto: Cantidad objetivo (ej: 8000)
        meses: Plazo en meses (ej: 12)
    """
    url = f"{BASE_URL}/api/v2/savings/goals"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "goal_name": nombre,
        "target_amount": monto,
        "months": meses
    }
    
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    
    if data["status"] == "success":
        meta = data["data"]["meta"]
        viabilidad = data["data"]["viabilidad"]
        
        print(f"🎯 Meta: {meta['nombre']}")
        print(f"💰 Objetivo: ${meta['monto_objetivo']:.2f}")
        print(f"📅 Plazo: {meta['meses']} meses")
        print(f"💵 Ahorro mensual requerido: ${meta['ahorro_mensual_requerido']:.2f}")
        print(f"✅ Alcanzable: {viabilidad['es_alcanzable']}")
        print(f"📊 Confianza: {viabilidad['confianza']}")
    
    return data

# Ejemplo de uso
token = obtener_token(USER_ID)
crear_meta_ahorro(token, "Vacaciones en Europa", 8000, 12)
```

---

## 🟨 JavaScript (Node.js)

### Instalación
```bash
npm install axios
```

### 1. Cliente API Completo

```javascript
const axios = require('axios');

const BASE_URL = 'https://api-google-colab.onrender.com';
const USER_ID = 'abc123xyz789';

class GestorFinancieroAPI {
  constructor() {
    this.baseURL = BASE_URL;
    this.token = null;
  }

  // 1. Obtener token
  async obtenerToken(userId = USER_ID) {
    try {
      const response = await axios.post(`${this.baseURL}/api/v2/auth/token`, {
        user_id: userId
      });
      
      if (response.data.status === 'success') {
        this.token = response.data.token;
        console.log('✅ Token obtenido correctamente');
        return this.token;
      }
    } catch (error) {
      console.error('❌ Error obteniendo token:', error.message);
      throw error;
    }
  }

  // 2. Headers con autenticación
  getHeaders() {
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json'
    };
  }

  // 3. Obtener predicción por categoría
  async obtenerPrediccionCategoria() {
    try {
      const response = await axios.post(
        `${this.baseURL}/api/v2/predict-category`,
        {}, // Body vacío para usar Firebase
        { headers: this.getHeaders() }
      );
      
      if (response.data.status === 'success') {
        console.log('✅ Predicción obtenida');
        return response.data.data;
      }
    } catch (error) {
      console.error('❌ Error:', error.response?.data || error.message);
      throw error;
    }
  }

  // 4. Crear nuevo gasto
  async crearGasto(usuarioId, categoria, cantidad, descripcion) {
    try {
      const response = await axios.post(
        `${this.baseURL}/api/v2/firebase/users/${usuarioId}/gastos`,
        {
          categoria,
          cantidad,
          descripcion
        },
        { headers: this.getHeaders() }
      );
      
      if (response.data.status === 'success') {
        console.log(`✅ Gasto creado: ${response.data.gasto_id}`);
        return response.data;
      }
    } catch (error) {
      console.error('❌ Error creando gasto:', error.response?.data || error.message);
      throw error;
    }
  }

  // 5. Obtener gastos del usuario
  async obtenerGastos(usuarioId) {
    try {
      const response = await axios.get(
        `${this.baseURL}/api/v2/firebase/users/${usuarioId}/gastos`,
        { headers: this.getHeaders() }
      );
      
      if (response.data.status === 'success') {
        console.log(`✅ ${response.data.total} gastos obtenidos`);
        return response.data.data;
      }
    } catch (error) {
      console.error('❌ Error obteniendo gastos:', error.response?.data || error.message);
      throw error;
    }
  }

  // 6. Detectar anomalías
  async detectarAnomalias() {
    try {
      const response = await axios.post(
        `${this.baseURL}/api/v2/detect-anomalies`,
        {},
        { headers: this.getHeaders() }
      );
      
      if (response.data.status === 'success') {
        const { cantidad, porcentaje, anomalias } = response.data.data;
        console.log(`✅ ${cantidad} anomalías detectadas (${porcentaje}%)`);
        return anomalias;
      }
    } catch (error) {
      console.error('❌ Error detectando anomalías:', error.response?.data || error.message);
      throw error;
    }
  }

  // 7. Crear meta de ahorro
  async crearMetaAhorro(nombre, monto, meses) {
    try {
      const response = await axios.post(
        `${this.baseURL}/api/v2/savings/goals`,
        {
          goal_name: nombre,
          target_amount: monto,
          months: meses
        },
        { headers: this.getHeaders() }
      );
      
      if (response.data.status === 'success') {
        const { meta, viabilidad } = response.data.data;
        console.log(`🎯 Meta: ${meta.nombre}`);
        console.log(`💵 Ahorro mensual: $${meta.ahorro_mensual_requerido.toFixed(2)}`);
        console.log(`✅ Alcanzable: ${viabilidad.es_alcanzable}`);
        return response.data.data;
      }
    } catch (error) {
      console.error('❌ Error creando meta:', error.response?.data || error.message);
      throw error;
    }
  }

  // 8. Análisis completo
  async obtenerAnalisisCompleto(usuarioId) {
    try {
      const response = await axios.get(
        `${this.baseURL}/api/v2/firebase/users/${usuarioId}/asesor-financiero`,
        { headers: this.getHeaders() }
      );
      
      if (response.data.status === 'success') {
        console.log('✅ Análisis completo obtenido');
        return response.data.data;
      }
    } catch (error) {
      console.error('❌ Error obteniendo análisis:', error.response?.data || error.message);
      throw error;
    }
  }
}

// Uso del cliente
async function main() {
  const api = new GestorFinancieroAPI();
  
  try {
    // 1. Obtener token
    await api.obtenerToken(USER_ID);
    
    // 2. Crear un gasto
    await api.crearGasto(
      USER_ID,
      'Comida',
      150.50,
      'Almuerzo en restaurante italiano'
    );
    
    // 3. Obtener gastos
    const gastos = await api.obtenerGastos(USER_ID);
    console.log(`Total de gastos: ${gastos.length}`);
    
    // 4. Obtener predicciones
    const prediccion = await api.obtenerPrediccionCategoria();
    console.log('Categorías predichas:', Object.keys(prediccion));
    
    // 5. Detectar anomalías
    const anomalias = await api.detectarAnomalias();
    
    // 6. Crear meta de ahorro
    await api.crearMetaAhorro('Vacaciones en Europa', 8000, 12);
    
    // 7. Análisis completo
    const analisis = await api.obtenerAnalisisCompleto(USER_ID);
    
  } catch (error) {
    console.error('Error en flujo principal:', error.message);
  }
}

// Ejecutar
main();
```

---

## 🌐 JavaScript (Fetch API - Browser)

```javascript
const BASE_URL = 'https://api-google-colab.onrender.com';
const USER_ID = 'abc123xyz789';

// 1. Obtener token
async function obtenerToken(userId) {
  try {
    const response = await fetch(`${BASE_URL}/api/v2/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ user_id: userId })
    });
    
    const data = await response.json();
    
    if (data.status === 'success') {
      localStorage.setItem('api_token', data.token);
      console.log('✅ Token guardado');
      return data.token;
    } else {
      throw new Error(data.error);
    }
  } catch (error) {
    console.error('❌ Error:', error);
    throw error;
  }
}

// 2. Crear gasto
async function crearGasto(categoria, cantidad, descripcion) {
  const token = localStorage.getItem('api_token');
  
  try {
    const response = await fetch(
      `${BASE_URL}/api/v2/firebase/users/${USER_ID}/gastos`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          categoria,
          cantidad,
          descripcion
        })
      }
    );
    
    const data = await response.json();
    
    if (data.status === 'success') {
      console.log('✅ Gasto creado:', data.gasto_id);
      return data;
    } else {
      throw new Error(data.error);
    }
  } catch (error) {
    console.error('❌ Error:', error);
    throw error;
  }
}

// 3. Obtener predicciones
async function obtenerPredicciones() {
  const token = localStorage.getItem('api_token');
  
  try {
    const response = await fetch(
      `${BASE_URL}/api/v2/predict-category`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      }
    );
    
    const data = await response.json();
    
    if (data.status === 'success') {
      console.log('✅ Predicciones obtenidas');
      return data.data;
    } else {
      throw new Error(data.error);
    }
  } catch (error) {
    console.error('❌ Error:', error);
    throw error;
  }
}

// Uso en página web
document.addEventListener('DOMContentLoaded', async () => {
  // Obtener o renovar token
  const token = await obtenerToken(USER_ID);
  
  // Crear gasto desde formulario
  const formGasto = document.getElementById('formGasto');
  formGasto.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const categoria = document.getElementById('categoria').value;
    const cantidad = parseFloat(document.getElementById('cantidad').value);
    const descripcion = document.getElementById('descripcion').value;
    
    await crearGasto(categoria, cantidad, descripcion);
    alert('Gasto creado exitosamente');
  });
  
  // Obtener predicciones
  const btnPredicciones = document.getElementById('btnPredicciones');
  btnPredicciones.addEventListener('click', async () => {
    const predicciones = await obtenerPredicciones();
    mostrarPredicciones(predicciones);
  });
});

function mostrarPredicciones(predicciones) {
  const container = document.getElementById('prediccionesContainer');
  container.innerHTML = '';
  
  for (const [categoria, datos] of Object.entries(predicciones)) {
    const div = document.createElement('div');
    div.className = 'prediccion-card';
    div.innerHTML = `
      <h3>${categoria}</h3>
      <p>Total predicho: $${datos.total.toFixed(2)}</p>
      <p>Promedio diario: $${datos.promedio_diario.toFixed(2)}</p>
    `;
    container.appendChild(div);
  }
}
```

---

## 🔵 C# (.NET)

```csharp
using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

public class GestorFinancieroClient
{
    private readonly HttpClient _httpClient;
    private readonly string _baseUrl;
    private string _token;

    public GestorFinancieroClient(string baseUrl = "https://api-google-colab.onrender.com")
    {
        _baseUrl = baseUrl;
        _httpClient = new HttpClient();
    }

    // 1. Obtener token
    public async Task<string> ObtenerTokenAsync(string userId)
    {
        var payload = new { user_id = userId };
        var content = new StringContent(
            JsonSerializer.Serialize(payload),
            Encoding.UTF8,
            "application/json"
        );

        var response = await _httpClient.PostAsync($"{_baseUrl}/api/v2/auth/token", content);
        var json = await response.Content.ReadAsStringAsync();
        var result = JsonSerializer.Deserialize<TokenResponse>(json);

        if (result.status == "success")
        {
            _token = result.token;
            Console.WriteLine("✅ Token obtenido");
            return _token;
        }

        throw new Exception($"Error: {result.error}");
    }

    // 2. Crear gasto
    public async Task<GastoResponse> CrearGastoAsync(
        string usuarioId,
        string categoria,
        decimal cantidad,
        string descripcion
    )
    {
        var payload = new
        {
            categoria,
            cantidad,
            descripcion
        };

        var request = new HttpRequestMessage(HttpMethod.Post,
            $"{_baseUrl}/api/v2/firebase/users/{usuarioId}/gastos");
        
        request.Headers.Add("Authorization", $"Bearer {_token}");
        request.Content = new StringContent(
            JsonSerializer.Serialize(payload),
            Encoding.UTF8,
            "application/json"
        );

        var response = await _httpClient.SendAsync(request);
        var json = await response.Content.ReadAsStringAsync();
        var result = JsonSerializer.Deserialize<GastoResponse>(json);

        if (result.status == "success")
        {
            Console.WriteLine($"✅ Gasto creado: {result.gasto_id}");
        }

        return result;
    }

    // 3. Obtener predicciones
    public async Task<PrediccionResponse> ObtenerPrediccionesAsync()
    {
        var request = new HttpRequestMessage(HttpMethod.Post,
            $"{_baseUrl}/api/v2/predict-category");
        
        request.Headers.Add("Authorization", $"Bearer {_token}");
        request.Content = new StringContent(
            "{}",
            Encoding.UTF8,
            "application/json"
        );

        var response = await _httpClient.SendAsync(request);
        var json = await response.Content.ReadAsStringAsync();
        var result = JsonSerializer.Deserialize<PrediccionResponse>(json);

        if (result.status == "success")
        {
            Console.WriteLine("✅ Predicciones obtenidas");
        }

        return result;
    }
}

// Modelos
public class TokenResponse
{
    public string status { get; set; }
    public string token { get; set; }
    public string error { get; set; }
}

public class GastoResponse
{
    public string status { get; set; }
    public string gasto_id { get; set; }
    public string message { get; set; }
}

public class PrediccionResponse
{
    public string status { get; set; }
    public Dictionary<string, CategoriaPrediccion> data { get; set; }
}

public class CategoriaPrediccion
{
    public decimal total { get; set; }
    public decimal promedio_diario { get; set; }
}

// Uso
class Program
{
    static async Task Main(string[] args)
    {
        var client = new GestorFinancieroClient();
        var userId = "abc123xyz789";

        try
        {
            // 1. Obtener token
            await client.ObtenerTokenAsync(userId);

            // 2. Crear gasto
            await client.CrearGastoAsync(
                userId,
                "Comida",
                150.50m,
                "Almuerzo italiano"
            );

            // 3. Obtener predicciones
            var predicciones = await client.ObtenerPrediccionesAsync();

            Console.WriteLine("Predicciones por categoría:");
            foreach (var (categoria, datos) in predicciones.data)
            {
                Console.WriteLine($"  {categoria}: ${datos.total:F2}");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Error: {ex.Message}");
        }
    }
}
```

---

## 🛠️ cURL (Línea de Comandos)

### Variables de entorno
```bash
export API_URL="https://api-google-colab.onrender.com"
export USER_ID="abc123xyz789"
```

### 1. Obtener token
```bash
TOKEN=$(curl -s -X POST "$API_URL/api/v2/auth/token" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"$USER_ID\"}" \
  | jq -r '.token')

echo "Token: $TOKEN"
```

### 2. Crear gasto
```bash
curl -X POST "$API_URL/api/v2/firebase/users/$USER_ID/gastos" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "categoria": "Comida",
    "cantidad": 150.50,
    "descripcion": "Almuerzo italiano"
  }'
```

### 3. Obtener predicciones
```bash
curl -X POST "$API_URL/api/v2/predict-category" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' \
  | jq '.'
```

### 4. Obtener análisis completo
```bash
curl -X GET "$API_URL/api/v2/firebase/users/$USER_ID/asesor-financiero" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.'
```

---

Para más información consulta la [Guía de Ejemplos API](./GUIA_EJEMPLOS_API.md)
