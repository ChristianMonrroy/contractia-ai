# 🔄 Guía de Migración: Notebook → Web Application

## 📋 Objetivo
Esta guía explica cómo migrar tu código del notebook `AGENTE_IA_CONTRATOS_VS44_Prueba.ipynb` a la arquitectura web modular.

---

## 🗺️ Mapeo de Componentes

### Del Notebook → A la Arquitectura Web

```
NOTEBOOK (Colab)                    →    WEB APPLICATION
──────────────────────────────────────────────────────────────
Celdas 1-2: Setup y autenticación   →    Dockerfile + env vars
Celda 3: Funciones de carga         →    contractia_core.py
Celdas 4-6: Procesamiento           →    contractia_core.py
Celda 7: Análisis LLM               →    contractia_core.py
Celda 8: Generación de informes     →    contractia_core.py
Celda 9: Ejecución principal        →    main.py (endpoints)
Outputs/prints                      →    app.py (Streamlit UI)
```

---

## 🔧 Paso a Paso: Migración del Código

### 1. Autenticación y Configuración

**ANTES (Notebook):**
```python
# Celda 1
NOMBRE_DEL_ARCHIVO_JSON = "agenteia-471917-d588639beeef.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = NOMBRE_DEL_ARCHIVO_JSON
```

**DESPUÉS (Web App):**
```python
# backend/main.py
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "agenteia-471917")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")

# Las credenciales se inyectan automáticamente en Cloud Run
```

---

### 2. Inicialización de Vertex AI

**ANTES (Notebook):**
```python
# Celda 2
def configurar_entorno_vertexai():
    PROJECT_ID = "agenteia-471917"
    LOCATION = "us-central1"
    vertexai.init(project=PROJECT_ID, location=LOCATION)
```

**DESPUÉS (Web App):**
```python
# backend/contractia_core.py
class ContractiaAgent:
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        self.llm = ChatVertexAI(model_name=model_name, temperature=0.0)
        self.embeddings = VertexAIEmbeddings(model_name="textembedding-gecko@latest")
```

---

### 3. Carga de Documentos

**ANTES (Notebook):**
```python
# Celda 3
def procesar_documentos_carpeta(folder_path):
    documentos_combinados = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            documentos_combinados.extend(docs)
    return documentos_combinados
```

**DESPUÉS (Web App):**
```python
# backend/contractia_core.py
class ContractiaAgent:
    def cargar_documento(self, pdf_path: str) -> List[Document]:
        loader = PyPDFLoader(pdf_path)
        self.documentos = loader.load()
        return self.documentos

# backend/main.py
@app.post("/api/v1/upload-document")
async def upload_document(file: UploadFile = File(...)):
    # Guardar en Cloud Storage
    blob.upload_from_string(contents, content_type='application/pdf')
```

---

### 4. Creación de Vectorstore

**ANTES (Notebook):**
```python
# Celda 4
text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
splits = text_splitter.split_documents(documentos)
vectorstore = FAISS.from_documents(splits, embeddings)
```

**DESPUÉS (Web App):**
```python
# backend/contractia_core.py
class ContractiaAgent:
    def crear_vectorstore(self, chunk_size: int = 2000, chunk_overlap: int = 200):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        splits = text_splitter.split_documents(self.documentos)
        self.vectorstore = FAISS.from_documents(splits, self.embeddings)
        return self.vectorstore
```

---

### 5. Análisis de Referencias

**ANTES (Notebook):**
```python
# Celda 5
def extraer_referencias(texto):
    patrones = [r'[Cc]láusula\s+\d+(?:\.\d+)*', ...]
    referencias = []
    for patron in patrones:
        matches = re.findall(patron, texto)
        referencias.extend(matches)
    return referencias

# Usar directamente
referencias = extraer_referencias(texto_documento)
```

**DESPUÉS (Web App):**
```python
# backend/contractia_core.py
class ContractiaAgent:
    def extraer_referencias(self, texto: str) -> List[str]:
        patrones = [r'[Cc]láusula\s+\d+(?:\.\d+)*', ...]
        referencias = []
        for patron in patrones:
            matches = re.findall(patron, texto)
            referencias.extend(matches)
        return list(set(referencias))
    
    def analizar_referencias_rotas(self) -> List[Dict]:
        texto_completo = "\n".join([doc.page_content for doc in self.documentos])
        todas_referencias = self.extraer_referencias(texto_completo)
        
        errores = []
        for ref in todas_referencias:
            validacion = self.validar_referencia(ref)
            if not validacion["existe"]:
                errores.append({...})
        
        return errores
```

