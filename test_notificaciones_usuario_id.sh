#!/bin/bash
# Ejemplos de cURL para probar los endpoints de notificaciones

# ============================================================
# 1. OBTENER JWT TOKEN
# ============================================================
echo "1️⃣  Obteniendo JWT Token..."
TOKEN_RESPONSE=$(curl -X POST https://api-google-colab.onrender.com/api/v2/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "test@example.com",
    "contrasena": "password123"
  }')

echo "Respuesta:"
echo "$TOKEN_RESPONSE" | jq '.'

# Extraer el token
JWT_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.token')
USUARIO_ID=$(echo "$TOKEN_RESPONSE" | jq -r '.usuario_id')

echo ""
echo "✅ JWT_TOKEN: $JWT_TOKEN"
echo "✅ USUARIO_ID: $USUARIO_ID"
echo ""

# ============================================================
# 2. REGISTRAR DISPOSITIVO
# ============================================================
echo "2️⃣  Registrando dispositivo..."
curl -X POST https://api-google-colab.onrender.com/api/v2/notifications/register-device \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dispositivo_token": "e7sJ2xK9nP3lQ5mR8vT2xZ1cA4dE6fG9hI0jK3lM5n",
    "dispositivo_info": {
      "tipo": "android",
      "modelo": "Pixel 6",
      "os": "Android 13"
    }
  }' | jq '.'

echo ""

# ============================================================
# 3. ENVIAR NOTIFICACIÓN AL USUARIO_ID ✅ (RECOMENDADO)
# ============================================================
echo "3️⃣  Enviando notificación a usuario_id (MÉTODO RECOMENDADO)..."
curl -X POST https://api-google-colab.onrender.com/api/Firebase/sendnotificacion-usuario \
  -H "Content-Type: application/json" \
  -d "{
    \"usuario_id\": \"$USUARIO_ID\",
    \"strTitle\": \"Gasto Detectado\",
    \"strMessage\": \"Detectamos un gasto de \$100 en Comida\",
    \"mapData\": {
      \"categoria\": \"Comida\",
      \"monto\": \"100\",
      \"tipo_alerta\": \"gasto_detectado\",
      \"id_transaccion\": \"txn_12345\"
    }
  }" | jq '.'

echo ""

# ============================================================
# 4. ENVIAR NOTIFICACIÓN CON TOKEN DIRECTO (Antiguo método)
# ============================================================
echo "4️⃣  Enviando con token directo (método antiguo)..."
curl -X POST https://api-google-colab.onrender.com/api/Firebase/sendnotificacion \
  -H "Content-Type: application/json" \
  -d '{
    "strToken": "e7sJ2xK9nP3lQ5mR8vT2xZ1cA4dE6fG9hI0jK3lM5n",
    "strTitle": "Prueba de Notificación",
    "strMessage": "Esta es una prueba",
    "mapData": {
      "test": "true"
    }
  }' | jq '.'

echo ""

# ============================================================
# 5. VER HISTORIAL DE NOTIFICACIONES
# ============================================================
echo "5️⃣  Obteniendo historial de notificaciones..."
curl -X GET https://api-google-colab.onrender.com/api/v2/notifications/history \
  -H "Authorization: Bearer $JWT_TOKEN" | jq '.'

echo ""
echo "✅ Pruebas completadas"
