# ============================================================
# 🚀 API MEJORADA CON 20 CARACTERÍSTICAS DE IA
# ============================================================
# PREDICCIÓN DE GASTOS (5 mejoras):
# 1. Predicción por categoría
# 2. Predicción mensual (30 días)
# 3. Detección de anomalías
# 4. Múltiples modelos ML (ARIMA, Prophet, LSTM)
# 5. Análisis de estacionalidad
#
# ANÁLISIS ESTADÍSTICO (5 mejoras):
# 6. Correlaciones entre categorías
# 7. Análisis temporal (mes actual vs anterior)
# 8. Clustering automático de gastos
# 9. Detección de tendencias
# 10. Identificación de outliers (IQR + Z-Score)
#
# RECOMENDACIONES DE AHORRO (5 mejoras):
# 11. Metas de ahorro (objetivos específicos)
# 12. Tips personalizados (basados en patrones)
# 13. Alertas de presupuesto (límites mensuales)
# 14. Gamificación (puntuación financiera)
# 15. Reportes automáticos (resumen semanal)
#
# GRÁFICOS Y VISUALIZACIÓN (5 mejoras):
# 16. Calendario de calor (Heatmap de gastos)
# 17. Gráfico Sankey (Flujo de dinero)
# 18. Dashboard interactivo (Panel con filtros)
# 19. Comparativas (Mes vs mes anterior)
# 20. Exportar como imagen (PNG/PDF)
# ============================================================

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, g
from werkzeug.exceptions import BadRequest
from firebase_admin import auth as firebase_auth
from functools import wraps
import jwt
import uuid
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from scipy.stats import pearsonr
import warnings
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import base64

warnings.filterwarnings('ignore')

# Cargar variables de entorno
load_dotenv()

# ============================================================
# 🔥 CONFIGURACIÓN DE FIREBASE
# ============================================================
FIREBASE_AVAILABLE = False
db = None

# ID de la base de datos Firestore - tu BD se llama "gestofin"
FIRESTORE_DATABASE_ID = os.getenv('FIRESTORE_DATABASE_ID', 'gestofin')

