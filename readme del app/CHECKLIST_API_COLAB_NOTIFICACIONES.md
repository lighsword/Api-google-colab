# ✅ Checklist: Implementación Completa de Notificaciones desde API Colab

## 📋 Fase 1: Preparación (Firebase)

### Backend - Google Cloud & Firebase Console

- [ ] **Acceder a Firebase Console**
  - URL: https://console.firebase.google.com
  - Proyecto: `gestor-financiero-28ac2`

- [ ] **Descargar Service Account Key**
  - Ir a: Configuración ⚙️ → Cuentas de Servicio
  - Haz clic en "Generar nueva clave privada"
  - Descarga el archivo JSON
  - ⚠️ **SEGURIDAD**: Nunca compartas ni subas a GitHub

- [ ] **Verificar Firestore Database**
  - Ve a: Firestore Database
  - Verifica que existe la base de datos `gestofin`
  - Status debe estar "En producción"

- [ ] **Crear índice (si es necesario)**
  - Si ves advertencia de índices, crea los necesarios
  - Firestore → Índices → Crear índice compuesto

### Estructura de Datos en Firestore

- [ ] **Colección `/users/{userId}`**
  ```
  users/
  └── userId123/
      ├── email: "user@example.com"
      ├── displayName: "Usuario"
      ├── createdAt: timestamp
      └── fcmTokens/ (subcollection)
  ```

- [ ] **Subcolección `/users/{userId}/fcmTokens/{token}`**
  ```
  fcmTokens/
  └── cJ3EHfNEfQ1K4.../
      ├── token: "cJ3EHfNEfQ1K4..."
      ├── deviceName: "Samsung Galaxy S21"
      ├── platform: "android"
      ├── createdAt: timestamp
      ├── lastUpdated: timestamp
      └── isActive: true
  ```

- [ ] **Actualizar reglas de Firestore**
  ```
  // En Firestore → Reglas
  rules_version = '2';
  service cloud.firestore {
    match /databases/{database}/documents {
      // Usuarios solo ven sus propios datos
      match /users/{userId} {
        allow read, write: if request.auth.uid == userId;
        
        // Tokens
        match /fcmTokens/{tokenId} {
          allow read, write: if request.auth.uid == userId;
        }
      }
    }
  }
  ```

---

## 📱 Fase 2: Implementación en Flutter

### Servicio de Notificaciones

- [ ] **Verificar `NotificationService` implementado**
  - Archivo: `lib/config/services/notification_service.dart`
  - Métodos requeridos:
    - ✅ `initialize()`
    - ✅ `saveTokenToDatabase(userId)`
    - ✅ `_setupFCMHandlers()`
    - ✅ `_setupTokenRefreshListener()`

- [ ] **Implementar guardado de token en Login**
  - Archivo: `lib/modules/auth/auth_provider.dart` o `LoginPage`
  - Después del login exitoso:
  ```dart
  await authProvider.signIn(email, password);
  if (authProvider.isAuthenticated) {
    final notificationService = NotificationService();
    await notificationService.saveTokenToDatabase(
      authProvider.user!.uid
    );
  }
  ```

- [ ] **Implementar handlers de notificaciones**
  - En `NotificationService`:
    - `_handleNotification()` - para cuando app está abierta
    - `_handleNotificationTap()` - cuando usuario toca la notificación
    - `_processNotificationData()` - procesar datos adicionales

- [ ] **Implementar filtrado por userId**
  - Crear `NotificationFilterService`
  - Verificar que `data['userId']` == usuario actual

### Configuración de AndroidManifest.xml

- [ ] **Permisos necesarios**
  ```xml
  <uses-permission android:name="android.permission.INTERNET" />
  <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
  <uses-permission android:name="com.google.android.c2dm.permission.RECEIVE" />
  ```

- [ ] **Servicio FCM**
  ```xml
  <service
    android:name=".firebase.MyFirebaseMessagingService"
    android:exported="false">
    <intent-filter>
      <action android:name="com.google.firebase.MESSAGING_EVENT" />
    </intent-filter>
  </service>
  ```

### Pruebas en Flutter

