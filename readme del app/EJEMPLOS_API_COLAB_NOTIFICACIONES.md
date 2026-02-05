# 🐍 Ejemplos Prácticos: API Colab Enviando Notificaciones

## Ejemplo 1: Setup Básico en Google Colab

```python
# ============================================
# INSTALACIÓN Y CONFIGURACIÓN
# ============================================

# Celda 1: Instalar dependencias
!pip install firebase-admin
!pip install requests
!pip install google-cloud-firestore
!pip install pandas
!pip install numpy

# Celda 2: Importar librerías
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from firebase_admin import firestore
from datetime import datetime, timedelta
import json
import pandas as pd
from typing import List, Dict, Optional

# Celda 3: Subir y configurar credenciales
from google.colab import files

print("📁 Sube tu archivo de Service Account (JSON)")
uploaded = files.upload()

# Obtener nombre del archivo
credential_file = list(uploaded.keys())[0]
print(f"✅ Archivo subido: {credential_file}")

# Inicializar Firebase
cred = credentials.Certificate(credential_file)
firebase_admin.initialize_app(cred)

# Obtener referencias a Firebase
db = firestore.client()
print("✅ Firebase inicializado correctamente")
```

---

## Ejemplo 2: Clase para Manejar Notificaciones

```python
# ============================================
# CLASE PRINCIPAL DE NOTIFICACIONES
# ============================================

class NotificationManager:
    """
    Administrador de notificaciones para la app de gastos.
    Envía notificaciones desde Google Colab a usuarios de Flutter.
    """
    
    def __init__(self, db_client):
        """
        Inicializar el administrador
        
        Args:
            db_client: Cliente de Firestore
        """
        self.db = db_client
        self.notificaciones_enviadas = []
    
    def obtener_tokens_usuario(self, user_id: str) -> List[Dict]:
        """
        Obtener todos los tokens FCM activos de un usuario
        
        Args:
            user_id (str): ID del usuario en Firebase
        
        Returns:
            List[Dict]: Lista de tokens con información del dispositivo
        """
        try:
            tokens_ref = self.db.collection('users').document(user_id).collection('fcmTokens')
            docs = tokens_ref.where('isActive', '==', True).stream()
            
            tokens = []
            for doc in docs:
                token_data = doc.to_dict()
                tokens.append({
                    'token': token_data.get('token'),
                    'deviceName': token_data.get('deviceName'),
                    'platform': token_data.get('platform'),
                    'lastUpdated': token_data.get('lastUpdated')
                })
            
            print(f"✅ Encontrados {len(tokens)} tokens para usuario {user_id}")
            return tokens
        
        except Exception as e:
            print(f"❌ Error obteniendo tokens: {e}")
            return []
    
    def enviar_notificacion(self, user_id: str, titulo: str, 
                          cuerpo: str, datos: Optional[Dict] = None) -> Dict:
        """
        Enviar notificación a todos los dispositivos de un usuario
        
        Args:
            user_id (str): ID del usuario
            titulo (str): Título de la notificación
            cuerpo (str): Cuerpo de la notificación
            datos (dict): Datos adicionales opcionales
        
        Returns:
            dict: Resultado del envío
        """
        try:
            # Obtener tokens
            tokens = self.obtener_tokens_usuario(user_id)
            
            if not tokens:
                print(f"⚠️ No hay dispositivos activos para {user_id}")
                return self._crear_resultado(user_id, 0, 0, [])
            
            # Preparar datos
            notif_data = datos or {}
            notif_data['userId'] = user_id
            notif_data['timestamp'] = datetime.now().isoformat()
            
            # Crear y enviar mensaje
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=titulo,
                    body=cuerpo,
                ),
                data=notif_data,
                tokens=[t['token'] for t in tokens]
            )
            
            response = messaging.send_multicast(message)
            
            # Guardar información
            resultado = self._crear_resultado(
                user_id,
                response.success_count,
                response.failure_count,
                tokens
            )
            
            print(f"✅ Notificación enviada: {response.success_count} exitosas")
            return resultado
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return self._crear_resultado(user_id, 0, 0, [])
    
    def _crear_resultado(self, user_id: str, exitosas: int, 
                        fallidas: int, tokens: List) -> Dict:
        """Helper para crear diccionario de resultado"""
        return {
            'user_id': user_id,
            'exitosas': exitosas,
            'fallidas': fallidas,
            'total_dispositivos': len(tokens),
            'timestamp': datetime.now().isoformat(),
            'dispositivos': tokens
        }
    
    def enviar_lote(self, usuarios_datos: List[Dict]) -> Dict:
        """
        Enviar notificaciones a múltiples usuarios
        
        Args:
            usuarios_datos (List[Dict]): Lista con dicts:
                {
                    'user_id': 'xxx',
                    'titulo': 'Título',
                    'cuerpo': 'Cuerpo',
                    'datos': {...}
                }
        
        Returns:
            dict: Resumen de envíos
        """
        resumen = {
            'total_usuarios': len(usuarios_datos),
            'usuarios_exitosos': 0,
            'usuarios_fallidos': 0,
            'notificaciones_totales': 0,
            'detalles': []
        }
        
        for item in usuarios_datos:
            resultado = self.enviar_notificacion(
                user_id=item['user_id'],
                titulo=item['titulo'],
                cuerpo=item['cuerpo'],
                datos=item.get('datos')
            )
            
            resumen['notificaciones_totales'] += resultado['exitosas']
            
            if resultado['exitosas'] > 0:
                resumen['usuarios_exitosos'] += 1
            else:
                resumen['usuarios_fallidos'] += 1
            
            resumen['detalles'].append(resultado)
        
        return resumen

# Crear instancia global
notif_manager = NotificationManager(db)
print("✅ NotificationManager inicializado")
```