---

### 6. Ejecución Principal y Resultados

**ANTES (Notebook):**
```python
# Celda 9 - Ejecución directa
if __name__ == "__main__":
    # Cargar docs
    documentos = procesar_documentos_carpeta("contratos/")
    
    # Crear vectorstore
    vectorstore = crear_vectorstore(documentos)
    
    # Analizar
    errores = analizar_referencias(documentos)
    
    # Mostrar resultados
    print(f"Errores encontrados: {len(errores)}")
    for error in errores:
        print(f"- {error}")
```

**DESPUÉS (Web App):**

```python
# backend/main.py
@app.post("/api/v1/audit", response_model=AuditoriaResponse)
async def iniciar_auditoria(request: AuditoriaRequest, background_tasks: BackgroundTasks):
    auditoria_id = str(uuid.uuid4())
    
    # Iniciar procesamiento asíncrono
    background_tasks.add_task(
        procesar_auditoria,
        auditoria_id,
        request.document_id,
        request.tipo_analisis
    )
    
    return AuditoriaResponse(
        auditoria_id=auditoria_id,
        status="processing",
        fecha_inicio=datetime.now(),
        ...
    )

async def procesar_auditoria(auditoria_id: str, document_id: str, tipo_analisis: str):
    # Instanciar agente
    agente = ContractiaAgent()
    
    # Descargar de GCS
    pdf_path = await descargar_de_gcs(document_id)
    
    # Procesar
    agente.cargar_documento(pdf_path)
    agente.crear_vectorstore()
    resultados = agente.auditoria_completa()
    
    # Guardar resultados
    await guardar_resultados(auditoria_id, resultados)

# frontend/app.py (Streamlit)
if st.button("🚀 Iniciar Auditoría"):
    resultado = iniciar_auditoria(document_id, tipo_analisis)
    st.success(f"Auditoría iniciada: {resultado['auditoria_id']}")
    
    # Mostrar progreso
    while estado := obtener_estado(resultado['auditoria_id']):
        if estado['status'] == 'completed':
            st.balloons()
            mostrar_resultados(estado['resultados'])
            break
        time.sleep(2)
```

---

## 🔄 Checklist de Migración

### ✅ Backend
- [ ] Extraer funciones del notebook a `contractia_core.py`
- [ ] Crear clase `ContractiaAgent` con métodos organizados
- [ ] Implementar endpoints REST en `main.py`
- [ ] Configurar variables de entorno en lugar de hardcoded
- [ ] Añadir manejo de errores y logging
- [ ] Implementar procesamiento asíncrono con BackgroundTasks
- [ ] Integrar con Cloud Storage para documentos
- [ ] Añadir persistencia de resultados (Firestore/Cloud SQL)

### ✅ Frontend
- [ ] Crear interfaz de upload en Streamlit
- [ ] Implementar visualización de resultados
- [ ] Añadir gráficos y métricas
- [ ] Crear sistema de progreso en tiempo real
- [ ] Implementar descarga de informes
- [ ] Añadir historial de auditorías

### ✅ Deployment
- [ ] Crear Dockerfile para backend
- [ ] Crear Dockerfile para frontend
- [ ] Configurar Cloud Run para ambos servicios
- [ ] Configurar Cloud Storage buckets
- [ ] Configurar IAM y permisos
- [ ] Implementar CI/CD con Cloud Build

---

## 📝 Patrones de Código

### Patrón 1: De función global a método de clase

**ANTES:**
```python
def analizar_documento(documento):
    # lógica
    return resultado
```

**DESPUÉS:**
```python
class ContractiaAgent:
    def analizar_documento(self) -> Dict:
        # lógica usando self.documentos
        return resultado
```

### Patrón 2: De prints a logging

**ANTES:**
```python
print("✅ Procesamiento completado")
print(f"Errores: {len(errores)}")
```

**DESPUÉS:**
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Procesamiento completado")
logger.info(f"Errores detectados: {len(errores)}")
```

### Patrón 3: De ejecución síncrona a asíncrona

**ANTES:**
```python
def procesar():
    resultado = analizar_contrato()
    return resultado
```

**DESPUÉS:**
```python
async def procesar():
    # Para operaciones I/O intensivas
    resultado = await analizar_contrato_async()
    return resultado

# O con BackgroundTasks para procesamiento largo
@app.post("/audit")
async def audit(background_tasks: BackgroundTasks):
    background_tasks.add_task(procesar_largo)
    return {"status": "processing"}