- [ ] **Verificar que app recibe el token**
  - Abre la app en Android Studio
  - Busca en Logcat: "FCM Token:"
  - Copia el token

- [ ] **Verificar que token se guarda en Firestore**
  - Firebase Console → Firestore
  - Ve a: users → tuUserId → fcmTokens
  - Debe existir una entrada con tu token

- [ ] **Probar recepción de notificación**
  - Envía una notificación de prueba desde Firebase Console
  - Cloud Messaging → Crear primera campaña
  - O usa el código de prueba en Colab

---

## 🐍 Fase 3: Implementación en Google Colab

### Instalación y Setup

- [ ] **Crear nuevo Notebook en Google Colab**
  - URL: https://colab.research.google.com

- [ ] **Instalar dependencias**
  ```python
  !pip install firebase-admin
  !pip install requests
  !pip install google-cloud-firestore
  !pip install pandas
  ```

- [ ] **Subir Service Account JSON**
  - En Colab: Ejecutar `files.upload()`
  - Sube el JSON descargado de Firebase

- [ ] **Inicializar Firebase en Colab**
  ```python
  import firebase_admin
  from firebase_admin import credentials, messaging, firestore
  
  cred = credentials.Certificate('gestor-financiero-28ac2-xxxxx.json')
  firebase_admin.initialize_app(cred)
  db = firestore.client()
  ```

### Implementar Clase de Notificaciones

- [ ] **Crear `NotificationManager`**
  - ✅ `obtener_tokens_usuario(user_id)`
  - ✅ `enviar_notificacion(user_id, titulo, cuerpo, datos)`
  - ✅ `enviar_lote(usuarios_datos)`

- [ ] **Crear `MLNotificationService`**
  - ✅ `notificar_prediccion_gasto()`
  - ✅ `notificar_anomalia()`
  - ✅ `notificar_recomendacion()`

- [ ] **Crear `ExpenseAnalyzer` (opcional pero recomendado)**
  - ✅ `analizar_usuario_y_notificar(user_id)`
  - ✅ `_detectar_anomalias(gastos)`
  - ✅ `_generar_predicciones(gastos)`
  - ✅ `_generar_recomendaciones(gastos)`

### Casos de Uso Básicos

- [ ] **Implementar notificación de predicción**
  ```python
  ml_service.notificar_prediccion_gasto('usuario_123', {
      'prediccion_id': 'pred_001',
      'gasto_predicho': 150.50,
      'categoria': 'Alimentación',
      'confianza': 0.85,
      'base_historica': 120.00
  })
  ```

- [ ] **Implementar notificación de anomalía**
  ```python
  ml_service.notificar_anomalia('usuario_123', {
      'tipo': 'gasto_anormal',
      'monto': 500.00,
      'categoria': 'Entretenimiento',
      'razon': 'Exceede 3x el promedio',
      'promedio': 150.00
  })
  ```

- [ ] **Implementar notificación de recomendación**
  ```python
  ml_service.notificar_recomendacion('usuario_123', {
      'accion': 'Reducir gastos en Entretenimiento',
      'categoria': 'Entretenimiento',
      'ahorro_potencial': 300.00,
      'porcentaje': 0.35
  })
  ```

### Pruebas en Colab

- [ ] **Ejecutar prueba de configuración**
  ```python
  probar_configuracion()  # Verifica conexión a Firebase
  ```

- [ ] **Enviar notificación de prueba**
  ```python
  resultado = notif_manager.enviar_notificacion(
      'usuario_123',
      '🧪 Prueba',
      'Si ves esto, ¡funciona!',
      {'tipo': 'test'}
  )
  print(resultado)
  ```

- [ ] **Verificar en app Flutter**
  - Debería recibir la notificación en el dispositivo

---

## 🔄 Fase 4: Integración Completa

### Flujo de Datos

- [ ] **Verificar flujo completo:**
  ```
  1. Usuario inicia sesión en Flutter
  2. App obtiene token FCM
  3. App guarda token en Firestore bajo users/{userId}/fcmTokens/
  4. API en Colab obtiene el token de Firestore
  5. API envía notificación a través de Firebase Cloud Messaging
  6. App recibe notificación y la muestra al usuario
  7. Usuario toca notificación → App navega a pantalla correspondiente
  ```

