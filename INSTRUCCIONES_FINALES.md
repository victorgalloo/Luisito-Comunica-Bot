# ✅ Instrucciones Finales - Proyecto Completado

¡El proyecto está 100% configurado para usar **Azure OpenAI**! 🎉

## 🔄 Cambios Realizados

He actualizado todos los archivos para usar **Azure OpenAI** en lugar de OpenAI directo:

### Archivos Modificados:
- ✅ `chatbot.py` - Ahora usa `AzureOpenAIEmbeddings` y `AzureChatOpenAI`
- ✅ `build_vectorstore.py` - Usa `AzureOpenAIEmbeddings` 
- ✅ `check_config.py` - Verifica configuración de Azure OpenAI
- ✅ `docker-compose.yml` - Variables de entorno de Azure OpenAI
- ✅ `requirements.txt` - Agregado `azure-openai==1.0.0`
- ✅ `.env.example` - Variables de Azure OpenAI
- ✅ `README.md` - Documentación actualizada
- ✅ `QUICKSTART.md` - Guía actualizada

---

## 📝 Lo Que TÚ Debes Hacer Ahora

### 1️⃣ Configurar Azure OpenAI

#### Paso A: Crear recurso en Azure
1. Ve a [Azure Portal](https://portal.azure.com)
2. Busca "Azure OpenAI" → "Create"
3. Configura:
   - **Subscription**: Tu suscripción
   - **Resource Group**: Nuevo o existente
   - **Region**: Cualquiera que soporte Azure OpenAI (ej: East US)
   - **Name**: `luisito-openai` (o el que prefieras)
   - **Pricing tier**: Standard S0
4. Click "Review + create" → "Create"

#### Paso B: Obtener Endpoint y API Key
1. Ve a tu recurso Azure OpenAI
2. En "Keys and Endpoint" → Copia:
   - **Endpoint**: `https://luisito-openai.openai.azure.com`
   - **API Key**: Cualquiera de las dos keys

#### Paso C: Crear Deployments
1. En el menú izquierdo: "Deployments" → "Create"
2. Crear **2 deployments**:
   
   **Deployment 1 - Embeddings:**
   - **Model**: `text-embedding-ada-002`
   - **Name**: `text-embedding-ada-002` (o el que prefieras)
   - **Version**: Use default
   
   **Deployment 2 - Chat:**
   - **Model**: `gpt-4o-mini`
   - **Name**: `gpt-4o-mini` (o el que prefieras)
   - **Version**: Use default

⚠️ **Importante**: Toma nota de los nombres que das a los deployments

### 2️⃣ Configurar el archivo .env

Crea el archivo `.env`:

```bash
# Opción fácil: copiar el ejemplo
cp .env.example .env

# Luego edita .env con tus valores reales
nano .env  # o usa tu editor favorito
```

**Ejemplo de .env completo:**

```bash
# MCP Configuration
MCP_URL=http://mcp-youtube-transcript:8080

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=TU_ACCOUNT;AccountKey=TU_KEY;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER=luisito-transcripts

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://luisito-openai.openai.azure.com
AZURE_OPENAI_API_KEY=TU_AZURE_OPENAI_KEY
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002

# YouTube Channel ID
YOUTUBE_CHANNEL_ID=UCECJDeK0MNapZbpaOzxrUPA
```

**Reemplaza:**
- `TU_ACCOUNT` - Nombre de tu cuenta de Azure Storage
- `TU_KEY` - Tu key de Azure Storage
- `https://luisito-openai.openai.azure.com` - Tu endpoint de Azure OpenAI
- `TU_AZURE_OPENAI_KEY` - Tu API key de Azure OpenAI
- Los deployment names si los cambiaste

### 3️⃣ Verificar Configuración

```bash
python check_config.py
```

Deberías ver:
- ✅ Docker: Instalado
- ✅ Docker Compose: Instalado
- ✅ Azure Blob Storage: Conectado correctamente
- ✅ Azure OpenAI: Conectado correctamente
- ✅ Todas las variables configuradas

Si algo falla, el script te dirá exactamente qué corregir.

### 4️⃣ Crear Lista de Videos

Crea `data/video_list.json` con al menos un video de prueba:

```bash
mkdir -p data
cat > data/video_list.json << 'EOF'
[
  {
    "video_id": "VIDEO_ID_DE_PRUEBA",
    "title": "Título del video",
    "published_at": "2024-01-01T00:00:00Z"
  }
]
EOF
```

**Para obtener un VIDEO_ID:**
1. Ve a un video de Luisito Comunica en YouTube
2. Copia la URL: `https://www.youtube.com/watch?v=ESTE_ES_EL_ID`
3. Copia el ID

### 5️⃣ Ejecutar el Proyecto

```bash
# 1. Iniciar MCP server
docker-compose up -d mcp-youtube-transcript

# Esperar 10 segundos para que inicie

# 2. Verificar logs
docker-compose logs -f mcp-youtube-transcript
# Deberías ver: "Server listening on port 8080"

# 3. Transcribir videos
docker-compose --profile transcriber up transcriber

# Esto tomará varios minutos dependiendo de cuántos videos tengas
# Verás logs como:
# [1/1] Transcribiendo: Título del video...
# Intento 1: MCP en http://mcp-youtube-transcript:8080...
# MCP exitoso
# Subido: video_id...

# 4. Ejecutar chatbot
docker-compose --profile chatbot up chatbot

# 5. Abrir en navegador
open http://localhost:8501
```

### 6️⃣ Probar el Chatbot

En el navegador, prueba preguntas como:
- "¿De qué trata el video?"
- "¿Qué lugares visitó Luisito?"
- "Cuéntame sobre X"

---

## 🆘 Si Algo Falla

### Error: "AZURE_OPENAI_ENDPOINT no está configurado"

**Solución**: Verifica que `.env` existe y tiene todas las variables de Azure OpenAI

### Error: "Azure OpenAI: Error conectando"

**Soluciones**:
1. Verifica que el endpoint esté correcto (sin `/` al final)
2. Verifica que la API key sea correcta
3. Verifica que los deployments existan en Azure

### Error: "Deployment not found"

**Solución**: Los nombres de los deployments en `.env` deben coincidir exactamente con los que creaste en Azure

### Error: "Container needs to be created in Azure"

**Solución**: El script lo crea automáticamente, pero verifica que tu connection string sea correcta

### MCP no responde

**Solución**:
```bash
docker-compose restart mcp-youtube-transcript
docker-compose logs mcp-youtube-transcript
```

---

## 📊 Costos Estimados

### Azure Blob Storage
- ~$0.30/mes por 50MB de transcripciones

### Azure OpenAI
- **Embeddings** (text-embedding-ada-002): ~$0.10 por 1M tokens
- **Chat** (gpt-4o-mini): ~$0.15 por 1M tokens input
- **Total estimado**: ~$10-15/mes con uso moderado

💡 **Consejo**: Azure OpenAI te da $200 gratis si es tu primera vez

---

## ✅ Checklist Final

Antes de celebrar, verifica:

- [ ] Azure OpenAI creado y configurado
- [ ] Deployments creados (embeddings + chat)
- [ ] Archivo `.env` completo con tus credenciales
- [ ] `check_config.py` pasa sin errores
- [ ] `data/video_list.json` tiene al menos un video
- [ ] Docker Desktop está corriendo
- [ ] MCP server iniciado (puerto 8080)
- [ ] Transcripciones generadas exitosamente
- [ ] Vector store construido
- [ ] Chatbot accesible en http://localhost:8501
- [ ] Chatbot responde preguntas correctamente

---

## 🎉 ¡Listo!

Si todo el checklist está ✅, ¡tu chatbot está funcionando!

**Próximos pasos sugeridos:**
1. Agregar más videos a `data/video_list.json`
2. Personalizar el chatbot (prompts, nombre, etc.)
3. Desplegar a producción (Azure Container Apps, etc.)
4. Agregar features (estadísticas, más modelos, etc.)

---

## 📞 Ayuda Adicional

- `README.md` - Documentación completa
- `SETUP_INSTRUCTIONS.md` - Guía detallada de setup
- `QUICKSTART.md` - Inicio rápido
- Logs: `docker-compose logs -f [servicio]`

**¿Problemas?** Ejecuta `python check_config.py` para diagnóstico automático.

