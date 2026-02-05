# 🚀 Guía Completa: Flutter + Control de Gastos + Notificaciones Push

## Visión General

Esta guía integra la app Flutter **Control de Gastos** con el backend de notificaciones push para enviar alertas automáticas cuando el usuario registra gastos.

---

## 📱 Arquitectura

```
┌─────────────────┐
│  Flutter App    │
│ (Control Gastos)│
└────────┬────────┘
         │
         ├─ 1. Autentica usuario
         │    POST /api/v2/auth/token
         │
         ├─ 2. Registra dispositivo (1x)
         │    POST /api/v2/notifications/register-device
         │
         └─ 3. Envía notificaciones
              POST /api/v2/notifications/send
              
                    ↓
         
         ┌─────────────────────────────┐
         │   Backend (Python/Flask)    │
         │   API_MEJORADA.py           │
         └────────┬────────────────────┘
                  │
                  ├─ Convierte datos a strings
                  ├─ Busca tokens del usuario
                  └─ Envía vía Firebase Cloud Messaging
                  
                    ↓
                    
         ┌─────────────────────────────┐
         │   Firebase Cloud Messaging  │
         └────────┬────────────────────┘
                  │
                  └─ 📲 Notificación en el celular
```

---

## 🔑 Paso 1: Configurar Firebase en Flutter

### En `pubspec.yaml`

```yaml
dependencies:
  flutter:
    sdk: flutter
  firebase_core: ^2.24.0
  firebase_messaging: ^14.6.0
  http: ^1.1.0
  
dev_dependencies:
  flutter_test:
    sdk: flutter
```

### En `main.dart`

```dart
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Inicializar Firebase
  await Firebase.initializeApp();
  
  // Configurar notificaciones
  await _configureFirebaseNotifications();
  
  runApp(const MyApp());
}

Future<void> _configureFirebaseNotifications() async {
  // Solicitar permisos
  final settings = await FirebaseMessaging.instance.requestPermission(
    alert: true,
    badge: true,
    sound: true,
  );

  print('Permisos: ${settings.authorizationStatus}');

  // Obtener token
  final token = await FirebaseMessaging.instance.getToken();
  print('📱 FCM Token: $token');
  
  // Guardar token (importante para registrar dispositivo)
  prefs.setString('fcm_token', token ?? '');

  // Listener para mensajes en primer plano
  FirebaseMessaging.onMessage.listen((RemoteMessage message) {
    print('📬 Mensaje recibido: ${message.notification?.title}');
    print('Body: ${message.notification?.body}');
    
    // Mostrar notificación personalizada
    _showNotification(message);
  });

  // Listener para mensajes en segundo plano
  FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
    print('👆 Usuario abrió notificación');
    // Navegar a pantalla específica
  });
}

void _showNotification(RemoteMessage message) {
  // Implementar UI para mostrar notificación
  // (snackbar, dialog, etc.)
}
```

---

## 🔐 Paso 2: Autenticación

### Crear servicio de autenticación

```dart
// services/auth_service.dart

import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class AuthService {
  static const String apiUrl = 'https://api-google-colab.onrender.com';
  
  Future<bool> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$apiUrl/api/v2/auth/token'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'usuario': email,
          'contrasena': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        
        // Guardar token y usuario_id
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('jwt_token', data['token']);
        await prefs.setString('usuario_id', data['usuario_id']);
        
        print('✅ Autenticación exitosa');
        return true;
      } else {
        print('❌ Error de autenticación: ${response.body}');
        return false;
      }
    } catch (e) {
      print('❌ Exception: $e');
      return false;
    }
  }

  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('jwt_token');
  }

  Future<String?> getUsuarioId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('usuario_id');
  }
}
```

---

## 📲 Paso 3: Registrar Dispositivo

### Crear servicio de notificaciones