```

---

## 🎯 Funciones Clave a Migrar

### Prioridad Alta (Core Functionality)
1. ✅ `cargar_documento()` → Migrada a `ContractiaAgent.cargar_documento()`
2. ✅ `crear_vectorstore()` → Migrada a `ContractiaAgent.crear_vectorstore()`
3. ✅ `extraer_referencias()` → Migrada a `ContractiaAgent.extraer_referencias()`
4. ✅ `validar_referencia()` → Migrada a `ContractiaAgent.validar_referencia()`
5. ⚠️ `analizar_con_llm()` → **PENDIENTE: Adaptar a método de clase**
6. ⚠️ `generar_informe()` → **PENDIENTE: Adaptar para markdown/PDF**

### Prioridad Media (Features Adicionales)
7. ⚠️ `analizar_fechas()` → **PENDIENTE: Implementar lógica completa**
8. ⚠️ `analizar_montos()` → **PENDIENTE: Implementar validaciones**
9. ⚠️ `validar_normativa()` → **PENDIENTE: Integrar documentos MEF**

### Prioridad Baja (Nice to Have)
10. ⚠️ `chat_interactivo()` → **OPCIONAL: Para versión futura**
11. ⚠️ `comparar_contratos()` → **OPCIONAL: Feature avanzado**

---

## 🚨 Consideraciones Importantes

### 1. Cambios en Manejo de Archivos

**NOTEBOOK:**
```python
# Archivos en /content/ de Colab
file_path = "/content/contratos/contrato.pdf"
```

**WEB APP:**
```python
# Archivos en Cloud Storage
file_url = "gs://contractia-documents/uploads/uuid/contrato.pdf"

# Descargar temporalmente para procesar
temp_path = await download_from_gcs(file_url)
```

### 2. Cambios en Autenticación

**NOTEBOOK:**
```python
# Archivo JSON subido manualmente
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"
```

**WEB APP:**
```python
# Credenciales inyectadas automáticamente por Cloud Run
# No necesita configuración manual
```

### 3. Cambios en Outputs

**NOTEBOOK:**
```python
# Display directo en Jupyter
display(Markdown(informe))
```

**WEB APP:**
```python
# API retorna JSON
return JSONResponse(content={"informe": informe_md})

# Frontend renderiza
st.markdown(resultados['informe'])
```

---

## 🧪 Testing Durante la Migración

### 1. Probar Funciones Individualmente
```python
# backend/test_contractia_core.py
import pytest
from contractia_core import ContractiaAgent

def test_extraer_referencias():
    agente = ContractiaAgent()
    texto = "Ver Cláusula 5.2 y Anexo B"
    referencias = agente.extraer_referencias(texto)
    assert "Cláusula 5.2" in referencias
    assert "Anexo B" in referencias

def test_cargar_documento():
    agente = ContractiaAgent()
    docs = agente.cargar_documento("test_contract.pdf")
    assert len(docs) > 0
```

### 2. Probar Endpoints
```python
# backend/test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload_document():
    with open("test.pdf", "rb") as f:
        response = client.post(
            "/api/v1/upload-document",
            files={"file": ("test.pdf", f, "application/pdf")}
        )
    assert response.status_code == 200
    assert "document_id" in response.json()
```

---

## 📚 Recursos Adicionales

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Streamlit Docs:** https://docs.streamlit.io/
- **Cloud Run Docs:** https://cloud.google.com/run/docs
- **LangChain Docs:** https://python.langchain.com/

---

## ❓ FAQ

**P: ¿Puedo seguir usando el notebook en paralelo?**  
R: Sí, manténlo para experimentación rápida, pero la versión web es la de producción.

**P: ¿Cómo migro los prompts del LLM?**  
R: Extrae los prompts a archivos separados o a un módulo `prompts.py` para mejor mantenimiento.

**P: ¿Necesito cambiar el modelo de Gemini?**  
R: No, `gemini-2.0-flash-exp` funciona igual en Colab y Vertex AI.

**P: ¿Cómo manejo el procesamiento largo?**  
R: Usa BackgroundTasks de FastAPI o Cloud Tasks para procesamiento asíncrono.

---

**✅ Una vez completada la migración, tendrás:**
- Sistema escalable y en producción
- API REST documentada automáticamente
- Interfaz web profesional
- Deployment automatizado en GCP
- Monitoreo y logs centralizados
- Base para tu tesis y presentación

🚀 **¡Adelante con la migración!**
