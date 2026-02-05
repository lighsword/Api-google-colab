# ============================================
# 🔔 CONTROLADOR DE NOTIFICACIONES PROFESIONAL
# ============================================
#
# Integración completa de notificaciones:
# - Firebase Cloud Messaging (FCM)
# - Firestore (almacenamiento de tokens)
# - Google Colab (envío de notificaciones ML)
# - Endpoints REST profesionales
#
# Autor: API Google Colab Mejorada
# Versión: 2.1
# Fecha: 2026-02-05

import firebase_admin
from firebase_admin import credentials, messaging, firestore
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import logging
from dataclasses import dataclass
import json

# ============================================
# CONFIGURACIÓN DE LOGGING
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('NotificationsController')

# ============================================
# ENUMS
# ============================================

class NotificationType(Enum):
    """Tipos de notificaciones soportadas"""
    GASTO_REGISTRADO = "gasto_registrado"
    ALERTA_PRESUPUESTO = "alerta_presupuesto"
    RECOMENDACION_ML = "recomendacion_ml"
    ANOMALIA_GASTOS = "anomalia_gastos"
    TIP_FINANCIERO = "tip_financiero"
    GENERAL = "general"


class AlertLevel(Enum):
    """Niveles de alerta"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


# ============================================
# DATACLASSES
# ============================================

@dataclass
class NotificationResult:
    """Resultado del envío de notificación"""
    exitoso: bool
    usuario_id: str
    tokens_exitosos: int
    tokens_fallidos: int
    total_dispositivos: int
    dispositivos: List[Dict] = None
    mensaje: str = ""
    timestamp: str = None

    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'exitoso': self.exitoso,
            'usuario_id': self.usuario_id,
            'tokens_exitosos': self.tokens_exitosos,
            'tokens_fallidos': self.tokens_fallidos,
            'total_dispositivos': self.total_dispositivos,
            'dispositivos': self.dispositivos or [],
            'mensaje': self.mensaje,
            'timestamp': self.timestamp or datetime.now().isoformat()
        }


# ============================================
# CLASE PRINCIPAL
# ============================================

class NotificationsController:
    """
    Controlador de notificaciones profesional.
    
    Características:
    - Envío de notificaciones por usuario_id
    - Búsqueda automática de tokens en Firestore
    - Soporte para múltiples dispositivos
    - Histórico de notificaciones
    - Reintentos automáticos
    - Validación de datos
    - Logging detallado
    """

    def __init__(self, db_instance=None):
        """
        Inicializar el controlador
        
        Args:
            db_instance: Cliente de Firestore (opcional, usa el global si no se proporciona)
        """
        try:
            self.db = db_instance or firestore.client()
            logger.info("✅ NotificationsController inicializado")
            self.notificaciones_enviadas = []
            self.max_reintentos = 3
        except Exception as e:
            logger.error(f"❌ Error inicializando controlador: {e}")
            raise

    # ============================================
    # MÉTODOS DE OBTENCIÓN DE TOKENS
    # ============================================

    def obtener_tokens_usuario(self, usuario_id: str) -> List[Dict]:
        """
        Obtener todos los tokens FCM activos de un usuario
        
        Args:
            usuario_id (str): ID del usuario en Firebase
        
        Returns:
            List[Dict]: Lista de tokens con información del dispositivo
        
        Ejemplo:
            tokens = controller.obtener_tokens_usuario("usuario_123")
            # [
            #   {
            #       'token': 'cJ3EHfN...',
            #       'dispositivo_info': {'tipo': 'Android', ...},
            #       'activo': True,
            #       'plataforma': 'android'
            #   },
            #   ...
            # ]
        """
        try:
            logger.info(f"🔍 Buscando tokens para usuario: {usuario_id}")
            
            tokens_ref = (
                self.db
                .collection('usuarios')
                .document(usuario_id)
                .collection('device_tokens')
            )
            
            docs = tokens_ref.where('activo', '==', True).stream()
            
            tokens = []
            for doc in docs:
                token_data = doc.to_dict()
                tokens.append({
                    'token': doc.id,  # El ID del documento es el token
                    'dispositivo_info': token_data.get('dispositivo_info', {}),
                    'activo': token_data.get('activo', True),
                    'plataforma': token_data.get('plataforma', 'unknown'),
                    'registrado_en': token_data.get('registrado_en'),
                    'ultima_actualizacion': token_data.get('ultima_actualizacion'),
                })
            
            logger.info(f"✅ Encontrados {len(tokens)} tokens activos para {usuario_id}")
            return tokens
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo tokens: {e}")
            return []

    # ============================================
    # MÉTODOS DE ENVÍO DE NOTIFICACIONES
    # ============================================

    def enviar_notificacion(
        self,
        usuario_id: str,
        titulo: str,
        cuerpo: str,
        tipo: NotificationType = NotificationType.GENERAL,
        datos_extra: Optional[Dict] = None,
        nivel_alerta: AlertLevel = AlertLevel.INFO
    ) -> NotificationResult:
        """
        Enviar notificación a todos los dispositivos de un usuario
        
        Args:
            usuario_id (str): ID del usuario
            titulo (str): Título de la notificación
            cuerpo (str): Cuerpo del mensaje
            tipo (NotificationType): Tipo de notificación
            datos_extra (dict): Datos adicionales (se convierten a strings automáticamente)
            nivel_alerta (AlertLevel): Nivel de alerta
        
        Returns:
            NotificationResult: Resultado del envío
        
        Ejemplo:
            resultado = controller.enviar_notificacion(
                usuario_id="usuario_123",
                titulo="💰 Gasto Registrado",
                cuerpo="Has registrado un gasto de $50",
                tipo=NotificationType.GASTO_REGISTRADO,
                datos_extra={
                    'monto': 50,
                    'categoria': 'Comida',
                    'descripcion': 'Almuerzo'
                }
            )
        """
        try:
            logger.info(f"📤 Enviando notificación a {usuario_id}")
            logger.info(f"   Tipo: {tipo.value}")
            logger.info(f"   Título: {titulo}")
            
            # Obtener tokens del usuario
            tokens = self.obtener_tokens_usuario(usuario_id)
            
            if not tokens:
                logger.warning(f"⚠️ No hay dispositivos activos para {usuario_id}")
                return NotificationResult(
                    exitoso=False,
                    usuario_id=usuario_id,
                    tokens_exitosos=0,
                    tokens_fallidos=0,
                    total_dispositivos=0,
                    mensaje="No hay dispositivos activos para este usuario"
                )
            
            # Preparar datos
            datos = self._preparar_datos(tipo, datos_extra)
            
            # Crear mensaje
            mensaje = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=titulo,
                    body=cuerpo,
                ),
                data=datos,
                tokens=[t['token'] for t in tokens]
            )
            
            # Enviar
            logger.info(f"📬 Enviando a {len(tokens)} dispositivos...")
            response = messaging.send_multicast(mensaje)
            
            # Procesar respuesta
            resultado = self._procesar_respuesta(
                response, usuario_id, tokens, tipo
            )
            
            # Guardar en historial
            self._guardar_en_historial(usuario_id, titulo, cuerpo, tipo, resultado)
            
            return resultado
        
        except Exception as e:
            logger.error(f"❌ Error enviando notificación: {e}")
            return NotificationResult(
                exitoso=False,
                usuario_id=usuario_id,
                tokens_exitosos=0,
                tokens_fallidos=0,
                total_dispositivos=0,
                mensaje=str(e)
            )

    def enviar_lote(
        self,
        usuarios_datos: List[Dict]
    ) -> Dict:
        """
        Enviar notificaciones a múltiples usuarios
        
        Args:
            usuarios_datos (List[Dict]): Lista de dicts con:
                {
                    'usuario_id': 'xxx',
                    'titulo': 'Título',
                    'cuerpo': 'Cuerpo',
                    'tipo': NotificationType.GENERAL,
                    'datos_extra': {...}
                }
        
        Returns:
            dict: Resumen de envíos
        
        Ejemplo:
            usuarios = [
                {
                    'usuario_id': 'user1',
                    'titulo': '💰 Gasto',
                    'cuerpo': '$50',
                    'tipo': NotificationType.GASTO_REGISTRADO,
                    'datos_extra': {'monto': 50}
                },
                {
                    'usuario_id': 'user2',
                    'titulo': '💡 Tip',
                    'cuerpo': 'Ahorra más',
                    'tipo': NotificationType.TIP_FINANCIERO,
                }
            ]
            resumen = controller.enviar_lote(usuarios)
        """
        logger.info(f"📤 Enviando lote de {len(usuarios_datos)} notificaciones")
        
        resumen = {
            'total_usuarios': len(usuarios_datos),
            'usuarios_exitosos': 0,
            'usuarios_fallidos': 0,
            'notificaciones_totales': 0,
            'detalles': []
        }
        
        for item in usuarios_datos:
            resultado = self.enviar_notificacion(
                usuario_id=item['usuario_id'],
                titulo=item['titulo'],
                cuerpo=item['cuerpo'],
                tipo=item.get('tipo', NotificationType.GENERAL),
                datos_extra=item.get('datos_extra'),
            )
            
            if resultado.exitoso:
                resumen['usuarios_exitosos'] += 1
                resumen['notificaciones_totales'] += resultado.tokens_exitosos
            else:
                resumen['usuarios_fallidos'] += 1
            
            resumen['detalles'].append(resultado.to_dict())
        
        logger.info(f"✅ Lote completado: {resumen['usuarios_exitosos']}/{resumen['total_usuarios']} exitosos")
        return resumen

    # ============================================
    # NOTIFICACIONES ESPECÍFICAS
    # ============================================

    def enviar_notificacion_gasto(
        self,
        usuario_id: str,
        monto: float,
        categoria: str,
        descripcion: str = ""
    ) -> NotificationResult:
        """
        Enviar notificación de gasto registrado
        
        Ejemplo:
            controller.enviar_notificacion_gasto(
                usuario_id="user_123",
                monto=50.0,
                categoria="Comida",
                descripcion="Almuerzo en restaurante"
            )
        """
        titulo = f"💰 {categoria}"
        cuerpo = f"Gastaste ${monto:.2f}"
        
        if descripcion:
            cuerpo += f" - {descripcion}"
        
        return self.enviar_notificacion(
            usuario_id=usuario_id,
            titulo=titulo,
            cuerpo=cuerpo,
            tipo=NotificationType.GASTO_REGISTRADO,
            datos_extra={
                'monto': monto,
                'categoria': categoria,
                'descripcion': descripcion,
            }
        )

    def enviar_alerta_presupuesto(
        self,
        usuario_id: str,
        categoria: str,
        gastado: float,
        presupuesto: float
    ) -> NotificationResult:
        """
        Enviar alerta de presupuesto
        
        Ejemplo:
            controller.enviar_alerta_presupuesto(
                usuario_id="user_123",
                categoria="Comida",
                gastado=45.0,
                presupuesto=50.0
            )
        """
        porcentaje = (gastado / presupuesto) * 100
        remaining = presupuesto - gastado
        
        if gastado >= presupuesto:
            titulo = "🚨 Presupuesto Excedido"
            cuerpo = f"¡Has excedido tu presupuesto de {categoria}!"
            nivel = AlertLevel.CRITICAL
        elif gastado >= presupuesto * 0.8:
            titulo = "⚠️ Presupuesto Casi Agotado"
            cuerpo = f"Te quedan ${remaining:.2f} de tu presupuesto de {categoria}"
            nivel = AlertLevel.WARNING
        else:
            titulo = "💰 Estado del Presupuesto"
            cuerpo = f"Has gastado ${gastado:.2f} de ${presupuesto:.2f} en {categoria}"
            nivel = AlertLevel.INFO
        
        return self.enviar_notificacion(
            usuario_id=usuario_id,
            titulo=titulo,
            cuerpo=cuerpo,
            tipo=NotificationType.ALERTA_PRESUPUESTO,
            datos_extra={
                'categoria': categoria,
                'gastado': gastado,
                'presupuesto': presupuesto,
                'porcentaje': round(porcentaje, 2),
            },
            nivel_alerta=nivel
        )

    def enviar_recomendacion_ml(
        self,
        usuario_id: str,
        recomendacion: str,
        categoria: str = "general",
        confianza: float = 0.85,
        accion: str = "revisar"
    ) -> NotificationResult:
        """
        Enviar recomendación del modelo de ML (desde Google Colab)
        
        Ejemplo:
            controller.enviar_recomendacion_ml(
                usuario_id="user_123",
                recomendacion="Podrías ahorrar más en comida",
                categoria="Comida",
                confianza=0.92,
                accion="ver_detalles"
            )
        """
        return self.enviar_notificacion(
            usuario_id=usuario_id,
            titulo="🤖 Recomendación Inteligente",
            cuerpo=recomendacion,
            tipo=NotificationType.RECOMENDACION_ML,
            datos_extra={
                'categoria': categoria,
                'confianza': round(confianza * 100, 1),
                'accion': accion,
            }
        )

    def enviar_alerta_anomalia(
        self,
        usuario_id: str,
        tipo_anomalia: str,
        monto: float,
        descripcion: str = "",
        categoria: str = "general"
    ) -> NotificationResult:
        """
        Enviar alerta de anomalía detectada
        
        Ejemplo:
            controller.enviar_alerta_anomalia(
                usuario_id="user_123",
                tipo_anomalia="gasto_inusual",
                monto=150.0,
                descripcion="Gasto muy superior a tu promedio",
                categoria="Entretenimiento"
            )
        """
        cuerpo = descripcion or "Se detectó un patrón inusual en tus gastos"
        
        return self.enviar_notificacion(
            usuario_id=usuario_id,
            titulo="🚨 Anomalía Detectada",
            cuerpo=cuerpo,
            tipo=NotificationType.ANOMALIA_GASTOS,
            datos_extra={
                'tipo_anomalia': tipo_anomalia,
                'monto': monto,
                'categoria': categoria,
                'descripcion': descripcion,
            },
            nivel_alerta=AlertLevel.CRITICAL
        )

    def enviar_tip_financiero(
        self,
        usuario_id: str,
        tip: str,
        categoria: str = "general",
        fuente: str = "ML"
    ) -> NotificationResult:
        """
        Enviar tip financiero
        
        Ejemplo:
            controller.enviar_tip_financiero(
                usuario_id="user_123",
                tip="Podrías establecer un presupuesto para entretenimiento",
                categoria="Entretenimiento",
                fuente="Machine Learning"
            )
        """
        return self.enviar_notificacion(
            usuario_id=usuario_id,
            titulo="💡 Consejo Financiero",
            cuerpo=tip,
            tipo=NotificationType.TIP_FINANCIERO,
            datos_extra={
                'categoria': categoria,
                'fuente': fuente,
            }
        )

    # ============================================
    # MÉTODOS AUXILIARES PRIVADOS
    # ============================================

    def _preparar_datos(
        self,
        tipo: NotificationType,
        datos_extra: Optional[Dict]
    ) -> Dict[str, str]:
        """
        Preparar datos para enviar a Firebase
        Convierte TODOS los valores a strings (requerimiento Firebase)
        
        Args:
            tipo: Tipo de notificación
            datos_extra: Datos adicionales
        
        Returns:
            dict: Datos con todos los valores como strings
        """
        datos = {'tipo': tipo.value}
        datos['timestamp'] = datetime.now().isoformat()
        
        if datos_extra:
            for clave, valor in datos_extra.items():
                # Convertir a string
                datos[str(clave)] = str(valor)
        
        logger.debug(f"📦 Datos preparados: {datos}")
        return datos

    def _procesar_respuesta(
        self,
        response,
        usuario_id: str,
        tokens: List[Dict],
        tipo: NotificationType
    ) -> NotificationResult:
        """
        Procesar respuesta de Firebase
        
        Args:
            response: Respuesta de messaging.send_multicast()
            usuario_id: ID del usuario
            tokens: Lista de tokens enviados
            tipo: Tipo de notificación
        
        Returns:
            NotificationResult: Resultado procesado
        """
        exitoso = response.failure_count == 0
        
        resultado = NotificationResult(
            exitoso=exitoso,
            usuario_id=usuario_id,
            tokens_exitosos=response.success_count,
            tokens_fallidos=response.failure_count,
            total_dispositivos=len(tokens),
            dispositivos=tokens,
            timestamp=datetime.now().isoformat()
        )
        
        if exitoso:
            logger.info(
                f"✅ Notificación enviada exitosamente: "
                f"{response.success_count}/{len(tokens)} dispositivos"
            )
            resultado.mensaje = f"Enviado a {response.success_count} dispositivos"
        else:
            logger.warning(
                f"⚠️ Algunos envíos fallaron: "
                f"{response.success_count} exitosos, "
                f"{response.failure_count} fallidos"
            )
            resultado.mensaje = (
                f"Enviado a {response.success_count}/{len(tokens)} dispositivos"
            )
        
        return resultado

    def _guardar_en_historial(
        self,
        usuario_id: str,
        titulo: str,
        cuerpo: str,
        tipo: NotificationType,
        resultado: NotificationResult
    ) -> None:
        """
        Guardar notificación en historial de Firestore
        
        Args:
            usuario_id: ID del usuario
            titulo: Título
            cuerpo: Cuerpo
            tipo: Tipo de notificación
            resultado: Resultado del envío
        """
        try:
            historial_data = {
                'titulo': titulo,
                'cuerpo': cuerpo,
                'tipo': tipo.value,
                'fecha_envio': firestore.SERVER_TIMESTAMP,
                'exitoso': resultado.exitoso,
                'tokens_exitosos': resultado.tokens_exitosos,
                'tokens_fallidos': resultado.tokens_fallidos,
            }
            
            self.db.collection('usuarios').document(usuario_id).collection(
                'notificaciones_historial'
            ).add(historial_data)
            
            logger.info(f"📝 Notificación guardada en historial")
        except Exception as e:
            logger.error(f"❌ Error guardando en historial: {e}")

    # ============================================
    # MÉTODOS DE CONSULTA
    # ============================================

    def obtener_historial(
        self,
        usuario_id: str,
        limite: int = 20
    ) -> List[Dict]:
        """
        Obtener historial de notificaciones de un usuario
        
        Args:
            usuario_id: ID del usuario
            limite: Número máximo de notificaciones
        
        Returns:
            List[Dict]: Historial de notificaciones
        """
        try:
            docs = (
                self.db
                .collection('usuarios')
                .document(usuario_id)
                .collection('notificaciones_historial')
                .order_by('fecha_envio', direction=firestore.Query.DESCENDING)
                .limit(limite)
                .stream()
            )
            
            historial = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                historial.append(data)
            
            logger.info(f"📋 Obtenido historial: {len(historial)} notificaciones")
            return historial
        except Exception as e:
            logger.error(f"❌ Error obteniendo historial: {e}")
            return []

    def obtener_estadisticas(self, usuario_id: str) -> Dict:
        """
        Obtener estadísticas de notificaciones
        
        Args:
            usuario_id: ID del usuario
        
        Returns:
            dict: Estadísticas
        """
        try:
            historial = self.obtener_historial(usuario_id, limite=100)
            
            total = len(historial)
            exitosas = sum(1 for n in historial if n.get('exitoso', False))
            por_tipo = {}
            
            for notif in historial:
                tipo = notif.get('tipo', 'general')
                por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
            
            return {
                'total_notificaciones': total,
                'exitosas': exitosas,
                'fallidas': total - exitosas,
                'tasa_exito': (exitosas / total * 100) if total > 0 else 0,
                'por_tipo': por_tipo
            }
        except Exception as e:
            logger.error(f"❌ Error calculando estadísticas: {e}")
            return {}


# ============================================
# FUNCIÓN AUXILIAR PARA INICIALIZAR
# ============================================

def inicializar_controlador(db=None) -> NotificationsController:
    """
    Inicializar y obtener el controlador de notificaciones
    
    Args:
        db: Cliente de Firestore (opcional)
    
    Returns:
        NotificationsController: Controlador inicializado
    """
    return NotificationsController(db_instance=db)
