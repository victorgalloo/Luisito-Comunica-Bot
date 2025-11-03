# 🎥 Luisito Comunica Chatbot

Un chatbot inteligente entrenado con transcripciones de todos los videos de Luisito Comunica, utilizando RAG (Retrieval-Augmented Generation) con ChromaDB y Azure OpenAI.

## 🏗️ Arquitectura

```
YouTube Videos → MCP Transcript → Azure Blob Storage → ChromaDB → Streamlit Chatbot
```

### Componentes

- **MCP YouTube Transcript**: Servidor MCP para transcripciones automáticas
- **Azure Blob Storage**: Almacenamiento de transcripciones
- **ChromaDB**: Vector database local para búsqueda semántica
- **Azure OpenAI**: Embeddings y generación de respuestas
- **Streamlit**: Interfaz web del chatbot

## 🚀 Inicio Rápido

### Prerrequisitos

- Docker y Docker Compose instalados
- Cuenta de Azure con Blob Storage configurado
- Azure OpenAI configurado (con deployments de embeddings y chat)

### 1. Clonar el repositorio

```bash
git clone <tu-repo>
cd LuisitoComunica
```

### 2. Configurar variables de entorno

Crea un archivo `.env` basado en `.env.example`:

```bash
cp .env.example .env
# Edita .env con tus credenciales
```

Variables necesarias:
- `AZURE_STORAGE_CONNECTION_STRING`: Connection string de Azure Blob Storage
- `AZURE_STORAGE_CONTAINER`: Nombre del contenedor
- `AZURE_OPENAI_ENDPOINT`: Endpoint de tu recurso Azure OpenAI
- `AZURE_OPENAI_API_KEY`: API key de Azure OpenAI
- `AZURE_OPENAI_CHAT_DEPLOYMENT`: Deployment del modelo de chat (ej: gpt-4o-mini)
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`: Deployment del modelo de embeddings (ej: text-embedding-ada-002)
- `YOUTUBE_CHANNEL_ID`: ID del canal de YouTube (ej: UCECJDeK0MNapZbpaOzxrUPA)

### 3. Obtener lista de videos

Necesitas crear un archivo `data/video_list.json` con la lista de videos:

```json
[
  {
    "video_id": "VIDEO_ID_1",
    "title": "Título del video 1",
    "published_at": "2024-01-01T00:00:00Z"
  },
  {
    "video_id": "VIDEO_ID_2",
    "title": "Título del video 2",
    "published_at": "2024-01-02T00:00:00Z"
  }
]
```

Puedes usar la YouTube Data API o herramientas como [YouTube Data Tools](https://github.com/abbondanzio/youtube-data-tools) para obtener esta lista.

### 4. Iniciar servicios con Docker

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 5. Transcribir videos

```bash
# Ejecutar transcripciones masivas
docker-compose --profile transcriber up transcriber

# Ver logs de transcripción
docker-compose logs -f transcriber
```

Esto:
1. Transcribe todos los videos usando MCP (o fallback a youtube-transcript-api)
2. Sube las transcripciones a Azure Blob Storage
3. Construye el vector store con ChromaDB

### 6. Acceder al chatbot

```bash
# Iniciar chatbot
docker-compose --profile chatbot up chatbot
```

Abre tu navegador en `http://localhost:8501`

## 📋 Pipeline Completo

### Opción A: Con Docker (Recomendado)

```bash
# 1. Iniciar MCP server
docker-compose up -d mcp-youtube-transcript

# 2. Transcribir videos
docker-compose --profile transcriber up transcriber

# 3. Acceder al chatbot
docker-compose --profile chatbot up chatbot
```

### Opción B: Sin Docker (Local)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Transcribir videos
python transcribe_mcp.py

# 3. Subir a Azure
python upload_to_azure.py

# 4. Construir vector store
python build_vectorstore.py

# 5. Ejecutar chatbot
streamlit run chatbot.py
```

## 📂 Estructura del Proyecto

```
LuisitoComunica/
├── docker-compose.yml          # Orquestación de servicios Docker
├── Dockerfile.transcriber      # Imagen para transcripciones
├── Dockerfile.chatbot          # Imagen para chatbot
├── requirements.txt            # Dependencias Python
├── .env                        # Variables de entorno (no commitear)
├── .env.example               # Ejemplo de variables
│
├── transcribe_mcp.py          # Script principal de transcripción
├── upload_to_azure.py         # Upload a Azure Blob Storage
├── build_vectorstore.py       # Construcción del vector store
├── chatbot.py                 # Interfaz del chatbot con Streamlit
│
├── data/                      # Transcripciones (generadas)
│   ├── video_list.json        # Lista de videos a transcribir
│   └── transcriptions_*.json  # Transcripciones generadas
│
├── chroma_db/                 # Vector database local (generado)
│
└── README.md                  # Este archivo
```

## 🐳 Servicios Docker

### mcp-youtube-transcript
Servidor MCP para transcripciones de YouTube
- Puerto: `8080`
- Imagen: `jkawamoto/mcp-youtube-transcript:latest`
- Health check incluido

### transcriber
Pipeline de transcripciones masivas
- Usa MCP cuando está disponible
- Fallback automático a youtube-transcript-api
- Sube automáticamente a Azure
- Construye el vector store

### chatbot
Interfaz web con Streamlit
- Puerto: `8501`
- Acceso: `http://localhost:8501`

