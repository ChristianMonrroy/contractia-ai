# 📋 CONTRACTIA AI - Sistema de Auditoría Automática de Contratos APP

Sistema web automatizado para la auditoría de contratos de concesión de Asociación Público-Privada (APP) en Perú, desarrollado como parte de una tesis de Maestría en Data Science e Inteligencia Artificial en UTEC.

![Version](https://img.shields.io/badge/version-1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![License](https://img.shields.io/badge/license-Academic-orange.svg)

---

## 🎯 Objetivos del Proyecto

- ✅ Reducir tiempo de revisión manual de **320+ horas** a **< 1 hora**
- ✅ Detectar **90%+** de inconsistencias en referencias cruzadas
- ✅ Identificar errores materiales en contratos APP
- ✅ Validar cumplimiento normativo automáticamente

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────┐
│      Streamlit Web Application          │
│  (Interfaz de usuario en la nube)       │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│     Contract Processor (Python)         │
│  - Segmentación automática              │
│  - Extracción de índices                │
│  - Validación de referencias            │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│      Google Cloud Platform (GCP)        │
│  - Vertex AI (Gemini 2.5 Pro)          │
│  - Embeddings (textembedding-gecko)     │
│  - Cloud Storage (opcional)             │
└─────────────────────────────────────────┘
```

---

## 🚀 Guía de Instalación y Despliegue

### **Opción 1: Despliegue Local (Desarrollo)**

#### Prerrequisitos
- Python 3.10 o superior
- Cuenta de Google Cloud Platform
- Vertex AI API habilitada
- Cuenta de servicio de GCP configurada

#### Pasos

1. **Clonar el proyecto** (o crear los archivos manualmente):

```bash
mkdir contractia-ai
cd contractia-ai
```

2. **Crear entorno virtual**:

```bash
python -m venv venv

# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

3. **Instalar dependencias**:

```bash
pip install -r requirements.txt
```

4. **Configurar credenciales de GCP**:

```bash
# Copiar el archivo .env.example
cp .env.example .env

# Editar .env con tus datos:
# - GCP_PROJECT_ID: Tu ID de proyecto de Google Cloud
# - GOOGLE_APPLICATION_CREDENTIALS: Ruta a tu archivo JSON de credenciales
```

5. **Descargar credenciales de cuenta de servicio**:
   - Ve a [Google Cloud Console](https://console.cloud.google.com/)
   - Navega a "IAM y administración" → "Cuentas de servicio"
   - Crea una nueva cuenta de servicio (o usa una existente)
   - Descarga el archivo JSON de credenciales
   - Guárdalo en la raíz del proyecto y actualiza `.env`

6. **Habilitar APIs necesarias en GCP**:

```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
```

7. **Ejecutar la aplicación**:

```bash
streamlit run app.py
```

8. **Acceder a la aplicación**:
   - Abre tu navegador en `http://localhost:8501`

---

### **Opción 2: Despliegue en Streamlit Community Cloud (GRATIS) ⭐ RECOMENDADO**

Esta es la opción **recomendada para el prototipo** ya que es completamente gratuita y no requiere gestión de servidores.

#### Pasos

1. **Preparar el repositorio en GitHub**:

```bash
# Inicializar repositorio Git (si no existe)
git init

# Agregar archivos
git add .
git commit -m "Initial commit - CONTRACTIA AI"

# Crear repositorio en GitHub y conectar
git remote add origin https://github.com/TU_USUARIO/contractia-ai.git
git push -u origin main
```

2. **Configurar Streamlit Community Cloud**:
   - Ve a [share.streamlit.io](https://share.streamlit.io/)
   - Inicia sesión con tu cuenta de GitHub
   - Click en "New app"
   - Selecciona tu repositorio `contractia-ai`
   - Selecciona la rama `main`
   - Archivo principal: `app.py`

3. **Configurar Secrets en Streamlit Cloud**:
   - En la configuración de tu app, ve a "Secrets"
   - Agrega el contenido de tu archivo JSON de credenciales de GCP:

```toml
[gcp_service_account]
type = "service_account"
project_id = "tu-project-id"
private_key_id = "tu-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "tu-service-account@tu-project.iam.gserviceaccount.com"
client_id = "tu-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

4. **Modificar `app.py` para usar Streamlit Secrets**:

Agregar al inicio de `app.py` (antes de `main()`):

```python
import json
import tempfile

# Cargar credenciales desde Streamlit Secrets (para deployment)
if "gcp_service_account" in st.secrets:
    service_account_info = dict(st.secrets["gcp_service_account"])
    # Guardar temporalmente para que Vertex AI pueda usarlo
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(service_account_info, f)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f.name
```

5. **Desplegar**:
   - Click en "Deploy"
   - Espera unos minutos mientras se construye
   - Tu aplicación estará disponible en una URL pública: `https://tu-app.streamlit.app`

---

### **Opción 3: Despliegue en Google Cloud Run (Producción)**

Para un entorno de producción con mayor control y escalabilidad.

#### Prerrequisitos
- Google Cloud SDK instalado
- Billing habilitado en GCP
- Cloud Run API habilitada

#### Pasos

1. **Crear Dockerfile**:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

ENV PORT=8080

CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

2. **Construir y subir imagen a Container Registry**:

```bash
# Configurar proyecto
gcloud config set project TU_PROJECT_ID

# Construir imagen
gcloud builds submit --tag gcr.io/TU_PROJECT_ID/contractia-ai

# Desplegar a Cloud Run
gcloud run deploy contractia-ai \
  --image gcr.io/TU_PROJECT_ID/contractia-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2
```

3. **Obtener URL de la aplicación**:

```bash
gcloud run services describe contractia-ai --region us-central1 --format 'value(status.url)'
```

**Nota**: Cloud Run tiene costo, pero ofrece un tier gratuito generoso:
- 2 millones de solicitudes/mes gratis
- 360,000 GB-segundos de memoria gratis
- 180,000 vCPU-segundos gratis

---

## 📊 Uso de la Aplicación

### 1. **Subir Contrato**
   - Navega a la pestaña "Cargar Contrato"
   - Sube el archivo PDF del contrato de concesión
   - (Opcional) Sube documentos normativos de referencia
   - Click en "Iniciar Análisis"

### 2. **Ver Resultados**
   - El sistema procesará el contrato (15-45 min dependiendo del tamaño)
   - Los resultados aparecerán en la pestaña "Resultados"
   - Incluye:
     * Métricas de auditoría
     * Reporte completo en Markdown
     * Hallazgos críticos clasificados por severidad
     * Opciones de descarga (MD y JSON)

### 3. **Interpretar Resultados**
   - **Referencias Rotas**: Referencias que apuntan a secciones inexistentes
   - **Hallazgos de Coherencia**: Inconsistencias lógicas detectadas por el LLM
   - **Severidad**: Alta (requiere atención inmediata), Media, Baja

---

## 🔧 Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `GCP_PROJECT_ID` | ID del proyecto de Google Cloud | `agenteia-471917` |
| `GCP_LOCATION` | Región de Vertex AI | `us-central1` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Ruta a credenciales JSON | `/path/to/key.json` |

### Configuración de Vertex AI

En `contract_processor.py` puedes ajustar:
- **Modelo LLM**: Por defecto `gemini-2.0-flash-exp`
- **Modelo de Embeddings**: Por defecto `textembedding-gecko@latest`
- **Temperatura**: Por defecto `0.1` (más determinístico)
- **Max Tokens**: Por defecto `8192`

---

## 💰 Costos Estimados (GCP)

### Vertex AI - Gemini 2.5 Pro
- **Entrada**: ~$0.00125 por 1K caracteres
- **Salida**: ~$0.00375 por 1K caracteres

### Para un contrato de 200 páginas (~500K caracteres):
- **Procesamiento**: ~$1-3 USD por análisis completo
- **Embeddings**: ~$0.10 USD
- **Total estimado**: ~$1.50 - $3.50 USD por contrato

### Tier Gratuito
- **Streamlit Community Cloud**: Completamente gratuito
- **Vertex AI**: Créditos iniciales de $300 USD
- **Cloud Storage**: 5 GB gratis al mes

---

## 📁 Estructura del Proyecto

```
contractia-ai/
│
├── app.py                      # Aplicación principal Streamlit
├── contract_processor.py       # Lógica de procesamiento de contratos
├── utils.py                    # Funciones auxiliares
├── requirements.txt            # Dependencias Python
├── .env.example               # Ejemplo de variables de entorno
├── .streamlit/
│   └── config.toml            # Configuración de Streamlit
│
├── README.md                  # Este archivo
│
└── tests/                     # Tests (próximamente)
    └── test_processor.py
```

---

## 🐛 Troubleshooting

### Error: "GOOGLE_APPLICATION_CREDENTIALS not set"
**Solución**: Asegúrate de que la variable de entorno esté correctamente configurada:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/key.json"
```

### Error: "API Vertex AI not enabled"
**Solución**: Habilita la API desde Cloud Console:
```bash
gcloud services enable aiplatform.googleapis.com
```

### Error: "ModuleNotFoundError: No module named 'XXX'"
**Solución**: Reinstala las dependencias:
```bash
pip install -r requirements.txt --upgrade
```

### La aplicación es muy lenta
**Solución**: 
- Verifica que estés usando la región correcta de Vertex AI
- Considera aumentar recursos en Cloud Run (si aplica)
- Optimiza el tamaño del contrato (pre-procesa si es > 50MB)

---

## 🤝 Contribuciones

Este es un proyecto académico como parte de una tesis de maestría. Para consultas o colaboraciones:

**Contacto**: Team DataLaw - UTEC  
**Autor Principal**: Christian  
**Co-autor**: Oscar Bueno

---

## 📄 Licencia

Este proyecto es para propósitos académicos y de investigación. Para uso comercial, contactar a los autores.

---

## 📚 Referencias

- [Documentación de Vertex AI](https://cloud.google.com/vertex-ai/docs)
- [Streamlit Docs](https://docs.streamlit.io/)
- [LangChain Documentation](https://python.langchain.com/)
- [Lineamientos ProInversión](https://www.proinversion.gob.pe/)

---

## 🎓 Cita Académica

Si utilizas este sistema en tu investigación, por favor cita:

```bibtex
@mastersthesis{contractia2025,
  author = {Christian and Oscar Bueno},
  title = {CONTRACTIA AI: Sistema Automatizado de Auditoría de Contratos APP},
  school = {Universidad de Ingeniería y Tecnología (UTEC)},
  year = {2025},
  type = {Tesis de Maestría},
  address = {Lima, Perú}
}
```

---

**Desarrollado con ❤️ por Team DataLaw**  
*Haciendo los contratos públicos más transparentes y eficientes*
