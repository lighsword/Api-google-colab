@echo off
REM Script para ejecutar la API Gestor Financiero
REM Este archivo activa el entorno virtual y ejecuta la API

echo.
echo ================================================================================
echo 🚀 INICIANDO GESTOR FINANCIERO API
echo ================================================================================
echo.

REM Navegar al directorio del proyecto
cd /d "%~dp0"

REM Verificar si el entorno virtual existe
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Entorno virtual no encontrado
    echo.
    echo Creando entorno virtual...
    python -m venv .venv
    echo ✅ Entorno virtual creado
    echo.
    echo Instalando dependencias...
    .venv\Scripts\pip install -r requirements.txt
    echo ✅ Dependencias instaladas
    echo.
)

REM Activar el entorno virtual
echo ⏳ Activando entorno virtual...
call .venv\Scripts\activate.bat

REM Ejecutar la API
echo.
echo ✅ Ejecutando API...
echo.
echo 📍 Accede a: http://localhost:5000
echo 📖 Swagger UI: http://localhost:5000/docs
echo.
echo ================================================================================
echo.

python API_MEJORADA.py

pause