---

## Ejemplo 3: Notificaciones de Predicciones ML

```python
# ============================================
# PREDICCIONES ML
# ============================================

class MLNotificationService:
    """Servicio para enviar notificaciones de predicciones ML"""
    
    def __init__(self, notification_manager):
        self.notif = notification_manager
    
    def notificar_prediccion_gasto(self, user_id: str, prediccion: Dict):
        """
        Notificar predicción de gasto futuro
        
        Args:
            user_id (str): ID del usuario
            prediccion (dict): Datos con estructura:
                {
                    'prediccion_id': 'pred_001',
                    'gasto_predicho': 150.50,
                    'categoria': 'Alimentación',
                    'mes': '2025-03',
                    'confianza': 0.85,
                    'base_historica': 120.00
                }
        """
        gasto = prediccion['gasto_predicho']
        categoria = prediccion['categoria']
        confianza = prediccion['confianza']
        base = prediccion.get('base_historica', 0)
        variacion = gasto - base
        
        # Crear título basado en la variación
        if variacion > 0:
            variacion_str = f"↑ +${variacion:.2f}"
        else:
            variacion_str = f"↓ ${abs(variacion):.2f}"
        
        titulo = f"📊 Predicción: {categoria}"
        cuerpo = f"${gasto:.2f} ({variacion_str}) - Confianza: {confianza:.0%}"
        
        datos = {
            'tipo': 'prediccion',
            'prediccion_id': prediccion['prediccion_id'],
            'gasto_predicho': str(gasto),
            'categoria': categoria,
            'confianza': str(confianza),
            'variacion': str(variacion)
        }
        
        return self.notif.enviar_notificacion(user_id, titulo, cuerpo, datos)
    
    def notificar_anomalia(self, user_id: str, anomalia: Dict):
        """
        Notificar detección de anomalía en gastos
        
        Args:
            anomalia (dict):
                {
                    'tipo': 'gasto_anormal',
                    'monto': 500.00,
                    'categoria': 'Entretenimiento',
                    'razon': 'Exceede 3x el promedio',
                    'promedio': 150.00
                }
        """
        tipo = anomalia['tipo']
        monto = anomalia['monto']
        categoria = anomalia['categoria']
        promedio = anomalia.get('promedio', 0)
        
        titulo = "⚠️ Gasto Inusual Detectado"
        
        if promedio > 0:
            multiplicador = monto / promedio
            cuerpo = f"${monto:.2f} en {categoria} ({multiplicador:.1f}x promedio)"
        else:
            cuerpo = f"${monto:.2f} en {categoria}"
        
        datos = {
            'tipo': 'anomalia',
            'monto': str(monto),
            'categoria': categoria,
            'promedio': str(promedio),
            'razon': anomalia.get('razon', '')
        }
        
        return self.notif.enviar_notificacion(user_id, titulo, cuerpo, datos)
    
    def notificar_recomendacion(self, user_id: str, recomendacion: Dict):
        """
        Notificar recomendación personalizada del ML
        
        Args:
            recomendacion (dict):
                {
                    'accion': 'Reducir gastos en Entretenimiento',
                    'categoria': 'Entretenimiento',
                    'ahorro_potencial': 300.00,
                    'porcentaje': 0.35
                }
        """
        accion = recomendacion['accion']
        ahorro = recomendacion['ahorro_potencial']
        porcentaje = recomendacion.get('porcentaje', 0)
        
        titulo = "💡 Recomendación Personalizada"
        cuerpo = f"{accion} - Ahorro: ${ahorro:.2f} ({porcentaje:.0%})"
        
        datos = {
            'tipo': 'recomendacion',
            'accion': accion,
            'ahorro_potencial': str(ahorro),
            'porcentaje': str(porcentaje)
        }
        
        return self.notif.enviar_notificacion(user_id, titulo, cuerpo, datos)

# Crear instancia
ml_service = MLNotificationService(notif_manager)
print("✅ MLNotificationService inicializado")

# EJEMPLO DE USO:
# ===============
resultado = ml_service.notificar_prediccion_gasto('usuario_123', {
    'prediccion_id': 'pred_2025_02_001',
    'gasto_predicho': 245.50,
    'categoria': 'Alimentación',
    'mes': '2025-02',
    'confianza': 0.92,
    'base_historica': 200.00
})
print(resultado)
```

