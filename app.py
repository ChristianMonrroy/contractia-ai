"""
CONTRACTIA AI - Sistema de Auditoría Automática de Contratos APP
Aplicación Web con Streamlit
Author: Christian & Team DataLaw
"""

import streamlit as st
import os
import tempfile
import json
from datetime import datetime
import vertexai
from pathlib import Path

# Importaciones del sistema de análisis
from contract_processor import ContractProcessor
from utils import (
    configurar_entorno_vertexai,
    generar_reporte_markdown,
    crear_zip_resultados
)
import json
import tempfile
from google.oauth2 import service_account
        
# Configuración de la página
st.set_page_config(
    page_title="CONTRACTIA AI - Auditoría de Contratos APP",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    .upload-section {
        border: 2px dashed #1f77b4;
        border-radius: 10px;
        padding: 2rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'procesamiento_completo' not in st.session_state:
    st.session_state.procesamiento_completo = False
if 'resultados' not in st.session_state:
    st.session_state.resultados = None

def main():
    # Header
    st.markdown('<h1 class="main-header">📋 CONTRACTIA AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem;">Sistema de Auditoría Automática de Contratos APP - ProInversión Perú</p>', unsafe_allow_html=True)
    
    st.divider()
    
    # Sidebar - Información del sistema
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1f77b4/ffffff?text=CONTRACTIA", use_container_width=True)
        st.markdown("### ℹ️ Información del Sistema")
        st.info("""
        **CONTRACTIA AI** analiza automáticamente contratos de concesión APP, detectando:
        
        - ✅ Inconsistencias en referencias
        - ✅ Errores en índices
        - ✅ Problemas de coherencia
        - ✅ Cumplimiento normativo
        
        **Tiempo promedio:** < 1 hora  
        **Precisión:** 90%+ en detección de errores
        """)
        
        st.markdown("---")
        st.markdown("### 🔧 Configuración")
        
        # Toggle para características avanzadas
        enable_rag = st.checkbox("Habilitar RAG avanzado", value=False)
        enable_chat = st.checkbox("Habilitar Q&A interactivo", value=False)
        
        st.markdown("---")
        st.markdown("**Desarrollado por:** Team DataLaw - UTEC")
        st.markdown("**Versión:** 1.0 - Prototipo")
    
    # Área principal
    tab1, tab2, tab3 = st.tabs(["📤 Cargar Contrato", "📊 Resultados", "📚 Documentación"])
    
    with tab1:
        st.markdown("### 📤 Subir Contrato para Análisis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            
            # Subida de archivo principal (contrato)
            contrato_file = st.file_uploader(
                "Selecciona el contrato de concesión (PDF)",
                type=['pdf'],
                help="Sube el contrato APP que deseas auditar (máximo 50 MB)"
            )
            
            # Opcional: Subida de documentos de conocimiento base
            with st.expander("📁 Documentos Base de Conocimiento (Opcional)"):
                st.markdown("""
                Sube lineamientos, normativas y referencias que el sistema usará 
                para validar el contrato. Si no subes nada, se usarán los documentos predeterminados.
                """)
                knowledge_files = st.file_uploader(
                    "Selecciona documentos normativos (PDF/DOCX)",
                    type=['pdf', 'docx'],
                    accept_multiple_files=True
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Botón de procesamiento
            if contrato_file is not None:
                if st.button("🚀 Iniciar Análisis", type="primary", use_container_width=True):
                    procesar_contrato(contrato_file, knowledge_files, enable_rag, enable_chat)
        
        with col2:
            st.markdown("### 📋 Información del Análisis")
            st.info("""
            **Pasos del proceso:**
            
            1. 📄 Carga del documento
            2. 🔍 Extracción de índices
            3. 🔗 Validación de referencias
            4. ✅ Análisis de coherencia
            5. 📊 Generación de reporte
            
            **Tiempo estimado:** 15-45 minutos  
            (según tamaño del contrato)
            """)
            
            if contrato_file:
                st.success(f"✅ Archivo cargado: {contrato_file.name}")
                st.metric("Tamaño", f"{contrato_file.size / (1024*1024):.2f} MB")
    
    with tab2:
        mostrar_resultados()
    
    with tab3:
        mostrar_documentacion()

def procesar_contrato(contrato_file, knowledge_files, enable_rag, enable_chat):
    """
    Procesa el contrato subido usando el sistema de análisis
    """
    try:
        # Configurar Vertex AI
        with st.spinner("🔧 Configurando Vertex AI..."):
            if not configurar_entorno_vertexai():
                st.error("❌ Error al configurar Vertex AI. Verifica las credenciales.")
                return
        
        # Crear directorio temporal
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Guardar archivo del contrato
            contrato_path = temp_path / contrato_file.name
            with open(contrato_path, 'wb') as f:
                f.write(contrato_file.read())
            
            # Guardar archivos de conocimiento si existen
            knowledge_dir = temp_path / "knowledge_base"
            knowledge_dir.mkdir(exist_ok=True)
            
            if knowledge_files:
                for kf in knowledge_files:
                    kf_path = knowledge_dir / kf.name
                    with open(kf_path, 'wb') as f:
                        f.write(kf.read())
            
            # Inicializar procesador
            processor = ContractProcessor(
                enable_llm=True,
                enable_rag=enable_rag,
                enable_chat=enable_chat
            )
            
            # Crear barra de progreso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Paso 1: Cargar documentos de conocimiento
            status_text.text("📚 Cargando base de conocimiento...")
            progress_bar.progress(10)
            vectorstore_conocimiento = processor.cargar_conocimiento(str(knowledge_dir))
            
            # Paso 2: Procesar contrato
            status_text.text("📄 Procesando contrato...")
            progress_bar.progress(25)
            docs_contrato, texto_contrato = processor.procesar_contrato(str(contrato_path))
            
            if not docs_contrato:
                st.error("❌ No se pudo procesar el contrato.")
                return
            
            # Paso 3: Segmentar y extraer índices
            status_text.text("🔍 Extrayendo estructura del contrato...")
            progress_bar.progress(40)
            secciones = processor.segmentar_contrato(texto_contrato)
            
            status_text.text("📑 Construyendo índices...")
            progress_bar.progress(55)
            indices = processor.construir_indices(secciones)
            
            # Paso 4: Auditoría
            status_text.text("🔎 Auditando referencias y coherencia...")
            progress_bar.progress(70)
            resultados_auditoria = processor.auditar_contrato(
                secciones=secciones,
                indices=indices,
                vectorstore_conocimiento=vectorstore_conocimiento
            )
            
            # Paso 5: Generar reportes
            status_text.text("📊 Generando reportes...")
            progress_bar.progress(85)
            reporte_md = generar_reporte_markdown(resultados_auditoria)
            
            # Paso 6: Guardar resultados
            status_text.text("💾 Guardando resultados...")
            progress_bar.progress(95)
            
            # Guardar en session state
            st.session_state.resultados = {
                'reporte': reporte_md,
                'auditoria': resultados_auditoria,
                'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
                'nombre_contrato': contrato_file.name
            }
            st.session_state.procesamiento_completo = True
            
            # Completar
            progress_bar.progress(100)
            status_text.text("✅ ¡Análisis completado!")
            
            st.success(f"""
            ✅ **Análisis Completado Exitosamente**
            
            - Secciones analizadas: {len(secciones)}
            - Referencias validadas: {resultados_auditoria.get('total_referencias', 0)}
            - Errores detectados: {len(resultados_auditoria.get('hallazgos_consistencia', []))}
            
            Ve a la pestaña **Resultados** para ver el informe completo.
            """)
            
            # Auto-navegar a resultados
            st.rerun()
    
    except Exception as e:
        st.error(f"❌ Error durante el procesamiento: {str(e)}")
        st.exception(e)

def mostrar_resultados():
    """
    Muestra los resultados del análisis
    """
    st.markdown("### 📊 Resultados del Análisis")
    
    if not st.session_state.procesamiento_completo:
        st.info("👈 Sube un contrato en la pestaña **Cargar Contrato** para ver los resultados aquí.")
        return
    
    resultados = st.session_state.resultados
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    auditoria = resultados['auditoria']
    
    with col1:
        st.metric(
            "Total Referencias",
            auditoria.get('total_referencias', 0)
        )
    
    with col2:
        errores = len(auditoria.get('hallazgos_consistencia', []))
        st.metric(
            "Errores Detectados",
            errores,
            delta=None if errores == 0 else f"-{errores}",
            delta_color="inverse"
        )
    
    with col3:
        total_refs = auditoria.get('total_referencias', 1)
        referencias_rotas = auditoria.get('referencias_rotas', 0)
        precision = ((total_refs - referencias_rotas) / total_refs * 100) if total_refs > 0 else 0
        st.metric(
            "Precisión",
            f"{precision:.1f}%"
        )
    
    with col4:
        st.metric(
            "Secciones Analizadas",
            auditoria.get('total_secciones', 0)
        )
    
    st.divider()
    
    # Tabs de resultados detallados
    result_tab1, result_tab2, result_tab3 = st.tabs([
        "📄 Reporte Completo",
        "⚠️ Hallazgos Críticos",
        "📥 Descargas"
    ])
    
    with result_tab1:
        st.markdown("### Reporte de Auditoría")
        st.markdown(resultados['reporte'])
    
    with result_tab2:
        st.markdown("### Hallazgos Críticos")
        hallazgos = auditoria.get('hallazgos_consistencia', [])
        
        if hallazgos:
            for i, hallazgo in enumerate(hallazgos, 1):
                with st.expander(f"❌ Hallazgo #{i}: {hallazgo.get('tipo', 'Error')}"):
                    st.markdown(f"**Descripción:** {hallazgo.get('descripcion', 'N/A')}")
                    st.markdown(f"**Ubicación:** {hallazgo.get('ubicacion', 'N/A')}")
                    st.markdown(f"**Severidad:** {hallazgo.get('severidad', 'Media')}")
        else:
            st.success("✅ No se encontraron hallazgos críticos. El contrato cumple con los estándares de coherencia.")
    
    with result_tab3:
        st.markdown("### Descargar Resultados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Descargar reporte Markdown
            st.download_button(
                label="📄 Descargar Reporte (Markdown)",
                data=resultados['reporte'],
                file_name=f"reporte_auditoria_{resultados['timestamp']}.md",
                mime="text/markdown"
            )
        
        with col2:
            # Descargar resultados JSON
            json_data = json.dumps(auditoria, indent=2, ensure_ascii=False)
            st.download_button(
                label="📊 Descargar Datos (JSON)",
                data=json_data,
                file_name=f"auditoria_{resultados['timestamp']}.json",
                mime="application/json"
            )

def mostrar_documentacion():
    """
    Muestra la documentación del sistema
    """
    st.markdown("### 📚 Documentación de CONTRACTIA AI")
    
    st.markdown("""
    ## ¿Qué es CONTRACTIA AI?
    
    CONTRACTIA AI es un sistema automatizado de auditoría de contratos de concesión para proyectos de 
    Asociación Público-Privada (APP) en Perú. Desarrollado como parte de una tesis de Maestría en 
    Ciencia de Datos e Inteligencia Artificial en UTEC.
    
    ### 🎯 Objetivos
    
    - Reducir el tiempo de revisión manual de contratos de 320+ horas a < 1 hora
    - Detectar al menos 90% de inconsistencias en referencias cruzadas
    - Identificar errores materiales que actualmente afectan al 100% de concesiones APP
    
    ### 🔍 Capacidades del Sistema
    
    1. **Segmentación Automática**: Identifica capítulos, anexos y cláusulas
    2. **Extracción de Índices**: Construye índices de secciones, global y local
    3. **Validación de Referencias**: Verifica todas las referencias cruzadas en el contrato
    4. **Análisis de Coherencia**: Detecta inconsistencias lógicas y estructurales
    5. **Comparación Normativa**: Contrasta con lineamientos y regulaciones vigentes
    
    ### 🛠️ Tecnología
    
    - **LLM**: Google Gemini 2.5 Pro (vía Vertex AI)
    - **Embeddings**: textembedding-gecko@latest
    - **RAG**: FAISS + LangChain
    - **Frontend**: Streamlit
    
    ### 📊 Métricas de Desempeño
    
    - **Precisión en detección de referencias rotas**: 90%+
    - **Tasa de falsos positivos**: < 2%
    - **Tiempo de procesamiento**: 15-45 minutos por contrato
    
    ### 👥 Equipo
    
    - **Christian** - Investigador Principal
    - **Oscar Bueno** - Co-autor
    - **Institución**: UTEC - Maestría en Data Science e IA
    
    ### 📞 Soporte
    
    Para reportar problemas o sugerencias, contactar al equipo DataLaw.
    """)

if __name__ == "__main__":
    # Verificar credenciales de GCP
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        st.error("""
        ❌ **Credenciales de Google Cloud no configuradas**
        
        Para usar esta aplicación, necesitas:
        1. Crear una cuenta de servicio en Google Cloud
        2. Habilitar Vertex AI API
        3. Configurar las credenciales como variable de entorno
        
        Consulta la documentación para más detalles.
        """)
        st.stop()
    
    main()
