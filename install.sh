#!/bin/bash

# =============================================================================
# CONTRACTIA AI - Script de Instalación Automática
# =============================================================================
# Este script automatiza la instalación local de CONTRACTIA AI
# Uso: bash install.sh
# =============================================================================

set -e  # Salir si hay algún error

echo "================================================"
echo "  🚀 CONTRACTIA AI - Instalación Automática"
echo "================================================"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# 1. Verificar Python
echo "Paso 1/6: Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_success "Python encontrado: $(python3 --version)"
    
    if (( $(echo "$PYTHON_VERSION >= 3.10" | bc -l) )); then
        print_success "Versión de Python válida (>= 3.10)"
    else
        print_error "Python 3.10+ requerido. Versión actual: $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3 no encontrado. Por favor instala Python 3.10+"
    exit 1
fi

# 2. Crear entorno virtual
echo ""
echo "Paso 2/6: Creando entorno virtual..."
if [ -d "venv" ]; then
    print_info "Entorno virtual ya existe. Eliminando..."
    rm -rf venv
fi

python3 -m venv venv
print_success "Entorno virtual creado"

# 3. Activar entorno virtual
echo ""
echo "Paso 3/6: Activando entorno virtual..."
source venv/bin/activate
print_success "Entorno virtual activado"

# 4. Actualizar pip
echo ""
echo "Paso 4/6: Actualizando pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "pip actualizado"

# 5. Instalar dependencias
echo ""
echo "Paso 5/6: Instalando dependencias..."
print_info "Esto puede tomar 2-3 minutos..."

if pip install -r requirements.txt > /dev/null 2>&1; then
    print_success "Dependencias instaladas correctamente"
else
    print_error "Error instalando dependencias. Verifica requirements.txt"
    exit 1
fi

# 6. Verificar credenciales de GCP
echo ""
echo "Paso 6/6: Verificando credenciales de GCP..."

if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    print_info "Variable GOOGLE_APPLICATION_CREDENTIALS no configurada"
    echo ""
    echo "Para configurar las credenciales de GCP:"
    echo "1. Descarga tu archivo JSON de Service Account"
    echo "2. Guárdalo en este directorio (ej: gcp-credentials.json)"
    echo "3. Ejecuta: export GOOGLE_APPLICATION_CREDENTIALS=\"\$(pwd)/gcp-credentials.json\""
    echo ""
    
    # Buscar archivos JSON en el directorio actual
    JSON_FILES=$(find . -maxdepth 1 -name "*.json" -type f)
    if [ -n "$JSON_FILES" ]; then
        print_info "Archivos JSON encontrados en el directorio:"
        echo "$JSON_FILES"
        echo ""
        read -p "¿Deseas usar uno de estos archivos? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            select JSON_FILE in $JSON_FILES; do
                if [ -n "$JSON_FILE" ]; then
                    export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/$JSON_FILE"
                    print_success "Credenciales configuradas: $JSON_FILE"
                    echo "export GOOGLE_APPLICATION_CREDENTIALS=\"$(pwd)/$JSON_FILE\"" >> venv/bin/activate
                    break
                fi
            done
        fi
    else
        print_info "No se encontraron archivos JSON en el directorio"
    fi
else
    print_success "Credenciales ya configuradas: $GOOGLE_APPLICATION_CREDENTIALS"
fi

# Mensaje final
echo ""
echo "================================================"
echo "  ✨ Instalación Completada"
echo "================================================"
echo ""
print_success "CONTRACTIA AI está listo para usar"
echo ""
echo "Para ejecutar la aplicación:"
echo "  1. Activa el entorno virtual: source venv/bin/activate"
echo "  2. Ejecuta: streamlit run app.py"
echo "  3. Abre tu navegador en: http://localhost:8501"
echo ""

if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    print_info "Recuerda configurar las credenciales de GCP antes de ejecutar"
fi

echo "Para más información, consulta:"
echo "  - QUICKSTART.md - Guía de inicio rápido"
echo "  - README.md - Documentación completa"
echo ""
print_success "¡Éxito! 🚀"