---

## Ejemplo 4: Análisis de Gastos y Notificaciones Automáticas

```python
# ============================================
# ANÁLISIS AUTOMÁTICO Y NOTIFICACIONES
# ============================================

class ExpenseAnalyzer:
    """Analiza gastos y envía notificaciones automáticas"""
    
    def __init__(self, notification_manager, ml_service):
        self.notif = notification_manager
        self.ml = ml_service
    
    def analizar_usuario_y_notificar(self, user_id: str) -> Dict:
        """
        Ejecutar análisis completo de un usuario y enviar notificaciones
        
        Args:
            user_id (str): ID del usuario en Firebase
        
        Returns:
            dict: Resumen de acciones tomadas
        """
        resumen = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'notificaciones_enviadas': 0,
            'acciones': []
        }
        
        try:
            # Obtener datos del usuario
            usuario_doc = self.db.collection('users').document(user_id).get()
            if not usuario_doc.exists:
                print(f"⚠️ Usuario {user_id} no encontrado")
                return resumen
            
            # Obtener gastos del mes actual
            gastos = self._obtener_gastos_mes_actual(user_id)
            
            if not gastos:
                print(f"ℹ️ No hay gastos para analizar en {user_id}")
                return resumen
            
            # 1. Detectar anomalías
            anomalias = self._detectar_anomalias(gastos)
            for anomalia in anomalias:
                self.ml.notificar_anomalia(user_id, anomalia)
                resumen['acciones'].append('anomalia_detectada')
                resumen['notificaciones_enviadas'] += 1
            
            # 2. Hacer predicciones
            predicciones = self._generar_predicciones(gastos)
            for prediccion in predicciones:
                self.ml.notificar_prediccion_gasto(user_id, prediccion)
                resumen['acciones'].append('prediccion_enviada')
                resumen['notificaciones_enviadas'] += 1
            
            # 3. Generar recomendaciones
            recomendaciones = self._generar_recomendaciones(gastos)
            for rec in recomendaciones:
                self.ml.notificar_recomendacion(user_id, rec)
                resumen['acciones'].append('recomendacion_enviada')
                resumen['notificaciones_enviadas'] += 1
            
            return resumen
        
        except Exception as e:
            print(f"❌ Error analizando usuario {user_id}: {e}")
            return resumen
    
    def _obtener_gastos_mes_actual(self, user_id: str) -> pd.DataFrame:
        """Obtener gastos del mes actual"""
        try:
            gastos_ref = (self.db.collection('users')
                         .document(user_id)
                         .collection('gastos'))
            
            # Filtrar por mes actual
            hoy = datetime.now()
            inicio_mes = datetime(hoy.year, hoy.month, 1)
            
            docs = gastos_ref.where('fecha', '>=', inicio_mes).stream()
            
            gastos_data = []
            for doc in docs:
                data = doc.to_dict()
                gastos_data.append(data)
            
            return pd.DataFrame(gastos_data)
        
        except Exception as e:
            print(f"Error obteniendo gastos: {e}")
            return pd.DataFrame()
    
    def _detectar_anomalias(self, gastos: pd.DataFrame) -> List[Dict]:
        """Detectar gastos anómalos usando estadísticas"""
        anomalias = []
        
        if gastos.empty:
            return anomalias
        
        # Agrupar por categoría
        for categoria in gastos['categoria'].unique():
            gastos_cat = gastos[gastos['categoria'] == categoria]['monto'].values
            
            if len(gastos_cat) < 2:
                continue
            
            # Calcular estadísticas
            promedio = gastos_cat.mean()
            desv_est = gastos_cat.std()
            
            # Detectar outliers (más de 2.5 desv est del promedio)
            for gasto in gastos_cat:
                z_score = abs((gasto - promedio) / desv_est) if desv_est > 0 else 0
                
                if z_score > 2.5 or gasto > promedio * 2.5:
                    anomalias.append({
                        'tipo': 'gasto_anormal',
                        'monto': float(gasto),
                        'categoria': categoria,
                        'promedio': float(promedio),
                        'razon': f'Excede {gasto/promedio:.1f}x el promedio'
                    })
        
        return anomalias
    
    def _generar_predicciones(self, gastos: pd.DataFrame) -> List[Dict]:
        """Generar predicciones simples"""
        predicciones = []
        
        if gastos.empty:
            return predicciones
        
        # Predicción simple por categoría
        for categoria in gastos['categoria'].unique():
            gastos_cat = gastos[gastos['categoria'] == categoria]
            promedio = gastos_cat['monto'].mean()
            cantidad = len(gastos_cat)
            
            # Confianza basada en cantidad de datos
            confianza = min(0.95, 0.5 + (cantidad * 0.05))
            
            predicciones.append({
                'prediccion_id': f"pred_{categoria}_{datetime.now().timestamp()}",
                'gasto_predicho': float(promedio * 1.1),  # Predicción: 10% más
                'categoria': categoria,
                'confianza': confianza,
                'base_historica': float(promedio)
            })
        
        return predicciones[:2]  # Top 2 categorías
    
    def _generar_recomendaciones(self, gastos: pd.DataFrame) -> List[Dict]:
        """Generar recomendaciones personalizadas"""
        recomendaciones = []
        
        if gastos.empty:
            return recomendaciones
        
        # Encontrar categoría con mayor gasto
        gastos_por_cat = gastos.groupby('categoria')['monto'].sum().sort_values(ascending=False)
        
        for categoria, total in gastos_por_cat.head(1).items():
            promedio_general = gastos['monto'].mean()
            
            if total > promedio_general * 2:
                ahorro = (total - promedio_general) * 0.5
                porcentaje = ahorro / total
                
                recomendaciones.append({
                    'accion': f'Reducir gastos en {categoria}',
                    'categoria': categoria,
                    'ahorro_potencial': float(ahorro),
                    'porcentaje': float(porcentaje)
                })
        
        return recomendaciones

# Crear instancia
analyzer = ExpenseAnalyzer(notif_manager, ml_service)
print("✅ ExpenseAnalyzer inicializado")

# EJEMPLO DE USO:
# ===============
resultado = analyzer.analizar_usuario_y_notificar('usuario_123')
print(json.dumps(resultado, indent=2, default=str))
```

