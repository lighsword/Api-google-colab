# 📱 Control de Gastos + Notificaciones Push - Guía Actualizada

> **ACTUALIZACIÓN**: La app ahora incluye **notificaciones push** automáticas cuando registras gastos. El backend ha sido actualizado para soportar esto correctamente.

---

## 🎯 Nuevas Funcionalidades

### ✨ Notificaciones Push (NUEVA)

- 📲 **Notificaciones automáticas** cuando registras un gasto\n- 💰 **Detalles del gasto** incluidos en la notificación\n- 🔔 **Alertas de presupuesto** cuando te acercas al límite\n- 💡 **Consejos personalizados** basados en tus patrones\n- 📊 **Historial de notificaciones** en la app

---

## 🚀 Funcionalidades Actuales

### ✅ Gestión Básica
* **Registro de Gastos:** Ingresa descripción, cantidad, categoría y fecha
* **Categorización Inteligente:** Comida, Transporte, Ocio, Servicios, etc.
* **Visualización de Lista:** Lista clara y organizada de gastos
* **Persistencia de Datos:** Firebase Firestore en tiempo real
* **Autenticación:** Sistema completo con email y roles

### 📊 PREDICCIÓN DE GASTOS
* **Predicción por Categoría:** Análisis individualizado
* **Predicción Mensual:** Proyecciones para próximos 30 días
* **Detección de Anomalías:** Identifica gastos inusuales
* **Múltiples Modelos ML:** ARIMA, Prophet, LSTM
* **Análisis de Estacionalidad:** Patrones estacionales

### 📈 ANÁLISIS ESTADÍSTICO AVANZADO
* **Correlaciones entre Categorías:** Relaciones entre gastos
* **Análisis Temporal:** Comparación mes actual vs anterior
* **Clustering Automático:** Agrupa gastos similares
* **Detección de Tendencias:** Aumento o disminución
* **Identificación de Outliers:** Valores atípicos

### 💡 RECOMENDACIONES DE AHORRO
* **Metas de Ahorro:** Objetivos específicos y progreso
* **Tips Personalizados:** Consejos basados en patrones
* **Alertas de Presupuesto:** Notificaciones de límites
* **Gamificación:** Sistema de puntuación financiera
* **Reportes Automáticos:** Resumen semanal/mensual

### 📱 NOTIFICACIONES PUSH (NUEVA) 🆕
* **Notificaciones automáticas** al registrar gasto
* **Alertas de presupuesto** personalizadas
* **Consejos de ahorro** enviados al dispositivo
* **Historial de notificaciones** sincronizado
* **Multi-dispositivo** - Recibe en todos tus celulares

### 📈 Visualización de Datos
* **Gráficos Interactivos:** Circular, barras, línea, área
* **Dashboard Completo:** Vista general de finanzas
* **Análisis por Período:** Filtros día, semana, mes, año

---

## 🔧 Instalación & Configuración

### 1. Requisitos

```bash
# Flutter & Dart
Flutter 3.0+
Dart 3.0+

# Dependencias adicionales
- Firebase (Core, Messaging, Firestore)
- Provider (state management)
- http (API calls)
```

### 2. Instalación

```bash
# Clonar repositorio
git clone https://github.com/TuUsuario/control_gastos.git
cd control_gastos

# Instalar dependencias
flutter pub get

# Configurar Firebase
# (Sigue instrucciones de Firebase para Android/iOS)

# Ejecutar app
flutter run
```

### 3. Configurar Notificaciones

#### En `main.dart`

```dart
import 'package:firebase_messaging/firebase_messaging.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  await Firebase.initializeApp();
  
  // Solicitar permisos de notificación
  await FirebaseMessaging.instance.requestPermission(
    alert: true,
    badge: true,
    sound: true,
  );
  
  runApp(const MyApp());
}
```

#### En `AuthService`

```dart
// Después de autenticar, registrar dispositivo
await notificationsService.registrarDispositivo();
```

---

## 📱 Cómo Funcionan las Notificaciones

```
1. Usuario abre app
   ↓
2. Se autentica con email/contraseña
   ↓
3. App registra su dispositivo (automático)
   ↓
4. Usuario registra un gasto
   ↓
5. App envía notificación al backend
   ↓
6. Backend procesa y envía vía Firebase
   ↓
7. 📲 Notificación aparece en el celular
```

---

## 🎯 Ejemplo: Registrar Gasto + Notificación

```dart
// Pantalla de registro de gasto
ElevatedButton(
  onPressed: () async {
    // 1. Guardar gasto en Firebase
    await guardarGastoEnFirebase(gasto);

    // 2. Enviar notificación (AUTOMÁTICO)
    await notificationsService.enviarNotificacionGasto(
      titulo: '💰 ${gasto.categoria}',
      cuerpo: '\$${gasto.monto.toStringAsFixed(2)} - ${gasto.descripcion}',
      monto: gasto.monto,
      categoria: gasto.categoria,
    );

    // 3. Mostrar confirmación
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('✅ Gasto registrado y notificación enviada')),
    );
  },
  child: Text('Guardar Gasto'),
)
```

**Resultado:** 📲 Notificación en el celular: "💰 Comida - $50.00 - Mi almuerzo"

---

