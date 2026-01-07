# CORS Configuration for Firebase & API

# Orígenes permitidos de Firebase
FIREBASE_HOSTING_DOMAINS = [
    "https://gestor-financiero-28ac2.firebaseapp.com",    # Tu Firebase Hosting específico
    "https://gestor-financiero-28ac2.web.app",             # Firebase Web App
]

# Dominios permitidos con patrones (desarrollo + producción)
ALLOWED_ORIGINS = [
    # Firebase Hosting (todos los proyectos)
    r"https?://.*\.firebaseapp\.com",
    r"https?://.*\.web\.app",
    
    # Firebase Console & Tools
    r"https?://.*\.firebase\.google\.com",
    r"https?://.*\.firebaseui\.net",
    
    # Desarrollo local
    "http://localhost:3000",      # React/Next.js típico
    "http://localhost:5000",      # API local
    "http://localhost:8080",      # Otros dev servers
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5000",
    "http://127.0.0.1:8080",
    
    # Producción (reemplaza con tu dominio)
    "https://tu-app.vercel.app",   # Si usas Vercel
    "https://tu-dominio.com",      # Tu dominio personalizado
]

# Headers permitidos
ALLOWED_HEADERS = [
    'Content-Type',
    'Authorization',
    'X-API-Key',
    'Accept',
    'Origin',
    'X-Requested-With',
    'Access-Control-Allow-Credentials',
    'User-Agent',
]

# Métodos HTTP permitidos
ALLOWED_METHODS = [
    'GET',
    'POST',
    'PUT',
    'DELETE',
    'OPTIONS',
    'PATCH',
    'HEAD'
]

# Headers expuestos al cliente
EXPOSE_HEADERS = [
    'Content-Type',
    'X-Total-Count',
    'X-Page-Count',
    'Authorization'
]

# Configuración CORS por defecto
CORS_CONFIG = {
    "origins": ALLOWED_ORIGINS,
    "allow_headers": ALLOWED_HEADERS,
    "methods": ALLOWED_METHODS,
    "supports_credentials": True,
    "max_age": 3600,
    "expose_headers": EXPOSE_HEADERS
}
