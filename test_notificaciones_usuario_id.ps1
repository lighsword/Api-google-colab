# Ejemplos de PowerShell para probar los endpoints de notificaciones
# Ejecutar en: Windows PowerShell o PowerShell 7+

# ============================================================
# 1. OBTENER JWT TOKEN
# ============================================================
Write-Host "1️⃣  Obteniendo JWT Token..." -ForegroundColor Cyan

$tokenResponse = Invoke-RestMethod -Uri "https://api-google-colab.onrender.com/api/v2/auth/token" `
  -Method POST `
  -Headers @{"Content-Type" = "application/json"} `
  -Body @{
    usuario = "test@example.com"
    contrasena = "password123"
  } | ConvertTo-Json

Write-Host "Respuesta:"
$tokenResponse | ConvertFrom-Json | Format-Table

# Extraer token
$token = ($tokenResponse | ConvertFrom-Json).token
$usuarioId = ($tokenResponse | ConvertFrom-Json).usuario_id

Write-Host ""
Write-Host "✅ JWT_TOKEN: $token" -ForegroundColor Green
Write-Host "✅ USUARIO_ID: $usuarioId" -ForegroundColor Green
Write-Host ""

# ============================================================
# 2. REGISTRAR DISPOSITIVO
# ============================================================
Write-Host "2️⃣  Registrando dispositivo..." -ForegroundColor Cyan

$registerResponse = Invoke-RestMethod -Uri "https://api-google-colab.onrender.com/api/v2/notifications/register-device" `
  -Method POST `
  -Headers @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
  } `
  -Body @{
    dispositivo_token = "e7sJ2xK9nP3lQ5mR8vT2xZ1cA4dE6fG9hI0jK3lM5n"
    dispositivo_info = @{
      tipo = "windows"
      modelo = "Surface Pro 8"
      os = "Windows 11"
    }
  } | ConvertTo-Json

$registerResponse | ConvertFrom-Json | Format-List
Write-Host ""

# ============================================================
# 3. ENVIAR NOTIFICACIÓN AL USUARIO_ID ✅ (RECOMENDADO)
# ============================================================
Write-Host "3️⃣  Enviando notificación a usuario_id (MÉTODO RECOMENDADO)..." -ForegroundColor Cyan

$notificationBody = @{
  usuario_id = $usuarioId
  strTitle = "Gasto Detectado"
  strMessage = "Detectamos un gasto de $100 en Comida"
  mapData = @{
    categoria = "Comida"
    monto = "100"
    tipo_alerta = "gasto_detectado"
    id_transaccion = "txn_12345"
  }
} | ConvertTo-Json

$sendResponse = Invoke-RestMethod -Uri "https://api-google-colab.onrender.com/api/Firebase/sendnotificacion-usuario" `
  -Method POST `
  -Headers @{"Content-Type" = "application/json"} `
  -Body $notificationBody

$sendResponse | Format-List
Write-Host ""
Write-Host "✅ Notificación enviada a $($sendResponse.tokens_enviados) dispositivo(s)" -ForegroundColor Green
Write-Host ""

# ============================================================
# 4. ENVIAR NOTIFICACIÓN CON TOKEN DIRECTO (Antiguo método)
# ============================================================
Write-Host "4️⃣  Enviando con token directo (método antiguo)..." -ForegroundColor Cyan

$directTokenBody = @{
  strToken = "e7sJ2xK9nP3lQ5mR8vT2xZ1cA4dE6fG9hI0jK3lM5n"
  strTitle = "Prueba de Notificación"
  strMessage = "Esta es una prueba"
  mapData = @{
    test = "true"
  }
} | ConvertTo-Json

try {
  $directResponse = Invoke-RestMethod -Uri "https://api-google-colab.onrender.com/api/Firebase/sendnotificacion" `
    -Method POST `
    -Headers @{"Content-Type" = "application/json"} `
    -Body $directTokenBody
  
  $directResponse | Format-List
} catch {
  Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# ============================================================
# 5. VER HISTORIAL DE NOTIFICACIONES
# ============================================================
Write-Host "5️⃣  Obteniendo historial de notificaciones..." -ForegroundColor Cyan

try {
  $historyResponse = Invoke-RestMethod -Uri "https://api-google-colab.onrender.com/api/v2/notifications/history" `
    -Method GET `
    -Headers @{
      "Authorization" = "Bearer $token"
    }
  
  $historyResponse | Format-List
  
  if ($historyResponse.notificaciones.Count -gt 0) {
    Write-Host "Total de notificaciones: $($historyResponse.notificaciones.Count)" -ForegroundColor Green
    $historyResponse.notificaciones | Format-Table
  }
} catch {
  Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "✅ Pruebas completadas" -ForegroundColor Green

# ============================================================
# 6. FUNCIÓN AUXILIAR: Enviar notificación rápidamente
# ============================================================
function Send-Notification {
  param(
    [string]$UsuarioId,
    [string]$Titulo,
    [string]$Mensaje,
    [hashtable]$Datos = @{}
  )
  
  $body = @{
    usuario_id = $UsuarioId
    strTitle = $Titulo
    strMessage = $Mensaje
    mapData = $Datos
  } | ConvertTo-Json
  
  Invoke-RestMethod -Uri "https://api-google-colab.onrender.com/api/Firebase/sendnotificacion-usuario" `
    -Method POST `
    -Headers @{"Content-Type" = "application/json"} `
    -Body $body
}

# Ejemplo de uso:
# Send-Notification -UsuarioId "7niAh4AIH4dyNDiXnAb86jiZVEj2" `
#   -Titulo "Nuevo gasto" `
#   -Mensaje "Se registró un nuevo gasto" `
#   -Datos @{"monto"="50"; "categoria"="Transporte"}
