"""
Contract Processor Module
Contiene la lógica principal de procesamiento de contratos de CONTRACTIA AI
Adaptado del notebook original para uso en aplicación web
"""

import os
import re
from typing import List, Dict, Tuple, Optional
from pathlib import Path

# LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_google_vertexai import VertexAIEmbeddings, ChatVertexAI
from langchain_core.prompts import PromptTemplate

class ContractProcessor:
    """
    Procesador principal de contratos APP
    """
    
    def __init__(self, credentials=None, enable_llm=True, enable_rag=False, enable_chat=False):
        """
        Inicializa el procesador con configuraciones
        
        Args:
            credentials: Objeto de credenciales de Google Cloud
            enable_llm: Habilitar uso de LLM para análisis
            enable_rag: Habilitar RAG avanzado
            enable_chat: Habilitar sistema de Q&A
        """
        self.enable_llm = enable_llm
        self.enable_rag = enable_rag
        self.enable_chat = enable_chat
        
        # Inicializar embeddings y LLM (aproximadamente línea 39)
        if enable_llm:
            # 2. Pasa las credenciales a VertexAIEmbeddings
            self.embeddings = VertexAIEmbeddings(
                model_name="textembedding-gecko@latest",
                credentials=credentials # <--- MODIFICACIÓN
            )
            
            # 3. Pasa las credenciales a ChatVertexAI
            self.llm = ChatVertexAI(
                model_name="gemini-2.0-flash-exp",
                temperature=0.1,
                max_tokens=8192,
                credentials=credentials # <--- MODIFICACIÓN
            )
        
        # Configuraciones
        self.chunk_size = 2000
        self.chunk_overlap = 200
        
    def cargar_conocimiento(self, knowledge_dir: str) -> Optional[FAISS]:
        """
        Carga documentos de la base de conocimiento y crea vectorstore
        
        Args:
            knowledge_dir: Directorio con documentos normativos
            
        Returns:
            FAISS vectorstore o None
        """
        try:
            knowledge_path = Path(knowledge_dir)
            if not knowledge_path.exists() or not list(knowledge_path.iterdir()):
                print("No se encontraron documentos de conocimiento")
                return None
            
            documentos_combinados = []
            
            for file_path in knowledge_path.iterdir():
                if file_path.is_file():
                    print(f"Cargando: {file_path.name}")
                    
                    try:
                        if file_path.suffix.lower() == '.pdf':
                            loader = PyPDFLoader(str(file_path))
                        elif file_path.suffix.lower() == '.docx':
                            loader = UnstructuredFileLoader(str(file_path))
                        else:
                            continue
                        
                        docs = loader.load()
                        documentos_combinados.extend(docs)
                    except Exception as e:
                        print(f"Error cargando {file_path.name}: {e}")
            
            if not documentos_combinados:
                return None
            
            # Dividir en chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            chunks = text_splitter.split_documents(documentos_combinados)
            
            # Crear vectorstore
            vectorstore = FAISS.from_documents(chunks, self.embeddings)
            print(f"✅ Base de conocimiento creada con {len(chunks)} chunks")
            
            return vectorstore
            
        except Exception as e:
            print(f"Error cargando conocimiento: {e}")
            return None
    
    def procesar_contrato(self, contrato_path: str) -> Tuple[Optional[List], Optional[str]]:
        """
        Carga y procesa el contrato PDF
        
        Args:
            contrato_path: Ruta al archivo del contrato
            
        Returns:
            (documentos, texto_completo) o (None, None)
        """
        try:
            loader = PyPDFLoader(contrato_path)
            docs = loader.load()
            
            if not docs:
                return None, None
            
            texto_completo = "\n\n".join([doc.page_content for doc in docs])
            
            print(f"✅ Contrato cargado: {len(docs)} páginas")
            return docs, texto_completo
            
        except Exception as e:
            print(f"Error procesando contrato: {e}")
            return None, None
    
    def segmentar_contrato(self, texto_contrato: str) -> List[Dict]:
        """
        Segmenta el contrato en secciones estructuradas
        
        Args:
            texto_contrato: Texto completo del contrato
            
        Returns:
            Lista de secciones con metadata
        """
        # Normalizar texto
        texto = self._norm_text(texto_contrato)
        
        secciones = []
        
        # Patrones para detectar secciones
        patron_capitulo = re.compile(
            r"^[ \t]*Capítulo[ \t]+([IVXLCDM]+)[ \t]+(.+?)$",
            re.IGNORECASE | re.MULTILINE
        )
        
        patron_anexo = re.compile(
            r"^[ \t]*Anexo(?:s)?[ \t]+([IVXLCDM]+|\d+|[A-Z])[ \t]+(.+?)$",
            re.IGNORECASE | re.MULTILINE
        )
        
        patron_clausula = re.compile(
            r"^[ \t]*Cláusula[ \t]+(\d+(?:\.\d+)*)[\.\s]+(.+?)$",
            re.IGNORECASE | re.MULTILINE
        )
        
        # Encontrar todas las secciones
        lineas = texto.split('\n')
        seccion_actual = None
        contenido_actual = []
        
        for i, linea in enumerate(lineas):
            linea_limpia = linea.strip()
            
            # Detectar capítulo
            match_cap = patron_capitulo.match(linea_limpia)
            if match_cap:
                if seccion_actual:
                    seccion_actual['contenido'] = '\n'.join(contenido_actual)
                    secciones.append(seccion_actual)
                
                seccion_actual = {
                    'tipo': 'capitulo',
                    'numero': match_cap.group(1),
                    'titulo': match_cap.group(2).strip(),
                    'linea_inicio': i
                }
                contenido_actual = []
                continue
            
            # Detectar anexo
            match_anexo = patron_anexo.match(linea_limpia)
            if match_anexo:
                if seccion_actual:
                    seccion_actual['contenido'] = '\n'.join(contenido_actual)
                    secciones.append(seccion_actual)
                
                seccion_actual = {
                    'tipo': 'anexo',
                    'numero': match_anexo.group(1),
                    'titulo': match_anexo.group(2).strip(),
                    'linea_inicio': i
                }
                contenido_actual = []
                continue
            
            # Detectar cláusula
            match_clausula = patron_clausula.match(linea_limpia)
            if match_clausula:
                if seccion_actual and seccion_actual['tipo'] != 'clausula':
                    seccion_actual['contenido'] = '\n'.join(contenido_actual)
                    secciones.append(seccion_actual)
                
                seccion_actual = {
                    'tipo': 'clausula',
                    'numero': match_clausula.group(1),
                    'titulo': match_clausula.group(2).strip(),
                    'linea_inicio': i
                }
                contenido_actual = []
                continue
            
            # Agregar contenido
            if seccion_actual:
                contenido_actual.append(linea)
        
        # Agregar última sección
        if seccion_actual:
            seccion_actual['contenido'] = '\n'.join(contenido_actual)
            secciones.append(seccion_actual)
        
        print(f"✅ Contrato segmentado en {len(secciones)} secciones")
        return secciones
    
    def construir_indices(self, secciones: List[Dict]) -> Dict:
        """
        Construye índices de secciones, global y local
        
        Args:
            secciones: Lista de secciones del contrato
            
        Returns:
            Diccionario con índices construidos
        """
        indice_secciones = {}
        indice_global = {}
        indice_local = {}
        
        for seccion in secciones:
            tipo = seccion['tipo']
            numero = seccion['numero']
            titulo = seccion['titulo']
            
            # Índice de secciones
            clave = f"{tipo}_{numero}"
            indice_secciones[clave] = {
                'tipo': tipo,
                'numero': numero,
                'titulo': titulo,
                'contenido': seccion.get('contenido', '')
            }
            
            # Índice global (por tipo y número)
            if tipo not in indice_global:
                indice_global[tipo] = {}
            indice_global[tipo][numero] = titulo
            
            # Índice local (cláusulas dentro de capítulos)
            if tipo == 'clausula':
                # Buscar el capítulo padre
                numero_partes = numero.split('.')
                if len(numero_partes) > 1:
                    capitulo_num = numero_partes[0]
                    if capitulo_num not in indice_local:
                        indice_local[capitulo_num] = {}
                    indice_local[capitulo_num][numero] = titulo
        
        indices = {
            'secciones': indice_secciones,
            'global': indice_global,
            'local': indice_local,
            'total_secciones': len(secciones)
        }
        
        print(f"✅ Índices construidos: {len(indice_secciones)} secciones")
        return indices
    
    def auditar_contrato(
        self,
        secciones: List[Dict],
        indices: Dict,
        vectorstore_conocimiento: Optional[FAISS] = None
    ) -> Dict:
        """
        Realiza auditoría completa del contrato
        
        Args:
            secciones: Secciones del contrato
            indices: Índices construidos
            vectorstore_conocimiento: Base de conocimiento (opcional)
            
        Returns:
            Resultados de auditoría
        """
        resultados = {
            'total_referencias': 0,
            'referencias_rotas': 0,
            'hallazgos_consistencia': [],
            'hallazgos_por_seccion': {},
            'total_secciones': len(secciones)
        }
        
        # Patrón para detectar referencias
        patron_ref = re.compile(
            r'\b(?:Capítulo|Cláusula|Anexo|Artículo)\s+([IVXLCDM]+|\d+(?:\.\d+)*|[A-Z])\b',
            re.IGNORECASE
        )
        
        for seccion in secciones:
            contenido = seccion.get('contenido', '')
            seccion_id = f"{seccion['tipo']}_{seccion['numero']}"
            
            # Buscar referencias en el contenido
            referencias = patron_ref.findall(contenido)
            resultados['total_referencias'] += len(referencias)
            
            hallazgos_seccion = []
            
            # Validar cada referencia
            for ref_num in referencias:
                # Buscar en índice global
                encontrada = False
                for tipo, refs in indices['global'].items():
                    if ref_num in refs:
                        encontrada = True
                        break
                
                if not encontrada:
                    resultados['referencias_rotas'] += 1
                    hallazgos_seccion.append({
                        'tipo': 'referencia_rota',
                        'descripcion': f'Referencia no encontrada: {ref_num}',
                        'ubicacion': seccion_id,
                        'severidad': 'alta'
                    })
            
            # Validación de coherencia con LLM (si está habilitado)
            if self.enable_llm and len(contenido) > 100:
                try:
                    hallazgos_llm = self._validar_coherencia_llm(
                        contenido=contenido,
                        seccion_id=seccion_id,
                        vectorstore=vectorstore_conocimiento
                    )
                    hallazgos_seccion.extend(hallazgos_llm)
                except Exception as e:
                    print(f"Error en validación LLM para {seccion_id}: {e}")
            
            if hallazgos_seccion:
                resultados['hallazgos_por_seccion'][seccion_id] = hallazgos_seccion
                resultados['hallazgos_consistencia'].extend(hallazgos_seccion)
        
        print(f"✅ Auditoría completada:")
        print(f"   - Referencias totales: {resultados['total_referencias']}")
        print(f"   - Referencias rotas: {resultados['referencias_rotas']}")
        print(f"   - Hallazgos: {len(resultados['hallazgos_consistencia'])}")
        
        return resultados
    
    def _validar_coherencia_llm(
        self,
        contenido: str,
        seccion_id: str,
        vectorstore: Optional[FAISS] = None
    ) -> List[Dict]:
        """
        Valida coherencia de una sección usando LLM
        
        Args:
            contenido: Contenido de la sección
            seccion_id: Identificador de la sección
            vectorstore: Base de conocimiento para RAG
            
        Returns:
            Lista de hallazgos
        """
        hallazgos = []
        
        try:
            # Limitar contenido para análisis
            contenido_analisis = contenido[:4000] if len(contenido) > 4000 else contenido
            
            # Contexto adicional de RAG (si está habilitado)
            contexto_adicional = ""
            if self.enable_rag and vectorstore:
                docs_relevantes = vectorstore.similarity_search(contenido_analisis, k=2)
                contexto_adicional = "\n\n".join([doc.page_content for doc in docs_relevantes])
            
            # Prompt para análisis
            prompt = f"""
Analiza la siguiente sección de un contrato de concesión APP y detecta posibles problemas:

SECCIÓN: {seccion_id}

CONTENIDO:
{contenido_analisis}

{f"CONTEXTO NORMATIVO:{contexto_adicional}" if contexto_adicional else ""}

Identifica ÚNICAMENTE problemas claros y verificables:
1. Inconsistencias lógicas evidentes
2. Contradicciones internas
3. Términos indefinidos que se referencian
4. Fechas o plazos contradictorios
5. Montos o valores inconsistentes

Responde SOLO con hallazgos concretos en formato:
TIPO: [tipo_de_problema]
DESCRIPCIÓN: [descripción_breve]
SEVERIDAD: [alta/media/baja]

Si NO hay problemas claros, responde: "SIN_HALLAZGOS"
"""
            
            # Llamar al LLM
            response = self.llm.invoke(prompt)
            respuesta = response.content
            
            # Parsear respuesta
            if "SIN_HALLAZGOS" not in respuesta:
                # Extraer hallazgos del texto
                lineas = respuesta.strip().split('\n')
                hallazgo_actual = {}
                
                for linea in lineas:
                    if linea.startswith('TIPO:'):
                        if hallazgo_actual:
                            hallazgos.append(hallazgo_actual)
                        hallazgo_actual = {
                            'tipo': linea.replace('TIPO:', '').strip(),
                            'ubicacion': seccion_id
                        }
                    elif linea.startswith('DESCRIPCIÓN:'):
                        hallazgo_actual['descripcion'] = linea.replace('DESCRIPCIÓN:', '').strip()
                    elif linea.startswith('SEVERIDAD:'):
                        hallazgo_actual['severidad'] = linea.replace('SEVERIDAD:', '').strip()
                
                if hallazgo_actual:
                    hallazgos.append(hallazgo_actual)
        
        except Exception as e:
            print(f"Error en validación LLM: {e}")
        
        return hallazgos
    
    def _norm_text(self, s: str) -> str:
        """Normaliza texto eliminando caracteres especiales"""
        s = s.replace("\ufeff", "").replace("\r", "")
        s = s.replace("\u00a0", " ")
        s = s.replace("\u00ad", "")
        s = re.sub(r"\f", "\n", s)
        s = re.sub(r"[ \t]+", " ", s)
        s = re.sub(r"\n{3,}", "\n\n", s)
        return s.strip()
