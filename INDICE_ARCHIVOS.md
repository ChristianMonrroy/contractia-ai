# 📁 ÍNDICE DE ARCHIVOS - CONTRACTIA AI

## Estructura Completa del Proyecto

```
contractia-ai/
│
├── 🚀 ARCHIVOS PRINCIPALES DE LA APLICACIÓN
│   ├── app.py                          (15 KB)  - Aplicación Streamlit principal
│   ├── contract_processor.py           (17 KB)  - Motor de procesamiento de contratos
│   ├── utils.py                        (9 KB)   - Funciones auxiliares
│   └── requirements.txt                (615 B)  - Dependencias Python
│
├── 📚 DOCUMENTACIÓN
│   ├── RESUMEN_EJECUTIVO.md           (9 KB)   - ⭐ EMPIEZA AQUÍ
│   ├── QUICKSTART.md                  (6 KB)   - Guía de inicio rápido (30 min)
│   ├── README.md                      (12 KB)  - Documentación completa
│   ├── ARCHITECTURE.md                (14 KB)  - Arquitectura técnica detallada
│   └── Este archivo                            - Índice de archivos
│
├── ⚙️ CONFIGURACIÓN
│   ├── .env.example                            - Template de variables de entorno
│   └── .streamlit/
│       └── config.toml                         - Configuración de Streamlit
│
└── 🛠️ SCRIPTS DE INSTALACIÓN
    ├── install.sh                     (4.5 KB) - Instalación automática (Linux/Mac)
    └── install.bat                    (3.7 KB) - Instalación automática (Windows)
```

---

## 📖 Descripción Detallada de Archivos

### 🚀 Archivos Principales

#### **app.py** (15 KB)
**Propósito:** Aplicación web principal con Streamlit

**Contiene:**
- Interfaz de usuario completa
- Sistema de tabs (Cargar Contrato, Resultados, Documentación)
- Lógica de subida de archivos
- Gestión de estado (session_state)
- Dashboard de métricas y resultados
- Sistema de descargas (MD, JSON)

**Cuándo modificar:**
- Para cambiar diseño de la UI
- Agregar nuevas features al dashboard
- Modificar flujo de usuario

---

#### **contract_processor.py** (17 KB)
**Propósito:** Motor de procesamiento de contratos

**Contiene:**
- Clase `ContractProcessor`
- Lógica de segmentación de contratos
- Construcción de índices (secciones, global, local)
- Validación de referencias cruzadas
- Análisis de coherencia con LLM
- Integración con Vertex AI

**Cuándo modificar:**
- Para ajustar algoritmos de análisis
- Mejorar detección de secciones
- Cambiar prompts del LLM
- Optimizar performance

---

#### **utils.py** (9 KB)
**Propósito:** Funciones auxiliares reutilizables

**Contiene:**
- `configurar_entorno_vertexai()` - Setup de GCP
- `generar_reporte_markdown()` - Generación de reportes
- `crear_zip_resultados()` - Empaquetado de resultados
- `validar_pdf()` - Validación de archivos
- `estimar_tiempo_procesamiento()` - Estimaciones
- `limpiar_temporales()` - Gestión de cache

**Cuándo modificar:**
- Para agregar nuevas utilidades
- Cambiar formato de reportes
- Ajustar estimaciones de tiempo

---

#### **requirements.txt** (615 B)
**Propósito:** Dependencias del proyecto

**Contiene:**
- Streamlit 1.31.0
- Google Cloud AI Platform
- LangChain y componentes
- PyPDF y procesamiento de docs
- FAISS para vectorstore

**Cuándo modificar:**
- Al agregar nuevas librerías
- Para actualizar versiones
- Resolver conflictos de dependencias

---

### 📚 Documentación

#### **RESUMEN_EJECUTIVO.md** ⭐ (9 KB)
**Propósito:** Punto de entrada - Lee esto primero

**Contiene:**
- Resumen de todo lo creado
- 3 opciones de deployment explicadas
- Checklist de implementación
- Comandos clave
- Próximos pasos

**Audiencia:** Tú (Christian) y cualquiera que inicie el proyecto

---

#### **QUICKSTART.md** (6 KB)
**Propósito:** Guía práctica para estar corriendo en 30 minutos

**Contiene:**
- Instalación local paso a paso
- Despliegue en Streamlit Cloud paso a paso
- Comandos copy-paste listos
- Troubleshooting común

**Audiencia:** Desarrolladores que quieren empezar rápido

---

#### **README.md** (12 KB)
**Propósito:** Documentación completa del proyecto

**Contiene:**
- Descripción del proyecto
- Arquitectura del sistema
- 3 opciones de instalación detalladas
- Guía de uso
- Configuración avanzada
- Costos detallados
- Troubleshooting completo
- Información académica

**Audiencia:** Todos (desarrolladores, stakeholders, evaluadores de tesis)

---

#### **ARCHITECTURE.md** (14 KB)
**Propósito:** Documentación técnica profunda

**Contiene:**
- Comparativa de opciones de deployment
- Stack tecnológico completo
- Flujo de datos detallado
- Análisis de costos por escenario
- Métricas de performance
- Roadmap de desarrollo
- Consideraciones de compliance

**Audiencia:** Arquitectos de software, evaluadores técnicos, futuro equipo de desarrollo

