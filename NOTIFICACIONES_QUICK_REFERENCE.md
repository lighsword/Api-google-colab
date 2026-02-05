# 🔔 QUICK REFERENCE - Notificaciones Push

## ⚡ 30 Segundos: Lo Más Importante

### Endpoint 1: Sin Token JWT
```bash
POST /api/Firebase/sendnotificacion
{
  "strToken": "device_token_fcm",
  "strTitle": "Título",
  "strMessage": "Mensaje"
}
```

### Endpoint 2: Con Token JWT
```bash
POST /api/v2/users/{usuario_id}/send-notification
Headers: Authorization: Bearer {jwt_token}
{
  "titulo": "Título",
  "cuerpo": "Mensaje"
}
```

---

## 📋 Checklist Rápido

### Para Probar Ahora
- [ ] Ir a: https://api-google-colab.onrender.com/swagger-ui.html
- [ ] Buscar sección "🔔 Notificaciones"
- [ ] Expandir `/api/Firebase/sendnotificacion`
- [ ] Click "Try it out"
- [ ] Click "Execute"

### Para Integrar en Tu App
- [ ] Obtener token FCM del dispositivo
- [ ] Guardar en Firestore: `usuarios/{uid}/device_tokens`
- [ ] Usar endpoint con autenticación
- [ ] Llamar cuando: anomalía, meta, presupuesto

### Para Automatizar Alertas
- [ ] Después de `detect_anomalies()` → enviar notificación
- [ ] Después de `predict_monthly()` → si presupuesto ↑ → alertar
- [ ] Después de `analysis_complete()` → si meta ✓ → celebrar

---

## 🧬 Estructura de Datos

### Request Sin Autenticación
```json
{
  "strToken": "abc123xyz789",
  "strTitle": "⚠️ Alerta",
  "strMessage": "Tu mensaje aquí",
  "mapData": {
    "key1": "value1",
    "key2": "value2"
  }
}
```

### Request Con Autenticación
```json
{
  "titulo": "Mi Título",
  "cuerpo": "Mi mensaje",
  "datos_extra": {
    "accion": "ver_detalles",
    "dato": "valor"
  }
}
```

### Response Exitosa
```json
{
  "status": "success",
  "mensaje": "Notificación enviada exitosamente",
  "message_id": "0:1675849384938204%3a1234567",
  "timestamp": "2026-02-05T18:15:30.123456"
}
```

---

## 🎯 Casos de Uso Comunes

| Situación | Endpoint | Datos |
|-----------|----------|-------|
| Gasto anómalo detectado | Sin JWT | tipo: "anomalia" |
| Meta alcanzada | Con JWT | tipo: "meta_alcanzada" |
| Presupuesto al 80% | Con JWT | tipo: "alerta_presupuesto" |
| Recomendación nueva | Con JWT | tipo: "consejo" |
| Recordatorio diario | Con JWT | tipo: "recordatorio" |

---

## 🔧 Integración con Predicción

```python
# Después de detect_anomalies
if anomalies['anomalias_detectadas'] > 0:
    send_push_notification(
        usuario_id,
        "⚠️ Gasto Anómalo",
        f"${anomalies['gastos_atipicos'][0]['monto']} detectado",
        {'tipo': 'anomalia'}
    )
```

---

## 📱 Cómo Funciona en App

```
Usuario gasta $500
      ↓
App envía a Firebase
      ↓
API predice & detecta anomalía
      ↓
API llama endpoint notificación
      ↓
Firebase Cloud Messaging
      ↓
Dispositivo recibe push
      ↓
Usuario ve alerta
```

---

## 🔒 Seguridad

| Endpoint | Requiere | Riesgo |
|----------|----------|--------|
| `/api/Firebase/sendnotificacion` | FCM token | Bajo (token unique) |
| `/api/v2/users/{id}/send-notification` | JWT | Muy bajo (JWT verificado) |

---

## ❌ Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| 400 | Falta strToken | Incluir token FCM |
| 401 | No hay JWT | Generar en /auth/token |
| 503 | Firebase offline | Esperar o verificar config |

---

## 📚 Documentación Completa

- **GUIA_NOTIFICACIONES.md**: Ejemplos detallados
- **EJEMPLOS_CURL_NOTIFICACIONES.md**: 50+ ejemplos
- **DIAGRAMA_NOTIFICACIONES.md**: Flujos visuales
- **swagger.yaml**: Especificación completa

---

## 🚀 Next Steps

1. Probar en Swagger UI
2. Generar token FCM en app
3. Llamar endpoint desde app
4. Integrar con alertas automáticas
5. Celebrar 🎉

---

**¡Listo para usar!**
