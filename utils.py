"""
Utils Module
Funciones auxiliares para CONTRACTIA AI
"""

import os
import vertexai
from datetime import datetime
from typing import Dict
import zipfile
from pathlib import Path

def configurar_entorno_vertexai() -> bool:
    """
    Configura el entorno de Vertex AI
    
    Returns:
        True si la configuración fue exitosa, False en caso contrario
    """
    try:
        # Obtener credenciales del entorno
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path:
            print("❌ Variable GOOGLE_APPLICATION_CREDENTIALS no configurada")
            return False
        
        # Configuración del proyecto
        PROJECT_ID = os.getenv("GCP_PROJECT_ID", "agenteia-471917")
        LOCATION = os.getenv("GCP_LOCATION", "us-central1")
        
        # Inicializar Vertex AI
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        
        print(f"✅ Vertex AI inicializado:")
        print(f"   - Proyecto: {PROJECT_ID}")
        print(f"   - Ubicación: {LOCATION}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando Vertex AI: {e}")
        return False


def generar_reporte_markdown(resultados: Dict) -> str:
    """
    Genera un reporte en formato Markdown a partir de los resultados de auditoría
    
    Args:
        resultados: Diccionario con resultados de auditoría
        
    Returns:
        Reporte en formato Markdown
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    reporte = f"""# 📋 Reporte de Auditoría de Contrato APP

**CONTRACTIA AI - Sistema Automatizado de Auditoría**  
**Fecha de análisis:** {timestamp}

---

## 📊 Resumen Ejecutivo

| Métrica | Valor |
|---------|-------|
| **Total de Secciones Analizadas** | {resultados.get('total_secciones', 0)} |
| **Referencias Totales Encontradas** | {resultados.get('total_referencias', 0)} |
| **Referencias Rotas Detectadas** | {resultados.get('referencias_rotas', 0)} |
| **Total de Hallazgos** | {len(resultados.get('hallazgos_consistencia', []))} |

### Precisión de Referencias
"""
    
    total_refs = resultados.get('total_referencias', 1)
    referencias_rotas = resultados.get('referencias_rotas', 0)
    if total_refs > 0:
        precision = ((total_refs - referencias_rotas) / total_refs) * 100
        reporte += f"- **Tasa de éxito:** {precision:.2f}%\n"
        reporte += f"- **Tasa de error:** {(100 - precision):.2f}%\n"
    else:
        reporte += "- No se encontraron referencias para analizar\n"
    
    reporte += "\n---\n\n"
    
    # Hallazgos por severidad
    hallazgos = resultados.get('hallazgos_consistencia', [])
    if hallazgos:
        reporte += "## ⚠️ Hallazgos Detectados\n\n"
        
        # Clasificar por severidad
        hallazgos_alta = [h for h in hallazgos if h.get('severidad') == 'alta']
        hallazgos_media = [h for h in hallazgos if h.get('severidad') == 'media']
        hallazgos_baja = [h for h in hallazgos if h.get('severidad') == 'baja']
        
        reporte += f"### 🔴 Severidad Alta ({len(hallazgos_alta)} hallazgos)\n\n"
        for i, h in enumerate(hallazgos_alta, 1):
            reporte += f"**{i}. {h.get('tipo', 'Error desconocido')}**\n"
            reporte += f"- **Ubicación:** {h.get('ubicacion', 'N/A')}\n"
            reporte += f"- **Descripción:** {h.get('descripcion', 'N/A')}\n\n"
        
        reporte += f"\n### 🟡 Severidad Media ({len(hallazgos_media)} hallazgos)\n\n"
        for i, h in enumerate(hallazgos_media, 1):
            reporte += f"**{i}. {h.get('tipo', 'Error desconocido')}**\n"
            reporte += f"- **Ubicación:** {h.get('ubicacion', 'N/A')}\n"
            reporte += f"- **Descripción:** {h.get('descripcion', 'N/A')}\n\n"
        
        reporte += f"\n### 🔵 Severidad Baja ({len(hallazgos_baja)} hallazgos)\n\n"
        for i, h in enumerate(hallazgos_baja, 1):
            reporte += f"**{i}. {h.get('tipo', 'Error desconocido')}**\n"
            reporte += f"- **Ubicación:** {h.get('ubicacion', 'N/A')}\n"
            reporte += f"- **Descripción:** {h.get('descripcion', 'N/A')}\n\n"
    else:
        reporte += "## ✅ Sin Hallazgos Críticos\n\n"
        reporte += "El contrato cumple con los estándares de coherencia y validación.\n"
    
    reporte += "\n---\n\n"
    
    # Hallazgos por sección
    hallazgos_por_seccion = resultados.get('hallazgos_por_seccion', {})
    if hallazgos_por_seccion:
        reporte += "## 📑 Hallazgos por Sección\n\n"
        
        for seccion_id, hallazgos_sec in hallazgos_por_seccion.items():
            reporte += f"### {seccion_id}\n\n"
            reporte += f"Total de hallazgos: **{len(hallazgos_sec)}**\n\n"
            
            for i, h in enumerate(hallazgos_sec, 1):
                reporte += f"{i}. **{h.get('tipo', 'Error')}** - {h.get('descripcion', 'N/A')}\n"
            
            reporte += "\n"
    
    # Recomendaciones
    reporte += "---\n\n## 💡 Recomendaciones\n\n"
    
    if referencias_rotas > 0:
        reporte += f"1. **Corregir referencias rotas:** Se detectaron {referencias_rotas} referencias que no apuntan a secciones existentes. Revisar y corregir todas las referencias cruzadas.\n\n"
    
    if len(hallazgos_alta) > 0:
        reporte += f"2. **Atender hallazgos críticos:** Hay {len(hallazgos_alta)} hallazgos de severidad alta que requieren atención inmediata.\n\n"
    
    reporte += "3. **Revisión legal:** Someter el contrato a revisión legal experta antes de la firma final.\n\n"
    reporte += "4. **Validación cruzada:** Contrastar con lineamientos vigentes de ProInversión y el MEF.\n\n"
    
    # Footer
    reporte += "---\n\n"
    reporte += "*Reporte generado automáticamente por CONTRACTIA AI*  \n"
    reporte += "*Team DataLaw - UTEC | Maestría en Data Science e Inteligencia Artificial*\n"
    
    return reporte


def crear_zip_resultados(
    reporte_md: str,
    resultados_json: str,
    timestamp: str,
    output_path: str = "/tmp"
) -> str:
    """
    Crea un archivo ZIP con todos los resultados
    
    Args:
        reporte_md: Contenido del reporte en Markdown
        resultados_json: Resultados en formato JSON
        timestamp: Timestamp del análisis
        output_path: Directorio donde guardar el ZIP
        
    Returns:
        Ruta al archivo ZIP creado
    """
    try:
        zip_filename = f"resultados_auditoria_{timestamp}.zip"
        zip_path = os.path.join(output_path, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Agregar reporte Markdown
            zipf.writestr("reporte_auditoria.md", reporte_md)
            
            # Agregar resultados JSON
            zipf.writestr("resultados_detallados.json", resultados_json)
            
            # Agregar README
            readme = f"""# Resultados de Auditoría CONTRACTIA AI