- [ ] **Conexión ML ↔ Notificaciones**
  - Tu modelo ML en Colab analiza gastos
  - Cuando encuentra algo importante (predicción, anomalía, recomendación)
  - Llama a `ml_service.notificar_*()` correspondiente
  - Notificación llega a la app del usuario

### Casos de Uso Avanzados

- [ ] **Notificaciones programadas**
  - Resumen diario cada día a cierta hora
  - Alertas semanales
  - Comparativas mensuales

- [ ] **Análisis automático**
  - Ejecutar análisis cada 6 horas
  - Detectar patrones de gasto
  - Generar recomendaciones personalizadas

- [ ] **Notificaciones a múltiples usuarios**
  - Cuando tienes un insight global
  - Ej: "Los usuarios ahorraron 15% este mes"

---

## 🛡️ Fase 5: Seguridad

### Configuración de Firebase

- [ ] **Permisos de Firestore restrictivos**
  - ✅ Los usuarios solo pueden leer sus propios tokens
  - ✅ Solo Service Account (Colab) puede enviar notificaciones
  - ✅ Tokens no se exponen en cliente

- [ ] **Proteger Service Account Key**
  - ❌ NO subir a GitHub
  - ❌ NO compartir
  - ✅ Usar variables de entorno en producción
  - ✅ Rota keys regularmente

- [ ] **Validación de datos**
  - ✅ Validar longitud de títulos/cuerpos
  - ✅ Validar estructura de datos
  - ✅ Filtrar by userId siempre

### Monitoreo

- [ ] **Verificar logs en Firestore**
  - Firebase Console → Cloud Messaging
  - Ver estadísticas de entregas

- [ ] **Monitorear errores en Colab**
  - Implementar try-except en todas las funciones
  - Loguear intentos fallidos
  - Registrar tokens que expiran

- [ ] **Auditoría de notificaciones**
  - Guardar log de notificaciones enviadas
  - Quién las recibió, cuándo, si las tocaron

---

## 📊 Fase 6: Métricas y Monitoreo

### Estadísticas a Rastrear

- [ ] **Notificaciones enviadas**
  - Total por día
  - Por tipo (predicción, anomalía, etc.)
  - Tasa de entrega

- [ ] **Tokens FCM**
  - Tokens activos por usuario
  - Tokens expirados
  - Nuevos tokens por día

- [ ] **Engagement**
  - % de notificaciones abiertas
  - Promedio de tiempo hasta abrir
  - Acciones tomadas después de notificación

### Dashboard (Recomendado)

- [ ] **Crear tabla en Firestore para logs**
  ```
  notification_logs/
  └── {logId}/
      ├── user_id: "xxx"
      ├── type: "prediccion"
      ├── title: "..."
      ├── body: "..."
      ├── sent_at: timestamp
      ├── delivered: true/false
      ├── opened: true/false
      └── opened_at: timestamp (opcional)
  ```

- [ ] **Queries útiles**
  ```python
  # Notificaciones entregadas hoy
  db.collection('notification_logs').where(
    'sent_at', '>=', datetime.now().replace(hour=0, minute=0, second=0)
  ).stream()
  
  # Tasa de apertura
  total = total_enviadas
  abiertas = db.collection('notification_logs').where(
    'opened', '==', True
  ).stream()
  tasa = len(list(abiertas)) / total
  ```

---

## 🧪 Fase 7: Testing

### Tests Unitarios

- [ ] **Test: Validación de datos**
  ```python
  def test_validar_datos():
      assert validar_datos_notificacion({
          'user_id': 'xxx',
          'titulo': 'Test',
          'cuerpo': 'Test'
      }) == True
  ```

- [ ] **Test: Obtener tokens**
  ```python
  def test_obtener_tokens():
      tokens = notif_manager.obtener_tokens_usuario('test_user')
      assert isinstance(tokens, list)
  ```

