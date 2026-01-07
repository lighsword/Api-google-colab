# 🔥 Configuración de Firebase + CORS para tu API

## ✅ CORS Configurado para Firebase

Tu API ahora está configurada para aceptar solicitudes desde:

### **1. Firebase Hosting** 
- `https://{tu-proyecto}.firebaseapp.com`
- `https://{tu-proyecto}.web.app`

### **2. Desarrollo Local**
- `http://localhost:3000` (React/Next.js)
- `http://localhost:5000` (API)
- `http://localhost:8080` (Otros dev servers)
- `http://127.0.0.1:*` (localhost)

### **3. Producción**
- Cualquier dominio que agregues en `cors_config.py`

---

## 🚀 Cómo Conectar Firebase con tu API

### **Paso 1: Configurar Firebase en tu Cliente**

Si usas React o JavaScript:

```javascript
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "tu-api-key",
  authDomain: "gestor-financiero-28ac2.firebaseapp.com",
  projectId: "gestor-financiero-28ac2",
  storageBucket: "gestor-financiero-28ac2.appspot.com",
  messagingSenderId: "tu-messaging-id",
  appId: "tu-app-id"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
```

### **Paso 2: Obtener Token de la API**

```javascript
// 1. Generar token desde tu API
const getToken = async (userId) => {
  const response = await fetch('https://tu-api.onrender.com/api/v2/auth/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ user_id: userId })
  });
  
  const data = await response.json();
  return data.token;
};

// 2. Guardar el token en localStorage
const token = await getToken('usuario123');
localStorage.setItem('apiToken', token);
```

### **Paso 3: Usar la API en tus Requests**

```javascript
// Con fetch
const callAPI = async (endpoint, method = 'GET', body = null) => {
  const token = localStorage.getItem('apiToken');
  
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: body ? JSON.stringify(body) : null
  };
  
  const response = await fetch(
    `https://tu-api.onrender.com/api/v2${endpoint}`,
    options
  );
  
  return await response.json();
};

// Ejemplo: Obtener predicción de gastos
const prediction = await callAPI('/predict-category', 'POST', {
  expenses: [
    { fecha: '2024-12-15', monto: 100, categoria: 'Comida' },
    { fecha: '2024-12-16', monto: 50, categoria: 'Transporte' }
  ]
});
```

### **Paso 4: Usar con Axios (Alternativa)**

```javascript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'https://tu-api.onrender.com/api/v2',
  headers: {
    'Content-Type': 'application/json',
  }
});

// Agregar token automáticamente
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('apiToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Usar en la app
const prediction = await apiClient.post('/predict-category', {
  expenses: [...]
});
```

---

## 🔐 Headers Requeridos

Todos los requests a tu API deben incluir:

```
Content-Type: application/json
Authorization: Bearer {tu-token}
```

O alternativa:

```
Content-Type: application/json
X-API-Key: {tu-token}
```

---

## ✨ Headers Permitidos por CORS

Tu API permite estos headers:

- `Content-Type` - Tipo de contenido
- `Authorization` - Token JWT
- `X-API-Key` - Clave alternativa
- `Accept` - Tipos aceptados
- `Origin` - Origen de la solicitud
- `X-Requested-With` - Para Ajax
- `User-Agent` - Información del cliente

---

## 🧪 Probar CORS desde el Navegador

Abre la consola del navegador (F12) y prueba:

```javascript
// Test 1: Health check
fetch('https://tu-api.onrender.com/api/v2/health', {
  method: 'GET',
  headers: { 'Content-Type': 'application/json' }
}).then(r => r.json()).then(console.log);

// Test 2: Generar token
fetch('https://tu-api.onrender.com/api/v2/auth/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_id: 'test' })
}).then(r => r.json()).then(console.log);

// Test 3: Con token
const token = 'tu-token-aqui';
fetch('https://tu-api.onrender.com/api/v2/predict-category', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({ expenses: [] })
}).then(r => r.json()).then(console.log);
```

---

## 📋 Modificar CORS para tu Caso Específico

Si necesitas agregar más dominios, edita `cors_config.py`:

```python
ALLOWED_ORIGINS = [
    # Tu Firebase
    "https://tu-proyecto.firebaseapp.com",
    "https://tu-proyecto.web.app",
    
    # Tu cliente en producción
    "https://mi-app.vercel.app",
    "https://mi-dominio.com",
    
    # Desarrollo local
    "http://localhost:3000",
]
```

Luego reinicia la API.

---

## 🚨 Troubleshooting

### Error: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Solución:** 
- Verifica que tu dominio esté en `ALLOWED_ORIGINS`
- Reinicia la API
- Limpia el caché del navegador (Ctrl+Shift+Del)

### Error: "Preflight request failed"

**Solución:**
- Es una solicitud OPTIONS
- Tu API debe responder con headers CORS
- Ya está configurado, prueba desde otro origen

### Error: "Token inválido"

**Solución:**
- Genera un nuevo token con `/api/v2/auth/token`
- Verifica que sea `Bearer {token}` en el header
- El token expira después de 24 horas

### Error: "401 Unauthorized"

**Solución:**
- Verifica que enviaste el header `Authorization`
- El formato debe ser: `Authorization: Bearer {token}`
- Valida el token con `/api/v2/auth/validate`

---

## ✅ Checklist Final

- [ ] CORS instalado (`flask-cors`)
- [ ] CORS configurado en `API_MEJORADA.py`
- [ ] `cors_config.py` actualizado con tus dominios
- [ ] API reiniciada
- [ ] Firebase configurado en el cliente
- [ ] Token generado correctamente
- [ ] Solicitudes incluyen el header `Authorization`
- [ ] ¡Probando desde el navegador! ✨

---

¡Listo! Tu API está conectada con Firebase y CORS habilitado. 🎉
