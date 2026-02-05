# ✅ Notificaciones Push - Implementadas

## 📍 Cambios Realizados

### **1. Nuevo Controlador en API_MEJORADA.py**

Se agregaron **2 nuevos endpoints** para enviar notificaciones push:

#### **Endpoint 1: Enviar a Dispositivo Específico (Sin Autenticación)**
```
POST /api/Firebase/sendnotificacion
```
- ✅ No requiere JWT
- ✅ Usa token FCM del dispositivo
- ✅ Ideal para alertas del servidor
- ✅ Soporta datos personalizados
- ✅ Compatible con Android, iOS y Web

**Ubicación en código:** [API_MEJORADA.py - Línea 2186](API_MEJORADA.py#L2186)

#### **Endpoint 2: Enviar a Todos los Dispositivos del Usuario (Con Autenticación)**
```
POST /api/v2/users/{usuario_id}/send-notification
```
- ✅ Requiere JWT (seguridad)
- ✅ Envía a TODOS los dispositivos registrados
- ✅ Ideal para notificaciones personalizadas
- ✅ Previene spam

**Ubicación en código:** [API_MEJORADA.py - Línea 2280](API_MEJORADA.py#L2280)

---

### **2. Documentación en Swagger (swagger.yaml)**

Se actualizó la especificación OpenAPI con:
- ✅ Descripción de ambos endpoints
- ✅ Esquemas de request/response
- ✅ Ejemplos de uso
- ✅ Códigos de error
- ✅ Integración con UI Swagger

**Ubicación:** [swagger.yaml - Línea 93](swagger.yaml#L93)

---

### **3. Archivos de Documentación**

#### **GUIA_NOTIFICACIONES.md**
Guía completa con:
- 4 casos de uso principales
- Ejemplos de código en JavaScript
- Flujo de datos
- Configuración necesaria en app (Android/iOS/Web)
- Troubleshooting

#### **EJEMPLOS_CURL_NOTIFICACIONES.md**
Ejemplos listos para usar en:
- ✅ cURL
- ✅ PowerShell
- ✅ Python
- ✅ JavaScript
- ✅ Ejemplos de respuestas

---

## 🚀 Cómo Usar Inmediatamente

### **Opción 1: Simple (Sin Token)**
```bash
curl -X POST https://api-google-colab.onrender.com/api/Firebase/sendnotificacion \
  -H "Content-Type: application/json" \
  -d '{
    "strToken": "token_fcm_del_dispositivo",
    "strTitle": "Gasto Detectado",
    "strMessage": "Se registró un gasto de $100"
  }'
```

### **Opción 2: Con Autenticación (Seguro)**
```bash
# Paso 1: Obtener token
TOKEN=$(curl -X POST https://api-google-colab.onrender.com/api/v2/auth/token \
  -H "Content-Type: application/json" \
  -d '{"user_id": "usuario123"}' | jq -r .token)

# Paso 2: Enviar notificación
curl -X POST https://api-google-colab.onrender.com/api/v2/users/usuario123/send-notification \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "¡Meta Alcanzada!",
    "cuerpo": "Ahorraste $1,000"
  }'
```

---

## 📊 Integración con Predicción

Tu API ahora puede hacer:

```
1. Usuario realiza gasto
   ↓
2. API llama predict-category
   ↓
3. Detecta si es gasto anómalo
   ↓
4. Envía notificación push automáticamente
   ↓
5. Usuario recibe alerta en tiempo real
```

### Ejemplo: Detectar Gasto Anómalo y Alertar

```python
# En tu código de predicción
expenses, _ = _normalized_expenses_for_user(usuario_id)
df = prepare_dataframe(expenses)

# Hacer predicción
anomalies = detect_anomalies(df)

# Si hay anomalías, alertar al usuario
if anomalies['anomalias_detectadas'] > 0:
    for gastoAtipico in anomalies['gastos_atipicos']:
        send_push_notification(
            usuario_id=usuario_id,
            titulo='⚠️ Gasto Anómalo Detectado',
            cuerpo=f"Gasto de ${gastoAtipico['monto']} detectado",
            datos_extra={
                'tipo': 'anomalia',
                'monto': str(gastoAtipico['monto']),
                'razon': gastoAtipico['razon']
            }
        )
```

---

## 🔐 Seguridad

✅ **Endpoint público** (`/api/Firebase/sendnotificacion`)
- Solo requiere token FCM válido
- Ideal para notificaciones del sistema

✅ **Endpoint privado** (`/api/v2/users/{id}/send-notification`)
- Requiere JWT válido
- Previene que otros usuarios envíen notificaciones
- Previene spam

---

## 📱 Soporte Multiplataforma

| Plataforma | Soporte | Características |
|-----------|---------|----------------|
| Android | ✅ Sí | Sonido, vibración, color |
| iOS | ✅ Sí | Sonido, badge, contenido mutable |
| Web | ✅ Sí | Ícono, título, cuerpo |
| Fallback | ✅ Sí | Almacenado en Firebase hasta que app se abra |

---

## ✨ Próximos Pasos Sugeridos

### **1. Integrar con Alertas Inteligentes**
```
Cuando: Usuario va a exceder presupuesto
Qué: Enviar notificación preventiva
Endpoint: POST /api/Firebase/sendnotificacion
```

### **2. Integrar con Metas**
```
Cuando: Usuario alcanza meta de ahorro
Qué: Celebrar logro
Endpoint: POST /api/v2/users/{id}/send-notification
```

### **3. Integrar con Recomendaciones**
```
Cuando: Sistema genera recomendación nueva
Qué: Notificar al usuario
Endpoint: POST /api/v2/users/{id}/send-notification
```

### **4. Integrar con Planes de Acción**
```
Cuando: Es hora del siguiente paso del plan
Qué: Recordar al usuario
Endpoint: POST /api/v2/users/{id}/send-notification
```

---

## 🧪 Testar los Endpoints

### En Swagger UI
1. Ir a: https://api-google-colab.onrender.com/swagger-ui.html
2. Ir a la sección "🔔 Notificaciones"
3. Probar los 2 nuevos endpoints
4. Ver documentación interactiva

### En Postman
1. Importar la colección desde swagger.yaml
2. Obtener token: POST /api/v2/auth/token
3. Usar token en endpoints autenticados
4. Probar casos de uso

---

## 📄 Archivos Modificados

| Archivo | Cambios | Líneas |
|---------|---------|--------|
| API_MEJORADA.py | +2 endpoints, +160 líneas | 2186-2345 |
| swagger.yaml | +2 documentaciones | 93-191 |
| GUIA_NOTIFICACIONES.md | Nuevo archivo | - |
| EJEMPLOS_CURL_NOTIFICACIONES.md | Nuevo archivo | - |

---

## 🎯 Caso de Uso Real

### Escenario: Usuario gastó más de lo previsto

```
1. Usuario realiza compra de $500 en Transporte
   
2. API ejecuta:
   GET /api/v2/users/user123/predict-category?category=Transporte
   
3. Función detect_anomalies() detecta que es 2x el promedio
   
4. API llama automáticamente:
   POST /api/Firebase/sendnotificacion
   {
     "strToken": "device_token_aqui",
     "strTitle": "⚠️ Gasto Muy Alto",
     "strMessage": "Gastos de $500 en Transporte (3x tu promedio)",
     "mapData": {
       "tipo": "alerta_anomalia",
       "categoria": "Transporte",
       "monto": "500",
       "promedio": "165"
     }
   }
   
5. Usuario recibe notificación en tiempo real
   
6. Usuario puede hacer clic y:
   - Ver detalles del gasto
   - Comparar con histórico
   - Revisar predicción
```

---

## ✅ Checklist de Implementación

- [x] Crear endpoint sin autenticación (`/api/Firebase/sendnotificacion`)
- [x] Crear endpoint con autenticación (`/api/v2/users/{id}/send-notification`)
- [x] Documentar en swagger.yaml
- [x] Crear guía de uso (GUIA_NOTIFICACIONES.md)
- [x] Crear ejemplos cURL (EJEMPLOS_CURL_NOTIFICACIONES.md)
- [x] Soportar datos personalizados
- [x] Soportar múltiples plataformas (Android/iOS/Web)
- [x] Validar campos requeridos
- [x] Manejar errores correctamente

---

## 🆘 Problemas Conocidos

### "Firebase no disponible"
**Causa:** `credentials.json` no está configurado en el servidor
**Solución:** Verificar que Firebase esté inicializado correctamente

### "No hay dispositivos registrados"
**Causa:** Usuario no tiene ningún dispositivo con token FCM
**Solución:** Usuario debe permitir notificaciones en app

### "Token FCM inválido"
**Causa:** Token expiró o es incorrecto
**Solución:** Refrescar token en app y guardar nuevo

---

## 📚 Referencias

- [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging)
- [OpenAPI 3.0.0 Spec](https://swagger.io/specification/)
- [Flutter FCM](https://firebase.flutter.dev/docs/messaging/overview/)
- [React Native FCM](https://www.notjust.dev/blog/react-native-firebase-setup)

---

**Fecha de implementación:** 5 de Febrero, 2026
**Estado:** ✅ Producción
**Próximas mejoras:** Sistema de plantillas, scheduling de notificaciones