---

## Ejemplo 5: Resumen Diario Automático

```python
# ============================================
# RESUMEN DIARIO DE GASTOS
# ============================================

def enviar_resumen_diario(user_id: str):
    """
    Enviar resumen diario de gastos a un usuario
    
    Args:
        user_id (str): ID del usuario
    """
    try:
        # Obtener gastos de hoy
        hoy = datetime.now().date()
        inicio = datetime.combine(hoy, datetime.min.time())
        fin = datetime.combine(hoy, datetime.max.time())
        
        gastos_ref = (db.collection('users')
                     .document(user_id)
                     .collection('gastos')
                     .where('fecha', '>=', inicio)
                     .where('fecha', '<=', fin))
        
        docs = gastos_ref.stream()
        gastos = [doc.to_dict() for doc in docs]
        
        if not gastos:
            return
        
        # Calcular totales
        total_diario = sum(g['monto'] for g in gastos)
        gastos_df = pd.DataFrame(gastos)
        categoria_mayor = gastos_df.groupby('categoria')['monto'].sum().idxmax()
        monto_categoria = gastos_df[gastos_df['categoria'] == categoria_mayor]['monto'].sum()
        cantidad = len(gastos)
        
        # Obtener promedio diario
        # (deberías calcularlo del histórico)
        promedio_diario = 100.00  # Placeholder
        tendencia = "↑" if total_diario > promedio_diario else "↓"
        porcentaje = abs((total_diario - promedio_diario) / promedio_diario * 100)
        
        titulo = "📊 Resumen Diario"
        cuerpo = f"Gastaste ${total_diario:.2f} ({tendencia} {porcentaje:.0f}%) | {categoria_mayor}: ${monto_categoria:.2f}"
        
        datos = {
            'tipo': 'resumen_diario',
            'total': str(total_diario),
            'cantidad': str(cantidad),
            'categoria_mayor': categoria_mayor,
            'promedio': str(promedio_diario),
            'fecha': hoy.isoformat()
        }
        
        return notif_manager.enviar_notificacion(user_id, titulo, cuerpo, datos)
    
    except Exception as e:
        print(f"Error enviando resumen: {e}")


def enviar_resumenes_diarios_todos_usuarios():
    """Enviar resumen diario a todos los usuarios activos"""
    try:
        usuarios = db.collection('users').stream()
        
        resultados = []
        for usuario_doc in usuarios:
            user_id = usuario_doc.id
            resultado = enviar_resumen_diario(user_id)
            if resultado:
                resultados.append(resultado)
        
        print(f"✅ {len(resultados)} resúmenes enviados")
        return resultados
    
    except Exception as e:
        print(f"Error: {e}")


# EJEMPLO DE USO:
# ===============
# Ejecutar cada día a las 22:00
# resultados = enviar_resumenes_diarios_todos_usuarios()
```

