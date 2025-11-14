# 🚀 Guía de Implementación Web - CONTRACTIA AI

## 📋 Tabla de Contenidos
1. [Arquitectura General](#arquitectura)
2. [Pre-requisitos](#pre-requisitos)
3. [Configuración Inicial](#configuración-inicial)
4. [Deployment Backend](#deployment-backend)
5. [Deployment Frontend](#deployment-frontend)
6. [Testing y Validación](#testing)
7. [Monitoreo y Logs](#monitoreo)
8. [Troubleshooting](#troubleshooting)

---

## 🏗️ Arquitectura General

```
┌─────────────────┐
│  Usuario Web    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  Frontend (Streamlit)       │
│  Cloud Run: contractia-ui   │
└────────┬────────────────────┘
         │ HTTPS
         ▼
┌─────────────────────────────┐
│  Backend API (FastAPI)      │
│  Cloud Run: contractia-api  │
└────────┬────────────────────┘
         │
         ├─────────► Vertex AI (Gemini 2.5 Pro)
         │
         ├─────────► Cloud Storage (Documentos)
         │
         └─────────► Firestore (Metadata/Logs)
```

---

## 📦 Pre-requisitos

### 1. Cuenta de Google Cloud Platform
- Proyecto creado: `agenteia-471917`
- Billing habilitado
- APIs habilitadas (el script lo hace automáticamente)

### 2. Herramientas Locales
```bash
# Instalar Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Autenticarse
gcloud auth login
gcloud config set project agenteia-471917

# Instalar Docker (opcional para testing local)
# https://docs.docker.com/get-docker/
```

### 3. Permisos IAM Necesarios
```bash
# Otorgar permisos a tu cuenta de servicio
gcloud projects add-iam-policy-binding agenteia-471917 \
    --member="serviceAccount:YOUR_SERVICE_ACCOUNT@agenteia-471917.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding agenteia-471917 \
    --member="serviceAccount:YOUR_SERVICE_ACCOUNT@agenteia-471917.iam.gserviceaccount.com" \
    --role="roles/storage.admin"
```

---

## ⚙️ Configuración Inicial

### 1. Clonar Estructura de Archivos
Los archivos creados están en:
- `/home/claude/backend/` - API Backend
- `/home/claude/frontend/` - Interfaz Web

### 2. Configurar Variables de Entorno

**Backend (.env)**
```bash
GCP_PROJECT_ID=agenteia-471917
GCP_LOCATION=us-central1
GCS_BUCKET=contractia-documents
GOOGLE_APPLICATION_CREDENTIALS=./agenteia-471917-d588639beeef.json
```

**Frontend (.streamlit/secrets.toml)**
```toml
API_URL = "https://contractia-api-XXXXXXX-uc.a.run.app"
```

### 3. Crear Cloud Storage Bucket
```bash
gsutil mb -p agenteia-471917 -l us-central1 gs://contractia-documents
gsutil mb -p agenteia-471917 -l us-central1 gs://contractia-reports
```

---

## 🔧 Deployment Backend

### Opción A: Deployment Automático (Recomendado)

```bash
cd backend
chmod +x deploy.sh
./deploy.sh
```

### Opción B: Deployment Manual

```bash
# 1. Construir imagen Docker
gcloud builds submit --tag gcr.io/agenteia-471917/contractia-api

# 2. Desplegar en Cloud Run
gcloud run deploy contractia-api \
    --image gcr.io/agenteia-471917/contractia-api \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 10 \
    --set-env-vars="GCP_PROJECT_ID=agenteia-471917,GCP_LOCATION=us-central1,GCS_BUCKET=contractia-documents"

# 3. Obtener URL
gcloud run services describe contractia-api --region us-central1 --format 'value(status.url)'
```

### Verificar Deployment
```bash
# Probar endpoint de salud
curl https://contractia-api-XXXXXXX-uc.a.run.app/

# Expected response:
# {"service":"CONTRACTIA AI API","status":"operational","version":"1.0.0"}
```

---

## 🎨 Deployment Frontend

### 1. Actualizar URL de la API
Edita `frontend/.streamlit/secrets.toml`:
```toml
API_URL = "https://contractia-api-XXXXXXX-uc.a.run.app"
```

### 2. Desplegar en Cloud Run
```bash
cd frontend

# Construir imagen
gcloud builds submit --tag gcr.io/agenteia-471917/contractia-ui

# Desplegar
gcloud run deploy contractia-ui \
    --image gcr.io/agenteia-471917/contractia-ui \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --port 8501

# Obtener URL
gcloud run services describe contractia-ui --region us-central1 --format 'value(status.url)'
```

---

## 🧪 Testing Local (Antes de Deploy)

### Backend Local
```bash
cd backend

# Instalar dependencias
pip install -r requirements.txt

# Configurar variable de entorno
export GOOGLE_APPLICATION_CREDENTIALS="./agenteia-471917-d588639beeef.json"

# Ejecutar servidor
uvicorn main:app --reload --port 8080

# En otra terminal, probar
curl http://localhost:8080/
```

### Frontend Local
```bash
cd frontend

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar Streamlit
streamlit run app.py

# Abrirá en http://localhost:8501
```

---

## 📊 Monitoreo y Logs

### Ver Logs del Backend
```bash
# Logs en tiempo real
gcloud logs tail --service contractia-api --region us-central1

# Logs históricos
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=contractia-api" --limit 50
```

### Métricas de Performance
```bash
# Abrir Cloud Console
gcloud console

# Navegar a: Cloud Run > contractia-api > Metrics
# Revisar:
# - Request count
# - Request latency
# - Error rate
# - Memory utilization
```

### Configurar Alertas
```bash
# Alerta por errores
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="CONTRACTIA API Errors" \
    --condition-display-name="Error rate > 5%" \
    --condition-threshold-value=5 \
    --condition-threshold-duration=60s
```

---

## 🔍 Troubleshooting

### Error: "Failed to initialize Vertex AI"
**Solución:**
```bash
# Verificar que la API esté habilitada
gcloud services enable aiplatform.googleapis.com

# Verificar permisos de la cuenta de servicio
gcloud projects get-iam-policy agenteia-471917
```

### Error: "Cloud Storage permission denied"
**Solución:**
```bash
# Otorgar permisos al bucket
gsutil iam ch serviceAccount:YOUR_SERVICE_ACCOUNT@agenteia-471917.iam.gserviceaccount.com:roles/storage.admin gs://contractia-documents
```

### Error: "Memory limit exceeded"
**Solución:**
```bash
# Aumentar memoria del servicio
gcloud run services update contractia-api \
    --region us-central1 \
    --memory 4Gi
```

### Lentitud en Procesamiento
**Optimizaciones:**
1. Aumentar CPU: `--cpu 4`
2. Implementar caché de embeddings
3. Procesar en background con Cloud Tasks
4. Usar instancias mínimas: `--min-instances 1`

---

## 📈 Optimizaciones Post-Deployment

### 1. Habilitar CDN
```bash
gcloud compute backend-services update contractia-api \
    --enable-cdn
```

### 2. Configurar Auto-scaling
```bash
gcloud run services update contractia-api \
    --min-instances 1 \
    --max-instances 20 \
    --concurrency 80
```

### 3. Implementar Caché
```python
# En main.py, agregar Redis para caché
from redis import Redis
cache = Redis(host='REDIS_HOST', port=6379)

@cache.memoize(timeout=3600)
def process_document(doc_id):
    # ...
```

### 4. Base de Datos para Metadata
```bash
# Crear instancia Cloud SQL
gcloud sql instances create contractia-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1

# Conectar desde Cloud Run
gcloud run services update contractia-api \
    --add-cloudsql-instances=agenteia-471917:us-central1:contractia-db
```

---

## 🔐 Seguridad

### 1. Autenticación de Usuarios
```python
# Implementar OAuth2 con Google
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/api/v1/audit")
async def audit(token: str = Depends(oauth2_scheme)):
    # Verificar token
    pass
```

### 2. Limitar Acceso por IP
```bash
gcloud run services update contractia-api \
    --ingress=internal-and-cloud-load-balancing
```

### 3. Secrets Management
```bash
# Crear secret
echo -n "your-api-key" | gcloud secrets create api-key --data-file=-

# Usar en Cloud Run
gcloud run services update contractia-api \
    --update-secrets=API_KEY=api-key:latest
```

---

## 💰 Estimación de Costos

Para un uso moderado (100 auditorías/mes):

| Servicio | Costo Mensual Estimado |
|----------|------------------------|
| Cloud Run (Backend) | $20-50 |
| Cloud Run (Frontend) | $10-20 |
| Vertex AI (Gemini) | $50-200 |
| Cloud Storage | $5-10 |
| Firestore | $5-15 |
| **TOTAL** | **$90-295/mes** |

Para reducir costos:
- Usar instancias mínimas = 0
- Implementar caché agresivo
- Optimizar prompts para reducir tokens
- Usar batch processing

---

## 📚 Recursos Adicionales

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Vertex AI Docs](https://cloud.google.com/vertex-ai/docs)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/)
- [Streamlit Docs](https://docs.streamlit.io/)

---

## 🤝 Soporte

Para problemas o preguntas:
1. Revisar logs en Cloud Console
2. Consultar esta guía
3. Contactar al equipo de desarrollo

**Desarrollado por:** Christian Choque  
**Institución:** UTEC - Maestría en Data Science & AI  
**Proyecto:** CONTRACTIA AI para ProInversión