---

### ⚙️ Configuración

#### **.env.example**
**Propósito:** Template de configuración

**Contiene:**
- Variables de entorno necesarias
- Ejemplos de valores
- Comentarios explicativos

**Cómo usar:**
```bash
cp .env.example .env
# Edita .env con tus valores reales
```

---

#### **.streamlit/config.toml**
**Propósito:** Configuración de Streamlit

**Contiene:**
- Tema de colores (azul #1f77b4)
- Límite de subida de archivos (50 MB)
- Configuraciones de seguridad

**Cuándo modificar:**
- Para cambiar colores del tema
- Ajustar límites de subida
- Configurar CORS

---

### 🛠️ Scripts de Instalación

#### **install.sh** (4.5 KB)
**Propósito:** Instalación automática en Linux/Mac

**Hace:**
1. Verifica Python 3.10+
2. Crea entorno virtual
3. Instala dependencias
4. Configura credenciales GCP (interactivo)

**Uso:**
```bash
chmod +x install.sh
./install.sh
```

---

#### **install.bat** (3.7 KB)
**Propósito:** Instalación automática en Windows

**Hace:**
1. Verifica Python
2. Crea entorno virtual
3. Instala dependencias
4. Configura credenciales GCP (interactivo)

**Uso:**
```cmd
install.bat
```

---

## 🗺️ Cómo Navegar Este Proyecto

### Si eres nuevo:
1. **Lee primero:** `RESUMEN_EJECUTIVO.md`
2. **Instala:** Sigue `QUICKSTART.md`
3. **Profundiza:** Consulta `README.md`

### Si quieres entender la arquitectura:
1. **Lee:** `ARCHITECTURE.md`
2. **Revisa código:** `contract_processor.py`
3. **Explora:** `app.py`

### Si quieres deployar:
1. **Opción 1 (Recomendada):** Sigue "Opción 2" en `QUICKSTART.md` (Streamlit Cloud)
2. **Opción 2 (Local):** Ejecuta `install.sh` o `install.bat`
3. **Opción 3 (Producción):** Sigue "Opción 3" en `README.md` (Cloud Run)

### Si quieres modificar:
1. **UI:** Edita `app.py`
2. **Lógica:** Edita `contract_processor.py`
3. **Utilidades:** Edita `utils.py`
4. **Dependencias:** Actualiza `requirements.txt`

---

## 📦 Qué Archivos Subir a GitHub

### Sí subir:
- ✅ Todos los archivos `.py`
- ✅ `requirements.txt`
- ✅ Todos los `.md`
- ✅ `.streamlit/config.toml`
- ✅ `.env.example`
- ✅ `install.sh` y `install.bat`

### NO subir:
- ❌ `.env` (con tus credenciales reales)
- ❌ `*.json` (archivos de credenciales GCP)
- ❌ `venv/` (entorno virtual)
- ❌ `__pycache__/`
- ❌ `*.pyc`

### Crear `.gitignore`:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Credenciales
.env
*.json
!.env.example

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Streamlit
.streamlit/secrets.toml
```

---

## 🎯 Archivos por Caso de Uso

### Para entender el proyecto:
- `RESUMEN_EJECUTIVO.md`
- `README.md`

### Para instalar localmente:
- `install.sh` o `install.bat`
- `QUICKSTART.md`

### Para deployar en la nube:
- `QUICKSTART.md` (sección Opción 2)
- `app.py` (agregar código de secrets)

### Para desarrollar/modificar:
- `app.py`
- `contract_processor.py`
- `utils.py`

### Para la tesis:
- `ARCHITECTURE.md` (diagramas y métricas)
- `README.md` (descripción completa)
- Screenshots de la app funcionando

### Para presentar a stakeholders:
- URL pública de la app (después de deploy)
- `RESUMEN_EJECUTIVO.md`
- Reportes de ejemplo generados

---

## 🔍 Dónde Encontrar...

### Código de la interfaz de usuario:
→ `app.py` líneas 1-350

### Lógica de procesamiento de contratos:
→ `contract_processor.py` clase `ContractProcessor`

### Integración con Vertex AI:
→ `contract_processor.py` líneas 1-50
→ `utils.py` función `configurar_entorno_vertexai()`

### Generación de reportes:
→ `utils.py` función `generar_reporte_markdown()`

### Configuración de colores/tema:
→ `.streamlit/config.toml`
→ `app.py` sección CSS (líneas 30-45)

### Instrucciones de deployment:
→ `QUICKSTART.md` para rápido
→ `README.md` para completo

### Análisis de costos:
→ `ARCHITECTURE.md` sección "Costos Estimados"

### Roadmap futuro:
→ `ARCHITECTURE.md` sección "Roadmap de Desarrollo"

---

## ✨ Resumen

**Total de archivos:** 12 archivos principales
**Total de documentación:** ~63 KB
**Total de código:** ~41 KB
**Tiempo de lectura completo:** ~2 horas
**Tiempo para estar corriendo:** 15-30 minutos

---

## 🚀 Siguiente Paso

**Lee:** `RESUMEN_EJECUTIVO.md` - Es tu punto de partida perfecto.

---

*Creado para CONTRACTIA AI - Team DataLaw - UTEC*
