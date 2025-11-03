# 🚀 Inicio Rápido - Luisito Comunica Chatbot

Guía rápida para tener el chatbot funcionando en 15 minutos.

## ⚡ Pasos Rápidos

### 1️⃣ Instalar Docker (si no lo tienes)

```bash
# macOS
brew install --cask docker

# Luego abre Docker Desktop desde Applications
open -a Docker
```

### 2️⃣ Configurar credenciales

Crea archivo `.env` con:

```bash
# Copia este contenido a .env
cp .env.example .env
# Luego edita .env con tus credenciales reales
```

O crea `.env` manualmente:
```bash
cat > .env << 'EOF'
MCP_URL=http://mcp-youtube-transcript:8080
AZURE_STORAGE_CONNECTION_STRING=tu-azure-connection-string
AZURE_STORAGE_CONTAINER=luisito-transcripts
AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com
AZURE_OPENAI_API_KEY=tu-azure-openai-key
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
YOUTUBE_CHANNEL_ID=UCECJDeK0MNapZbpaOzxrUPA
EOF
```

**Donde conseguir las credenciales:**
- **Azure Storage**: Portal de Azure → Storage Accounts → Access Keys
- **Azure OpenAI**: Portal de Azure → OpenAI → Keys and Endpoint

### 3️⃣ Crear lista de videos

Crea archivo `data/video_list.json`:

```bash
mkdir -p data
cat > data/video_list.json << 'EOF'
[
  {
    "video_id": "TU_VIDEO_ID_AQUI",
    "title": "Título del video",
    "published_at": "2024-01-01T00:00:00Z"
  }
]
EOF
```

**Tip:** Para obtener el VIDEO_ID, copia la URL del video:
`https://www.youtube.com/watch?v=ESTE_ES_EL_VIDEO_ID`

### 4️⃣ Verificar configuración

```bash
python check_config.py
```

Este script verificará que todo esté correcto.

### 5️⃣ Ejecutar

```bash
# Paso 1: Iniciar MCP
docker-compose up -d mcp-youtube-transcript

# Esperar 10 segundos...

# Paso 2: Transcribir videos
docker-compose --profile transcriber up transcriber

# Paso 3: Ejecutar chatbot
docker-compose --profile chatbot up chatbot
```

### 6️⃣ Usar el chatbot

Abre en tu navegador: **http://localhost:8501**

Prueba preguntas como:
- ¿De qué trata el video de Japón?
- ¿Qué lugares ha visitado Luisito?

---

## 🐛 Si algo falla

### Docker no inicia

```bash
# Reiniciar Docker
open -a Docker
# Esperar 30 segundos
docker ps
```

### MCP no responde

```bash
# Ver logs
docker-compose logs mcp-youtube-transcript

# Reiniciar
docker-compose restart mcp-youtube-transcript
```

### Error en transcripciones

```bash
# Ver logs
docker-compose logs transcriber

# Ver archivos generados
ls -la data/
```

### Chatbot no carga

```bash
# Verificar que existe vector store
ls -la chroma_db/

# Si no existe, crear manualmente
docker exec luisito-transcriber python build_vectorstore.py
```

---

## 📝 Comandos Útiles

```bash
# Ver todos los logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f transcriber

# Reiniciar un servicio
docker-compose restart chatbot

# Detener todo
docker-compose down

# Ver contenedores corriendo
docker ps

# Acceder a un contenedor
docker exec -it luisito-transcriber bash
```

---

## ✅ Checklist

Antes de empezar:
- [ ] Docker Desktop instalado y corriendo
- [ ] Azure Blob Storage creado
- [ ] OpenAI API Key obtenida
- [ ] Archivo `.env` configurado
- [ ] Archivo `data/video_list.json` creado

Después de ejecutar:
- [ ] MCP server respondiendo en puerto 8080
- [ ] Transcripciones en `data/transcriptions_*.json`
- [ ] Vector store en `chroma_db/`
- [ ] Chatbot accesible en http://localhost:8501
- [ ] Chatbot responde preguntas

---

## 🆘 Ayuda

Si necesitas más ayuda:
1. Lee `SETUP_INSTRUCTIONS.md` para detalles completos
2. Lee `README.md` para documentación completa
3. Revisa logs: `docker-compose logs -f`
4. Ejecuta verificación: `python check_config.py`

---

**¿Todo funcionando? 🎉 ¡Disfruta tu chatbot!**