---

## Ejemplo 6: Programación Automática con Google Colab

```python
# ============================================
# EJECUCIÓN PROGRAMADA
# ============================================

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit

# Crear scheduler
scheduler = BackgroundScheduler()

# Tarea 1: Analizar todos los usuarios cada 6 horas
@scheduler.scheduled_job('interval', hours=6)
def tarea_analizar_todos():
    print(f"🔄 Iniciando análisis de todos los usuarios...")
    usuarios = db.collection('users').stream()
    
    for usuario_doc in usuarios:
        user_id = usuario_doc.id
        print(f"📊 Analizando {user_id}...")
        analyzer.analizar_usuario_y_notificar(user_id)


# Tarea 2: Enviar resumen diario a las 22:00
@scheduler.scheduled_job(CronTrigger(hour=22, minute=0))
def tarea_resumen_diario():
    print("📋 Enviando resúmenes diarios...")
    enviar_resumenes_diarios_todos_usuarios()


# Tarea 3: Verificar y limpiar tokens inactivos cada 24 horas
@scheduler.scheduled_job('interval', days=1)
def tarea_limpiar_tokens():
    print("🧹 Limpiando tokens inactivos...")
    usuarios = db.collection('users').stream()
    
    tokens_eliminados = 0
    for usuario_doc in usuarios:
        user_id = usuario_doc.id
        tokens_ref = usuario_doc.reference.collection('fcmTokens')
        
        # Eliminar tokens de hace más de 30 días
        fecha_limite = datetime.now() - timedelta(days=30)
        docs = (tokens_ref
               .where('lastUpdated', '<', fecha_limite)
               .stream())
        
        for doc in docs:
            doc.reference.delete()
            tokens_eliminados += 1
    
    print(f"✅ {tokens_eliminados} tokens eliminados")


# Iniciar scheduler
if not scheduler.running:
    scheduler.start()
    print("✅ Scheduler iniciado")

# Asegurar que se detiene limpiamente
atexit.register(lambda: scheduler.shutdown())
```