Fecha: {timestamp}

## Contenido del archivo

1. **reporte_auditoria.md** - Reporte completo en formato Markdown
2. **resultados_detallados.json** - Datos estructurados en JSON

## Uso

### Reporte Markdown
Puedes abrir el archivo `.md` con cualquier editor de texto o visualizador de Markdown.

### Datos JSON
Los datos estructurados pueden ser procesados programáticamente o importados a otras herramientas.

## Soporte

Para consultas sobre los resultados, contactar al equipo DataLaw.

---
*CONTRACTIA AI - Sistema de Auditoría Automatizada de Contratos APP*
"""
            zipf.writestr("README.txt", readme)
        
        print(f"✅ ZIP creado: {zip_path}")
        return zip_path
        
    except Exception as e:
        print(f"❌ Error creando ZIP: {e}")
        return None


def validar_pdf(file_path: str) -> bool:
    """
    Valida que el archivo sea un PDF válido
    
    Args:
        file_path: Ruta al archivo
        
    Returns:
        True si es un PDF válido, False en caso contrario
    """
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            return header == b'%PDF'
    except Exception:
        return False


def estimar_tiempo_procesamiento(size_mb: float) -> str:
    """
    Estima el tiempo de procesamiento basado en el tamaño del archivo
    
    Args:
        size_mb: Tamaño del archivo en MB
        
    Returns:
        Estimación de tiempo como string
    """
    # Estimaciones basadas en benchmark
    if size_mb < 5:
        return "5-10 minutos"
    elif size_mb < 10:
        return "10-20 minutos"
    elif size_mb < 20:
        return "20-35 minutos"
    else:
        return "35-45 minutos"


def limpiar_temporales(directorio: str):
    """
    Limpia archivos temporales después del procesamiento
    
    Args:
        directorio: Directorio con archivos temporales
    """
    try:
        path = Path(directorio)
        if path.exists():
            for item in path.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    limpiar_temporales(str(item))
                    item.rmdir()
            print(f"✅ Temporales limpiados: {directorio}")
    except Exception as e:
        print(f"⚠️ Error limpiando temporales: {e}")