```dart
// services/notifications_service.dart

import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'auth_service.dart';

class NotificationsService {
  static const String apiUrl = 'https://api-google-colab.onrender.com';
  final AuthService authService = AuthService();

  /// Registra el dispositivo para recibir notificaciones
  /// Debe llamarse después de autenticar
  Future<bool> registrarDispositivo() async {
    try {
      // Obtener token FCM
      final fcmToken = await FirebaseMessaging.instance.getToken();
      if (fcmToken == null) {
        print('❌ No se pudo obtener token FCM');
        return false;
      }

      // Obtener JWT token
      final jwtToken = await authService.getToken();
      if (jwtToken == null) {
        print('❌ No hay JWT token');
        return false;
      }

      // Registrar dispositivo en API
      final response = await http.post(
        Uri.parse('$apiUrl/api/v2/notifications/register-device'),
        headers: {
          'Authorization': 'Bearer $jwtToken',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'dispositivo_token': fcmToken,
          'dispositivo_info': {
            'tipo': 'flutter',
            'app': 'Control de Gastos',
            'os': 'Android/iOS',
            'timestamp': DateTime.now().toString(),
          }
        }),
      );

      if (response.statusCode == 200) {
        print('✅ Dispositivo registrado correctamente');
        return true;
      } else {
        print('❌ Error al registrar dispositivo: ${response.body}');
        return false;
      }
    } catch (e) {
      print('❌ Exception: $e');
      return false;
    }
  }

  /// Envía una notificación de gasto
  Future<bool> enviarNotificacionGasto({
    required String titulo,
    required String cuerpo,
    required double monto,
    required String categoria,
    String? descripcion,
    String? tipoAlerta = 'gasto_registrado',
  }) async {
    try {
      final jwtToken = await authService.getToken();
      final usuarioId = await authService.getUsuarioId();

      if (jwtToken == null || usuarioId == null) {
        print('❌ Faltan credenciales');
        return false;
      }

      final response = await http.post(
        Uri.parse('$apiUrl/api/v2/notifications/send'),
        headers: {
          'Authorization': 'Bearer $jwtToken',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'usuario_id': usuarioId,
          'titulo': titulo,
          'cuerpo': cuerpo,
          'datos': {
            'monto': monto.toString(),  // ✅ String
            'categoria': categoria,
            'descripcion': descripcion ?? '',
            'tipo_alerta': tipoAlerta,
            'timestamp': DateTime.now().toString(),
          }
        }),
      );

      if (response.statusCode == 200) {
        print('✅ Notificación enviada');
        return true;
      } else {
        print('❌ Error: ${response.body}');
        return false;
      }
    } catch (e) {
      print('❌ Exception: $e');
      return false;
    }
  }

  /// Envía notificación de alerta de presupuesto
  Future<bool> enviarAlertaPresupuesto({
    required double presupuestoMensual,
    required double gastoActual,
  }) async {
    try {
      final jwtToken = await authService.getToken();
      final usuarioId = await authService.getUsuarioId();

      if (jwtToken == null || usuarioId == null) return false;

      final response = await http.post(
        Uri.parse('$apiUrl/api/v2/notifications/send-alert/$usuarioId'),
        headers: {
          'Authorization': 'Bearer $jwtToken',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'presupuesto_mensual': presupuestoMensual,
        }),
      );

      return response.statusCode == 200;
    } catch (e) {
      print('❌ Exception: $e');
      return false;
    }
  }
}
```

---

## 💾 Paso 4: Integrar con Registro de Gastos

### Modificar pantalla de registro de gasto

```dart
// screens/register_gasto_screen.dart

import 'package:flutter/material.dart';
import '../services/notifications_service.dart';

class RegisterGastoScreen extends StatefulWidget {
  const RegisterGastoScreen({Key? key}) : super(key: key);

  @override
  State<RegisterGastoScreen> createState() => _RegisterGastoScreenState();
}

class _RegisterGastoScreenState extends State<RegisterGastoScreen> {
  final notificationsService = NotificationsService();
  
  final descriptionController = TextEditingController();
  final montoController = TextEditingController();
  String selectedCategory = 'Comida';

  @override
  void initState() {
    super.initState();
    // Registrar dispositivo al abrir la pantalla (primera vez)
    _registrarDispositivoSiEsNecesario();
  }

  Future<void> _registrarDispositivoSiEsNecesario() async {
    final prefs = await SharedPreferences.getInstance();
    final estaRegistrado = prefs.getBool('dispositivo_registrado') ?? false;
    
    if (!estaRegistrado) {
      await notificationsService.registrarDispositivo();
      await prefs.setBool('dispositivo_registrado', true);
    }
  }

  Future<void> guardarGasto() async {
    final monto = double.parse(montoController.text);
    final descripcion = descriptionController.text;

    // Guardar en Firebase Firestore
    // ... tu código aquí ...

    // ✅ Enviar notificación
    await notificationsService.enviarNotificacionGasto(
      titulo: '💰 ${selectedCategory}',
      cuerpo: '\$${monto.toStringAsFixed(2)} en ${descripcion.isEmpty ? selectedCategory : descripcion}',
      monto: monto,
      categoria: selectedCategory,
      descripcion: descripcion,
      tipoAlerta: 'gasto_registrado',
    );

    // Mostrar confirmación
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('✅ Gasto registrado y notificación enviada')),
      );
    }

    // Limpiar formulario
    descriptionController.clear();
    montoController.clear();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Registrar Gasto')),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              // Categoría
              DropdownButton<String>(
                value: selectedCategory,
                onChanged: (String? newValue) {
                  setState(() {
                    selectedCategory = newValue ?? 'Comida';
                  });
                },
                items: ['Comida', 'Transporte', 'Ocio', 'Servicios', 'Otro']
                    .map((category) => DropdownMenuItem<String>(
                      value: category,
                      child: Text(category),
                    ))
                    .toList(),
              ),
              const SizedBox(height: 16),

              // Monto
              TextField(
                controller: montoController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  label: Text('Monto'),
                  prefixText: '\$',
                ),
              ),
              const SizedBox(height: 16),

              // Descripción
              TextField(
                controller: descriptionController,
                decoration: const InputDecoration(
                  label: Text('Descripción (opcional)'),
                ),
              ),
              const SizedBox(height: 32),

              // Botón Guardar
              ElevatedButton(
                onPressed: guardarGasto,
                child: const Text('Guardar Gasto'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    descriptionController.dispose();
    montoController.dispose();
    super.dispose();
  }
}
```

