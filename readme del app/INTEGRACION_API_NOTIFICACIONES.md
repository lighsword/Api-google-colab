# 🔌 INTEGRACIÓN CON API FLASK
# 
# Cómo usar el NotificationsController en API_MEJORADA.py
# Para enviar notificaciones desde la API hacia usuarios Flutter

## 📋 TABLA DE CONTENIDOS

1. [Importar el Controlador](#importar)
2. [Inicializar en la API](#inicializar)
3. [Nuevos Endpoints](#endpoints)
4. [Ejemplo de Uso Completo](#ejemplo)
5. [Integración con Google Colab](#colab)
6. [Testing](#testing)

---

## 🔌 Importar el Controlador {#importar}

En tu `API_MEJORADA.py`, agrega esta importación al inicio:

```python
# En API_MEJORADA.py
from notifications_controller import (
    NotificationsController,
    NotificationType,
    AlertLevel
)
```

---

## ⚙️ Inicializar en la API {#inicializar}

Después de inicializar Firebase, crea una instancia global del controlador:

```python
# En API_MEJORADA.py (después de: db = firestore.client())

from notifications_controller import NotificationsController

# Inicializar controlador de notificaciones
notifications = NotificationsController(db_instance=db)
print("✅ Controlador de notificaciones inicializado")
```

---

## 📤 Nuevos Endpoints {#endpoints}

### Endpoint 1: Enviar Notificación Personalizada

```python
@app.route('/api/notificaciones/enviar', methods=['POST'])
@require_auth
def send_custom_notification():
    """
    Enviar notificación personalizada
    
    Body:
    {
        "usuario_id": "usuario_123",
        "titulo": "Título de la notificación",
        "cuerpo": "Cuerpo del mensaje",
        "tipo": "general",
        "datos": {
            "clave1": "valor1",
            "clave2": 123
        }
    }
    """
    try:
        data = request.get_json()
        
        usuario_id = data.get('usuario_id')
        titulo = data.get('titulo')
        cuerpo = data.get('cuerpo')
        tipo_str = data.get('tipo', 'general')
        datos_extra = data.get('datos', {})
        
        # Convertir tipo a enum
        tipo = NotificationType[tipo_str.upper()] if tipo_str else NotificationType.GENERAL
        
        # Enviar
        resultado = notifications.enviar_notificacion(
            usuario_id=usuario_id,
            titulo=titulo,
            cuerpo=cuerpo,
            tipo=tipo,
            datos_extra=datos_extra
        )
        
        return jsonify(resultado.to_dict()), 200 if resultado.exitoso else 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Endpoint 2: Enviar Notificación de Gasto

```python
@app.route('/api/notificaciones/gasto', methods=['POST'])
@require_auth
def send_gasto_notification():
    """
    Enviar notificación de gasto registrado
    
    Body:
    {
        "usuario_id": "usuario_123",
        "monto": 50.0,
        "categoria": "Comida",
        "descripcion": "Almuerzo"
    }
    """
    try:
        data = request.get_json()
        
        resultado = notifications.enviar_notificacion_gasto(
            usuario_id=data['usuario_id'],
            monto=float(data['monto']),
            categoria=data['categoria'],
            descripcion=data.get('descripcion', '')
        )
        
        return jsonify(resultado.to_dict()), 200 if resultado.exitoso else 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Endpoint 3: Enviar Alerta de Presupuesto

```python
@app.route('/api/notificaciones/alerta-presupuesto', methods=['POST'])
@require_auth
def send_budget_alert():
    """
    Enviar alerta de presupuesto
    
    Body:
    {
        "usuario_id": "usuario_123",
        "categoria": "Comida",
        "gastado": 80.0,
        "presupuesto": 100.0
    }
    """
    try:
        data = request.get_json()
        
        resultado = notifications.enviar_alerta_presupuesto(
            usuario_id=data['usuario_id'],
            categoria=data['categoria'],
            gastado=float(data['gastado']),
            presupuesto=float(data['presupuesto'])
        )
        
        return jsonify(resultado.to_dict()), 200 if resultado.exitoso else 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Endpoint 4: Enviar Recomendación de ML

```python
@app.route('/api/notificaciones/recomendacion-ml', methods=['POST'])
@require_auth
def send_ml_recommendation():
    """
    Enviar recomendación de ML
    
    Body:
    {
        "usuario_id": "usuario_123",
        "recomendacion": "Podrías ahorrar más",
        "categoria": "Comida",
        "confianza": 0.87,
        "accion": "revisar"
    }
    """
    try:
        data = request.get_json()
        
        resultado = notifications.enviar_recomendacion_ml(
            usuario_id=data['usuario_id'],
            recomendacion=data['recomendacion'],
            categoria=data.get('categoria', 'general'),
            confianza=float(data.get('confianza', 0.85)),
            accion=data.get('accion', 'revisar')
        )
        
        return jsonify(resultado.to_dict()), 200 if resultado.exitoso else 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Endpoint 5: Enviar Alerta de Anomalía

```python
@app.route('/api/notificaciones/anomalia', methods=['POST'])
@require_auth
def send_anomaly_alert():
    """
    Enviar alerta de anomalía
    
    Body:
    {
        "usuario_id": "usuario_123",
        "tipo_anomalia": "gasto_inusual",
        "monto": 150.0,
        "descripcion": "Gasto muy inusual",
        "categoria": "Compras"
    }
    """
    try:
        data = request.get_json()
        
        resultado = notifications.enviar_alerta_anomalia(
            usuario_id=data['usuario_id'],
            tipo_anomalia=data['tipo_anomalia'],
            monto=float(data['monto']),
            descripcion=data.get('descripcion', ''),
            categoria=data.get('categoria', 'general')
        )
        
        return jsonify(resultado.to_dict()), 200 if resultado.exitoso else 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Endpoint 6: Enviar Lote de Notificaciones

```python
@app.route('/api/notificaciones/lote', methods=['POST'])
@require_auth
def send_batch_notifications():
    """
    Enviar notificaciones a múltiples usuarios
    
    Body:
    {
        "notificaciones": [
            {
                "usuario_id": "user1",
                "titulo": "Título",
                "cuerpo": "Cuerpo",
                "tipo": "gasto_registrado",
                "datos_extra": {}
            },
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        
        resumen = notifications.enviar_lote(data.get('notificaciones', []))
        
        return jsonify(resumen), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Endpoint 7: Obtener Historial

```python
@app.route('/api/notificaciones/historial/<usuario_id>', methods=['GET'])
@require_auth
def get_notification_history(usuario_id):
    """
    Obtener historial de notificaciones
    
    Query params:
    - limit (opcional): 20 por defecto
    """
    try:
        limite = int(request.args.get('limit', 20))
        
        historial = notifications.obtener_historial(usuario_id, limite=limite)
        
        return jsonify({
            'exitoso': True,
            'total': len(historial),
            'notificaciones': historial
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Endpoint 8: Obtener Estadísticas

```python
@app.route('/api/notificaciones/estadisticas/<usuario_id>', methods=['GET'])
@require_auth
def get_notification_stats(usuario_id):
    """
    Obtener estadísticas de notificaciones
    """
    try:
        stats = notifications.obtener_estadisticas(usuario_id)
        
        return jsonify({
            'exitoso': True,
            'estadisticas': stats
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## 🎯 Ejemplo Completo {#ejemplo}

### Caso: Detectar gasto alto y enviar notificaciones

```python
@app.route('/api/gastos/registrar', methods=['POST'])
@require_auth
def registrar_gasto():
    """
    Registrar un gasto y enviar notificación
    """
    try:
        user = obtener_usuario_actual()  # Tu función de autenticación
        data = request.get_json()
        
        usuario_id = user.get('uid')
        monto = float(data['monto'])
        categoria = data['categoria']
        descripcion = data.get('descripcion', '')
        
        # 1️⃣ Guardar gasto en Firestore
        gasto_ref = db.collection('usuarios').document(usuario_id).collection('gastos').add({
            'monto': monto,
            'categoria': categoria,
            'descripcion': descripcion,
            'fecha': firestore.SERVER_TIMESTAMP,
        })
        
        # 2️⃣ Enviar notificación de gasto registrado
        notifications.enviar_notificacion_gasto(
            usuario_id=usuario_id,
            monto=monto,
            categoria=categoria,
            descripcion=descripcion
        )
        
        # 3️⃣ Verificar presupuesto
        presupuesto_doc = (
            db.collection('usuarios')
            .document(usuario_id)
            .collection('presupuestos')
            .document(categoria)
            .get()
        )
        
        if presupuesto_doc.exists:
            presupuesto = presupuesto_doc.get('monto')
            
            # Calcular gastado este mes
            from datetime import datetime, timedelta
            ahora = datetime.now()
            inicio_mes = ahora.replace(day=1)
            
            gastos_mes = db.collection('usuarios').document(usuario_id).collection('gastos').where(
                'categoria', '==', categoria
            ).where(
                'fecha', '>=', inicio_mes
            ).stream()
            
            total_gastado = sum(g.get('monto') for g in gastos_mes)
            
            # 4️⃣ Enviar alerta si es necesario
            if total_gastado > presupuesto * 0.8:
                notifications.enviar_alerta_presupuesto(
                    usuario_id=usuario_id,
                    categoria=categoria,
                    gastado=total_gastado,
                    presupuesto=presupuesto
                )
        
        return jsonify({
            'exitoso': True,
            'mensaje': 'Gasto registrado',
            'gasto_id': gasto_ref[1].id
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## 🤖 Integración con Google Colab {#colab}

Desde Google Colab, puedes acceder a tu API y enviar notificaciones:

```python
# En Google Colab

import requests
import json

BASE_URL = "https://tu-api-en-render.onrender.com"
TOKEN = "tu_jwt_token"  # Obtener del login

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Enviar notificación de alerta de presupuesto
payload = {
    "usuario_id": "user_123",
    "categoria": "Comida",
    "gastado": 80.0,
    "presupuesto": 100.0
}

response = requests.post(
    f"{BASE_URL}/api/notificaciones/alerta-presupuesto",
    json=payload,
    headers=headers
)

print(response.json())
```

O directamente con el controlador en Colab:

```python
# En Google Colab (opción 2: Acceso directo a Firestore)

from notifications_controller import NotificationsController
import firebase_admin
from firebase_admin import credentials, firestore

# Cargar credenciales
cred = credentials.Certificate('service-account.json')
firebase_admin.initialize_app(cred)

db = firestore.client()
controller = NotificationsController(db_instance=db)

# Analizar datos y enviar notificaciones
for usuario_id in lista_usuarios:
    # Tu análisis de ML aquí
    if condicion_alerta:
        controller.enviar_alerta_presupuesto(
            usuario_id=usuario_id,
            categoria="Comida",
            gastado=100,
            presupuesto=80
        )
```

---

## 🧪 Testing {#testing}

### Test con cURL

```bash
# 1. Obtener token
TOKEN=$(curl -X POST http://localhost:5000/api/v2/auth/token \
  -H "Content-Type: application/json" \
  -d '{"usuario": "test@example.com", "contraseña": "password"}' \
  | jq -r '.token')

# 2. Enviar notificación
curl -X POST http://localhost:5000/api/notificaciones/gasto \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": "user_123",
    "monto": 50.0,
    "categoria": "Comida",
    "descripcion": "Almuerzo"
  }'

# 3. Obtener historial
curl http://localhost:5000/api/notificaciones/historial/user_123 \
  -H "Authorization: Bearer $TOKEN"

# 4. Obtener estadísticas
curl http://localhost:5000/api/notificaciones/estadisticas/user_123 \
  -H "Authorization: Bearer $TOKEN"
```

### Test con Python

```python
import requests
from notifications_controller import NotificationsController, NotificationType

# Suponiendo que ya tengo el controlador inicializado
resultado = notifications.enviar_notificacion_gasto(
    usuario_id="test_user",
    monto=50.0,
    categoria="Comida",
    descripcion="Test"
)

print(f"Exitoso: {resultado.exitoso}")
print(f"Dispositivos: {resultado.total_dispositivos}")
print(f"Mensaje: {resultado.mensaje}")
```

---

## ✅ Checklist de Integración

- [ ] Copiar `notifications_controller.py` a la carpeta del proyecto
- [ ] Importar en `API_MEJORADA.py`
- [ ] Inicializar el controlador
- [ ] Agregar nuevos endpoints
- [ ] Probar con cURL
- [ ] Probar con Python
- [ ] Integrar con Google Colab
- [ ] Verificar que Firestore tenga los datos de tokens
- [ ] Verificar logs en la API
- [ ] Probar en producción (Render)

---

## 🔗 Referencia Rápida

| Método | Uso |
|--------|-----|
| `enviar_notificacion()` | Notificación genérica |
| `enviar_notificacion_gasto()` | Gasto registrado |
| `enviar_alerta_presupuesto()` | Alerta de presupuesto |
| `enviar_recomendacion_ml()` | Recomendación de ML |
| `enviar_alerta_anomalia()` | Alerta de anomalía |
| `enviar_tip_financiero()` | Tips financieros |
| `enviar_lote()` | Múltiples usuarios |
| `obtener_historial()` | Historial de notificaciones |
| `obtener_estadisticas()` | Estadísticas |

---

**¡Listo! Ahora tienes un controlador de notificaciones profesional integrado con tu API. 🎉**
