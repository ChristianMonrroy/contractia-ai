# 🏗️ ARQUITECTURA Y DECISIONES TÉCNICAS - CONTRACTIA AI

## 📊 Comparativa de Opciones de Despliegue

| Característica | Local | Streamlit Cloud | Cloud Run | Heroku |
|---------------|-------|-----------------|-----------|---------|
| **Costo** | Gratis | **Gratis** ✅ | ~$10-30/mes | ~$7-25/mes |
| **Tiempo Setup** | 10 min | 15 min | 30 min | 20 min |
| **Disponibilidad** | Solo cuando ejecutas | 24/7 | 24/7 | 24/7 |
| **URL Pública** | No | Sí | Sí | Sí |
| **Escalabilidad** | No | Limitada | Alta | Media |
| **SSL/HTTPS** | No | Sí | Sí | Sí |
| **CI/CD Automático** | No | Sí | Manual | Sí |
| **Límites** | Ilimitado | 1 app gratis | Pay-per-use | 550 hrs/mes gratis |
| **Recomendado para** | Desarrollo | **Prototipo** ✅ | Producción | Prototipo |

### 🏆 Recomendación: **Streamlit Community Cloud**

**Por qué es la mejor opción para tu prototipo:**
1. ✅ **100% Gratuito** - Sin límites de tiempo
2. ✅ **Deploy en 15 minutos** - Más rápido que cualquier otra opción
3. ✅ **URL pública automática** - Puedes compartir con stakeholders inmediatamente
4. ✅ **CI/CD incluido** - Actualización automática con cada push a GitHub
5. ✅ **Soporte SSL/HTTPS** - Seguridad lista out-of-the-box
6. ✅ **Secrets management** - Manejo seguro de credenciales GCP
7. ✅ **Sin gestión de servidores** - Zero DevOps

---

## 🔧 Arquitectura Técnica Detallada

### Stack Tecnológico Completo

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                      │
│                                                              │
│  Streamlit 1.31.0                                           │
│  - Componentes interactivos (file_uploader, progress_bar)  │
│  - Sistema de tabs y layout responsivo                      │
│  - Session state management                                 │
│  - Markdown rendering para reportes                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE LÓGICA DE NEGOCIO                 │
│                                                              │
│  ContractProcessor (contract_processor.py)                  │
│  ├─ Carga y procesamiento de documentos                    │
│  ├─ Segmentación inteligente (capítulos, anexos, cláusulas)│
│  ├─ Construcción de índices (triple-level)                 │
│  ├─ Validación de referencias cruzadas                     │
│  └─ Análisis de coherencia con LLM                         │
│                                                              │
│  Utils (utils.py)                                            │
│  ├─ Configuración de Vertex AI                             │
│  ├─ Generación de reportes Markdown                        │
│  └─ Gestión de archivos temporales                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE INTEGRACIÓN                       │
│                                                              │
│  LangChain                                                   │
│  ├─ Document Loaders (PyPDF, Unstructured)                 │
│  ├─ Text Splitters (RecursiveCharacterTextSplitter)        │
│  ├─ Vector Stores (FAISS)                                  │
│  └─ LLM Chain Management                                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE SERVICIOS (GCP)                   │
│                                                              │
│  Vertex AI                                                   │
│  ├─ Gemini 2.0 Flash Exp (LLM principal)                   │
│  │  • Temperature: 0.1 (determinístico)                    │
│  │  • Max tokens: 8192                                     │
│  │  • Casos de uso: Análisis de coherencia, validación    │
│  │                                                          │
│  └─ Text Embedding Gecko Latest                             │
│     • Dimensión: 768                                        │
│     • Casos de uso: RAG, búsqueda semántica                │
│                                                              │
│  (Opcional) Cloud Storage                                   │
│  └─ Almacenamiento temporal de documentos                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 Gestión de Credenciales y Seguridad

### Variables de Entorno (Local)

```bash
# .env
GCP_PROJECT_ID=agenteia-471917
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

### Secrets en Streamlit Cloud

```toml
# secrets.toml (en Streamlit Cloud dashboard)
[gcp_service_account]
type = "service_account"
project_id = "agenteia-471917"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "service-account@agenteia-471917.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

**Flujo de Autenticación:**
1. Streamlit lee secrets al inicio
2. Crea archivo temporal JSON con credenciales
3. Configura `GOOGLE_APPLICATION_CREDENTIALS` apuntando al archivo temporal
4. Vertex AI usa credenciales automáticamente
5. Archivo temporal se elimina al finalizar sesión

---

## 💰 Análisis de Costos Detallado

### Vertex AI Pricing (Región us-central1)

#### Gemini 2.0 Flash Exp
```
Input:  $0.00125 por 1,000 caracteres
Output: $0.00375 por 1,000 caracteres
```

#### Text Embeddings Gecko
```
$0.00002 por 1,000 caracteres
```

### Cálculo para Contrato Típico (200 páginas)

```
Documento:           500,000 caracteres
Segmentación:        100 llamadas LLM × 2,000 chars input = 200K chars
Análisis coherencia: 50 llamadas LLM × 4,000 chars input = 200K chars
Respuestas LLM:      50 llamadas × 500 chars output = 25K chars
Embeddings:          500,000 caracteres

TOTAL COSTOS:
- LLM Input:  400K chars × $0.00125 = $0.50
- LLM Output: 25K chars × $0.00375 = $0.09
- Embeddings: 500K chars × $0.00002 = $0.01

TOTAL POR CONTRATO: ~$0.60 USD
```

