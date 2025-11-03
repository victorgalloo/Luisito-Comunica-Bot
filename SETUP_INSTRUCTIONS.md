# 📋 Instrucciones de Configuración Paso a Paso

Esta guía te llevará a través de la configuración completa del proyecto Luisito Comunica Chatbot.

## 🎯 Objetivo

Crear un chatbot que responde preguntas sobre los videos de Luisito Comunica usando transcripciones y RAG.

## ⏱️ Tiempo Estimado

- Configuración inicial: 15-20 minutos
- Transcribir videos: 30-60 minutos (depende de cantidad)
- Construir vector store: 10-15 minutos
- Total: ~1-2 horas

---

## 📝 Paso 1: Prerrequisitos

### 1.1 Instalar Docker Desktop

**macOS:**
```bash
# Descarga desde: https://www.docker.com/products/docker-desktop/
brew install --cask docker
```

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

**Verificar instalación:**
```bash
docker --version
docker-compose --version
```

### 1.2 Obtener Credenciales Necesarias

Necesitas:
1. ✅ Azure Blob Storage (Connection String)
2. ✅ OpenAI API Key
3. ✅ (Opcional) YouTube Data API Key

---

## 🔧 Paso 2: Configurar Azure Blob Storage

### 2.1 Crear cuenta en Azure

1. Ve a https://azure.microsoft.com/free/
2. Crea una cuenta gratuita
3. Obtén $200 en créditos por 30 días

### 2.2 Crear Storage Account

1. En Azure Portal, busca "Storage Accounts"
2. Click "Create"
3. Configuración:
   - **Resource Group**: Crea uno nuevo o usa existente
   - **Storage account name**: `luisito-bot` (debe ser único)
   - **Region**: Elige la más cercana
   - **Performance**: Standard
   - **Redundancy**: LRS (más barato)
4. Click "Review + Create"

### 2.3 Obtener Connection String

1. Ve a tu Storage Account
2. En el menú izquierdo: "Access Keys"
3. Click "Show" en cualquiera de las keys
4. Copia "Connection string"

### 2.4 Crear Contenedor (Opcional)

El script lo crea automáticamente, pero puedes hacerlo manualmente:

1. Ve a "Containers" en tu Storage Account
2. Click "New container"
3. Nombre: `luisito-transcripts`
4. Public access level: Private

---

## 🔑 Paso 3: Configurar OpenAI

### 3.1 Crear cuenta en OpenAI

1. Ve a https://platform.openai.com/
2. Crea una cuenta
3. Agrega método de pago (requerido para usar APIs)

### 3.2 Obtener API Key

1. Ve a https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Nombre: `Luisito Chatbot`
4. Copia la key (solo se muestra una vez)
5. Guárdala en un lugar seguro

### 3.3 Verificar Límites

1. Ve a https://platform.openai.com/account/limits
2. Verifica que tengas:
   - Embeddings habilitadas
   - Chat habilitado
   - Límites suficientes

---

## 📽️ Paso 4: Configurar YouTube Data API (Opcional)

**Necesitas esto solo si quieres obtener la lista de videos automáticamente.**

### 4.1 Crear proyecto en Google Cloud

1. Ve a https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Nombre: `Luisito Bot`
4. Click "Create"

### 4.2 Habilitar YouTube Data API v3

1. Ve a "APIs & Services" → "Library"
2. Busca "YouTube Data API v3"
3. Click "Enable"

### 4.3 Crear API Key

1. Ve a "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "API Key"
3. Copia la API Key

### 4.4 Restringir API Key (Recomendado)

1. Click en tu API Key
2. Bajo "API restrictions":
   - Selecciona "Restrict key"
   - Elige "YouTube Data API v3"
3. Click "Save"

---

## ⚙️ Paso 5: Configurar el Proyecto

### 5.1 Clonar/Descargar el proyecto

```bash
cd /Users/victorgallo/LuisitoComunica
```

### 5.2 Crear archivo .env

```bash
# En el terminal, desde el directorio del proyecto:
cat > .env << 'EOF'
# MCP Configuration
MCP_URL=http://mcp-youtube-transcript:8080

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=LUISITO-BOT;AccountKey=TU_KEY_AQUI;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER=luisito-transcripts

# OpenAI API
OPENAI_API_KEY=sk-TU_OPENAI_KEY_AQUI

# YouTube
YOUTUBE_CHANNEL_ID=UCECJDeK0MNapZbpaOzxrUPA

# Opcional: YouTube Data API
YOUTUBE_API_KEY=TU_YOUTUBE_API_KEY_AQUI
EOF
```

**Importante:** Reemplaza los valores con tus credenciales reales.

### 5.3 Verificar configuración

