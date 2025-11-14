@echo off
REM =============================================================================
REM CONTRACTIA AI - Script de Instalación Automática (Windows)
REM =============================================================================
REM Este script automatiza la instalación local de CONTRACTIA AI
REM Uso: install.bat
REM =============================================================================

echo ================================================
echo   CONTRACTIA AI - Instalacion Automatica
echo ================================================
echo.

REM 1. Verificar Python
echo Paso 1/6: Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no encontrado. Por favor instala Python 3.10+
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo OK: Python encontrado - Version %PYTHON_VERSION%

REM 2. Crear entorno virtual
echo.
echo Paso 2/6: Creando entorno virtual...
if exist venv (
    echo Eliminando entorno virtual existente...
    rmdir /s /q venv
)

python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)
echo OK: Entorno virtual creado

REM 3. Activar entorno virtual
echo.
echo Paso 3/6: Activando entorno virtual...
call venv\Scripts\activate.bat
echo OK: Entorno virtual activado

REM 4. Actualizar pip
echo.
echo Paso 4/6: Actualizando pip...
python -m pip install --upgrade pip >nul 2>&1
echo OK: pip actualizado

REM 5. Instalar dependencias
echo.
echo Paso 5/6: Instalando dependencias...
echo Esto puede tomar 2-3 minutos...

pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Error instalando dependencias
    pause
    exit /b 1
)
echo OK: Dependencias instaladas correctamente

REM 6. Verificar credenciales GCP
echo.
echo Paso 6/6: Verificando credenciales de GCP...

if not defined GOOGLE_APPLICATION_CREDENTIALS (
    echo INFO: Variable GOOGLE_APPLICATION_CREDENTIALS no configurada
    echo.
    echo Para configurar las credenciales de GCP:
    echo 1. Descarga tu archivo JSON de Service Account
    echo 2. Guardalo en este directorio ^(ej: gcp-credentials.json^)
    echo 3. Ejecuta: set GOOGLE_APPLICATION_CREDENTIALS=%cd%\gcp-credentials.json
    echo.
    
    REM Buscar archivos JSON
    dir /b *.json >nul 2>&1
    if %errorlevel% equ 0 (
        echo INFO: Archivos JSON encontrados en el directorio:
        dir /b *.json
        echo.
        set /p USE_JSON="Deseas configurar uno de estos archivos? (s/n): "
        if /i "%USE_JSON%"=="s" (
            set /p JSON_FILE="Ingresa el nombre del archivo JSON: "
            if exist !JSON_FILE! (
                set GOOGLE_APPLICATION_CREDENTIALS=%cd%\!JSON_FILE!
                echo OK: Credenciales configuradas: !JSON_FILE!
                echo set GOOGLE_APPLICATION_CREDENTIALS=%cd%\!JSON_FILE! >> venv\Scripts\activate.bat
            )
        )
    )
) else (
    echo OK: Credenciales ya configuradas: %GOOGLE_APPLICATION_CREDENTIALS%
)

REM Mensaje final
echo.
echo ================================================
echo   Instalacion Completada
echo ================================================
echo.
echo OK: CONTRACTIA AI esta listo para usar
echo.
echo Para ejecutar la aplicacion:
echo   1. Activa el entorno virtual: venv\Scripts\activate
echo   2. Ejecuta: streamlit run app.py
echo   3. Abre tu navegador en: http://localhost:8501
echo.

if not defined GOOGLE_APPLICATION_CREDENTIALS (
    echo INFO: Recuerda configurar las credenciales de GCP antes de ejecutar
)

echo Para mas informacion, consulta:
echo   - QUICKSTART.md - Guia de inicio rapido
echo   - README.md - Documentacion completa
echo.
echo OK: Exito! 
echo.
pause