---

## Ejemplo 7: Testing y Validación

```python
# ============================================
# PRUEBAS Y VALIDACIÓN
# ============================================

def probar_configuracion():
    """Probar que todo está configurado correctamente"""
    
    print("\n🧪 INICIANDO PRUEBAS DE CONFIGURACIÓN\n")
    
    # 1. Probar conexión a Firebase
    print("1️⃣  Probando conexión a Firebase...")
    try:
        db.collection('_test').document('test').set({'test': True})
        db.collection('_test').document('test').delete()
        print("   ✅ Conexión OK\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        return False
    
    # 2. Listar usuarios
    print("2️⃣  Listando usuarios registrados...")
    try:
        usuarios = db.collection('users').stream()
        usuarios_list = [u.id for u in usuarios]
        print(f"   ✅ {len(usuarios_list)} usuarios encontrados")
        print(f"   Usuarios: {usuarios_list[:5]}...\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        return False
    
    # 3. Verificar tokens de un usuario
    if usuarios_list:
        user_id = usuarios_list[0]
        print(f"3️⃣  Verificando tokens para {user_id}...")
        try:
            tokens = notif_manager.obtener_tokens_usuario(user_id)
            print(f"   ✅ {len(tokens)} tokens encontrados\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
    
    # 4. Enviar notificación de prueba
    if usuarios_list and len(notif_manager.obtener_tokens_usuario(usuarios_list[0])) > 0:
        print(f"4️⃣  Enviando notificación de prueba...")
        try:
            resultado = notif_manager.enviar_notificacion(
                usuarios_list[0],
                "🧪 Prueba de Notificación",
                "Si ves esto, ¡todo está funcionando correctamente!",
                {'tipo': 'test', 'timestamp': datetime.now().isoformat()}
            )
            print(f"   ✅ Notificación enviada")
            print(f"   Exitosas: {resultado['exitosas']}")
            print(f"   Fallidas: {resultado['fallidas']}\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
    
    print("✅ Pruebas completadas\n")
    return True


# EJECUTAR PRUEBA:
# ================
probar_configuracion()
```

---

## Conclusión

Estos ejemplos te permiten:

1. **Setup inicial** en Google Colab
2. **Enviar notificaciones** desde Colab a Flutter
3. **Analizar gastos** y generar notificaciones automáticas
4. **Crear flujos personalizados** de análisis ML
5. **Programar tareas** automáticas
6. **Validar** que todo funciona

Adapta estos códigos a tu lógica de ML específica.