## 📚 Documentación Detallada

### Para Desarrolladores

- **[GUIA_FLUTTER_NOTIFICACIONES.md](GUIA_FLUTTER_NOTIFICACIONES.md)** - Setup completo de notificaciones
- **[SOLUCION_ERROR_NON_STRING_VALUES.md](SOLUCION_ERROR_NON_STRING_VALUES.md)** - Guía de errores comunes

### Para Backend

- **[QUICK_START_NOTIFICACIONES.md](QUICK_START_NOTIFICACIONES.md)** - Inicio rápido
- **[GUIA_NOTIFICACIONES_USUARIO_ID.md](GUIA_NOTIFICACIONES_USUARIO_ID.md)** - Guía completa API

### Endpoints Disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v2/auth/token` | POST | Obtener JWT token |
| `/api/v2/notifications/register-device` | POST | Registrar dispositivo |
| `/api/v2/notifications/send` | POST | Enviar notificación |
| `/api/v2/notifications/send-alert/{uid}` | POST | Alerta de presupuesto |
| `/api/v2/notifications/send-tips/{uid}` | POST | Tips personalizados |
| `/api/v2/notifications/history` | GET | Ver historial |

---

## 🤖 Machine Learning: 3 Opciones

Esta app incluye **3 formas diferentes** de usar ML:

### Opción 1: Google Colab + Ngrok (Nube) ☁️
- ✅ Predicciones en tiempo real
- ✅ Modelo se puede reentrenar
- ✅ Gratis
- ⚠️ Requiere internet

### Opción 2: API Backend Propio 🚀
- ✅ URL permanente
- ✅ Profesional y escalable
- ⚠️ Puede tener costo

### Opción 3: TensorFlow Lite Local (Offline) 📱
- ✅ Sin internet necesario
- ✅ Predicciones en <100ms
- ✅ 100% privado y gratis
- ⚠️ Modelo fijo

---

## 🎨 Interface de Usuario

### Pantallas Principales

1. **Login** - Autenticación con Firebase
2. **Dashboard** - Resumen financiero
3. **Registro de Gasto** - Formulario de ingreso
4. **Lista de Gastos** - Todos los gastos registrados
5. **Análisis** - Gráficos y estadísticas
6. **Metas** - Establecer objetivos de ahorro
7. **Notificaciones** - Ver historial

### Características UI

- 🌙 Modo oscuro automático
- 📊 Gráficos interactivos
- 🎨 Diseño moderno y limpio
- ⚡ Animaciones fluidas
- 📱 Responsive en todos los tamaños

---

## 🔔 Tipos de Notificaciones

### 1. Gasto Registrado

```
💰 Comida
$50.00 - Mi almuerzo
```

### 2. Alerta de Presupuesto

```
🚨 ¡Presupuesto excedido!
Has gastado $900 de tu presupuesto $1000
```

### 3. Consejos de Ahorro

```
💡 Consejo
Tu gasto en comida ha aumentado 30% este mes
```

### 4. Meta Alcanzada

```
🎉 ¡Felicidades!
Alcanzaste tu meta de ahorro de $500
```

---

## 🚀 Despliegue

### Android

```bash
# Generar APK
flutter build apk --release

# Generar AAB (Google Play)
flutter build appbundle --release
```

### iOS

```bash
# Generar IPA
flutter build ios --release
```

### Configurar Firebase Notifications

1. Ir a [Firebase Console](https://console.firebase.google.com)
2. Crear proyecto
3. Agregar apps para Android e iOS
4. Descargar archivos de configuración
5. Agregar a pubspec.yaml

---

## 📋 Checklist de Configuración

- [ ] Flutter instalado (3.0+)
- [ ] Firebase configurado (Firestore + Messaging)
- [ ] Permisos de notificación en AndroidManifest.xml
- [ ] APNs certificates en iOS
- [ ] JWT token authentication funcionando
- [ ] Notificaciones probadas en emulador/dispositivo
- [ ] API backend disponible
- [ ] Base de datos Firestore creada

---

## 🚨 Errores Comunes

### "No se pueden recibir notificaciones"
1. Verifica que el dispositivo está registrado
2. Comprueba permisos de notificación
3. Verifica que Firebase está configurado

### "Error en autenticación"
1. Verifica email y contraseña
2. Comprueba conexión a internet
3. Verifica que el backend está disponible

### "Message.data must not contain non-string values"
1. Asegúrate de convertir números a strings
2. Consulta [SOLUCION_ERROR_NON_STRING_VALUES.md](SOLUCION_ERROR_NON_STRING_VALUES.md)

---

## 📞 Soporte

- 📖 Ver documentación completa
- 🐛 Reportar bugs en GitHub Issues
- 💬 Preguntas en Discussions
- 📧 Email: [email de soporte]

---

## 🎉 ¡Listo!

Tu app Control de Gastos ahora incluye:
- ✅ Notificaciones push automáticas
- ✅ Alertas de presupuesto
- ✅ Consejos personalizados
- ✅ ML predicciones
- ✅ Análisis avanzado

¡Comienza a registrar gastos y recibe notificaciones instantáneas! 📲

---

**Versión**: 2.0  
**Última actualización**: 05 de Febrero de 2026  
**Estado**: ✅ Producción