## 📊 Características

### ✨ Transcripción Inteligente
- **MCP first**: Usa servidor MCP cuando está disponible
- **Fallback**: Automático a youtube-transcript-api
- **Batch processing**: Transcribe todos los videos
- **Manejo de errores**: Continúa aunque algunos videos fallen

### 🧠 RAG (Retrieval-Augmented Generation)
- **Búsqueda semántica**: ChromaDB con embeddings de OpenAI
- **Contexto relevante**: Encuentra la información más pertinente
- **Multilenguaje**: Soporta transcripciones en español e inglés

### 🎨 Interfaz Moderna
- **Streamlit**: UI moderna y responsiva
- **Fuentes**: Muestra de dónde viene cada respuesta
- **Memoria**: Mantiene contexto de la conversación
- **Sidebar**: Información y ejemplos

## 🔧 Comandos Útiles

```bash
# Ver logs de un servicio
docker-compose logs -f mcp-youtube-transcript
docker-compose logs -f transcriber
docker-compose logs -f chatbot

# Reiniciar un servicio
docker-compose restart chatbot

# Detener todos los servicios
docker-compose down

# Limpiar volúmenes (borrar transcripciones y vector store)
docker-compose down -v

# Reconstruir imágenes
docker-compose build --no-cache

# Acceder al contenedor
docker exec -it luisito-transcriber bash
docker exec -it luisito-chatbot bash
```

## 📝 Ejemplos de Uso

### Transcribir videos específicos

Edita `data/video_list.json` con solo los videos que necesitas:

```json
[
  {
    "video_id": "VIDEO_ID_ESPECIFICO",
    "title": "Mi video favorito",
    "published_at": "2024-01-01T00:00:00Z"
  }
]
```

### Ver estadísticas del vector store

```python
import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(persist_directory="./chroma_db"))
collection = client.get_collection("luisito_transcripts")
print(f"Total documentos: {collection.count()}")
```

### Descargar transcripciones de Azure

```python
from upload_to_azure import download_transcriptions

transcripts = download_transcriptions()
print(f"Descargados {len(transcripts)} videos")
```

## 🐛 Troubleshooting

### "No se pudo conectar al servidor MCP"
- Verifica que `mcp-youtube-transcript` esté corriendo: `docker-compose ps`
- Verifica el puerto: `curl http://localhost:8080/health`
- Lee los logs: `docker-compose logs mcp-youtube-transcript`

### "OPENAI_API_KEY no está configurada"
- Verifica tu archivo `.env`
- Asegúrate de que las variables se carguen: `python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"`

### "No se encontró el vector store"
- Ejecuta primero `build_vectorstore.py`
- Verifica que exista `chroma_db/`
- Revisa los logs: `docker-compose logs transcriber`

### "Rate limit exceeded" en OpenAI
- Reduce el `batch_size` en `build_vectorstore.py`
- Agrega delays entre requests
- Usa un plan de OpenAI con más rate limits

### Transcripciones vacías
- Verifica que los videos tengan subtítulos habilitados
- Algunos videos pueden no tener transcripciones disponibles
- Revisa los logs para ver qué videos fallaron

## 💰 Costos Estimados

### Azure Blob Storage
- $0.0184 por GB al mes
- Para ~1000 videos (~50MB): ~$0.30/mes

### OpenAI
- **Embeddings** (text-embedding-ada-002): $0.0001 por 1K tokens
- **Chat** (gpt-4o-mini): $0.15 por 1M tokens input
- Para ~1000 videos: ~$5-10 de embeddings + ~$10-20/mes de chat

### Total Estimado
**~$15-20/mes** con uso moderado

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit tus cambios: `git commit -am 'Agrega nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 🙏 Agradecimientos

- **Luisito Comunica**: Por crear contenido increíble
- **YouTube**: Por la plataforma y las transcripciones
- **MCP Community**: Por el servidor de transcripciones
- **OpenAI**: Por las APIs de embeddings y chat
- **Streamlit**: Por la framework de UI

## 📞 Soporte

Si tienes problemas o preguntas:
1. Revisa la sección [Troubleshooting](#🐛-troubleshooting)
2. Abre un issue en GitHub
3. Revisa los logs: `docker-compose logs -f`

---

Hecho con ❤️ para los fans de Luisito Comunica