```bash
# Verificar que las variables se cargan correctamente
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('OK' if os.getenv('OPENAI_API_KEY') else 'ERROR')"
```

---

## 📺 Paso 6: Obtener Lista de Videos

### Opción A: Automático (con YouTube Data API)

```bash
# Asegúrate de tener YOUTUBE_API_KEY en .env
python get_video_list_example.py
```

### Opción B: Manual

Crea el archivo `data/video_list.json` con los videos que quieres transcribir:

```bash
mkdir -p data
cat > data/video_list.json << 'EOF'
[
  {
    "video_id": "VIDEO_ID_1",
    "title": "Título del video",
    "published_at": "2024-01-01T00:00:00Z"
  }
]
EOF
```

**Para obtener el VIDEO_ID de un video de YouTube:**
1. Ve al video en YouTube
2. Copia la URL: `https://www.youtube.com/watch?v=VIDEO_ID`
3. El VIDEO_ID es la parte después de `v=`

---

## 🐳 Paso 7: Ejecutar con Docker

### 7.1 Verificar Docker

```bash
docker --version
docker-compose --version
```

### 7.2 Iniciar servicios

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 7.3 Verificar que MCP está corriendo

```bash
# En otra terminal
curl http://localhost:8080/health
```

Deberías ver una respuesta JSON.

---

## 📝 Paso 8: Transcribir Videos

### 8.1 Ejecutar transcripciones

```bash
# Ejecutar transcripciones
docker-compose --profile transcriber up transcriber

# Ver logs en tiempo real
docker-compose logs -f transcriber
```

### 8.2 Verificar resultados

```bash
# Ver transcripciones generadas
ls -lh data/

# Ver una transcripción
cat data/transcriptions_*.json | head -50
```

---

## 🧠 Paso 9: Construir Vector Store

El script de transcripción lo hace automáticamente, pero puedes ejecutarlo manualmente:

```bash
# Dentro del contenedor
docker exec -it luisito-transcriber python build_vectorstore.py

# O localmente
python build_vectorstore.py
```

### Verificar vector store

```bash
# Ver el vector store
ls -lh chroma_db/

# Contar documentos
python -c "
import chromadb
from chromadb.config import Settings
client = chromadb.Client(Settings(persist_directory='./chroma_db'))
collection = client.get_collection('luisito_transcripts')
print(f'Total documentos: {collection.count()}')
"
```

---

## 🚀 Paso 10: Ejecutar Chatbot

### 10.1 Iniciar chatbot

```bash
# Iniciar chatbot
docker-compose --profile chatbot up chatbot
```

### 10.2 Acceder al chatbot

Abre tu navegador en: `http://localhost:8501`

### 10.3 Probar

Prueba preguntas como:
- ¿De qué trata el video de Japón?
- ¿Qué lugares ha visitado Luisito?
- Cuéntame sobre el video de Dubai

---

## ✅ Verificación Final

### Checklist

- [ ] Docker Desktop instalado y corriendo
- [ ] Azure Blob Storage configurado
- [ ] OpenAI API Key configurada
- [ ] Archivo `.env` con todas las credenciales
- [ ] Lista de videos en `data/video_list.json`
- [ ] MCP server corriendo en puerto 8080
- [ ] Transcripciones generadas en `data/`
- [ ] Vector store creado en `chroma_db/`
- [ ] Chatbot accesible en `http://localhost:8501`
- [ ] Chatbot responde preguntas correctamente

---

## 🐛 Problemas Comunes

### "Cannot connect to Docker daemon"

**Solución:**
```bash
# Inicia Docker Desktop
open -a Docker
```

### "Port 8080 already in use"

**Solución:**
```bash
# Ver qué está usando el puerto
lsof -i :8080

# Detener el proceso o cambiar el puerto en docker-compose.yml
```

### "OPENAI_API_KEY not found"

**Solución:**
```bash
# Verificar que el archivo .env existe
ls -la .env

# Verificar formato (sin espacios, sin comillas)
cat .env
```

### "Azure connection failed"

**Solución:**
```bash
# Verificar connection string en Azure Portal
# Asegúrate de que tenga formato:
# DefaultEndpointsProtocol=https;AccountName=NAME;AccountKey=KEY;EndpointSuffix=core.windows.net
```

---

## 🎉 ¡Listo!

Tu chatbot de Luisito Comunica está listo para usar. 

**Próximos pasos:**
- Transcribe más videos
- Mejora los prompts del chatbot
- Personaliza la interfaz
- Agrega más funcionalidades

---

**¿Necesitas ayuda?** 
- Revisa los logs: `docker-compose logs -f`
- Lee el README.md
- Abre un issue en GitHub

