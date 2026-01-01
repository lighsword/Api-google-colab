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
from flask import Flask, request, jsonify
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

warnings.filterwarnings('ignore')

# Cargar variables de entorno
load_dotenv()

# ============================================================
# 🔥 CONFIGURACIÓN DE FIREBASE
# ============================================================
FIREBASE_AVAILABLE = False
db = None

try:
    # Opción 1: Usar archivo JSON si existe localmente
    if os.path.exists('gestor-financiero-28ac2-firebase-adminsdk-fbsvc-6efa11cbf8.json'):
        cred = credentials.Certificate('gestor-financiero-28ac2-firebase-adminsdk-fbsvc-6efa11cbf8.json')
        # Inicializar con databaseURL para Realtime Database o sin él para Firestore
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://gestor-financiero-28ac2.firebaseio.com'
        })
        # Usar Firestore
        db = firestore.client()
        FIREBASE_AVAILABLE = True
        print("✅ Firebase conectado correctamente (desde archivo JSON)")
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
            'databaseURL': f"https://{os.getenv('FIREBASE_PROJECT_ID')}.firebaseio.com"
        })
        db = firestore.client()
        FIREBASE_AVAILABLE = True
        print("✅ Firebase conectado correctamente (desde variables de entorno)")
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
    """Verifica la validez del JWT token"""
    try:
        if token not in active_tokens:
            return False
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return True
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
        
        if not verify_token(token):
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
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
    
    return {
        'diarias': predictions,
        'total_mes': round(df_pred['prediccion'].sum(), 2),
        'promedio_diario': round(avg_daily, 2),
        'resumen_semanal': weekly.to_dict()
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
                {'nombre': 'Pie Categorías', 'base64': fig1.to_image(format='png')},
                {'nombre': 'Series Temporal', 'base64': fig2.to_image(format='png')},
                {'nombre': 'Barras Categorías', 'base64': fig3.to_image(format='png')},
                {'nombre': 'Box Plot', 'base64': fig4.to_image(format='png')}
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
        
        is_valid = verify_token(token)
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

@app.route('/api/v2/firebase/usuarios', methods=['GET'])
def get_usuarios_firebase():
    """Obtiene todos los usuarios registrados en Firebase"""
    if not FIREBASE_AVAILABLE:
        return jsonify({'error': 'Firebase no disponible'}), 503
    
    @app.route('/api/v2/firebase/debug', methods=['GET'])
    def firebase_debug():
        """Diagnóstico de conexión Firestore: proyecto y colecciones"""
        try:
            info = {
                'firebase_available': bool(FIREBASE_AVAILABLE),
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
            return jsonify({'status': 'success', 'data': info}), 200
        except Exception as e:
            return jsonify({'error': f'Debug Firestore: {str(e)}'}), 500
    try:
        usuarios = []
        docs = db.collection('gestofin').collection('users').stream()
        
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
    """Obtiene un usuario específico por ID"""
    if not FIREBASE_AVAILABLE:
        return jsonify({'error': 'Firebase no disponible'}), 503
    
    try:
        # Estructura correcta: gestofin (colección) → {usuario_id} (documento) → budget (subcolección) → current (documento)
        usuario = {'id': usuario_id}
        try:
            budget_doc = db.collection('gestofin').document(usuario_id).collection('budget').document('current').get()
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
    """Obtiene todos los gastos de un usuario desde Firebase"""
    if not FIREBASE_AVAILABLE:
        return jsonify({'error': 'Firebase no disponible'}), 503
    
    try:
        gastos = []
        path_used = None
        # Intento 1: gestofin/{uid}/gastos
        try:
            docs = db.collection('gestofin').document(usuario_id).collection('gastos').stream()
            path_used = f'gestofin/{usuario_id}/gastos'
            for doc in docs:
                gasto = doc.to_dict()
                gasto['id'] = doc.id
                gastos.append(gasto)
        except Exception:
            pass
        
        # Intento 2 (fallback): users/{uid}/gastos
        if not gastos:
            try:
                docs = db.collection('users').document(usuario_id).collection('gastos').stream()
                path_used = f'users/{usuario_id}/gastos'
                for doc in docs:
                    gasto = doc.to_dict()
                    gasto['id'] = doc.id
                    gastos.append(gasto)
            except Exception:
                pass
        
        return jsonify({
            'status': 'success',
            'usuario_id': usuario_id,
            'total_gastos': len(gastos),
            'path_usado': path_used,
            'data': gastos
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
        path_used = None
        # Intento 1: gestofin/{uid}/gastos
        try:
            docs = db.collection('gestofin').document(usuario_id).collection('gastos').stream()
            path_used = f'gestofin/{usuario_id}/gastos'
            for doc in docs:
                gasto = doc.to_dict()
                gasto['id'] = doc.id
                gastos.append(gasto)
        except Exception:
            pass
        
        # Intento 2 (fallback): users/{uid}/gastos
        if not gastos:
            try:
                docs = db.collection('users').document(usuario_id).collection('gastos').stream()
                path_used = f'users/{usuario_id}/gastos'
                for doc in docs:
                    gasto = doc.to_dict()
                    gasto['id'] = doc.id
                    gastos.append(gasto)
            except Exception:
                pass
        
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


@app.route('/api/v2/firebase/users/<usuario_id>/gastos', methods=['POST'])
@token_required
def crear_gasto_firebase(usuario_id):
    """Crea un nuevo gasto en Firebase para un usuario"""
    if not FIREBASE_AVAILABLE:
        return jsonify({'error': 'Firebase no disponible'}), 503
    
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        cantidad = data.get('cantidad') or data.get('monto')
        if not cantidad or not data.get('categoria'):
            return jsonify({'error': 'Faltan campos requeridos: cantidad, categoria'}), 400
        
        gasto = {
            'cantidad': float(cantidad),
            'categoria': data.get('categoria'),
            'descripcion': data.get('descripcion', ''),
            'fecha': data.get('fecha', datetime.now().isoformat()),
            'createdAt': datetime.now().isoformat()
        }
        
        # Guardar en Firebase: intentar en gestofin/{uid}/gastos, si falla, en users/{uid}/gastos
        try:
            doc_ref = db.collection('gestofin').document(usuario_id).collection('gastos').document()
            doc_ref.set(gasto)
            path_used = f'gestofin/{usuario_id}/gastos/{doc_ref.id}'
        except Exception:
            doc_ref = db.collection('users').document(usuario_id).collection('gastos').document()
            doc_ref.set(gasto)
            path_used = f'users/{usuario_id}/gastos/{doc_ref.id}'
        
        return jsonify({
            'status': 'success',
            'mensaje': 'Gasto creado correctamente',
            'gasto_id': doc_ref.id,
            'path_usado': path_used,
            'data': gasto
        }), 201
    except Exception as e:
        return jsonify({'error': f'Error creando gasto: {str(e)}'}), 500


@app.route('/api/v2/predict-category', methods=['POST'])
@token_required
def predict_category():
    """Predicción separada por categoría (30 días). REQUIERE TOKEN."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
        df = prepare_dataframe(expenses)
        predictions = predict_by_category(df, days=30)
        
        return jsonify({
            'status': 'success',
            'data': predictions
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/predict-monthly', methods=['POST'])
def predict_monthly_endpoint():
    """Predicción mensual con 30 días."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
        df = prepare_dataframe(expenses)
        predictions = predict_monthly(df, days=30)
        
        return jsonify({
            'status': 'success',
            'data': predictions
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/detect-anomalies', methods=['POST'])
def detect_anomalies_endpoint():
    """Detección automática de anomalías."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
        df = prepare_dataframe(expenses)
        anomalies = detect_anomalies(df)
        
        return jsonify({
            'status': 'success',
            'data': anomalies
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/compare-models', methods=['POST'])
def compare_models_endpoint():
    """Comparación de múltiples modelos ML."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
        df = prepare_dataframe(expenses)
        comparison = compare_models(df)
        
        return jsonify({
            'status': 'success',
            'data': comparison
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/seasonality', methods=['POST'])
def seasonality_endpoint():
    """Análisis de estacionalidad."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
        df = prepare_dataframe(expenses)
        seasonality = analyze_seasonality(df)
        
        return jsonify({
            'status': 'success',
            'data': seasonality
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/analysis-complete', methods=['POST'])
def analysis_complete():
    """Análisis completo con las 5 mejoras."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
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


@app.route('/api/v2/stat/correlations', methods=['POST'])
def correlations_endpoint():
    """Análisis de correlaciones entre categorías."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
        df = prepare_dataframe(expenses)
        correlations = analyze_correlations(df)
        
        return jsonify({
            'status': 'success',
            'data': correlations
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/stat/temporal-comparison', methods=['POST'])
def temporal_comparison_endpoint():
    """Comparación mes actual vs anterior."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
        df = prepare_dataframe(expenses)
        comparison = analyze_temporal_comparison(df)
        
        return jsonify({
            'status': 'success',
            'data': comparison
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/stat/clustering', methods=['POST'])
def clustering_endpoint():
    """Agrupamiento automático de gastos similares."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        n_clusters = data.get('n_clusters', 3)
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
        df = prepare_dataframe(expenses)
        clusters = perform_clustering(df, n_clusters=n_clusters)
        
        return jsonify({
            'status': 'success',
            'data': clusters
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/stat/trends', methods=['POST'])
def trends_endpoint():
    """Detección de tendencias en gastos."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
        df = prepare_dataframe(expenses)
        trends = detect_trends(df)
        
        return jsonify({
            'status': 'success',
            'data': trends
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/stat/outliers', methods=['POST'])
def outliers_endpoint():
    """Detección de gastos atípicos con IQR y Z-Score."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
        df = prepare_dataframe(expenses)
        outliers = detect_outliers_iqr(df)
        
        return jsonify({
            'status': 'success',
            'data': outliers
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/stat/complete', methods=['POST'])
def statistical_analysis_complete():
    """Análisis estadístico completo (todas las 5 mejoras)."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
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


@app.route('/api/v2/savings/goals', methods=['POST'])
def savings_goals_endpoint():
    """Calcular metas de ahorro personalizadas."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        goal_name = data.get('goal_name', 'Meta')
        target_amount = data.get('target_amount', 1000)
        months = data.get('months', 12)
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
        df = prepare_dataframe(expenses)
        goals = calculate_savings_goals(df, goal_name, target_amount, months)
        
        return jsonify({
            'status': 'success',
            'data': goals
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/savings/tips', methods=['POST'])
def personalized_tips_endpoint():
    """Generar tips personalizados de ahorro."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
        df = prepare_dataframe(expenses)
        tips = generate_personalized_tips(df)
        
        return jsonify({
            'status': 'success',
            'data': tips
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/savings/budget-alerts', methods=['POST'])
def budget_alerts_endpoint():
    """Generar alertas de presupuesto."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        monthly_budget = data.get('monthly_budget', 3000)
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
        df = prepare_dataframe(expenses)
        alerts = generate_budget_alerts(df, monthly_budget)
        
        return jsonify({
            'status': 'success',
            'data': alerts
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/savings/health-score', methods=['POST'])
def health_score_endpoint():
    """Calcular puntuación de salud financiera."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        monthly_budget = data.get('monthly_budget', 3000)
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
        df = prepare_dataframe(expenses)
        score = calculate_financial_health_score(df, monthly_budget)
        
        return jsonify({
            'status': 'success',
            'data': score
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/savings/weekly-report', methods=['POST'])
def weekly_report_endpoint():
    """Generar resumen semanal para reportes automáticos."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
        df = prepare_dataframe(expenses)
        report = generate_weekly_report(df)
        
        return jsonify({
            'status': 'success',
            'data': report
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/savings/complete', methods=['POST'])
def savings_analysis_complete():
    """Análisis completo de recomendaciones (todas las 5 mejoras)."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        goal_name = data.get('goal_name', 'Meta general')
        target_amount = data.get('target_amount', 5000)
        months = data.get('months', 12)
        monthly_budget = data.get('monthly_budget', 3000)
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
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


@app.route('/api/v2/charts/heatmap', methods=['POST'])
def heatmap_endpoint():
    """Generar calendario de calor de gastos."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
        df = prepare_dataframe(expenses)
        heatmap = generate_heatmap(df)
        
        return jsonify({
            'status': 'success',
            'data': heatmap
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/charts/sankey', methods=['POST'])
def sankey_endpoint():
    """Generar diagrama Sankey de flujo de dinero."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
        df = prepare_dataframe(expenses)
        sankey = generate_sankey_diagram(df)
        
        return jsonify({
            'status': 'success',
            'data': sankey
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/charts/dashboard', methods=['POST'])
def dashboard_endpoint():
    """Generar dashboard interactivo."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
        df = prepare_dataframe(expenses)
        dashboard = generate_interactive_dashboard(df)
        
        return jsonify({
            'status': 'success',
            'data': dashboard
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/charts/comparison', methods=['POST'])
def comparison_endpoint():
    """Generar gráficos comparativos mes vs mes."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
        df = prepare_dataframe(expenses)
        comparison = generate_month_comparison_chart(df)
        
        return jsonify({
            'status': 'success',
            'data': comparison
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/charts/export', methods=['POST'])
def export_graphics_endpoint():
    """Exportar gráficos como imágenes (JSON o BASE64)."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        output_format = data.get('format', 'json')  # 'json' o 'base64'
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
        df = prepare_dataframe(expenses)
        exported = export_graphics_as_image(df, output_format)
        
        return jsonify({
            'status': 'success',
            'data': exported
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v2/charts/complete', methods=['POST'])
def charts_complete():
    """Generar todos los gráficos disponibles."""
    try:
        data = request.get_json()
        expenses = data.get('expenses', [])
        
        if not expenses or not validate_expense_data(expenses):
            return jsonify({'error': 'Datos inválidos'}), 400
        
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