- [ ] **Test: Enviar notificación**
  ```python
  def test_enviar():
      resultado = notif_manager.enviar_notificacion(
          'test_user', 'Test', 'Test'
      )
      assert resultado['exitosas'] >= 0
  ```

### Tests de Integración

- [ ] **Test E2E: Notificación completa**
  1. Loguear usuario en Flutter
  2. Verificar que token se guarda en Firestore
  3. Enviar notificación desde Colab
  4. Verificar que app la recibe
  5. Verificar que se muestra al usuario

- [ ] **Test de recuperación de fallos**
  1. Desactivar internet en app
  2. Enviar notificación desde Colab
  3. Reactivar internet
  4. Verificar que app la recibe (debería estar en queue)

---

## 📝 Fase 8: Documentación

- [ ] **Documentar endpoints**
  - Cada función con docstring
  - Parámetros esperados
  - Valores retornados
  - Excepciones posibles

- [ ] **Crear ejemplos de código**
  - Para cada tipo de notificación
  - Con datos reales de ejemplo
  - Casos de uso comunes

- [ ] **Crear guía de troubleshooting**
  - Problemas comunes
  - Cómo debuguear
  - Logs útiles

- [ ] **Actualizar README**
  - Cómo usar el sistema
  - Requisitos previos
  - Pasos de configuración

---

## 🚀 Fase 9: Deployment en Producción

### Antes de Ir a Producción

- [ ] **Verificación final de Firestore**
  - Todos los índices creados
  - Reglas de seguridad correctas
  - Datos de prueba limpiados

- [ ] **Configuración de Colab**
  - Service Account key en variable de entorno
  - NO en código fuente
  - Acceso restringido al notebook

- [ ] **Tests en staging**
  - Probar con usuarios de prueba
  - Verificar que notificaciones llegan
  - Medir rendimiento

- [ ] **Plan de rollback**
  - Cómo desactivar notificaciones si hay problema
  - Cómo limpiar datos de prueba
  - Backup de configuración

### En Producción

- [ ] **Monitorear constantemente**
  - Firebase Console
  - Logs de Colab
  - Feedback de usuarios

- [ ] **Mantener actualizado**
  - Revisar regularmente Service Account
  - Actualizar dependencias
  - Monitorear cambios en Firebase API

- [ ] **Performance**
  - Medir tiempo de entrega
  - Optimizar queries a Firestore
  - Implementar rate limiting si es necesario

- [ ] **Seguridad continua**
  - Auditar acceso a Service Account
  - Rotar credenciales regularmente
  - Revisar logs de seguridad

---

## 🎯 Resumen de Archivos Necesarios

### En Flutter (`lib/`)
- ✅ `config/services/notification_service.dart` - Ya existe
- ✅ `config/services/push_notifications_service.dart` - Ya existe
- ✅ Actualizar `modules/auth/auth_provider.dart` - Guardar token en login
- ✅ Crear `NotificationFilterService` - Opcional pero recomendado

### En Google Colab
- 📄 `notification_manager.py` - Gestionar envíos
- 📄 `ml_notification_service.py` - Notificaciones de ML
- 📄 `expense_analyzer.py` - Análisis de gastos
- 📄 `main_notification_system.py` - Sistema completo

### Documentación (ya creada)
- ✅ `docs/GUIA_API_COLAB_NOTIFICACIONES.md` - Guía completa
- ✅ `docs/EJEMPLOS_API_COLAB_NOTIFICACIONES.md` - Ejemplos de código

---

## 📞 Soporte y Debugging

Si algo no funciona:

1. **Verificar conexión a Firebase**
   - Console: `probar_configuracion()`
   
2. **Ver logs en Firebase**
   - Firebase Console → Cloud Messaging
   - Buscar el userId específico

3. **Verificar tokens en Firestore**
   - Firebase Console → Firestore
   - Navigate: users → {userId} → fcmTokens

4. **Leer documentación oficial**
   - Firebase: https://firebase.google.com/docs/cloud-messaging
   - Flutter: https://pub.dev/packages/firebase_messaging
   - Python: https://firebase.google.com/docs/reference/admin/python

---

**Última actualización**: Febrero 2025
**Estado**: ✅ Pronto para producción
