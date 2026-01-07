#!/usr/bin/env powershell
# Script para ejecutar la API Gestor Financiero con PowerShell

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "🚀 INICIANDO GESTOR FINANCIERO API" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Cambiar al directorio del script
Set-Location $PSScriptRoot

# Verificar si el entorno virtual existe
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "❌ Entorno virtual no encontrado" -ForegroundColor Red
    Write-Host ""
    Write-Host "Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "✅ Entorno virtual creado" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Instalando dependencias..." -ForegroundColor Yellow
    & ".\.venv\Scripts\pip.exe" install -r requirements.txt
    Write-Host "✅ Dependencias instaladas" -ForegroundColor Green
    Write-Host ""
}

# Activar el entorno virtual
Write-Host "⏳ Activando entorno virtual..." -ForegroundColor Yellow

& ".\.venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "✅ Ejecutando API..." -ForegroundColor Green
Write-Host ""
Write-Host "📍 Accede a: http://localhost:5000" -ForegroundColor Cyan
Write-Host "📖 Swagger UI: http://localhost:5000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

python API_MEJORADA.py

Write-Host ""
Write-Host "API finalizada" -ForegroundColor Yellow
pause