try:
    # Opción 1: Usar archivo JSON si existe localmente
    if os.path.exists('gestor-financiero-28ac2-firebase-adminsdk-fbsvc-6efa11cbf8.json'):
        cred = credentials.Certificate('gestor-financiero-28ac2-firebase-adminsdk-fbsvc-6efa11cbf8.json')
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://gestor-financiero-28ac2.firebaseio.com',
            'projectId': 'gestor-financiero-28ac2'
        })
        # Usar Firestore con database_id específico (nombre correcto del parámetro)
        try:
            from google.cloud.firestore_v1 import Client as FirestoreClient
            db = FirestoreClient(project='gestor-financiero-28ac2', database=FIRESTORE_DATABASE_ID, credentials=cred._credentials)
            print(f"✅ Firebase conectado con database_id='{FIRESTORE_DATABASE_ID}' (Cliente directo)")
        except Exception as e1:
            try:
                db = firestore.client(database_id=FIRESTORE_DATABASE_ID)
                print(f"✅ Firebase conectado con database_id='{FIRESTORE_DATABASE_ID}'")
            except TypeError:
                db = firestore.client()
                print(f"⚠️ SDK antiguo - usando database (default), no soporta database_id")
        FIREBASE_AVAILABLE = True
        try:
            import firebase_admin as _fb
            app_opts = _fb.get_app().options if _fb.get_app() else {}
            print(f"📡 Firestore ProjectId: {app_opts.get('projectId')}")
        except Exception:
            pass
    # Opción 2: Usar variables de entorno en Render
    elif all([os.getenv('FIREBASE_TYPE'), os.getenv('FIREBASE_PROJECT_ID'), os.getenv('FIREBASE_PRIVATE_KEY')]):
        firebase_config = {
            "type": os.getenv('FIREBASE_TYPE'),
            "project_id": os.getenv('FIREBASE_PROJECT_ID'),
            "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
            "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
            "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
            "client_id": os.getenv('FIREBASE_CLIENT_ID'),
            "auth_uri": os.getenv('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
            "token_uri": os.getenv('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
            "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
            "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL')
        }
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred, {
            'databaseURL': f"https://{os.getenv('FIREBASE_PROJECT_ID')}.firebaseio.com",
            'projectId': os.getenv('FIREBASE_PROJECT_ID')
        })
        # Usar Firestore con database_id específico (nombre correcto del parámetro)
        try:
            from google.cloud.firestore_v1 import Client as FirestoreClient
            from google.oauth2 import service_account
            # Crear credenciales desde el config
            gcloud_creds = service_account.Credentials.from_service_account_info(firebase_config)
            db = FirestoreClient(project=os.getenv('FIREBASE_PROJECT_ID'), database=FIRESTORE_DATABASE_ID, credentials=gcloud_creds)
            print(f"✅ Firebase conectado con database_id='{FIRESTORE_DATABASE_ID}' (Cliente directo)")
        except Exception as e1:
            print(f"⚠️ Error con cliente directo: {e1}")
            try:
                db = firestore.client(database_id=FIRESTORE_DATABASE_ID)
                print(f"✅ Firebase conectado con database_id='{FIRESTORE_DATABASE_ID}'")
            except TypeError:
                db = firestore.client()
                print(f"⚠️ SDK antiguo - usando database (default), no soporta database_id")
        FIREBASE_AVAILABLE = True
        try:
            import firebase_admin as _fb
            app_opts = _fb.get_app().options if _fb.get_app() else {}
            print(f"📡 Firestore ProjectId: {app_opts.get('projectId')} | ENV: {os.getenv('FIREBASE_PROJECT_ID')}")
        except Exception:
            pass
    else:
        print("⚠️  Firebase no disponible - Configura variables de entorno en Render")
except Exception as e:
    print(f"⚠️  Error conectando Firebase: {str(e)}")

# ============================================================
# 🔐 CONFIGURACIÓN DE SEGURIDAD Y AUTENTICACIÓN
# ============================================================
SECRET_KEY = os.getenv('SECRET_KEY', 'tu_clave_secreta_super_segura_2024')
TOKEN_EXPIRATION_HOURS = 24

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# Diccionario para almacenar tokens activos
active_tokens = {}

def generate_token(user_id='default_user'):
    """Genera un JWT token único con expiración"""
    try:
        payload = {
            'user_id': user_id,
            'token_id': str(uuid.uuid4()),
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRATION_HOURS)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        active_tokens[token] = payload
        return token
    except Exception as e:
        return None

def verify_token(token):
    """Verifica la validez del JWT token. Devuelve payload si es válido, False si no."""
    try:
        if token not in active_tokens:
            return False
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False

def token_required(f):
    """Decorator para validar token en endpoints protegidos"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Obtener token del header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Token formato inválido. Usar: Authorization: Bearer <token>'}), 401
        elif 'X-API-Key' in request.headers:
            token = request.headers['X-API-Key']
        
        if not token:
            return jsonify({'error': 'Token requerido. Obtener en /api/v2/auth/token'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        # Exponer user_id en el contexto de la request
        try:
            g.user_id = payload.get('user_id')
        except Exception:
            pass
        
        return f(*args, **kwargs)
    return decorated

# Importes opcionales para visualización
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import seaborn as sns
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import kaleido
    KALEIDO_AVAILABLE = True
except ImportError:
    KALEIDO_AVAILABLE = False

# Importes opcionales para modelos avanzados
try:
    from statsmodels.tsa.arima.model import ARIMA
    ARIMA_AVAILABLE = True
except ImportError:
    ARIMA_AVAILABLE = False

try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense
    LSTM_AVAILABLE = True
except ImportError:
    LSTM_AVAILABLE = False


# ============================================================
# 🛠️ UTILIDADES Y HELPERS
# ============================================================

def validate_expense_data(data):
    """Valida que los datos tengan campos requeridos."""
    required_fields = {'fecha', 'monto', 'categoria'}
    return all(field in item for item in data for field in required_fields)


def prepare_dataframe(expenses):
    """Prepara DataFrame con validación y conversión de tipos."""
    df = pd.DataFrame(expenses)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['monto'] = pd.to_numeric(df['monto'])
    return df.sort_values('fecha').reset_index(drop=True)


def _expenses_from_firebase_for_user(user_id):
    """Obtiene gastos de Firestore y los adapta al esquema esperado por endpoints (fecha, monto, categoria)."""
    if not FIREBASE_AVAILABLE or not db:
        return None, 'Firebase no disponible'
    gastos, error = obtener_gastos_firebase(user_id)
    if error:
        return None, error
    expenses = []
    for g_item in gastos:
        try:
            dt = procesar_fecha(g_item.get('fecha') or g_item.get('createdAt'))
            categoria = g_item.get('categoria') or 'Sin categoría'
            monto_val = g_item.get('cantidad') if 'cantidad' in g_item else g_item.get('monto', 0)
            monto = float(monto_val) if monto_val is not None else 0.0
            expenses.append({
                'fecha': dt.strftime('%Y-%m-%d'),
                'monto': monto,
                'categoria': categoria
            })
        except Exception:
            continue
    return expenses, None


def _get_expenses_or_firebase(data):
    """Devuelve expenses del body si son válidos; si no, intenta cargarlos desde Firebase usando g.user_id."""
    data = data or {}
    expenses = data.get('expenses') or []
    if expenses and validate_expense_data(expenses):
        return expenses, None
    # Intentar con Firebase si hay user_id en token
    try:
        user_id = getattr(g, 'user_id', None)
    except Exception:
        user_id = None
    if user_id:
        return _expenses_from_firebase_for_user(user_id)
    return None, 'No se proporcionaron expenses y no se pudo determinar el usuario'


# ============================================================
# 1️⃣ PREDICCIÓN POR CATEGORÍA
# ============================================================

def predict_by_category(df, days=30):
    """
    Predice gastos separados para cada categoría.
    
    Args:
        df: DataFrame con gastos
        days: Días a predecir (default: 30)
    
    Returns:
        Dict con predicciones por categoría
    """
    predictions = {}
    
    for category in df['categoria'].unique():
        cat_data = df[df['categoria'] == category].copy()
        
        if len(cat_data) < 3:
            continue
        
        # Features temporales
        cat_data['day_of_week'] = cat_data['fecha'].dt.dayofweek
        cat_data['day_of_month'] = cat_data['fecha'].dt.day
        
        X = cat_data[['day_of_week', 'day_of_month']].values
        y = cat_data['monto'].values
        
        # Entrenar modelo
        model = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
        model.fit(X, y)
        
        # Predicciones
        last_date = cat_data['fecha'].max()
        preds = []
        
        for i in range(1, days + 1):
            future_date = last_date + timedelta(days=i)
            features = np.array([[future_date.weekday(), future_date.day]])
            pred_value = max(0, model.predict(features)[0])
            
            preds.append({
                'fecha': future_date.strftime('%Y-%m-%d'),
                'monto': round(pred_value, 2)
            })
        
        predictions[category] = {
            'predicciones': preds,
            'total': round(sum(p['monto'] for p in preds), 2),
            'promedio_diario': round(sum(p['monto'] for p in preds) / days, 2)
        }
    
    return predictions


# ============================================================
# 2️⃣ PREDICCIÓN MENSUAL (30 DÍAS)
# ============================================================

def predict_monthly(df, days=30):
    """
    Predice gastos para los próximos 30 días con intervalos de confianza.
    
    Args:
        df: DataFrame con gastos
        days: Días a predecir (default: 30)
    
    Returns:
        Dict con predicciones diarias y resumen semanal
    """
    # Agrupar por día
    daily = df.groupby(df['fecha'].dt.date)['monto'].sum()
    
    avg_daily = daily.mean()
    std_daily = daily.std()
    
    predictions = []
    last_date = df['fecha'].max()
    
    for i in range(1, days + 1):
        future_date = last_date + timedelta(days=i)
        week = (i - 1) // 7 + 1
        
        # Ajustes por patrón
        if future_date.weekday() >= 5:  # Fin de semana
            base_pred = avg_daily * 1.15
        else:
            base_pred = avg_daily
        
        predictions.append({
            'fecha': future_date.strftime('%Y-%m-%d'),
            'dia_semana': future_date.strftime('%A'),
            'semana': week,
            'prediccion': round(base_pred, 2),
            'min': round(max(0, base_pred - std_daily), 2),
            'max': round(base_pred + std_daily, 2)
        })
    
    df_pred = pd.DataFrame(predictions)
    
    # Resumen semanal
    weekly = df_pred.groupby('semana').agg({
        'prediccion': ['sum', 'mean']
    }).round(2)
    # Aplanar columnas MultiIndex para que sea JSON-serializable
    weekly.columns = ['total', 'promedio_diario']
    weekly_summary = {
        int(k): {
            'total': float(v['total']),
            'promedio_diario': float(v['promedio_diario'])
        }
        for k, v in weekly.to_dict(orient='index').items()
    }
    
    return {
        'diarias': predictions,
        'total_mes': round(df_pred['prediccion'].sum(), 2),
        'promedio_diario': round(avg_daily, 2),
        'resumen_semanal': weekly_summary
    }


# ============================================================
# 3️⃣ DETECCIÓN DE ANOMALÍAS
# ============================================================

def detect_anomalies(df, zscore_threshold=2.5):
    """
    Detecta gastos anómalos usando múltiples métodos.
    
    Args:
        df: DataFrame con gastos
        zscore_threshold: Umbral de desviación estándar
    
    Returns:
        Dict con anomalías detectadas
    """
    anomalies = []
    
    # Método 1: Z-Score
    from scipy.stats import zscore
    z_scores = np.abs(zscore(df['monto']))
    z_anomalies = df[z_scores > zscore_threshold]
    
    for idx, row in z_anomalies.iterrows():
        anomalies.append({
            'fecha': row['fecha'].strftime('%Y-%m-%d'),
            'monto': row['monto'],
            'categoria': row['categoria'],
            'metodo': 'Z-Score',
            'razon': f"Desviación {z_scores[idx]:.2f}σ del promedio"
        })
    
    # Método 2: Isolation Forest
    iso = IsolationForest(contamination=0.1, random_state=42)
    outliers = iso.fit_predict(df[['monto']].values) == -1
    
    for idx in df[outliers].index:
        if idx not in z_anomalies.index:
            row = df.loc[idx]
            anomalies.append({
                'fecha': row['fecha'].strftime('%Y-%m-%d'),
                'monto': row['monto'],
                'categoria': row['categoria'],
                'metodo': 'Isolation Forest',
                'razon': 'Patrón anómalo detectado'
            })
    
    # Deduplicar
    unique_anomalies = {
        (a['fecha'], a['monto']): a 
        for a in anomalies
    }.values()
    
    return {
        'cantidad': len(unique_anomalies),
        'anomalias': list(unique_anomalies),
        'porcentaje': round((len(unique_anomalies) / len(df)) * 100, 2)
    }


# ============================================================
# 4️⃣ MÚLTIPLES MODELOS ML
# ============================================================

def compare_models(df):
    """
    Entrena y compara múltiples modelos ML.
    
    Args:
        df: DataFrame con gastos
    
    Returns:
        Dict con resultados de comparación y mejor modelo
    """
    results = {}
    
    X = np.arange(len(df)).reshape(-1, 1)
    y = df['monto'].values
    split = int(len(df) * 0.8)
    
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    # Modelo 1: Random Forest
    rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    
    results['RandomForest'] = {
        'mae': round(mean_absolute_error(y_test, y_pred_rf), 2),
        'r2': round(r2_score(y_test, y_pred_rf), 4),
        'modelo': 'RandomForest'
    }
    
    # Modelo 2: ARIMA (si disponible)
    if ARIMA_AVAILABLE and len(y_train) >= 10:
        try:
            arima = ARIMA(y_train, order=(1, 1, 1))
            arima_fit = arima.fit()
            y_pred_arima = arima_fit.predict(start=len(y_train), end=len(y_train) + len(y_test) - 1)
            
            results['ARIMA'] = {
                'mae': round(mean_absolute_error(y_test, y_pred_arima[:len(y_test)]), 2),
                'r2': round(r2_score(y_test, y_pred_arima[:len(y_test)]), 4),
                'modelo': 'ARIMA'
            }
        except:
            pass
    
    # Modelo 3: Exponential Smoothing (Prophet alternativo)
    if PROPHET_AVAILABLE and len(y_train) >= 10:
        try:
            exp = ExponentialSmoothing(y_train, trend='add')
            exp_fit = exp.fit()
            y_pred_exp = exp_fit.predict(start=len(y_train), end=len(y_train) + len(y_test) - 1)
            
            results['ExponentialSmoothing'] = {
                'mae': round(mean_absolute_error(y_test, y_pred_exp[:len(y_test)]), 2),
                'r2': round(r2_score(y_test, y_pred_exp[:len(y_test)]), 4),
                'modelo': 'ExponentialSmoothing'
            }
        except:
            pass
    
    # Encontrar mejor modelo
    best_model = max(results.items(), key=lambda x: x[1]['r2'])
    
    return {
        'modelos': list(results.keys()),
        'resultados': results,
        'mejor': best_model[0],
        'mejor_r2': best_model[1]['r2']
    }


# ============================================================
# 5️⃣ ANÁLISIS DE ESTACIONALIDAD
# ============================================================

def analyze_seasonality(df):
    """
    Detecta patrones semanales y mensuales.
    
    Args:
        df: DataFrame con gastos
    
    Returns:
        Dict con patrones identificados
    """
    patterns = {}
    
    # Por día de semana
    df['dia_semana'] = df['fecha'].dt.day_name()
    df['num_dia'] = df['fecha'].dt.weekday
    
    weekly = []
    dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for i, day in enumerate(dias):
        day_data = df[df['num_dia'] == i]
        if len(day_data) > 0:
            weekly.append({
                'dia': day,
                'promedio': round(day_data['monto'].mean(), 2),
                'total': round(day_data['monto'].sum(), 2)
            })
    
    patterns['semanal'] = weekly
    
    # Fin de semana vs entre semana
    is_weekend = df['num_dia'].isin([5, 6])
    weekend_avg = df[is_weekend]['monto'].mean()
    weekday_avg = df[~is_weekend]['monto'].mean()
    
    patterns['fin_semana_vs_semana'] = {
        'fin_semana': round(weekend_avg, 2),
        'entre_semana': round(weekday_avg, 2),
        'diferencia_pct': round(((weekend_avg - weekday_avg) / weekday_avg * 100), 2)
    }
    
    # Día más caro
    if weekly:
        most_expensive_day = max(weekly, key=lambda x: x['promedio'])
        patterns['dia_mas_caro'] = most_expensive_day['dia']
    
    return patterns


# ============================================================
# 6️⃣ ANÁLISIS DE CORRELACIONES
# ============================================================

def analyze_correlations(df):
    """
    Encuentra relaciones entre categorías de gastos.
    
    Args:
        df: DataFrame con gastos
    
    Returns:
        Dict con correlaciones y patrones
    """
    correlations = {}
    categories = df['categoria'].unique()
    
    # Agrupar por categoría y fecha
    df['fecha_dia'] = df['fecha'].dt.date
    
    for cat in categories:
        correlations[cat] = {}
    
    # Calcular correlaciones entre categorías
    for i, cat1 in enumerate(categories):
        for cat2 in categories[i+1:]:
            cat1_data = df[df['categoria'] == cat1].groupby('fecha_dia')['monto'].sum()
            cat2_data = df[df['categoria'] == cat2].groupby('fecha_dia')['monto'].sum()
            
            # Alinear índices
            common_dates = cat1_data.index.intersection(cat2_data.index)
            
            if len(common_dates) > 2:
                corr, _ = pearsonr(
                    cat1_data[common_dates].values,
                    cat2_data[common_dates].values
                )
                correlations[cat1][cat2] = round(corr, 3)
                correlations[cat2][cat1] = round(corr, 3)
    
    # Encontrar categorías más correlacionadas
    max_corr = {'cat1': '', 'cat2': '', 'valor': -1}
    for cat, corrs in correlations.items():
        for other_cat, corr_value in corrs.items():
            if corr_value > max_corr['valor']:
                max_corr = {'cat1': cat, 'cat2': other_cat, 'valor': corr_value}
    
    return {
        'correlaciones': correlations,
        'mas_correlacionadas': max_corr if max_corr['valor'] > -1 else None,
        'interpretacion': 'Valores cerca de 1 indican gasto simultáneo'
    }


# ============================================================
# 7️⃣ ANÁLISIS TEMPORAL - MES ACTUAL VS ANTERIOR
# ============================================================

def analyze_temporal_comparison(df):
    """
    Compara gastos del mes actual vs mes anterior.
    
    Args:
        df: DataFrame con gastos
    
    Returns:
        Dict con comparación temporal
    """
    df['año_mes'] = df['fecha'].dt.to_period('M')
    
    monthly_totals = df.groupby('año_mes')['monto'].agg(['sum', 'count', 'mean']).reset_index()
    monthly_totals = monthly_totals.sort_values('año_mes', ascending=False)
    
    if len(monthly_totals) < 2:
        return {'error': 'Se necesitan al menos 2 meses de datos'}
    
    current_month = monthly_totals.iloc[0]
    previous_month = monthly_totals.iloc[1]
    
    # Calcular variaciones
    change_amount = current_month['sum'] - previous_month['sum']
    change_pct = (change_amount / previous_month['sum'] * 100) if previous_month['sum'] > 0 else 0
    
    # Análisis por categoría
    current_cat = df[df['año_mes'] == current_month['año_mes']].groupby('categoria')['monto'].sum()
    previous_cat = df[df['año_mes'] == previous_month['año_mes']].groupby('categoria')['monto'].sum()
    
    cat_changes = {}
    for cat in current_cat.index:
        prev_amount = previous_cat.get(cat, 0)
        curr_amount = current_cat[cat]
        cat_change = curr_amount - prev_amount
        cat_changes[cat] = {
            'mes_actual': round(curr_amount, 2),
            'mes_anterior': round(prev_amount, 2),
            'cambio': round(cat_change, 2),
            'cambio_pct': round((cat_change / max(prev_amount, 1)) * 100, 2)
        }
    
    return {
        'mes_actual': str(current_month['año_mes']),
        'mes_anterior': str(previous_month['año_mes']),
        'total_actual': round(current_month['sum'], 2),
        'total_anterior': round(previous_month['sum'], 2),
        'cambio_absoluto': round(change_amount, 2),
        'cambio_porcentual': round(change_pct, 2),
        'tendencia': 'AUMENTO' if change_pct > 0 else 'DISMINUCIÓN',
        'transacciones_actual': int(current_month['count']),
        'transacciones_anterior': int(previous_month['count']),
        'por_categoria': cat_changes
    }


# ============================================================
# 8️⃣ CLUSTERING - AGRUPAR GASTOS SIMILARES
# ============================================================

def perform_clustering(df, n_clusters=3):
    """
    Agrupa gastos similares automáticamente usando KMeans.
    
    Args:
        df: DataFrame con gastos
        n_clusters: Número de grupos (default: 3)
    
    Returns:
        Dict con clusters identificados
    """
    if len(df) < n_clusters:
        n_clusters = max(2, len(df) // 2)
    
    # Preparar features
    X = df[['monto']].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Entrenar KMeans
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled)
    
    # Analizar clusters
    clusters_info = []
    for cluster_id in range(n_clusters):
        cluster_data = df[df['cluster'] == cluster_id]
        
        clusters_info.append({
            'id': cluster_id,
            'cantidad_gastos': len(cluster_data),
            'monto_minimo': round(cluster_data['monto'].min(), 2),
            'monto_maximo': round(cluster_data['monto'].max(), 2),
            'monto_promedio': round(cluster_data['monto'].mean(), 2),
            'total': round(cluster_data['monto'].sum(), 2),
            'categorias': cluster_data['categoria'].unique().tolist(),
            'descripcion': f"Gastos de ${cluster_data['monto'].min():.2f} a ${cluster_data['monto'].max():.2f}"
        })
    
    clusters_info = sorted(clusters_info, key=lambda x: x['monto_promedio'])
    
    return {
        'numero_clusters': n_clusters,
        'clusters': clusters_info,
        'distribucion': [c['cantidad_gastos'] for c in clusters_info]
    }


# ============================================================
# 9️⃣ ANÁLISIS DE TENDENCIAS
# ============================================================

def detect_trends(df):
    """
    Detecta si los gastos están subiendo o bajando en el tiempo.
    
    Args:
        df: DataFrame con gastos
    
    Returns:
        Dict con tendencias identificadas
    """
    # Agrupar por semana
    df['semana'] = df['fecha'].dt.isocalendar().week
    df['año'] = df['fecha'].dt.isocalendar().year
    
    weekly_totals = df.groupby(['año', 'semana'])['monto'].sum().reset_index()
    weekly_totals = weekly_totals.sort_values(['año', 'semana'])
    
    if len(weekly_totals) < 2:
        return {'error': 'Se necesitan al menos 2 semanas de datos'}
    
    # Calcular tendencia con regresión simple
    x = np.arange(len(weekly_totals)).reshape(-1, 1)
    y = weekly_totals['monto'].values
    
    model = LinearRegression()
    model.fit(x, y)
    slope = model.coef_[0]
    
    # Variación semana a semana
    week_changes = []
    for i in range(1, len(weekly_totals)):
        prev = weekly_totals.iloc[i-1]['monto']
        curr = weekly_totals.iloc[i]['monto']
        change_pct = ((curr - prev) / prev * 100) if prev > 0 else 0
        week_changes.append({
            'semana': i,
            'gasto': round(curr, 2),
            'cambio_pct': round(change_pct, 2)
        })
    
    # Promedio móvil (3 semanas)
    moving_avg = []
    for i in range(len(weekly_totals)):
        if i < 2:
            moving_avg.append(round(weekly_totals.iloc[i]['monto'], 2))
        else:
            avg = weekly_totals.iloc[i-2:i+1]['monto'].mean()
            moving_avg.append(round(avg, 2))
    
    # Clasificar tendencia
    if slope > 0:
        tendencia_general = 'AUMENTANDO'
        consejo = 'Los gastos tienden a crecer. Considera revisar presupuesto.'
    elif slope < -10:
        tendencia_general = 'DISMINUYENDO'
        consejo = 'Los gastos están bajando. ¡Buen control!'
    else:
        tendencia_general = 'ESTABLE'
        consejo = 'Los gastos se mantienen relativamente estables.'
    
    return {
        'tendencia_general': tendencia_general,
        'pendiente': round(slope, 2),
        'consejo': consejo,
        'cambios_semanales': week_changes,
        'promedio_movil_3sem': moving_avg,
        'gasto_promedio_semanal': round(y.mean(), 2)
    }


# ============================================================
# 🔟 DETECCIÓN DE OUTLIERS (IQR + Z-Score)
# ============================================================

def detect_outliers_iqr(df):
    """
    Identifica gastos atípicos usando IQR y Z-Score.
    
    Args:
        df: DataFrame con gastos
    
    Returns:
        Dict con outliers y clasificación
    """
    from scipy.stats import zscore
    
    outliers_list = []
    outlier_indices = set()
    
    # Método 1: IQR
    Q1 = df['monto'].quantile(0.25)
    Q3 = df['monto'].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    iqr_outliers = df[(df['monto'] < lower_bound) | (df['monto'] > upper_bound)]
    
    for idx, row in iqr_outliers.iterrows():
        outlier_indices.add(idx)
        outliers_list.append({
            'fecha': row['fecha'].strftime('%Y-%m-%d'),
            'monto': row['monto'],
            'categoria': row['categoria'],
            'metodo': 'IQR',
            'razon': f"Fuera del rango [{lower_bound:.2f}, {upper_bound:.2f}]"
        })
    
    # Método 2: Z-Score
    z_scores = np.abs(zscore(df['monto']))
    z_outliers = df[z_scores > 2.5]
    
    for idx, row in z_outliers.iterrows():
        if idx not in outlier_indices:
            outlier_indices.add(idx)
            outliers_list.append({
                'fecha': row['fecha'].strftime('%Y-%m-%d'),
                'monto': row['monto'],
                'categoria': row['categoria'],
                'metodo': 'Z-Score',
                'razon': f"Desviación de {z_scores[idx]:.2f}σ"
            })
    
    # Estadísticas normales para contexto
    stats = {
        'q1': round(Q1, 2),
        'q3': round(Q3, 2),
        'iqr': round(IQR, 2),
        'limite_inferior': round(lower_bound, 2),
        'limite_superior': round(upper_bound, 2),
        'media': round(df['monto'].mean(), 2),
        'desv_std': round(df['monto'].std(), 2)
    }
    
    return {
        'outliers_detectados': len(outlier_indices),
        'porcentaje': round((len(outlier_indices) / len(df)) * 100, 2),
        'outliers': outliers_list[:20],  # Top 20
        'estadisticas': stats,
        'interpretacion': 'Valores atípicos que podrían necesitar revisión'
    }


# ============================================================
# 1️⃣1️⃣ METAS DE AHORRO
# ============================================================

def calculate_savings_goals(df, goal_name, target_amount, months=12):
    """
    Calcula cuánto ahorrar mensualmente para alcanzar metas específicas.
    
    Args:
        df: DataFrame con gastos
        goal_name: Nombre de la meta (ej: "Vacaciones", "Coche")
        target_amount: Monto a ahorrar
        months: Meses para alcanzar meta
    
    Returns:
        Dict con desglose de meta y plan de ahorro
    """
    monthly_spend = df.groupby(df['fecha'].dt.to_period('M'))['monto'].sum()
    
    if len(monthly_spend) == 0:
        return {'error': 'Sin datos de gastos'}
    
    avg_monthly_spend = monthly_spend.mean()
    
    # Calcular ahorro mensual necesario
    monthly_savings_needed = target_amount / months
    
    # Sugerir reducción de gastos
    reduction_pct = (monthly_savings_needed / avg_monthly_spend) * 100
    
    # Identificar categorías donde se puede reducir
    category_spend = df.groupby('categoria')['monto'].agg(['sum', 'count', 'mean'])
    category_spend = category_spend.sort_values('sum', ascending=False)
    
    reductions = []
    for cat, row in category_spend.iterrows():
        potential_reduction = row['sum'] * 0.1  # 10% de reducción
        reductions.append({
            'categoria': cat,
            'gasto_actual': round(row['sum'], 2),
            'reduccion_10pct': round(potential_reduction, 2),
            'promedio_gasto': round(row['mean'], 2)
        })
    
    return {
        'meta': goal_name,
        'monto_objetivo': round(target_amount, 2),
        'plazo_meses': months,
        'ahorro_mensual_requerido': round(monthly_savings_needed, 2),
        'gasto_promedio_actual': round(avg_monthly_spend, 2),
        'reduccion_necesaria_pct': round(reduction_pct, 2),
        'sugerencias_reduccion': reductions[:5],
        'estimado_alcanzable': 'SÍ' if reduction_pct <= 30 else 'DIFÍCIL'
    }


# ============================================================
# 1️⃣2️⃣ TIPS PERSONALIZADOS
# ============================================================

def generate_personalized_tips(df):
    """
    Genera recomendaciones basadas en patrones de gasto individual.
    
    Args:
        df: DataFrame con gastos
    
    Returns:
        List de tips personalizados con prioridad
    """
    tips = []
    total_spend = df['monto'].sum()
    
    # Análisis por categoría
    category_spend = df.groupby('categoria')['monto'].sum().sort_values(ascending=False)
    
    # Tip 1: Categoría dominante
    if len(category_spend) > 0:
        top_cat = category_spend.index[0]
        top_pct = (category_spend.iloc[0] / total_spend) * 100
        
        if top_pct > 40:
            tips.append({
                'prioridad': 'ALTA',
                'titulo': f'Reducir gastos en {top_cat}',
                'descripcion': f'Esta categoría representa el {top_pct:.1f}% de tus gastos',
                'accion': f'Intenta reducir un 15% en {top_cat}',
                'impacto_potencial': round(category_spend.iloc[0] * 0.15, 2)
            })
    
    # Tip 2: Frecuencia de gastos pequeños
    small_expenses = df[df['monto'] < df['monto'].quantile(0.25)]
    if len(small_expenses) > 0:
        small_total = small_expenses['monto'].sum()
        small_pct = (small_total / total_spend) * 100
        
        if small_pct > 15:
            tips.append({
                'prioridad': 'MEDIA',
                'titulo': 'Gastos pequeños acumulados',
                'descripcion': f'Los gastos pequeños suman ${small_total:.2f} ({small_pct:.1f}%)',
                'accion': 'Implementa un sistema de presupuesto para gastos menores',
                'impacto_potencial': round(small_total * 0.20, 2)
            })
    
    # Tip 3: Patrones de fin de semana
    df['dia_semana'] = df['fecha'].dt.weekday
    weekend_spend = df[df['dia_semana'].isin([5, 6])]['monto'].sum()
    weekday_spend = df[~df['dia_semana'].isin([5, 6])]['monto'].sum()
    
    if weekday_spend > 0:
        weekend_pct = (weekend_spend / (weekend_spend + weekday_spend)) * 100
        if weekend_pct > 40:
            tips.append({
                'prioridad': 'MEDIA',
                'titulo': 'Gasto elevado en fin de semana',
                'descripcion': f'Gastas {weekend_pct:.1f}% de tu dinero el fin de semana',
                'accion': 'Planifica actividades económicas o presupuesta mejor para fines de semana',
                'impacto_potencial': round(weekend_spend * 0.15, 2)
            })
    
    # Tip 4: Tendencia alcista
    monthly = df.groupby(df['fecha'].dt.to_period('M'))['monto'].sum()
    if len(monthly) >= 3:
        recent_avg = monthly.tail(2).mean()
        earlier_avg = monthly.head(2).mean()
        if recent_avg > earlier_avg * 1.2:
            tips.append({
                'prioridad': 'ALTA',
                'titulo': 'Tendencia alcista detectada',
                'descripcion': 'Tus gastos están aumentando mes a mes',
                'accion': 'Revisa presupuestos y nuevos gastos recurrentes',
                'impacto_potencial': round((recent_avg - earlier_avg), 2)
            })
    
    # Tip 5: Diversificación
    if len(category_spend) < 3:
        tips.append({
            'prioridad': 'BAJA',
            'titulo': 'Pocos tipos de gasto registrados',
            'descripcion': f'Solo tienes {len(category_spend)} categorías de gasto',
            'accion': 'Considera categorizar mejor tus gastos para mejor control',
            'impacto_potencial': 0
        })
    
    return sorted(tips, key=lambda x: {'ALTA': 0, 'MEDIA': 1, 'BAJA': 2}[x['prioridad']])


# ============================================================
# 1️⃣3️⃣ ALERTAS DE PRESUPUESTO
# ============================================================

def generate_budget_alerts(df, monthly_budget):
    """
    Genera alertas cuando se aproxima o excede el presupuesto mensual.
    
    Args:
        df: DataFrame con gastos
        monthly_budget: Presupuesto mensual disponible
    
    Returns:
        Dict con alertas y estado de presupuesto
    """
    current_date = df['fecha'].max()
    current_month_start = pd.Timestamp(current_date.year, current_date.month, 1)
    current_month_data = df[df['fecha'] >= current_month_start]
    
    current_spend = current_month_data['monto'].sum()
    days_passed = (current_date - current_month_start).days + 1
    days_in_month = 31  # Aproximado
    
    remaining_days = max(1, days_in_month - days_passed)
    remaining_budget = monthly_budget - current_spend
    
    # Proyección
    daily_avg = current_spend / days_passed if days_passed > 0 else 0
    projected_end_month = current_spend + (daily_avg * remaining_days)
    
    # Determinar estado
    budget_pct = (current_spend / monthly_budget * 100) if monthly_budget > 0 else 0
    
    alerts = []
    
    if budget_pct >= 100:
        alerts.append({
            'tipo': '🚨 CRÍTICO',
            'titulo': 'Presupuesto excedido',
            'descripcion': f'Has gastado ${current_spend:.2f} de tu presupuesto de ${monthly_budget:.2f}',
            'accion': 'Reduce gastos inmediatamente',
            'severidad': 1
        })
    elif budget_pct >= 85:
        alerts.append({
            'tipo': '⚠️ ADVERTENCIA',
            'titulo': 'Presupuesto casi agotado',
            'descripcion': f'Has utilizado el {budget_pct:.1f}% de tu presupuesto mensual',
            'accion': 'Sé cuidadoso con los gastos restantes',
            'severidad': 2
        })
    elif budget_pct >= 70:
        alerts.append({
            'tipo': '📌 ATENCIÓN',
            'titulo': 'Presupuesto moderado',
            'descripcion': f'Has gastado el {budget_pct:.1f}% de tu presupuesto',
            'accion': 'Mantén control sobre gastos futuros',
            'severidad': 3
        })
    else:
        alerts.append({
            'tipo': '✅ BUENO',
            'titulo': 'Dentro de presupuesto',
            'descripcion': f'Has gastado el {budget_pct:.1f}% de tu presupuesto mensual',
            'accion': 'Continúa manteniendo este ritmo',
            'severidad': 4
        })
    
    # Alerta de proyección
    projection_ratio = projected_end_month / monthly_budget if monthly_budget > 0 else 0
    
    if projection_ratio > 1.1:
        alerts.append({
            'tipo': '⚡ PROYECCIÓN',
            'titulo': f'Proyección excede presupuesto en {(projection_ratio - 1) * 100:.1f}%',
            'descripcion': f'Si continúas al ritmo actual, terminarás con ${projected_end_month:.2f}',
            'accion': f'Necesitas reducir gasto diario a ${remaining_budget / remaining_days:.2f}',
            'severidad': 2
        })
    
    return {
        'presupuesto_mensual': round(monthly_budget, 2),
        'gasto_actual': round(current_spend, 2),
        'porcentaje_utilizado': round(budget_pct, 2),
        'presupuesto_restante': round(remaining_budget, 2),
        'dias_transcurridos': days_passed,
        'dias_restantes': remaining_days,
        'gasto_diario_promedio': round(daily_avg, 2),
        'proyeccion_mes': round(projected_end_month, 2),
        'alertas': alerts
    }


# ============================================================
# 1️⃣4️⃣ GAMIFICACIÓN - PUNTUACIÓN FINANCIERA
# ============================================================

def calculate_financial_health_score(df, monthly_budget):
    """
    Calcula puntuación de "salud financiera" basada en múltiples factores.
    
    Args:
        df: DataFrame con gastos
        monthly_budget: Presupuesto mensual
    
    Returns:
        Dict con puntuación y desglose de factores
    """
    score = 100  # Comenzar con puntuación máxima
    factors = []
    
    # Factor 1: Control de presupuesto (-30 puntos máximo)
    current_spend = df.groupby(df['fecha'].dt.to_period('M')).tail(1)['monto'].sum()
    if current_spend > 0:
        budget_ratio = current_spend / monthly_budget if monthly_budget > 0 else 0
        if budget_ratio > 1.0:
            deduction = min(30, (budget_ratio - 1) * 30)
            score -= deduction
            factors.append({
                'factor': 'Control de presupuesto',
                'deduccion': round(deduction, 2),
                'estado': 'Excedido' if budget_ratio > 1.0 else 'Controlado'
            })
        else:
            factors.append({
                'factor': 'Control de presupuesto',
                'deduccion': 0,
                'estado': 'Excelente'
            })
    
    # Factor 2: Consistencia de gastos (-15 puntos máximo)
    monthly = df.groupby(df['fecha'].dt.to_period('M'))['monto'].sum()
    if len(monthly) > 1:
        cv = monthly.std() / monthly.mean() if monthly.mean() > 0 else 0
        if cv > 0.5:  # Coeficiente de variación
            score -= min(15, cv * 10)
            factors.append({
                'factor': 'Consistencia',
                'deduccion': min(15, cv * 10),
                'estado': 'Inconsistente'
            })
        else:
            factors.append({
                'factor': 'Consistencia',
                'deduccion': 0,
                'estado': 'Estable'
            })
    
    # Factor 3: Diversificación de gastos (+10 puntos máximo)
    categories = df['categoria'].nunique()
    if categories >= 5:
        score += 10
        bonus = 10
    elif categories >= 3:
        score += 5
        bonus = 5
    else:
        bonus = 0
    
    factors.append({
        'factor': 'Diversificación',
        'bonus': bonus,
        'estado': f'{categories} categorías'
    })
    
    # Factor 4: Ausencia de anomalías (-15 puntos)
    from scipy.stats import zscore
    z_scores = np.abs(zscore(df['monto']))
    anomalies = (z_scores > 2.5).sum()
    
    if anomalies > 0:
        deduction = min(15, anomalies * 2)
        score -= deduction
        factors.append({
            'factor': 'Anomalías detectadas',
            'deduccion': deduction,
            'estado': f'{anomalies} anomalías'
        })
    else:
        factors.append({
            'factor': 'Anomalías',
            'deduccion': 0,
            'estado': 'Ninguna'
        })
    
    # Factor 5: Tendencia (-15 puntos)
    if len(monthly) >= 3:
        recent = monthly.tail(2).mean()
        earlier = monthly.head(2).mean()
        if recent > earlier * 1.2:
            score -= 15
            factors.append({
                'factor': 'Tendencia',
                'deduccion': 15,
                'estado': 'Gastos aumentando'
            })
        elif recent < earlier * 0.8:
            factors.append({
                'factor': 'Tendencia',
                'deduccion': 0,
                'bonus': 5,
                'estado': 'Gastos disminuyendo'
            })
            score += 5
        else:
            factors.append({
                'factor': 'Tendencia',
                'deduccion': 0,
                'estado': 'Estable'
            })
    
    # Asegurar que la puntuación esté entre 0 y 100
    score = max(0, min(100, score))
    
    # Clasificación
    if score >= 80:
        rating = '⭐⭐⭐ EXCELENTE'
    elif score >= 60:
        rating = '⭐⭐ BUENO'
    elif score >= 40:
        rating = '⭐ ACEPTABLE'
    else:
        rating = '❌ NECESITA MEJORA'
    
    return {
        'puntuacion': round(score, 1),
        'clasificacion': rating,
        'factores': factors,
        'consejos': [f['estado'] for f in factors if 'deduccion' in f and f['deduccion'] > 0]
    }


# ============================================================
# 1️⃣5️⃣ REPORTES AUTOMÁTICOS (RESUMEN SEMANAL)
# ============================================================

def generate_weekly_report(df):
    """
    Genera resumen semanal de gastos para reportes automáticos.
    
    Args:
        df: DataFrame con gastos
    
    Returns:
        Dict con resumen semanal estructurado
    """
    # Obtener última semana completa
    df['fecha'] = pd.to_datetime(df['fecha'])
    end_date = df['fecha'].max()
    start_date = end_date - timedelta(days=7)
    
    week_data = df[(df['fecha'] >= start_date) & (df['fecha'] <= end_date)]
    
    if len(week_data) == 0:
        return {'error': 'Sin datos de la última semana'}
    
    # Estadísticas semanales
    total_spend = week_data['monto'].sum()
    num_transactions = len(week_data)
    avg_transaction = total_spend / num_transactions if num_transactions > 0 else 0
    
    # Por categoría
    category_breakdown = week_data.groupby('categoria').agg({
        'monto': ['sum', 'count', 'mean']
    }).round(2)
    
    category_list = []
    for cat, row in category_breakdown.iterrows():
        category_list.append({
            'categoria': cat,
            'total': row[('monto', 'sum')],
            'transacciones': int(row[('monto', 'count')]),
            'promedio': row[('monto', 'mean')]
        })
    
    category_list = sorted(category_list, key=lambda x: x['total'], reverse=True)
    
    # Día más costoso
    daily_spend = week_data.groupby(week_data['fecha'].dt.date)['monto'].sum()
    if len(daily_spend) > 0:
        costliest_day = daily_spend.idxmax()
        costliest_amount = daily_spend.max()
    else:
        costliest_day = None
        costliest_amount = 0
    
    # Principales gastos
    top_expenses = week_data.nlargest(5, 'monto')[['fecha', 'categoria', 'monto']].to_dict('records')
    
    # Resumen HTML para email
    html_summary = f"""
    <h2>📊 Resumen Semanal de Gastos</h2>
    <p>Período: {start_date.date()} a {end_date.date()}</p>
    
    <h3>💰 Totales</h3>
    <ul>
        <li>Gasto total: ${total_spend:.2f}</li>
        <li>Número de transacciones: {num_transactions}</li>
        <li>Promedio por transacción: ${avg_transaction:.2f}</li>
        <li>Día más costoso: {costliest_day} (${costliest_amount:.2f})</li>
    </ul>
    
    <h3>🏷️ Desglose por Categoría</h3>
    <ul>
    """
    
    for cat_info in category_list[:5]:
        html_summary += f"<li>{cat_info['categoria']}: ${cat_info['total']:.2f} ({cat_info['transacciones']} transacciones)</li>"
    
    html_summary += """
    </ul>
    
    <h3>🔝 Top 5 Gastos</h3>
    <ul>
    """
    
    for expense in top_expenses:
        html_summary += f"<li>{expense['fecha']}: ${expense['monto']:.2f} ({expense['categoria']})</li>"
    
    html_summary += "</ul>"
    
    return {
        'periodo': f'{start_date.date()} a {end_date.date()}',
        'fecha_reporte': datetime.now().isoformat(),
        'total_gasto': round(total_spend, 2),
        'num_transacciones': num_transactions,
        'promedio_transaccion': round(avg_transaction, 2),
        'dia_mas_costoso': str(costliest_day) if costliest_day else None,
        'monto_dia_costoso': round(costliest_amount, 2),
        'por_categoria': category_list,
        'top_5_gastos': [
            {
                'fecha': str(e['fecha']),
                'categoria': e['categoria'],
                'monto': e['monto']
            } for e in top_expenses
        ],
        'resumen_email_html': html_summary
    }


# ============================================================
# 1️⃣6️⃣ CALENDARIO DE CALOR (HEATMAP)
# ============================================================

def generate_heatmap(df):
    """
    Crea un calendario de calor mostrando gastos por día.
    
    Args:
        df: DataFrame con gastos
    
    Returns:
        Dict con datos del heatmap y configuración
    """
    if not PLOTLY_AVAILABLE:
        return {'error': 'Plotly no disponible. Instala: pip install plotly'}
    
    # Preparar datos
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['dia'] = df['fecha'].dt.date
    daily_spend = df.groupby('dia')['monto'].sum().reset_index()
    daily_spend['fecha'] = pd.to_datetime(daily_spend['dia'])
    daily_spend['semana'] = daily_spend['fecha'].dt.isocalendar().week
    daily_spend['dia_semana'] = daily_spend['fecha'].dt.weekday
    
    # Crear matriz para heatmap
    pivot_data = daily_spend.pivot_table(
        values='monto',
        index='dia_semana',
        columns='semana',
        aggfunc='sum'
    )
    
    dias_es = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    pivot_data.index = [dias_es[i] if i < len(dias_es) else f'Día {i}' for i in pivot_data.index]
    
    # Crear figura con plotly
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='RdYlGn_r',
        colorbar=dict(title='Gasto ($)')
    ))
    
    fig.update_layout(
        title='📅 Calendario de Calor - Gastos por Día',
        xaxis_title='Semana',
        yaxis_title='Día de la Semana',
        height=400
    )
    
    return {
        'tipo': 'heatmap',
        'titulo': '📅 Calendario de Calor',
        'grafico_json': fig.to_json(),
        'datos_resumen': {
            'dia_max_gasto': daily_spend.loc[daily_spend['monto'].idxmax()]['dia'].isoformat(),
            'monto_max': round(daily_spend['monto'].max(), 2),
            'dia_min_gasto': daily_spend.loc[daily_spend['monto'].idxmin()]['dia'].isoformat(),
            'monto_min': round(daily_spend['monto'].min(), 2),
            'promedio_diario': round(daily_spend['monto'].mean(), 2)
        }
    }


# ============================================================
# 1️⃣7️⃣ GRÁFICO SANKEY (FLUJO DE DINERO)
# ============================================================

def generate_sankey_diagram(df):
    """
    Crea un diagrama Sankey mostrando flujo de dinero por categoría.
    
    Args:
        df: DataFrame con gastos
    
    Returns:
        Dict con diagrama Sankey
    """
    if not PLOTLY_AVAILABLE:
        return {'error': 'Plotly no disponible. Instala: pip install plotly'}
    
    # Agrupar por categoría
    cat_spend = df.groupby('categoria')['monto'].sum().reset_index()
    cat_spend = cat_spend.sort_values('monto', ascending=False)
    
    # Crear nodos: "Ingresos" -> Categorías -> "Total Gastado"
    nodes = ['TOTAL'] + cat_spend['categoria'].tolist() + ['GASTOS']
    
    # Crear enlaces
    source = [0] * len(cat_spend)  # Todos vienen del nodo 0 (TOTAL)
    target = list(range(1, len(cat_spend) + 1))  # Hacia las categorías
    value = cat_spend['monto'].tolist()
    
    # Agregar enlace final a GASTOS
    source.append(0)
    target.append(len(nodes) - 1)
    value.append(cat_spend['monto'].sum())
    
    # Colores
    colors = ['rgba(255, 0, 0, 0.4)'] + ['rgba(0, 100, 200, 0.4)'] * len(cat_spend) + ['rgba(0, 200, 0, 0.4)']
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='black', width=0.5),
            label=nodes,
            color=['red'] + ['blue'] * len(cat_spend) + ['green']
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=['rgba(0, 100, 200, 0.2)'] * len(source)
        )
    )])
    
    fig.update_layout(
        title='🌊 Flujo de Dinero - Diagrama Sankey',
        font=dict(size=12),
        height=500
    )
    
    return {
        'tipo': 'sankey',
        'titulo': '🌊 Diagrama Sankey',
        'grafico_json': fig.to_json(),
        'categorias': cat_spend.to_dict('records')
    }


# ============================================================
# 1️⃣8️⃣ DASHBOARD INTERACTIVO
# ============================================================

def generate_interactive_dashboard(df):
    """
    Crea un dashboard interactivo con múltiples gráficos.
    
    Args:
        df: DataFrame con gastos
    
    Returns:
        Dict con múltiples gráficos en subplots
    """
    if not PLOTLY_AVAILABLE:
        return {'error': 'Plotly no disponible. Instala: pip install plotly'}
    
    # Preparar datos
    cat_spend = df.groupby('categoria')['monto'].sum().sort_values(ascending=False).head(10)
    monthly = df.groupby(df['fecha'].dt.to_period('M'))['monto'].sum()
    daily = df.groupby(df['fecha'].dt.date)['monto'].sum().tail(30)
    
    # Crear subplots
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('📊 Gasto por Categoría', '📅 Gastos Mensuales',
                       '📈 Últimos 30 Días', '💰 Distribución'),
        specs=[[{'type': 'bar'}, {'type': 'scatter'}],
               [{'type': 'bar'}, {'type': 'pie'}]]
    )
    
    # Gráfico 1: Categorías
    fig.add_trace(
        go.Bar(x=cat_spend.index, y=cat_spend.values, name='Por Categoría'),
        row=1, col=1
    )
    
    # Gráfico 2: Mensual
    fig.add_trace(
        go.Scatter(x=monthly.index.astype(str), y=monthly.values, 
                   mode='lines+markers', name='Mensual'),
        row=1, col=2
    )
    
    # Gráfico 3: Últimos 30 días
    fig.add_trace(
        go.Bar(x=daily.index.astype(str), y=daily.values, name='Diario'),
        row=2, col=1
    )
    
    # Gráfico 4: Pie
    fig.add_trace(
        go.Pie(labels=cat_spend.index, values=cat_spend.values, name='Distribución'),
        row=2, col=2
    )
    
    fig.update_layout(
        title_text='📊 Dashboard Interactivo de Gastos',
        showlegend=False,
        height=800,
        hovermode='x unified'
    )
    
    return {
        'tipo': 'dashboard',
        'titulo': '📊 Dashboard Interactivo',
        'grafico_json': fig.to_json(),
        'resumen': {
            'total_gasto': round(df['monto'].sum(), 2),
            'transacciones': len(df),
            'promedio': round(df['monto'].mean(), 2),
            'max_gasto': round(df['monto'].max(), 2),
            'min_gasto': round(df['monto'].min(), 2)
        }
    }


# ============================================================
# 1️⃣9️⃣ COMPARATIVAS (MES VS MES)
# ============================================================

def generate_month_comparison_chart(df):
    """
    Crea gráficos comparativos entre meses.
    
    Args:
        df: DataFrame con gastos
    
    Returns:
        Dict con gráficos de comparación
    """
    if not PLOTLY_AVAILABLE:
        return {'error': 'Plotly no disponible. Instala: pip install plotly'}
    
    # Agrupar por mes y categoría
    df['año_mes'] = df['fecha'].dt.to_period('M')
    
    monthly_cat = df.groupby(['año_mes', 'categoria'])['monto'].sum().reset_index()
    monthly_cat = monthly_cat.sort_values('año_mes', ascending=False).head(50)
    
    # Obtener últimos 2 meses completos
    unique_months = monthly_cat['año_mes'].unique()
    if len(unique_months) < 2:
        return {'error': 'Se necesitan al menos 2 meses de datos'}
    
    current_month = unique_months[0]
    previous_month = unique_months[1]
    
    current_data = monthly_cat[monthly_cat['año_mes'] == current_month]
    previous_data = monthly_cat[monthly_cat['año_mes'] == previous_month]
    
    # Crear gráfico comparativo
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=previous_data['categoria'],
        y=previous_data['monto'],
        name=str(previous_month),
        opacity=0.7
    ))
    
    fig.add_trace(go.Bar(
        x=current_data['categoria'],
        y=current_data['monto'],
        name=str(current_month),
        opacity=0.7
    ))
    
    fig.update_layout(
        title=f'🔄 Comparación: {current_month} vs {previous_month}',
        xaxis_title='Categoría',
        yaxis_title='Monto ($)',
        barmode='group',
        height=500,
        hovermode='x unified'
    )
    
    # Calcular variaciones
    cambios = {}
    for cat in set(list(current_data['categoria']) + list(previous_data['categoria'])):
        curr = current_data[current_data['categoria'] == cat]['monto'].sum() if cat in current_data['categoria'].values else 0
        prev = previous_data[previous_data['categoria'] == cat]['monto'].sum() if cat in previous_data['categoria'].values else 0
        cambio = curr - prev
        cambio_pct = (cambio / prev * 100) if prev > 0 else 0
        
        cambios[cat] = {
            'mes_actual': round(curr, 2),
            'mes_anterior': round(prev, 2),
            'cambio': round(cambio, 2),
            'cambio_pct': round(cambio_pct, 2)
        }
    
    return {
        'tipo': 'comparacion',
        'titulo': '🔄 Comparativa Mes vs Mes',
        'meses_comparados': f'{previous_month} vs {current_month}',
        'grafico_json': fig.to_json(),
        'cambios_por_categoria': cambios
    }


# ============================================================
# 2️⃣0️⃣ EXPORTAR GRÁFICOS COMO IMAGEN
# ============================================================

def export_graphics_as_image(df, output_format='json'):
    """
    Exporta gráficos principales en formato JSON o BASE64.
    
    Args:
        df: DataFrame con gastos
        output_format: 'json' (gráficos interactivos) o 'base64' (imágenes)
    
    Returns:
        Dict con datos de exportación
    """
    if not PLOTLY_AVAILABLE:
        return {'error': 'Plotly no disponible. Instala: pip install plotly'}
    
    graphics = {
        'timestamp': datetime.now().isoformat(),
        'formato': output_format,
        'graficos': []
    }
    
    # Gráfico 1: Pie de categorías
    cat_spend = df.groupby('categoria')['monto'].sum()
    fig1 = go.Figure(data=[go.Pie(labels=cat_spend.index, values=cat_spend.values)])
    fig1.update_layout(title='Distribución de Gastos por Categoría')
    
    # Gráfico 2: Series temporal
    daily = df.groupby(df['fecha'].dt.date)['monto'].sum()
    fig2 = go.Figure(data=[go.Scatter(x=daily.index.astype(str), y=daily.values, 
                                       mode='lines', fill='tozeroy')])
    fig2.update_layout(title='Gastos Diarios', xaxis_title='Fecha', yaxis_title='Monto ($)')
    
    # Gráfico 3: Barras por categoría
    fig3 = go.Figure(data=[go.Bar(x=cat_spend.index, y=cat_spend.values)])
    fig3.update_layout(title='Gastos por Categoría')
    
    # Gráfico 4: Box plot
    df_categories = []
    for cat in df['categoria'].unique():
        montos = df[df['categoria'] == cat]['monto'].tolist()
        df_categories.append({'categoria': cat, 'montos': montos})
    
    fig4_data = []
    for item in df_categories:
        fig4_data.append(go.Box(y=item['montos'], name=item['categoria']))
    
    fig4 = go.Figure(data=fig4_data)
    fig4.update_layout(title='Distribución de Montos por Categoría')
    
    if output_format == 'json':
        graphics['graficos'] = [
            {'nombre': 'Pie Categorías', 'json': fig1.to_json()},
            {'nombre': 'Series Temporal', 'json': fig2.to_json()},
            {'nombre': 'Barras Categorías', 'json': fig3.to_json()},
            {'nombre': 'Box Plot', 'json': fig4.to_json()}
        ]
    
    elif output_format == 'base64' and KALEIDO_AVAILABLE:
        try:
            graphics['graficos'] = [
                {'nombre': 'Pie Categorías', 'base64': base64.b64encode(fig1.to_image(format='png')).decode('ascii')},
                {'nombre': 'Series Temporal', 'base64': base64.b64encode(fig2.to_image(format='png')).decode('ascii')},
                {'nombre': 'Barras Categorías', 'base64': base64.b64encode(fig3.to_image(format='png')).decode('ascii')},
                {'nombre': 'Box Plot', 'base64': base64.b64encode(fig4.to_image(format='png')).decode('ascii')}
            ]
        except:
            graphics['graficos'] = [
                {'nombre': 'Pie Categorías', 'json': fig1.to_json()},
                {'nombre': 'Series Temporal', 'json': fig2.to_json()},
                {'nombre': 'Barras Categorías', 'json': fig3.to_json()},
                {'nombre': 'Box Plot', 'json': fig4.to_json()}
            ]
            graphics['nota'] = 'Kaleido no disponible. Usando formato JSON. Instala: pip install kaleido'
    
    else:
        graphics['graficos'] = [
            {'nombre': 'Pie Categorías', 'json': fig1.to_json()},
            {'nombre': 'Series Temporal', 'json': fig2.to_json()},
            {'nombre': 'Barras Categorías', 'json': fig3.to_json()},
            {'nombre': 'Box Plot', 'json': fig4.to_json()}
        ]
    
    return graphics


# ============================================================
# 🚀 INICIALIZAR FLASK Y ENDPOINTS
# ============================================================

# ============================================================
# 🔐 ENDPOINT DE AUTENTICACIÓN (DEBE SER EL PRIMERO)
# ============================================================

@app.route('/api/v2/auth/token', methods=['POST'])
def get_token():
    """
    Genera un nuevo token JWT para acceder a los demás endpoints.
    
    CÓMO USAR EN POSTMAN:
    1. URL: POST http://localhost:5000/api/v2/auth/token
    2. Body (JSON): {"user_id": "tu_usuario"}
    3. Copia el token generado
    
    EJEMPLO RESPUESTA:
    {
        "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "expires_in": 86400,
        "message": "Token generado exitosamente"
    }
    
    LUEGO USA EL TOKEN EN OTROS ENDPOINTS:
    Headers → Authorization: Bearer <token>
    O
    Headers → X-API-Key: <token>
    """
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 'default_user')
        
        token = generate_token(user_id)
        if not token:
            return jsonify({'error': 'No se pudo generar el token'}), 500
        
        return jsonify({
            'status': 'success',
            'token': token,
            'expires_in': TOKEN_EXPIRATION_HOURS * 3600,
            'message': f'Token generado para {user_id}. Válido por {TOKEN_EXPIRATION_HOURS} horas',
            'instrucciones': 'Usar en headers: Authorization: Bearer <token> o X-API-Key: <token>'
        }), 200
    except Exception as e:
        return jsonify({'error': f'Error generando token: {str(e)}'}), 500

@app.route('/api/v2/auth/validate', methods=['POST'])
def validate_token_endpoint():
    """Valida si un token es aún válido"""
    try:
        token = request.headers.get('X-API-Key') or request.headers.get('Authorization', '').split()[-1]
        if not token:
            return jsonify({'valid': False, 'message': 'Token no proporcionado'}), 400
        
        is_valid = bool(verify_token(token))
        return jsonify({
            'valid': is_valid,
            'message': 'Token válido' if is_valid else 'Token inválido o expirado'
        }), 200
    except Exception as e:
        return jsonify({'error': f'Error validando token: {str(e)}'}), 500

# ============================================================
# 📊 ENDPOINTS DE LA API
# ============================================================

@app.route('/api/v2/health', methods=['GET'])
def health():
    """Verificar estado de la API."""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'firebase': FIREBASE_AVAILABLE,
        'modelos_disponibles': {
            'arima': ARIMA_AVAILABLE,
            'prophet': PROPHET_AVAILABLE,
            'lstm': LSTM_AVAILABLE
        }
    }), 200


# ============================================================
# 🔥 ENDPOINTS DE FIREBASE - CONSUMIR DATOS DEL APP FLUTTER
# ============================================================

@app.route('/api/v2/firebase/debug', methods=['GET'])
def firebase_debug():
    """Diagnóstico de conexión Firestore: proyecto, colecciones y prueba de lectura"""
    try:
        info = {
            'firebase_available': bool(FIREBASE_AVAILABLE),
            'database_id': FIRESTORE_DATABASE_ID,
        }
        if not FIREBASE_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Firebase no disponible', 'data': info}), 503
        
        # Proyecto
        import firebase_admin as _fb
        app_opts = _fb.get_app().options if _fb.get_app() else {}
        info['projectId'] = app_opts.get('projectId')
        info['env_projectId'] = os.getenv('FIREBASE_PROJECT_ID')
        
        # Colecciones top-level
        try:
            top_cols = [c.id for c in db.collections()]
        except Exception as e:
            top_cols = [f'error_listando: {str(e)}']
        info['collections'] = top_cols
        
        # Prueba de lectura en users
        try:
            users_docs = list(db.collection('users').limit(5).stream())
            info['users_count'] = len(users_docs)
            info['users_ids'] = [d.id for d in users_docs]
        except Exception as e:
            info['users_error'] = str(e)
        
        # Prueba de lectura de gastos del primer usuario
        if info.get('users_ids'):
            try:
                first_user = info['users_ids'][0]
                gastos_docs = list(db.collection('users').document(first_user).collection('gastos').limit(3).stream())
                info['gastos_sample'] = {
                    'user_id': first_user,
                    'count': len(gastos_docs),
                    'ids': [d.id for d in gastos_docs]
                }
            except Exception as e:
                info['gastos_error'] = str(e)
        
        return jsonify({'status': 'success', 'data': info}), 200
    except Exception as e:
        return jsonify({'error': f'Debug Firestore: {str(e)}'}), 500


@app.route('/api/v2/firebase/usuarios', methods=['GET'])
def get_usuarios_firebase():
    """Obtiene todos los usuarios registrados en Firebase (colección users)"""
    if not FIREBASE_AVAILABLE:
        return jsonify({'error': 'Firebase no disponible'}), 503
    
    try:
        usuarios = []
        # Leer directamente de la colección 'users'
        docs = db.collection('users').stream()
        
        for doc in docs:
            usuario = doc.to_dict()
            usuario['id'] = doc.id
            usuarios.append(usuario)
        
        return jsonify({
            'status': 'success',
            'total': len(usuarios),
            'data': usuarios
        }), 200
    except Exception as e:
        return jsonify({'error': f'Error obteniendo usuarios: {str(e)}'}), 500


@app.route('/api/v2/firebase/usuarios/<usuario_id>', methods=['GET'])
def get_usuario_firebase(usuario_id):
    """Obtiene un usuario específico por ID con su budget"""
    if not FIREBASE_AVAILABLE:
        return jsonify({'error': 'Firebase no disponible'}), 503
    
    try:
        # Obtener documento del usuario en users/{usuario_id}
        user_doc = db.collection('users').document(usuario_id).get()
        
        if not user_doc.exists:
            return jsonify({
                'status': 'error',
                'message': f'Usuario {usuario_id} no encontrado'
            }), 404
        
        usuario = user_doc.to_dict()
        usuario['id'] = user_doc.id
        
        # Intentar obtener budget si existe
        try:
            budget_doc = db.collection('users').document(usuario_id).collection('budget').document('current').get()
            if budget_doc.exists:
                usuario['budget'] = budget_doc.to_dict()
        except Exception:
            pass
        
        return jsonify({
            'status': 'success',
            'data': usuario
        }), 200
    except Exception as e:
        return jsonify({'error': f'Error obteniendo usuario: {str(e)}'}), 500


@app.route('/api/v2/firebase/users/<usuario_id>/gastos', methods=['GET'])
def get_gastos_firebase(usuario_id):
    """Obtiene todos los gastos de un usuario desde Firebase (path: users/{userId}/gastos)"""
    if not FIREBASE_AVAILABLE:
        return jsonify({'error': 'Firebase no disponible'}), 503
    
    try:
        gastos = []
        path_used = f'users/{usuario_id}/gastos'
        error_detail = None
        
        # Path único según tu estructura Firebase: users/{uid}/gastos
        try:
            docs = db.collection('users').document(usuario_id).collection('gastos').stream()
            for doc in docs:
                gasto = doc.to_dict()
                gasto['id'] = doc.id
                gastos.append(gasto)
        except Exception as e:
            error_detail = str(e)
        
        # Si no hay gastos, verificar si el usuario existe
        if not gastos:
            try:
                user_doc = db.collection('users').document(usuario_id).get()
                user_exists = user_doc.exists
            except Exception:
                user_exists = False
            
            return jsonify({
                'status': 'success',
                'usuario_id': usuario_id,
                'total_gastos': 0,
                'path_usado': path_used,
                'user_exists': user_exists,
                'error_detail': error_detail,
                'data': [],
                'message': 'No se encontraron gastos' if user_exists else 'Usuario no existe en Firebase'
            }), 200
        
        return jsonify({
            'status': 'success',
            'usuario_id': usuario_id,
            'total_gastos': len(gastos),
            'path_usado': path_used,
            'data': gastos if request.args.get('ids_only') != 'true' else [g['id'] for g in gastos]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Error obteniendo gastos: {str(e)}'}), 500


@app.route('/api/v2/firebase/users/<usuario_id>/gastos-procesados', methods=['GET'])
@token_required
def get_gastos_procesados_firebase(usuario_id):
    """Obtiene gastos de Firebase y aplica análisis de IA"""
    if not FIREBASE_AVAILABLE:
        return jsonify({'error': 'Firebase no disponible'}), 503
    
    try:
        gastos = []
        path_used = f'users/{usuario_id}/gastos'
        
        # Path único: users/{uid}/gastos
        try:
            docs = db.collection('users').document(usuario_id).collection('gastos').stream()
            for doc in docs:
                gasto = doc.to_dict()
                gasto['id'] = doc.id
                gastos.append(gasto)
        except Exception as e:
            return jsonify({'error': f'Error leyendo gastos: {str(e)}'}), 500
        
        if not gastos:
            return jsonify({
                'status': 'success',
                'mensaje': 'Sin gastos registrados',
                'path_usado': path_used,
                'data': []
            }), 200
        
        # Procesar gastos con pandas
        df = pd.DataFrame(gastos)
        
        # Elegir columna métrica disponible: 'cantidad' (preferida) o 'monto' (fallback)
        metric_col = 'cantidad' if 'cantidad' in df.columns else ('monto' if 'monto' in df.columns else None)
        if not metric_col:
            return jsonify({
                'status': 'success',
                'usuario_id': usuario_id,
                'mensaje': 'No hay columna de monto/cantidad en los gastos',
                'path_usado': path_used,
                'data': gastos
            }), 200
        
        # Resumen por categoría usando la métrica disponible
        resumen = df.groupby('categoria')[metric_col].agg(['sum', 'count', 'mean']).round(2).to_dict()
        
        return jsonify({
            'status': 'success',
            'usuario_id': usuario_id,
            'total_gastos': len(gastos),
            'path_usado': path_used,
            'gasto_total': float(df['cantidad'].sum()) if 'cantidad' in df.columns else float(df['monto'].sum()),
            'promedio_gasto': float(df['cantidad'].mean()) if 'cantidad' in df.columns else float(df['monto'].mean()),
            'resumen_por_categoria': resumen,
            'data': gastos
        }), 200

    except Exception as e:
        return jsonify({'error': f'Error procesando gastos: {str(e)}'}), 500


@app.route('/api/v2/firebase/users/<usuario_id>/gastos-ids', methods=['GET'])
def get_gastos_ids(usuario_id):
    """Devuelve solo la lista de IDs de los documentos de gastos"""
    if not FIREBASE_AVAILABLE:
        return jsonify({'error': 'Firebase no disponible'}), 503
    try:
        ids = []
        path_used = f'users/{usuario_id}/gastos'
        
        # Path único: users/{uid}/gastos
        try:
            docs = db.collection('users').document(usuario_id).collection('gastos').stream()
            ids = [doc.id for doc in docs]
        except Exception as e:
            return jsonify({'error': f'Error leyendo IDs: {str(e)}'}), 500
        
        return jsonify({
            'status': 'success',
            'usuario_id': usuario_id,
            'total_gastos': len(ids),
            'path_usado': path_used,
            'ids': ids
        }), 200
    except Exception as e:
        return jsonify({'error': f'Error listando IDs de gastos: {str(e)}'}), 500


@app.route('/api/v2/firebase/users/<usuario_id>/gastos', methods=['POST'])
@token_required
def crear_gasto_firebase(usuario_id):
    """Crea un nuevo gasto en Firebase para un usuario"""
    if not FIREBASE_AVAILABLE:
        return jsonify({'error': 'Firebase no disponible'}), 503
    
    try:
        # Intentar leer JSON de forma tolerante
        try:
            data = request.get_json(silent=True)
        except BadRequest as e:
            return jsonify({'error': 'JSON inválido', 'detalle': str(e)}), 400

        # Fallback a form-data si no viene JSON
        if data is None:
            data = request.form.to_dict() or {}
            if not data:
                return jsonify({
                    'error': 'Cuerpo vacío o no es JSON',
                    'hint': 'Use Content-Type: application/json o envíe form-data',
                    'example': {'cantidad': 10.5, 'categoria': 'comida', 'descripcion': 'opcional'}
                }), 400
        cantidad_val = data.get('cantidad') or data.get('monto')
        categoria = data.get('categoria')
        if cantidad_val is None or not categoria:
            return jsonify({'error': 'Faltan campos requeridos: cantidad, categoria'}), 400
        # Validar que cantidad sea numérica
        try:
            cantidad_num = float(cantidad_val)
        except (TypeError, ValueError):
            return jsonify({'error': 'Cantidad/monto inválido', 'valor': cantidad_val}), 400
        
        gasto = {
            'cantidad': float(cantidad_num),
            'categoria': categoria,
            'descripcion': data.get('descripcion', ''),
            'fecha': data.get('fecha', datetime.now().isoformat()),
            'createdAt': datetime.now().isoformat(),
            'userId': usuario_id
        }
        
        # Verificación opcional de Firebase ID Token para respetar reglas de escritura
        id_token = request.headers.get('X-Firebase-Id-Token')
        if id_token:
            try:
                decoded = firebase_auth.verify_id_token(id_token)
                uid = decoded.get('uid')
                if uid != usuario_id:
                    return jsonify({'error': 'UID del token no coincide con usuario_id'}), 403
            except Exception as e:
                return jsonify({'error': 'ID token inválido', 'detalle': str(e)}), 401

        # Guardar en Firebase: path único users/{uid}/gastos
        path_used = f'users/{usuario_id}/gastos'
        try:
            doc_ref = db.collection('users').document(usuario_id).collection('gastos').document()
            doc_ref.set(gasto)
            path_used = f'{path_used}/{doc_ref.id}'
        except Exception as e:
            return jsonify({'error': f'Error escribiendo en Firebase: {str(e)}'}), 500
        
        return jsonify({
            'status': 'success',
            'mensaje': 'Gasto creado correctamente',
            'gasto_id': doc_ref.id,
            'path_usado': path_used,
            'data': gasto
        }), 201
    except Exception as e:
        return jsonify({'error': f'Error creando gasto: {str(e)}'}), 500


@app.route('/api/v2/predict-category', methods=['GET', 'POST'])
@token_required
def predict_category():
    """Predicción separada por categoría (30 días). REQUIERE TOKEN."""
    try:
        data = request.get_json()
        expenses, err = _get_expenses_or_firebase(data)
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        
        df = prepare_dataframe(expenses)
        predictions = predict_by_category(df, days=30)
        
        return jsonify({
            'status': 'success',
            'data': predictions
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/predict-monthly', methods=['GET', 'POST'])
@token_required
def predict_monthly_endpoint():
    """Predicción mensual con 30 días."""
    try:
        data = request.get_json()
        expenses, err = _get_expenses_or_firebase(data)
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        
        df = prepare_dataframe(expenses)
        predictions = predict_monthly(df, days=30)
        
        return jsonify({
            'status': 'success',
            'data': predictions
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/detect-anomalies', methods=['GET', 'POST'])
@token_required
def detect_anomalies_endpoint():
    """Detección automática de anomalías."""
    try:
        data = request.get_json()
        expenses, err = _get_expenses_or_firebase(data)
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        
        df = prepare_dataframe(expenses)
        anomalies = detect_anomalies(df)
        
        return jsonify({
            'status': 'success',
            'data': anomalies
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/compare-models', methods=['GET', 'POST'])
@token_required
def compare_models_endpoint():
    """Comparación de múltiples modelos ML."""
    try:
        data = request.get_json()
        expenses, err = _get_expenses_or_firebase(data)
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        
        df = prepare_dataframe(expenses)
        comparison = compare_models(df)
        
        return jsonify({
            'status': 'success',
            'data': comparison
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/seasonality', methods=['GET', 'POST'])
@token_required
def seasonality_endpoint():
    """Análisis de estacionalidad."""
    try:
        data = request.get_json()
        expenses, err = _get_expenses_or_firebase(data)
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        
        df = prepare_dataframe(expenses)
        seasonality = analyze_seasonality(df)
        
        return jsonify({
            'status': 'success',
            'data': seasonality
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/analysis-complete', methods=['GET', 'POST'])
@token_required
def analysis_complete():
    """Análisis completo con las 5 mejoras."""
    try:
        data = request.get_json()
        expenses, err = _get_expenses_or_firebase(data)
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        
        df = prepare_dataframe(expenses)
        
        result = {
            'prediccion_categoria': predict_by_category(df),
            'prediccion_mensual': predict_monthly(df),
            'anomalias': detect_anomalies(df),
            'comparacion_modelos': compare_models(df),
            'estacionalidad': analyze_seasonality(df),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/stat/correlations', methods=['GET', 'POST'])
@token_required
def correlations_endpoint():
    """Análisis de correlaciones entre categorías."""
    try:
        data = request.get_json()
        expenses, err = _get_expenses_or_firebase(data)
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        
        df = prepare_dataframe(expenses)
        correlations = analyze_correlations(df)
        
        return jsonify({
            'status': 'success',
            'data': correlations
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/stat/temporal-comparison', methods=['GET', 'POST'])
@token_required
def temporal_comparison_endpoint():
    """Comparación mes actual vs anterior."""
    try:
        data = request.get_json()
        expenses, err = _get_expenses_or_firebase(data)
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        
        df = prepare_dataframe(expenses)
        comparison = analyze_temporal_comparison(df)
        
        return jsonify({
            'status': 'success',
            'data': comparison
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/stat/clustering', methods=['GET', 'POST'])
@token_required
def clustering_endpoint():
    """Agrupamiento automático de gastos similares."""
    try:
        data = request.get_json()
        expenses, err = _get_expenses_or_firebase(data)
        n_clusters = data.get('n_clusters', 3)
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        
        df = prepare_dataframe(expenses)
        clusters = perform_clustering(df, n_clusters=n_clusters)
        
        return jsonify({
            'status': 'success',
            'data': clusters
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/stat/trends', methods=['GET', 'POST'])
@token_required
def trends_endpoint():
    """Detección de tendencias en gastos."""
    try:
        data = request.get_json()
        expenses, err = _get_expenses_or_firebase(data)
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        
        df = prepare_dataframe(expenses)
        trends = detect_trends(df)
        
        return jsonify({
            'status': 'success',
            'data': trends
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/stat/outliers', methods=['GET', 'POST'])
@token_required
def outliers_endpoint():
    """Detección de gastos atípicos con IQR y Z-Score."""
    try:
        data = request.get_json()
        expenses, err = _get_expenses_or_firebase(data)
        
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        
        df = prepare_dataframe(expenses)
        outliers = detect_outliers_iqr(df)
        
        return jsonify({
            'status': 'success',
            'data': outliers
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/stat/complete', methods=['GET', 'POST'])
@token_required
def statistical_analysis_complete():
    """Análisis estadístico completo (todas las 5 mejoras)."""
    try:
        data = request.get_json()
        expenses, err = _get_expenses_or_firebase(data)
        
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        
        df = prepare_dataframe(expenses)
        
        result = {
            'correlaciones': analyze_correlations(df),
            'comparacion_temporal': analyze_temporal_comparison(df),
            'clustering': perform_clustering(df),
            'tendencias': detect_trends(df),
            'outliers': detect_outliers_iqr(df),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/savings/goals', methods=['GET', 'POST'])
@token_required
def savings_goals_endpoint():
    """Calcular metas de ahorro personalizadas."""
    try:
        data = request.get_json(silent=True) or {}
        expenses, err = _get_expenses_or_firebase(data)
        goal_name = data.get('goal_name') or request.args.get('goal_name', 'Meta')
        target_amount = data.get('target_amount') or request.args.get('target_amount', 1000)
        months = data.get('months') or request.args.get('months', 12)
        try:
            target_amount = float(target_amount)
        except Exception:
            target_amount = 1000
        try:
            months = int(months)
        except Exception:
            months = 12
        
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        
        df = prepare_dataframe(expenses)
        goals = calculate_savings_goals(df, goal_name, target_amount, months)
        
        return jsonify({
            'status': 'success',
            'data': goals
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/savings/tips', methods=['GET', 'POST'])
@token_required
def personalized_tips_endpoint():
    """Generar tips personalizados de ahorro."""
    try:
        data = request.get_json(silent=True) or {}
        expenses, err = _get_expenses_or_firebase(data)
        
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        
        df = prepare_dataframe(expenses)
        tips = generate_personalized_tips(df)
        
        return jsonify({
            'status': 'success',
            'data': tips
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/savings/budget-alerts', methods=['GET', 'POST'])
@token_required
def budget_alerts_endpoint():
    """Generar alertas de presupuesto."""
    try:
        data = request.get_json(silent=True) or {}
        expenses, err = _get_expenses_or_firebase(data)
        monthly_budget = data.get('monthly_budget') or request.args.get('monthly_budget', 3000)
        try:
            monthly_budget = float(monthly_budget)
        except Exception:
            monthly_budget = 3000
        
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        
        df = prepare_dataframe(expenses)
        alerts = generate_budget_alerts(df, monthly_budget)
        
        return jsonify({
            'status': 'success',
            'data': alerts
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/savings/health-score', methods=['GET', 'POST'])
@token_required
def health_score_endpoint():
    """Calcular puntuación de salud financiera."""
    try:
        data = request.get_json(silent=True) or {}
        expenses, err = _get_expenses_or_firebase(data)
        monthly_budget = data.get('monthly_budget') or request.args.get('monthly_budget', 3000)
        try:
            monthly_budget = float(monthly_budget)
        except Exception:
            monthly_budget = 3000
        
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        
        df = prepare_dataframe(expenses)
        score = calculate_financial_health_score(df, monthly_budget)
        
        return jsonify({
            'status': 'success',
            'data': score
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/savings/weekly-report', methods=['GET', 'POST'])
@token_required
def weekly_report_endpoint():
    """Generar resumen semanal para reportes automáticos."""
    try:
        data = request.get_json(silent=True) or {}
        expenses, err = _get_expenses_or_firebase(data)
        
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        
        df = prepare_dataframe(expenses)
        report = generate_weekly_report(df)
        
        return jsonify({
            'status': 'success',
            'data': report
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/savings/complete', methods=['GET', 'POST'])
@token_required
def savings_analysis_complete():
    """Análisis completo de recomendaciones (todas las 5 mejoras)."""
    try:
        data = request.get_json(silent=True) or {}
        expenses, err = _get_expenses_or_firebase(data)
        goal_name = (data.get('goal_name') or request.args.get('goal_name') or 'Meta general')
        target_amount = (data.get('target_amount') or request.args.get('target_amount') or 5000)
        months = (data.get('months') or request.args.get('months') or 12)
        monthly_budget = (data.get('monthly_budget') or request.args.get('monthly_budget') or 3000)
        try:
            target_amount = float(target_amount)
        except Exception:
            target_amount = 5000
        try:
            months = int(months)
        except Exception:
            months = 12
        try:
            monthly_budget = float(monthly_budget)
        except Exception:
            monthly_budget = 3000
        
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        
        df = prepare_dataframe(expenses)
        
        result = {
            'metas_ahorro': calculate_savings_goals(df, goal_name, target_amount, months),
            'tips_personalizados': generate_personalized_tips(df),
            'alertas_presupuesto': generate_budget_alerts(df, monthly_budget),
            'salud_financiera': calculate_financial_health_score(df, monthly_budget),
            'reporte_semanal': generate_weekly_report(df),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/charts/heatmap', methods=['GET', 'POST'])
@token_required
def heatmap_endpoint():
    """Generar calendario de calor de gastos."""
    try:
        data = request.get_json(silent=True) or {}
        expenses, err = _get_expenses_or_firebase(data)
        
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        
        df = prepare_dataframe(expenses)
        heatmap = generate_heatmap(df)
        
        return jsonify({
            'status': 'success',
            'data': heatmap
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/charts/sankey', methods=['GET', 'POST'])
@token_required
def sankey_endpoint():
    """Generar diagrama Sankey de flujo de dinero."""
    try:
        data = request.get_json(silent=True) or {}
        expenses, err = _get_expenses_or_firebase(data)
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        sankey = generate_sankey_diagram(df)
        
        return jsonify({
            'status': 'success',
            'data': sankey
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/charts/dashboard', methods=['GET', 'POST'])
@token_required
def dashboard_endpoint():
    """Generar dashboard interactivo."""
    try:
        data = request.get_json(silent=True) or {}
        expenses, err = _get_expenses_or_firebase(data)
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        dashboard = generate_interactive_dashboard(df)
        
        return jsonify({
            'status': 'success',
            'data': dashboard
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/charts/comparison', methods=['GET', 'POST'])
@token_required
def comparison_endpoint():
    """Generar gráficos comparativos mes vs mes."""
    try:
        data = request.get_json(silent=True) or {}
        expenses, err = _get_expenses_or_firebase(data)
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        comparison = generate_month_comparison_chart(df)
        
        return jsonify({
            'status': 'success',
            'data': comparison
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/charts/export', methods=['GET', 'POST'])
@token_required
def export_graphics_endpoint():
    """Exportar gráficos como imágenes (JSON o BASE64)."""
    try:
        data = request.get_json(silent=True) or {}
        expenses, err = _get_expenses_or_firebase(data)
        output_format = (data.get('format') or request.args.get('format') or 'json')
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        exported = export_graphics_as_image(df, output_format)
        
        return jsonify({
            'status': 'success',
            'data': exported
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/charts/complete', methods=['GET', 'POST'])
@token_required
def charts_complete():
    """Generar todos los gráficos disponibles."""
    try:
        data = request.get_json(silent=True) or {}
        expenses, err = _get_expenses_or_firebase(data)
        if not expenses:
            return jsonify({'error': 'Datos inválidos o no hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        
        result = {
            'heatmap': generate_heatmap(df),
            'sankey': generate_sankey_diagram(df),
            'dashboard': generate_interactive_dashboard(df),
            'comparacion_meses': generate_month_comparison_chart(df),
            'exportacion': export_graphics_as_image(df, 'json'),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("✅ API Mejorada iniciada - 20 mejoras de IA")
    print("📊 ENDPOINTS - PREDICCIÓN (5):")
    print("   • POST /api/v2/predict-category - Predicción por categoría")
    print("   • POST /api/v2/predict-monthly - Predicción mensual (30 días)")
    print("   • POST /api/v2/detect-anomalies - Detección de anomalías")
    print("   • POST /api/v2/compare-models - Comparación de modelos ML")
    print("   • POST /api/v2/seasonality - Análisis de estacionalidad")
    print("   • POST /api/v2/analysis-complete - Análisis completo (predicción)")
    print("\n📈 ENDPOINTS - ANÁLISIS ESTADÍSTICO (5):")
    print("   • POST /api/v2/stat/correlations - Correlaciones entre categorías")
    print("   • POST /api/v2/stat/temporal-comparison - Mes actual vs anterior")
    print("   • POST /api/v2/stat/clustering - Agrupamiento de gastos")
    print("   • POST /api/v2/stat/trends - Detección de tendencias")
    print("   • POST /api/v2/stat/outliers - Detección de outliers (IQR+Z-Score)")
    print("   • POST /api/v2/stat/complete - Análisis estadístico completo")
    print("\n💡 ENDPOINTS - RECOMENDACIONES DE AHORRO (5):")
    print("   • POST /api/v2/savings/goals - Metas de ahorro personalizadas")
    print("   • POST /api/v2/savings/tips - Tips personalizados")
    print("   • POST /api/v2/savings/budget-alerts - Alertas de presupuesto")
    print("   • POST /api/v2/savings/health-score - Puntuación financiera")
    print("   • POST /api/v2/savings/weekly-report - Resumen semanal")
    print("   • POST /api/v2/savings/complete - Análisis completo (recomendaciones)")
    print("\n📊 ENDPOINTS - GRÁFICOS Y VISUALIZACIÓN (5):")
    print("   • POST /api/v2/charts/heatmap - Calendario de calor")
    print("   • POST /api/v2/charts/sankey - Diagrama Sankey")
    print("   • POST /api/v2/charts/dashboard - Dashboard interactivo")
    print("   • POST /api/v2/charts/comparison - Comparativas mes vs mes")
    print("   • POST /api/v2/charts/export - Exportar gráficos (JSON/BASE64)")
    print("   • POST /api/v2/charts/complete - Todos los gráficos")
    print("\n🔧 UTILIDAD:")
    print("   • GET  /api/v2/health - Estado de la API")
    print("   • POST /api/v2/auth/token - Generar token JWT")
    print("   • POST /api/v2/auth/validate - Validar token")
    
    print("\n" + "="*80)
    print("🔐 INSTRUCCIONES DE USO CON POSTMAN")
    print("="*80)
    print("\n✅ PASO 1: OBTENER TOKEN")
    print("   1. Abre Postman")
    print("   2. Método: POST")
    print("   3. URL: http://localhost:5000/api/v2/auth/token")
    print("   4. Tab 'Body' → Raw → JSON")
    print("   5. Código:")
    print("      {")
    print("        \"user_id\": \"mi_usuario\"")
    print("      }")
    print("   6. Click 'Send'")
    print("   7. Copia el valor del campo 'token' de la respuesta")
    print("\n✅ PASO 2: USAR EL TOKEN EN OTROS ENDPOINTS")
    print("   1. En cualquier endpoint (ej: /api/v2/predict-category)")
    print("   2. Tab 'Headers'")
    print("   3. Agregar header: Authorization")
    print("   4. Valor: Bearer <tu_token_aqui>")
    print("   5. O usar: X-API-Key: <tu_token_aqui>")
    print("   6. Tab 'Body' → Raw → JSON → Tu data")
    print("   7. Click 'Send'")
    print("\n✅ PASO 3: EJEMPLO COMPLETO")
    print("   Predicción de gastos por categoría:")
    print("   URL: http://localhost:5000/api/v2/predict-category")
    print("   Headers:")
    print("      Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...")
    print("   Body (JSON):")
    print("      {")
    print("        \"expenses\": [")
    print("          {\"fecha\": \"2024-12-01\", \"monto\": 50, \"categoria\": \"Comida\"},")
    print("          {\"fecha\": \"2024-12-02\", \"monto\": 30, \"categoria\": \"Transporte\"},")
    print("          {\"fecha\": \"2024-12-03\", \"monto\": 100, \"categoria\": \"Comida\"}")
    print("        ]")
    print("      }")
    print("\n⚠️  NOTA: Tokens válidos por 24 horas. Generar nuevo si expira.")
    print("="*80 + "\n")


# ============================================================
# 🤖 ASESOR FINANCIERO IA - ENDPOINTS AVANZADOS
# ============================================================
# Integra análisis completo de Firebase con:
# 1. Predicción de gastos futuros
# 2. Análisis estadístico avanzado
# 3. Recomendaciones personalizadas de ahorro
# 4. Datos para gráficos interactivos
# ============================================================

def obtener_gastos_firebase(usuario_id):
    """Obtiene todos los gastos de un usuario desde Firebase"""
    if not FIREBASE_AVAILABLE or not db:
        return None, "Firebase no disponible"
    
    try:
        gastos_ref = db.collection('users').document(usuario_id).collection('gastos')
        gastos_docs = gastos_ref.stream()
        
        gastos = []
        for doc in gastos_docs:
            gasto = doc.to_dict()
            gasto['id'] = doc.id
            gastos.append(gasto)
        
        return gastos, None
    except Exception as e:
        return None, str(e)


def obtener_budget_usuario(usuario_id):
    """Lee la subcolección budget/current para traer presupuesto/ingresos mensuales del usuario."""
    if not FIREBASE_AVAILABLE or not db:
        return None, 'Firebase no disponible'
    try:
        doc = db.collection('users').document(usuario_id).collection('budget').document('current').get()
        if not doc.exists:
            return None, None
        data = doc.to_dict() or {}
        # Normalizar posibles nombres de campos
        budget_info = {
            'monthly_budget': data.get('monthly_budget') or data.get('budget') or data.get('monthlyBudget') or data.get('limit'),
            'monthly_income': data.get('monthly_income') or data.get('income') or data.get('monthlyIncome'),
            'currency': data.get('currency')
        }
        return budget_info, None
    except Exception as e:
        return None, str(e)


def procesar_fecha(fecha_str):
    """Convierte diferentes formatos de fecha a datetime"""
    if fecha_str is None:
        return datetime.now()
    
    if isinstance(fecha_str, datetime):
        return fecha_str
    
    formatos = [
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%d-%m-%Y'
    ]
    
    for fmt in formatos:
        try:
            return datetime.strptime(str(fecha_str)[:26], fmt)
        except:
            continue
    
    return datetime.now()


@app.route('/api/v2/firebase/users/<usuario_id>/asesor-financiero', methods=['GET'])
@token_required
def asesor_financiero_completo(usuario_id):
    """
    🤖 ASESOR FINANCIERO IA COMPLETO
    
    Devuelve análisis integral con:
    - Predicciones de gastos futuros (próximos 30 días)
    - Análisis estadístico completo
    - Recomendaciones personalizadas de ahorro
    - Datos preparados para gráficos
    """
    if not FIREBASE_AVAILABLE:
        return jsonify({'error': 'Firebase no disponible'}), 503
    
    try:
        # Obtener gastos de Firebase
        gastos, error = obtener_gastos_firebase(usuario_id)
        if error:
            return jsonify({'error': f'Error obteniendo gastos: {error}'}), 500
        
        if not gastos or len(gastos) < 3:
            return jsonify({
                'status': 'error',
                'mensaje': 'Se necesitan al menos 3 gastos registrados para el análisis',
                'gastos_actuales': len(gastos) if gastos else 0
            }), 400
        
        # Convertir a DataFrame
        df = pd.DataFrame(gastos)
        df['fecha'] = df['fecha'].apply(procesar_fecha)
        df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0)
        df['mes'] = df['fecha'].dt.month
        df['año'] = df['fecha'].dt.year
        df['dia_semana'] = df['fecha'].dt.dayofweek
        df['dia_mes'] = df['fecha'].dt.day
        df['semana'] = df['fecha'].dt.isocalendar().week
        
        # ============================================
        # 1. PREDICCIÓN DE GASTOS FUTUROS
        # ============================================
        predicciones = generar_predicciones(df)
        
        # ============================================
        # 2. ANÁLISIS ESTADÍSTICO
        # ============================================
        analisis = generar_analisis_estadistico(df)
        
        # ============================================
        # 3. RECOMENDACIONES DE AHORRO
        # ============================================
        budget_info, _ = obtener_budget_usuario(usuario_id)
        recomendaciones = generar_recomendaciones(df, analisis, budget_info=budget_info, predicciones=predicciones)
        
        # ============================================
        # 4. DATOS PARA GRÁFICOS
        # ============================================
        graficos = preparar_datos_graficos(df)
        
        # Puntuación financiera (gamificación)
        score = calcular_score_financiero(df, analisis)
        
        return jsonify({
            'status': 'success',
            'usuario_id': usuario_id,
            'fecha_analisis': datetime.now().isoformat(),
            'resumen': {
                'total_gastos_registrados': len(gastos),
                'gasto_total': round(df['cantidad'].sum(), 2),
                'gasto_promedio': round(df['cantidad'].mean(), 2),
                'periodo_analizado': {
                    'desde': df['fecha'].min().strftime('%Y-%m-%d'),
                    'hasta': df['fecha'].max().strftime('%Y-%m-%d'),
                    'dias': (df['fecha'].max() - df['fecha'].min()).days
                }
            },
            'score_financiero': score,
            'predicciones': predicciones,
            'analisis_estadistico': analisis,
            'recomendaciones': recomendaciones,
            'graficos': graficos
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': f'Error en asesor financiero: {str(e)}',
            'detalle': traceback.format_exc()
        }), 500


def generar_predicciones(df):
    """Genera predicciones de gastos futuros"""
    predicciones = {
        'proximo_mes': {},
        'por_categoria': {},
        'tendencia': '',
        'alerta_gastos': []
    }
    
    try:
        # Gasto diario promedio
        dias_unicos = df['fecha'].dt.date.nunique()
        gasto_diario = df['cantidad'].sum() / max(dias_unicos, 1)
        
        # Predicción próximo mes (30 días)
        prediccion_mes = round(gasto_diario * 30, 2)
        
        # Calcular tendencia usando regresión
        df_agrupado = df.groupby(df['fecha'].dt.date)['cantidad'].sum().reset_index()
        df_agrupado['dias'] = range(len(df_agrupado))
        
        tendencia_valor = 0
        if len(df_agrupado) >= 3:
            X = df_agrupado['dias'].values.reshape(-1, 1)
            y = df_agrupado['cantidad'].values
            modelo = LinearRegression()
            modelo.fit(X, y)
            tendencia_valor = modelo.coef_[0]
        
        if tendencia_valor > 0.5:
            tendencia = 'AUMENTANDO'
            prediccion_ajustada = prediccion_mes * 1.1
        elif tendencia_valor < -0.5:
            tendencia = 'DISMINUYENDO'
            prediccion_ajustada = prediccion_mes * 0.9
        else:
            tendencia = 'ESTABLE'
            prediccion_ajustada = prediccion_mes
        
        predicciones['proximo_mes'] = {
            'estimacion_base': prediccion_mes,
            'estimacion_ajustada': round(prediccion_ajustada, 2),
            'gasto_diario_promedio': round(gasto_diario, 2),
            'confianza': 'ALTA' if len(df) > 20 else 'MEDIA' if len(df) > 10 else 'BAJA'
        }
        
        predicciones['tendencia'] = tendencia
        
        # Predicción por categoría
        for categoria in df['categoria'].unique():
            df_cat = df[df['categoria'] == categoria]
            dias_cat = df_cat['fecha'].dt.date.nunique()
            gasto_cat_diario = df_cat['cantidad'].sum() / max(dias_cat, 1)
            predicciones['por_categoria'][categoria] = {
                'prediccion_30_dias': round(gasto_cat_diario * 30, 2),
                'promedio_por_gasto': round(df_cat['cantidad'].mean(), 2),
                'total_registros': len(df_cat)
            }
        
        # Alertas de gastos altos
        gasto_promedio = df['cantidad'].mean()
        gasto_std = df['cantidad'].std()
        umbral = gasto_promedio + (1.5 * gasto_std)
        
        for categoria in df['categoria'].unique():
            gasto_cat = df[df['categoria'] == categoria]['cantidad'].mean()
            if gasto_cat > umbral:
                predicciones['alerta_gastos'].append({
                    'categoria': categoria,
                    'mensaje': f'Gastos elevados en {categoria}',
                    'promedio': round(gasto_cat, 2),
                    'umbral': round(umbral, 2)
                })
    
    except Exception as e:
        predicciones['error'] = str(e)
    
    return predicciones


def generar_analisis_estadistico(df):
    """Genera análisis estadístico completo"""
    analisis = {
        'por_categoria': {},
        'por_mes': {},
        'por_año': {},
        'por_trimestre': {},
        'por_dia_semana': {},
        'comparativas': {},
        'outliers': [],
        'patrones': {}
    }
    
    try:
        # Análisis por categoría
        for categoria in df['categoria'].unique():
            df_cat = df[df['categoria'] == categoria]
            analisis['por_categoria'][categoria] = {
                'total': round(df_cat['cantidad'].sum(), 2),
                'promedio': round(df_cat['cantidad'].mean(), 2),
                'maximo': round(df_cat['cantidad'].max(), 2),
                'minimo': round(df_cat['cantidad'].min(), 2),
                'desviacion': round(df_cat['cantidad'].std(), 2) if len(df_cat) > 1 else 0,
                'cantidad_gastos': len(df_cat),
                'porcentaje_total': round((df_cat['cantidad'].sum() / df['cantidad'].sum()) * 100, 2)
            }
        
        # Análisis por mes
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
        for mes in df['mes'].unique():
            df_mes = df[df['mes'] == mes]
            nombre_mes = meses[int(mes) - 1] if 1 <= mes <= 12 else f'Mes {mes}'
            analisis['por_mes'][nombre_mes] = {
                'total': round(df_mes['cantidad'].sum(), 2),
                'promedio': round(df_mes['cantidad'].mean(), 2),
                'cantidad_gastos': len(df_mes),
                'categoria_top': df_mes.groupby('categoria')['cantidad'].sum().idxmax() if len(df_mes) > 0 else None
            }

        # Análisis por año
        for year in df['año'].unique():
            df_year = df[df['año'] == year]
            analisis['por_año'][str(int(year))] = {
                'total': round(df_year['cantidad'].sum(), 2),
                'promedio': round(df_year['cantidad'].mean(), 2),
                'cantidad_gastos': len(df_year),
                'categoria_top': df_year.groupby('categoria')['cantidad'].sum().idxmax() if len(df_year) > 0 else None
            }

        # Análisis por trimestre
        df['trimestre_num'] = df['fecha'].dt.quarter
        df['trimestre_label'] = df['año'].astype(str) + '-Q' + df['trimestre_num'].astype(str)
        for tlabel in df['trimestre_label'].unique():
            df_tri = df[df['trimestre_label'] == tlabel]
            analisis['por_trimestre'][tlabel] = {
                'total': round(df_tri['cantidad'].sum(), 2),
                'promedio': round(df_tri['cantidad'].mean(), 2),
                'cantidad_gastos': len(df_tri),
                'categoria_top': df_tri.groupby('categoria')['cantidad'].sum().idxmax() if len(df_tri) > 0 else None
            }
        
        # Análisis por día de semana
        for dia in df['dia_semana'].unique():
            df_dia = df[df['dia_semana'] == dia]
            nombre_dia = dias_semana[int(dia)] if 0 <= dia <= 6 else f'Día {dia}'
            analisis['por_dia_semana'][nombre_dia] = {
                'total': round(df_dia['cantidad'].sum(), 2),
                'promedio': round(df_dia['cantidad'].mean(), 2),
                'cantidad_gastos': len(df_dia)
            }
        
        # Comparativa mes actual vs anterior
        hoy = datetime.now()
        mes_actual = hoy.month
        año_actual = hoy.year
        
        df_mes_actual = df[(df['mes'] == mes_actual) & (df['año'] == año_actual)]
        
        if mes_actual == 1:
            mes_anterior = 12
            año_anterior = año_actual - 1
        else:
            mes_anterior = mes_actual - 1
            año_anterior = año_actual
        
        df_mes_anterior = df[(df['mes'] == mes_anterior) & (df['año'] == año_anterior)]
        
        gasto_actual = df_mes_actual['cantidad'].sum()
        gasto_anterior = df_mes_anterior['cantidad'].sum()
        
        if gasto_anterior > 0:
            variacion = ((gasto_actual - gasto_anterior) / gasto_anterior) * 100
        else:
            variacion = 100 if gasto_actual > 0 else 0
        
        analisis['comparativas']['mes_actual_vs_anterior'] = {
            'mes_actual': {
                'nombre': meses[mes_actual - 1],
                'total': round(gasto_actual, 2),
                'cantidad_gastos': len(df_mes_actual)
            },
            'mes_anterior': {
                'nombre': meses[mes_anterior - 1],
                'total': round(gasto_anterior, 2),
                'cantidad_gastos': len(df_mes_anterior)
            },
            'variacion_porcentaje': round(variacion, 2),
            'tendencia': 'AUMENTO' if variacion > 5 else 'DISMINUCIÓN' if variacion < -5 else 'ESTABLE'
        }
        
        # Detectar outliers (gastos inusuales)
        Q1 = df['cantidad'].quantile(0.25)
        Q3 = df['cantidad'].quantile(0.75)
        IQR = Q3 - Q1
        umbral_superior = Q3 + 1.5 * IQR
        
        outliers_df = df[df['cantidad'] > umbral_superior]
        for _, row in outliers_df.iterrows():
            analisis['outliers'].append({
                'categoria': row['categoria'],
                'cantidad': round(row['cantidad'], 2),
                'fecha': row['fecha'].strftime('%Y-%m-%d'),
                'descripcion': row.get('descripcion', ''),
                'motivo': 'Gasto significativamente mayor al promedio'
            })
        
        # Patrones detectados
        dia_mas_gasto = df.groupby('dia_semana')['cantidad'].sum().idxmax()
        categoria_mas_frecuente = df['categoria'].value_counts().idxmax()
        hora_pico = None  # Si tuviéramos hora
        
        analisis['patrones'] = {
            'dia_mas_gastos': dias_semana[int(dia_mas_gasto)] if 0 <= dia_mas_gasto <= 6 else 'N/A',
            'categoria_mas_frecuente': categoria_mas_frecuente,
            'gasto_promedio_general': round(df['cantidad'].mean(), 2),
            'gasto_mediano': round(df['cantidad'].median(), 2)
        }
        
    except Exception as e:
        analisis['error'] = str(e)
    
    return analisis


def generar_recomendaciones(df, analisis, budget_info=None, predicciones=None):
    """Genera recomendaciones personalizadas de ahorro"""
    recomendaciones = {
        'ahorro': [],
        'alertas': [],
        'metas_sugeridas': [],
        'tips_personalizados': []
    }
    
    try:
        gasto_total = df['cantidad'].sum()
        gasto_promedio = df['cantidad'].mean()
        
        # Analizar categorías con mayor gasto
        gastos_categoria = df.groupby('categoria')['cantidad'].sum().sort_values(ascending=False)
        
        # Top 3 categorías con más gasto
        for i, (categoria, total) in enumerate(gastos_categoria.head(3).items()):
            porcentaje = (total / gasto_total) * 100
            
            if porcentaje > 40:
                recomendaciones['alertas'].append({
                    'tipo': 'GASTO_EXCESIVO',
                    'categoria': categoria,
                    'mensaje': f'⚠️ {categoria} representa el {porcentaje:.1f}% de tus gastos. Considera reducirlo.',
                    'porcentaje': round(porcentaje, 2),
                    'monto': round(total, 2)
                })
                
                ahorro_sugerido = total * 0.2  # Sugerir reducir 20%
                recomendaciones['ahorro'].append({
                    'categoria': categoria,
                    'ahorro_potencial': round(ahorro_sugerido, 2),
                    'estrategia': f'Reducir gastos en {categoria} un 20% podría ahorrarte ${ahorro_sugerido:.2f}',
                    'prioridad': 'ALTA'
                })
            
            elif porcentaje > 25:
                recomendaciones['ahorro'].append({
                    'categoria': categoria,
                    'ahorro_potencial': round(total * 0.15, 2),
                    'estrategia': f'Optimizar gastos en {categoria} (representa {porcentaje:.1f}% del total)',
                    'prioridad': 'MEDIA'
                })
        
        # Metas sugeridas dinámicas (evitar "números rojos")
        gasto_mensual_promedio = gasto_total / max(df['mes'].nunique(), 1)
        # Obtener predicción próxima (si no viene, calcular)
        if not predicciones:
            predicciones = generar_predicciones(df)
        pred_next = predicciones.get('proximo_mes', {}).get('estimacion_ajustada') or predicciones.get('proximo_mes', {}).get('estimacion_base') or gasto_mensual_promedio
        # Determinar presupuesto/ingresos
        monthly_budget = None
        monthly_income = None
        if budget_info:
            monthly_budget = budget_info.get('monthly_budget')
            monthly_income = budget_info.get('monthly_income')
        # Si no hay budget, usar gasto del mes anterior como referencia
        comp = analisis.get('comparativas', {}).get('mes_actual_vs_anterior', {})
        ref_prev_total = comp.get('mes_anterior', {}).get('total') if comp else None
        ref_budget = monthly_budget if monthly_budget is not None else ref_prev_total
        # Calcular ahorro necesario para balancear
        base_capacidad = monthly_income if monthly_income is not None else ref_budget
        savings_needed = None
        if base_capacidad is not None:
            savings_needed = max(0.0, float(pred_next) - float(base_capacidad))
        else:
            # Fallback: si no hay referencia, sugerir reducir el exceso vs promedio
            savings_needed = max(0.0, float(pred_next) - float(gasto_mensual_promedio)) * 0.5
        # Dificultad según proporción del ahorro necesario
        ratio = (savings_needed / pred_next) if pred_next > 0 else 0
        dificultad = 'FÁCIL' if ratio <= 0.1 else 'MEDIA' if ratio <= 0.25 else 'DIFÍCIL'
        recomendaciones['metas_sugeridas'] = [
            {
                'tipo': 'EVITAR_NUMEROS_ROJOS',
                'meta': round(savings_needed, 2),
                'descripcion': 'Ahorro necesario para cerrar el mes sin déficit',
                'base': {
                    'prediccion_mes': round(pred_next, 2),
                    'presupuesto': float(monthly_budget) if monthly_budget is not None else None,
                    'ingreso': float(monthly_income) if monthly_income is not None else None,
                    'referencia_mes_anterior': float(ref_prev_total) if ref_prev_total is not None else None
                },
                'dificultad': dificultad
            },
            {
                'tipo': 'BUFFER_PREVENTIVO',
                'meta': round(pred_next * 0.1, 2),
                'descripcion': 'Crear un colchón del 10% de la proyección para imprevistos',
                'dificultad': 'MEDIA'
            },
            {
                'tipo': 'REDUCCION_CATEGORIA',
                'categoria': gastos_categoria.index[0] if len(gastos_categoria) > 0 else 'N/A',
                'meta': round((gastos_categoria.iloc[0] * 0.15) if len(gastos_categoria) > 0 else 0, 2),
                'descripcion': f'Reducir {gastos_categoria.index[0]} en 15%' if len(gastos_categoria) > 0 else 'Reducir categoría principal en 15%',
                'dificultad': 'MEDIA'
            }
        ]
        
        # Tips personalizados
        comparativa = analisis.get('comparativas', {}).get('mes_actual_vs_anterior', {})
        variacion = comparativa.get('variacion_porcentaje', 0)
        
        if variacion > 20:
            recomendaciones['tips_personalizados'].append({
                'icono': '📈',
                'titulo': 'Gastos en aumento',
                'mensaje': f'Tus gastos aumentaron {variacion:.1f}% este mes. Revisa tus compras recientes.',
                'accion': 'Establece un presupuesto diario'
            })
        elif variacion < -10:
            recomendaciones['tips_personalizados'].append({
                'icono': '🎉',
                'titulo': '¡Felicidades!',
                'mensaje': f'Redujiste tus gastos {abs(variacion):.1f}% este mes. ¡Sigue así!',
                'accion': 'Mantén este ritmo de ahorro'
            })
        
        # Tips por día de la semana
        patrones = analisis.get('patrones', {})
        dia_mas_gastos = patrones.get('dia_mas_gastos', '')
        
        if dia_mas_gastos:
            recomendaciones['tips_personalizados'].append({
                'icono': '📅',
                'titulo': f'Patrón detectado: {dia_mas_gastos}',
                'mensaje': f'Los {dia_mas_gastos} son tu día de mayor gasto. Planifica con anticipación.',
                'accion': f'Evita compras impulsivas los {dia_mas_gastos}'
            })
        
        # Tip de categoría frecuente
        cat_frecuente = patrones.get('categoria_mas_frecuente', '')
        if cat_frecuente:
            recomendaciones['tips_personalizados'].append({
                'icono': '🔄',
                'titulo': f'Categoría frecuente: {cat_frecuente}',
                'mensaje': f'Gastas frecuentemente en {cat_frecuente}. Busca alternativas más económicas.',
                'accion': f'Compara precios antes de gastar en {cat_frecuente}'
            })
        
        # Tip general
        recomendaciones['tips_personalizados'].append({
            'icono': '💡',
            'titulo': 'Regla 50/30/20',
            'mensaje': 'Destina 50% a necesidades, 30% a deseos y 20% a ahorro.',
            'accion': 'Revisa si cumples esta proporción'
        })
        
    except Exception as e:
        recomendaciones['error'] = str(e)
    
    return recomendaciones


def preparar_datos_graficos(df):
    """Prepara datos estructurados para gráficos en frontend"""
    graficos = {}
    
    try:
        # 1. Gráfico de pastel - Distribución por categoría
        categorias = df.groupby('categoria')['cantidad'].sum()
        graficos['pie_categorias'] = {
            'tipo': 'pie',
            'titulo': 'Distribución de Gastos por Categoría',
            'labels': categorias.index.tolist(),
            'values': [round(v, 2) for v in categorias.values],
            'colors': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#7CFC00', '#DC143C'][:len(categorias)]
        }
        
        # 2. Gráfico de barras - Gastos por mes
        meses_nombres = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        gastos_mes = df.groupby('mes')['cantidad'].sum()
        
        graficos['bar_meses'] = {
            'tipo': 'bar',
            'titulo': 'Gastos por Mes',
            'labels': [meses_nombres[int(m)-1] for m in gastos_mes.index],
            'values': [round(v, 2) for v in gastos_mes.values],
            'color': '#36A2EB'
        }
        
        # 3. Gráfico de línea - Tendencia temporal
        gastos_diarios = df.groupby(df['fecha'].dt.date)['cantidad'].sum().reset_index()
        gastos_diarios.columns = ['fecha', 'total']
        gastos_diarios = gastos_diarios.sort_values('fecha').tail(30)  # Últimos 30 días
        
        graficos['line_tendencia'] = {
            'tipo': 'line',
            'titulo': 'Tendencia de Gastos (Últimos 30 días)',
            'labels': [str(f) for f in gastos_diarios['fecha'].values],
            'values': [round(v, 2) for v in gastos_diarios['total'].values],
            'color': '#FF6384'
        }
        
        # 4. Gráfico de barras - Gastos por día de semana
        dias = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        gastos_dia = df.groupby('dia_semana')['cantidad'].sum()
        
        graficos['bar_dias_semana'] = {
            'tipo': 'bar',
            'titulo': 'Gastos por Día de la Semana',
            'labels': [dias[int(d)] for d in sorted(gastos_dia.index)],
            'values': [round(gastos_dia.get(d, 0), 2) for d in sorted(gastos_dia.index)],
            'color': '#4BC0C0'
        }
        
        # 5. Heatmap data - Calendario de gastos
        gastos_calendario = df.groupby([df['fecha'].dt.date])['cantidad'].sum()
        graficos['heatmap_calendario'] = {
            'tipo': 'heatmap',
            'titulo': 'Calendario de Gastos',
            'data': [
                {'fecha': str(fecha), 'valor': round(valor, 2)}
                for fecha, valor in gastos_calendario.items()
            ]
        }
        
        # 6. Comparativa de categorías (stacked bar)
        cat_por_mes = df.groupby(['mes', 'categoria'])['cantidad'].sum().unstack(fill_value=0)
        graficos['stacked_categorias_mes'] = {
            'tipo': 'stacked_bar',
            'titulo': 'Categorías por Mes',
            'labels': [meses_nombres[int(m)-1] for m in cat_por_mes.index],
            'datasets': [
                {
                    'label': cat,
                    'data': [round(cat_por_mes.loc[m, cat] if cat in cat_por_mes.columns else 0, 2) for m in cat_por_mes.index]
                }
                for cat in df['categoria'].unique()
            ]
        }
        
        # 7. Top 5 gastos más grandes
        top_gastos = df.nlargest(5, 'cantidad')[['categoria', 'cantidad', 'descripcion', 'fecha']]
        graficos['top_gastos'] = {
            'tipo': 'lista',
            'titulo': 'Top 5 Gastos Más Grandes',
            'data': [
                {
                    'categoria': row['categoria'],
                    'cantidad': round(row['cantidad'], 2),
                    'descripcion': row.get('descripcion', 'N/A'),
                    'fecha': row['fecha'].strftime('%Y-%m-%d')
                }
                for _, row in top_gastos.iterrows()
            ]
        }
        
    except Exception as e:
        graficos['error'] = str(e)
    
    return graficos


def calcular_score_financiero(df, analisis):
    """Calcula un score de salud financiera (gamificación)"""
    score = 100
    detalles = []
    
    try:
        # Penalizar por gastos muy concentrados en una categoría
        for cat, datos in analisis.get('por_categoria', {}).items():
            if datos.get('porcentaje_total', 0) > 50:
                score -= 15
                detalles.append(f'-15: {cat} supera el 50% de gastos')
            elif datos.get('porcentaje_total', 0) > 40:
                score -= 10
                detalles.append(f'-10: {cat} supera el 40% de gastos')
        
        # Penalizar por muchos outliers
        outliers = len(analisis.get('outliers', []))
        if outliers > 5:
            score -= 10
            detalles.append(f'-10: Demasiados gastos atípicos ({outliers})')
        elif outliers > 2:
            score -= 5
            detalles.append(f'-5: Varios gastos atípicos ({outliers})')
        
        # Evaluar tendencia
        comparativa = analisis.get('comparativas', {}).get('mes_actual_vs_anterior', {})
        variacion = comparativa.get('variacion_porcentaje', 0)
        
        if variacion > 30:
            score -= 15
            detalles.append('-15: Aumento de gastos superior al 30%')
        elif variacion > 15:
            score -= 8
            detalles.append('-8: Aumento de gastos superior al 15%')
        elif variacion < -10:
            score += 10
            detalles.append('+10: Reducción de gastos superior al 10%')
        
        # Bonus por consistencia
        if len(df) > 20:
            score += 5
            detalles.append('+5: Buen historial de registros')
        
        # Limitar entre 0 y 100
        score = max(0, min(100, score))
        
        # Determinar nivel
        if score >= 80:
            nivel = 'EXCELENTE'
            emoji = '🌟'
            mensaje = '¡Excelente manejo financiero!'
        elif score >= 60:
            nivel = 'BUENO'
            emoji = '👍'
            mensaje = 'Buen control, con margen de mejora'
        elif score >= 40:
            nivel = 'REGULAR'
            emoji = '⚠️'
            mensaje = 'Hay áreas que necesitan atención'
        else:
            nivel = 'CRÍTICO'
            emoji = '🚨'
            mensaje = 'Requiere atención inmediata'
        
    except Exception as e:
        return {'score': 50, 'nivel': 'ERROR', 'mensaje': str(e)}
    
    return {
        'score': score,
        'nivel': nivel,
        'emoji': emoji,
        'mensaje': mensaje,
        'detalles': detalles
    }


# Endpoints adicionales separados para componentes específicos

@app.route('/api/v2/firebase/users/<usuario_id>/predicciones', methods=['GET'])
@token_required
def obtener_predicciones(usuario_id):
    """Obtiene solo las predicciones de gastos"""
    if not FIREBASE_AVAILABLE:
        return jsonify({'error': 'Firebase no disponible'}), 503
    
    try:
        gastos, error = obtener_gastos_firebase(usuario_id)
        if error:
            return jsonify({'error': error}), 500
        
        if not gastos or len(gastos) < 3:
            return jsonify({'error': 'Datos insuficientes'}), 400
        
        df = pd.DataFrame(gastos)
        df['fecha'] = df['fecha'].apply(procesar_fecha)
        df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0)
        
        return jsonify({
            'status': 'success',
            'usuario_id': usuario_id,
            'predicciones': generar_predicciones(df)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/firebase/users/<usuario_id>/analisis', methods=['GET'])
@token_required
def obtener_analisis(usuario_id):
    """Obtiene solo el análisis estadístico"""
    if not FIREBASE_AVAILABLE:
        return jsonify({'error': 'Firebase no disponible'}), 503
    
    try:
        gastos, error = obtener_gastos_firebase(usuario_id)
        if error:
            return jsonify({'error': error}), 500
        
        if not gastos or len(gastos) < 3:
            return jsonify({'error': 'Datos insuficientes'}), 400
        
        df = pd.DataFrame(gastos)
        df['fecha'] = df['fecha'].apply(procesar_fecha)
        df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0)
        df['mes'] = df['fecha'].dt.month
        df['año'] = df['fecha'].dt.year
        df['dia_semana'] = df['fecha'].dt.dayofweek

        # Filtros de periodo opcionales via query params
        period = request.args.get('period')
        value = request.args.get('value')
        filtro_aplicado = None

        def _filtrar(df_in, p, v):
            if not p or not v:
                return df_in, None
            p_norm = p.lower()
            p_norm = {'mes': 'month', 'año': 'year', 'trimestre': 'quarter'}.get(p_norm, p_norm)
            try:
                if p_norm == 'month':
                    # v: YYYY-MM
                    df_in['period_m'] = df_in['fecha'].dt.to_period('M').astype(str)
                    return df_in[df_in['period_m'] == v], {'period': p, 'value': v}
                elif p_norm == 'year':
                    yr = int(v)
                    return df_in[df_in['fecha'].dt.year == yr], {'period': p, 'value': v}
                elif p_norm == 'quarter':
                    # v: YYYY-Qn or Qn-YYYY
                    if '-' in v:
                        parts = v.split('-')
                        if parts[0].startswith('Q'):
                            q = int(parts[0][1:])
                            yr = int(parts[1])
                        else:
                            yr = int(parts[0])
                            q = int(parts[1][1:]) if parts[1].startswith('Q') else int(parts[1])
                    else:
                        yr, qstr = v.split('Q') if 'Q' in v else (v, '1')
                        yr = int(yr)
                        q = int(qstr)
                    mask = (df_in['fecha'].dt.year == yr) & (df_in['fecha'].dt.quarter == q)
                    return df_in[mask], {'period': p, 'value': f'{yr}-Q{q}'}
            except Exception:
                return df_in, None
            return df_in, None

        df, filtro_aplicado = _filtrar(df, period, value)
        
        return jsonify({
            'status': 'success',
            'usuario_id': usuario_id,
            'analisis': generar_analisis_estadistico(df),
            'filtro': filtro_aplicado
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/firebase/users/<usuario_id>/recomendaciones', methods=['GET'])
@token_required
def obtener_recomendaciones(usuario_id):
    """Obtiene solo las recomendaciones de ahorro"""
    if not FIREBASE_AVAILABLE:
        return jsonify({'error': 'Firebase no disponible'}), 503
    
    try:
        gastos, error = obtener_gastos_firebase(usuario_id)
        if error:
            return jsonify({'error': error}), 500
        
        if not gastos or len(gastos) < 3:
            return jsonify({'error': 'Datos insuficientes'}), 400
        
        df = pd.DataFrame(gastos)
        df['fecha'] = df['fecha'].apply(procesar_fecha)
        df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0)
        df['mes'] = df['fecha'].dt.month
        df['año'] = df['fecha'].dt.year
        df['dia_semana'] = df['fecha'].dt.dayofweek
        
        analisis = generar_analisis_estadistico(df)
        predicciones = generar_predicciones(df)
        budget_info, _ = obtener_budget_usuario(usuario_id)
        
        return jsonify({
            'status': 'success',
            'usuario_id': usuario_id,
            'recomendaciones': generar_recomendaciones(df, analisis, budget_info=budget_info, predicciones=predicciones)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/firebase/users/<usuario_id>/graficos', methods=['GET'])
@token_required
def obtener_graficos(usuario_id):
    """Obtiene solo los datos para gráficos"""
    if not FIREBASE_AVAILABLE:
        return jsonify({'error': 'Firebase no disponible'}), 503
    
    try:
        gastos, error = obtener_gastos_firebase(usuario_id)
        if error:
            return jsonify({'error': error}), 500
        
        if not gastos or len(gastos) < 3:
            return jsonify({'error': 'Datos insuficientes'}), 400
        
        df = pd.DataFrame(gastos)
        df['fecha'] = df['fecha'].apply(procesar_fecha)
        df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0)
        df['mes'] = df['fecha'].dt.month
        df['año'] = df['fecha'].dt.year
        df['dia_semana'] = df['fecha'].dt.dayofweek
        
        return jsonify({
            'status': 'success',
            'usuario_id': usuario_id,
            'graficos': preparar_datos_graficos(df)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/firebase/users/<usuario_id>/score', methods=['GET'])
@token_required
def obtener_score(usuario_id):
    """Obtiene el score financiero del usuario"""
    if not FIREBASE_AVAILABLE:
        return jsonify({'error': 'Firebase no disponible'}), 503
    
    try:
        gastos, error = obtener_gastos_firebase(usuario_id)
        if error:
            return jsonify({'error': error}), 500
        
        if not gastos or len(gastos) < 3:
            return jsonify({'error': 'Datos insuficientes'}), 400
        
        df = pd.DataFrame(gastos)
        df['fecha'] = df['fecha'].apply(procesar_fecha)
        df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0)
        df['mes'] = df['fecha'].dt.month
        df['año'] = df['fecha'].dt.year
        df['dia_semana'] = df['fecha'].dt.dayofweek
        
        analisis = generar_analisis_estadistico(df)
        score = calcular_score_financiero(df, analisis)
        
        return jsonify({
            'status': 'success',
            'usuario_id': usuario_id,
            'score_financiero': score
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# 📌 RUTAS ESPEJO IA BAJO /api/v2/firebase/users/{usuario_id}
# ============================================================

def _normalized_expenses_for_user(usuario_id):
    """Carga gastos desde Firebase y normaliza al esquema de 'expenses'."""
    expenses, err = _expenses_from_firebase_for_user(usuario_id)
    if not expenses:
        return None, (err or 'Sin gastos para usuario')
    return expenses, None

# ----- Predicción -----
@app.route('/api/v2/firebase/users/<usuario_id>/predict-category', methods=['GET'])
@token_required
def predict_category_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': predict_by_category(df)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/firebase/users/<usuario_id>/predict-monthly', methods=['GET'])
@token_required
def predict_monthly_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': predict_monthly(df)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/firebase/users/<usuario_id>/detect-anomalies', methods=['GET'])
@token_required
def detect_anomalies_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': detect_anomalies(df)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/firebase/users/<usuario_id>/compare-models', methods=['GET'])
@token_required
def compare_models_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': compare_models(df)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/firebase/users/<usuario_id>/seasonality', methods=['GET'])
@token_required
def seasonality_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': analyze_seasonality(df)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/firebase/users/<usuario_id>/analysis-complete', methods=['GET'])
@token_required
def analysis_complete_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        result = {
            'prediccion_categoria': predict_by_category(df),
            'prediccion_mensual': predict_monthly(df),
            'anomalias': detect_anomalies(df),
            'comparacion_modelos': compare_models(df),
            'estacionalidad': analyze_seasonality(df),
            'timestamp': datetime.now().isoformat()
        }
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ----- Estadística -----
@app.route('/api/v2/firebase/users/<usuario_id>/stat/correlations', methods=['GET'])
@token_required
def correlations_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': analyze_correlations(df)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/firebase/users/<usuario_id>/stat/temporal-comparison', methods=['GET'])
@token_required
def temporal_comparison_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': analyze_temporal_comparison(df)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/firebase/users/<usuario_id>/stat/clustering', methods=['GET'])
@token_required
def clustering_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        n_clusters = int(request.args.get('n_clusters', 3))
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': perform_clustering(df, n_clusters)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/firebase/users/<usuario_id>/stat/trends', methods=['GET'])
@token_required
def trends_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': detect_trends(df)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/firebase/users/<usuario_id>/stat/outliers', methods=['GET'])
@token_required
def outliers_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': detect_outliers_iqr(df)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/firebase/users/<usuario_id>/stat/complete', methods=['GET'])
@token_required
def stat_complete_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        result = {
            'correlaciones': analyze_correlations(df),
            'comparacion_temporal': analyze_temporal_comparison(df),
            'clustering': perform_clustering(df),
            'tendencias': detect_trends(df),
            'outliers': detect_outliers_iqr(df),
            'timestamp': datetime.now().isoformat()
        }
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ----- Ahorro -----
@app.route('/api/v2/firebase/users/<usuario_id>/savings/goals', methods=['GET'])
@token_required
def savings_goals_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        goal_name = request.args.get('goal_name', 'Meta')
        target_amount = float(request.args.get('target_amount', 1000))
        months = int(request.args.get('months', 12))
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': calculate_savings_goals(df, goal_name, target_amount, months)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/firebase/users/<usuario_id>/savings/tips', methods=['GET'])
@token_required
def savings_tips_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': generate_personalized_tips(df)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/firebase/users/<usuario_id>/savings/budget-alerts', methods=['GET'])
@token_required
def savings_budget_alerts_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        monthly_budget = float(request.args.get('monthly_budget', 3000))
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': generate_budget_alerts(df, monthly_budget)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/firebase/users/<usuario_id>/savings/health-score', methods=['GET'])
@token_required
def savings_health_score_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        monthly_budget = float(request.args.get('monthly_budget', 3000))
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': calculate_financial_health_score(df, monthly_budget)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/firebase/users/<usuario_id>/savings/weekly-report', methods=['GET'])
@token_required
def savings_weekly_report_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': generate_weekly_report(df)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/firebase/users/<usuario_id>/savings/complete', methods=['GET'])
@token_required
def savings_complete_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        goal_name = request.args.get('goal_name', 'Meta general')
        target_amount = float(request.args.get('target_amount', 5000))
        months = int(request.args.get('months', 12))
        monthly_budget = float(request.args.get('monthly_budget', 3000))
        result = {
            'metas_ahorro': calculate_savings_goals(df, goal_name, target_amount, months),
            'tips_personalizados': generate_personalized_tips(df),
            'alertas_presupuesto': generate_budget_alerts(df, monthly_budget),
            'salud_financiera': calculate_financial_health_score(df, monthly_budget),
            'reporte_semanal': generate_weekly_report(df),
            'timestamp': datetime.now().isoformat()
        }
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ----- Gráficos -----
@app.route('/api/v2/firebase/users/<usuario_id>/charts/heatmap', methods=['GET'])
@token_required
def charts_heatmap_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': generate_heatmap(df)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/firebase/users/<usuario_id>/charts/sankey', methods=['GET'])
@token_required
def charts_sankey_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': generate_sankey_diagram(df)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/firebase/users/<usuario_id>/charts/dashboard', methods=['GET'])
@token_required
def charts_dashboard_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': generate_interactive_dashboard(df)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/firebase/users/<usuario_id>/charts/comparison', methods=['GET'])
@token_required
def charts_comparison_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': generate_month_comparison_chart(df)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/firebase/users/<usuario_id>/charts/export', methods=['GET'])
@token_required
def charts_export_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        output_format = request.args.get('format', 'json')
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': export_graphics_as_image(df, output_format)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v2/firebase/users/<usuario_id>/charts/complete', methods=['GET'])
@token_required
def charts_complete_user(usuario_id):
    try:
        expenses, err = _normalized_expenses_for_user(usuario_id)
        if not expenses:
            return jsonify({'error': 'No hay gastos en Firebase', 'detalle': err}), 400
        df = prepare_dataframe(expenses)
        result = {
            'heatmap': generate_heatmap(df),
            'sankey': generate_sankey_diagram(df),
            'dashboard': generate_interactive_dashboard(df),
            'comparacion_meses': generate_month_comparison_chart(df),
            'exportacion': export_graphics_as_image(df, 'json'),
            'timestamp': datetime.now().isoformat()
        }
        return jsonify({'status': 'success', 'usuario_id': usuario_id, 'data': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    print("\n" + "="*80)
    print("🚀 API MEJORADA CON 20 CARACTERÍSTICAS DE IA")
    print("="*80)
    print(f"✅ Servidor corriendo en: http://0.0.0.0:{port}")
    print(f"📍 Puerto: {port}")
    print(f"🔧 Debug: {debug}")
    print("="*80 + "\n")
    
    app.run(debug=debug, host='0.0.0.0', port=port, use_reloader=False)