### Costo con Créditos Gratuitos de GCP

```
Créditos iniciales: $300 USD
Contratos procesables: ~500 contratos
Suficiente para: TODO tu proyecto de tesis + demos
```

### Costos Escalados (Post-Tesis)

```
Escenario 1: ProInversión (10 contratos/mes)
$0.60 × 10 = $6/mes

Escenario 2: Producción Media (50 contratos/mes)
$0.60 × 50 = $30/mes

Escenario 3: Producción Alta (200 contratos/mes)
$0.60 × 200 = $120/mes
```

---

## 📈 Performance y Optimizaciones

### Tiempos de Procesamiento

| Tamaño Contrato | Páginas | Tiempo Estimado | Optimización |
|----------------|---------|-----------------|--------------|
| Pequeño | < 50 | 5-10 min | Procesamiento paralelo |
| Mediano | 50-150 | 15-25 min | Caché de embeddings |
| Grande | 150-250 | 30-40 min | Chunking adaptativo |
| Muy Grande | 250+ | 40-60 min | Procesamiento incremental |

### Estrategias de Optimización

1. **Caché de Embeddings**
   ```python
   # Guardar embeddings procesados
   vectorstore.save_local("cache/embeddings_{hash}")
   
   # Reutilizar en análisis posteriores
   if exists(cache_path):
       vectorstore = FAISS.load_local(cache_path)
   ```

2. **Procesamiento Paralelo**
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   with ThreadPoolExecutor(max_workers=5) as executor:
       results = executor.map(process_section, sections)
   ```

3. **Batch Processing**
   ```python
   # Procesar múltiples referencias en un solo LLM call
   batch_prompt = "\n".join([ref for ref in references])
   llm.invoke(batch_prompt)
   ```

---

## 🔄 Flujo de Datos Completo

```
┌──────────────┐
│  Usuario     │
│  Sube PDF    │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  1. INGESTA          │
│  - Validación PDF    │
│  - Carga temporal    │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  2. PROCESAMIENTO    │
│  - PyPDFLoader       │
│  - Extracción texto  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  3. SEGMENTACIÓN     │
│  - Regex patterns    │
│  - NLP parsing       │
│  - Índice building   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  4. RAG SETUP        │
│  - Chunking          │
│  - Embeddings        │
│  - FAISS vectorstore │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  5. VALIDACIÓN       │
│  - Referencias       │
│  - Coherencia (LLM)  │
│  - Normativa (RAG)   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  6. REPORTE          │
│  - Markdown gen      │
│  - JSON export       │
│  - ZIP packaging     │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Usuario Descarga    │
│  Resultados          │
└──────────────────────┘
```

---

## 🚀 Roadmap de Desarrollo

### Fase 1: Prototipo MVP ✅ (ACTUAL)
- [x] Aplicación Streamlit básica
- [x] Integración con Vertex AI
- [x] Procesamiento de contratos
- [x] Validación de referencias
- [x] Generación de reportes

### Fase 2: Mejoras Funcionales (1-2 semanas)
- [ ] Sistema de Q&A interactivo
- [ ] Comparación de múltiples contratos
- [ ] Dashboard de métricas avanzadas
- [ ] Exportación a Word/PDF
- [ ] Caché de resultados

### Fase 3: Producción (1 mes)
- [ ] Autenticación de usuarios
- [ ] Base de datos PostgreSQL
- [ ] Sistema de colas para procesamiento
- [ ] API REST
- [ ] Monitoreo y logging avanzado
- [ ] Migración a Cloud Run

### Fase 4: Escalado (Futuro)
- [ ] Procesamiento batch
- [ ] Machine learning personalizado
- [ ] Integración con sistemas ProInversión
- [ ] Multi-tenancy
- [ ] Compliance GDPR/Ley 29733

---

## 📝 Consideraciones de Compliance

### Ley N° 29733 - Perú (Protección de Datos Personales)

1. **Datos Procesados**: Contratos públicos (no datos personales sensibles)
2. **Almacenamiento**: Temporal (eliminado post-análisis)
3. **Transferencia Internacional**: GCP us-central1 (requiere autorización para datos personales)
4. **Registro**: No aplicable para datos públicos de contratos

### Recomendaciones:
- Documentar flujos de datos
- Implementar política de retención (automática)
- Auditar accesos (Cloud Audit Logs)
- Cifrado en tránsito y reposo (por defecto en GCP)

---

## 🎯 KPIs del Sistema

### Métricas Técnicas
- **Uptime**: 99.9% (objetivo)
- **Tiempo de respuesta**: < 1 hora por contrato
- **Precisión en referencias**: 90%+
- **Tasa de falsos positivos**: < 2%

### Métricas de Negocio
- **Reducción de tiempo**: 99.7% (320h → 1h)
- **Contratos procesados**: Target 50+ para tesis
- **Satisfacción usuarios**: Objetivo 8/10

### Métricas de Costo
- **Costo por contrato**: $0.60 USD
- **ROI**: Positivo desde el primer contrato
- **TCO mensual**: $0 (tier gratuito)

---

**Documento creado por:** Team DataLaw  
**Fecha:** Noviembre 2025  
**Versión:** 1.0