---

## 🎯 Flujo Completo de Uso

### 1. Usuario abre la app
- Autentica con email y contraseña
- Dispositivo se registra automáticamente (primera vez)

### 2. Usuario registra un gasto
- Ingresa monto: 50
- Categoría: Comida
- Presiona "Guardar"

### 3. App envía notificación
```json
{
  "usuario_id": "BCc7NaZ4KQTqFY3dUxgStWH62dh2",
  "titulo": "💰 Comida",
  "cuerpo": "$50.00 en Mi almuerzo",
  "datos": {
    "monto": "50.0",
    "categoria": "Comida",
    "tipo_alerta": "gasto_registrado"
  }
}
```

### 4. Notificación llega al celular
📲 **Comida** - $50.00 en Mi almuerzo

---

## 🔄 Ciclo de Vida

```
App inicia
    ↓
Firebase initialized
    ↓
Solicitar permisos notificaciones
    ↓
Usuario autentica
    ↓
Registrar dispositivo (si no existe)
    ↓
Usuario registra gasto
    ↓
Enviar notificación
    ↓
✅ Notificación en el celular
```

---

## 📋 Checklist

- [ ] Firebase configurado en Flutter
- [ ] Permisos de notificación solicitados
- [ ] AuthService creado
- [ ] NotificationsService creado
- [ ] Dispositivo se registra al autenticar
- [ ] Notificación se envía al registrar gasto
- [ ] JWT token es válido
- [ ] usuario_id es correcto
- [ ] Datos se convierten a strings

---

## 🚨 Errores Comunes

### "No se pudo obtener token FCM"
- Firebase no está inicializado
- Permisos no fueron otorgados
- Dispositivo sin Google Play Services

### "Message.data must not contain non-string values"
- Los datos tienen números o booleanos sin convertir a strings
- Solución: Usar `.toString()` en todos los valores

### "Token requerido o inválido"
- JWT token expiró
- Usuario no está autenticado
- Solución: Solicitar nuevo token

### "No hay dispositivos registrados"
- Usuario no registró su dispositivo
- Solución: Llamar a `registrarDispositivo()`

---

## 📚 Referencia Completa de Endpoints

| Endpoint | Método | Auth | Descripción |
|----------|--------|------|-------------|
| `/api/v2/auth/token` | POST | No | Obtener JWT token |
| `/api/v2/notifications/register-device` | POST | Sí | Registrar dispositivo |
| `/api/v2/notifications/send` | POST | Sí | Enviar notificación |
| `/api/v2/notifications/send-alert/{uid}` | POST | Sí | Alerta de presupuesto |
| `/api/v2/notifications/send-tips/{uid}` | POST | Sí | Consejos personalizados |
| `/api/v2/notifications/history` | GET | Sí | Ver historial |

---

## 🎉 ¡Listo!

Ya tienes integradas las notificaciones push en tu app Flutter. Cada vez que el usuario registre un gasto, recibirá una notificación automática.

¿Necesitas ayuda? Revisa [SOLUCION_ERROR_NON_STRING_VALUES.md](SOLUCION_ERROR_NON_STRING_VALUES.md)
