# 🚀 GUÍA DE INICIO RÁPIDO - CONTRACTIA AI

Esta guía te ayudará a tener tu aplicación web funcionando en menos de 30 minutos.

---

## ✅ Prerrequisitos (5 minutos)

1. **Cuenta de Google Cloud Platform**
   - Crea una cuenta en https://cloud.google.com/
   - Activa los créditos gratuitos de $300 USD

2. **Habilitar Vertex AI API**
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```

3. **Crear Cuenta de Servicio**
   - Ve a GCP Console → IAM y administración → Cuentas de servicio
   - Crea nueva cuenta de servicio
   - Asigna roles:
     * Vertex AI User
     * Storage Object Viewer (opcional)
   - Descarga el archivo JSON de credenciales

---

## 🖥️ Opción 1: Ejecutar Localmente (10 minutos)

### Paso 1: Instalar Python y dependencias

```bash
# Clonar o crear el directorio
mkdir contractia-ai
cd contractia-ai

# Copiar todos los archivos del proyecto aquí

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 2: Configurar credenciales

```bash
# Copiar tu archivo JSON de credenciales al proyecto
cp /ruta/a/tu/service-account-key.json ./gcp-credentials.json

# Configurar variable de entorno
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/gcp-credentials.json"

# En Windows PowerShell:
# $env:GOOGLE_APPLICATION_CREDENTIALS = "$(pwd)\gcp-credentials.json"
```

### Paso 3: Ejecutar

```bash
streamlit run app.py
```

¡Listo! Abre http://localhost:8501 en tu navegador.

---

## ☁️ Opción 2: Desplegar en la Nube GRATIS (15 minutos)

Esta es la **OPCIÓN RECOMENDADA** para tu prototipo.

### Paso 1: Subir a GitHub

```bash
# Inicializar Git (si no lo has hecho)
git init
git add .
git commit -m "Initial commit - CONTRACTIA AI"

# Crear repositorio en GitHub
# Ve a https://github.com/new y crea un nuevo repositorio llamado "contractia-ai"

# Conectar y subir
git remote add origin https://github.com/TU_USUARIO/contractia-ai.git
git branch -M main
git push -u origin main
```

### Paso 2: Desplegar en Streamlit Cloud

1. Ve a https://share.streamlit.io/
2. Inicia sesión con tu cuenta de GitHub
3. Click en **"New app"**
4. Selecciona:
   - Repository: `TU_USUARIO/contractia-ai`
   - Branch: `main`
   - Main file path: `app.py`
5. Click en **"Advanced settings"**
6. En **"Secrets"**, pega el contenido de tu archivo JSON de credenciales en formato TOML:

```toml
[gcp_service_account]
type = "service_account"
project_id = "tu-project-id-aqui"
private_key_id = "tu-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nTU_PRIVATE_KEY_AQUI\n-----END PRIVATE KEY-----\n"
client_email = "tu-service-account@tu-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

7. Click en **"Deploy"**
8. Espera 5-10 minutos mientras se construye

### Paso 3: Actualizar app.py

Agrega este código al inicio de `app.py` (línea ~15, después de los imports):

```python
import json
import tempfile

# Configurar credenciales para Streamlit Cloud
if "gcp_service_account" in st.secrets:
    service_account_info = dict(st.secrets["gcp_service_account"])
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(service_account_info, f)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f.name
```

Guarda y haz push:

```bash
git add app.py
git commit -m "Add Streamlit Cloud credentials support"
git push
```

¡Tu app se actualizará automáticamente y estará disponible en: `https://tu-app.streamlit.app`!

---

## 🧪 Probar la Aplicación

1. Abre la URL de tu aplicación
2. Ve a la pestaña **"Cargar Contrato"**
3. Sube un contrato PDF de prueba
4. Click en **"Iniciar Análisis"**
5. Espera 15-45 minutos (según el tamaño)
6. Ve a **"Resultados"** para ver el reporte completo

---

## 📝 Notas Importantes

### Para Desarrollo Local:
- La variable `GOOGLE_APPLICATION_CREDENTIALS` debe estar configurada en cada sesión
- Agrega esto a tu `.bashrc` o `.zshrc` para hacerlo permanente:
  ```bash
  export GOOGLE_APPLICATION_CREDENTIALS="/ruta/completa/a/gcp-credentials.json"
  ```

### Para Streamlit Cloud:
- Los secrets se mantienen privados y no se suben a GitHub
- Puedes actualizar los secrets en cualquier momento desde la configuración de la app
- La app se reconstruye automáticamente con cada push a GitHub

### Costos:
- **Streamlit Cloud**: 100% GRATIS (ilimitado)
- **Vertex AI**: Primeros $300 USD gratis (suficiente para ~100-200 contratos)
- **Después de créditos**: ~$1.50-3.50 USD por contrato

---

## ❓ ¿Problemas?

### Error: "GOOGLE_APPLICATION_CREDENTIALS not set"
- **Local**: Verifica que la variable de entorno esté configurada
- **Cloud**: Verifica que los secrets estén correctamente configurados en Streamlit

### Error: "Permission denied"
- Ve a GCP Console → IAM
- Asegúrate de que tu cuenta de servicio tenga el rol "Vertex AI User"

### La app no se actualiza en Streamlit Cloud
- Ve a la configuración de tu app → Click en "Reboot app"
- O haz un cambio dummy y push a GitHub

### Más ayuda
- Revisa el `README.md` completo
- Consulta la documentación de Streamlit: https://docs.streamlit.io/
- Documentación de Vertex AI: https://cloud.google.com/vertex-ai/docs

---

## 🎯 Próximos Pasos

Una vez que tu app esté funcionando:

1. **Personaliza la interfaz**
   - Edita `app.py` para cambiar colores, textos, etc.
   - Modifica `.streamlit/config.toml` para el tema

2. **Mejora el análisis**
   - Ajusta prompts en `contract_processor.py`
   - Experimenta con diferentes parámetros del LLM

3. **Agrega features**
   - Sistema de Q&A interactivo
   - Comparación de múltiples contratos
   - Exportación a Word/PDF

4. **Comparte**
   - Envía la URL pública a stakeholders
   - Recoge feedback
   - Itera y mejora

---

¡Éxito con tu proyecto! 🚀
