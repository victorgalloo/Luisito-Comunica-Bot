"""
API REST para el chatbot de Luisito Comunica
Usa FastAPI para servir endpoints que pueden ser consumidos por React/Next.js
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from pathlib import Path
import chromadb
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

app = FastAPI(
    title="Luisito Comunica Chatbot API",
    description="API REST para el chatbot de Luisito Comunica usando RAG",
    version="1.0.0"
)

# Configurar CORS para permitir requests desde React/Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominio exacto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic para request/response
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []

class Source(BaseModel):
    title: str
    video_id: Optional[str] = None
    url: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[Source]
    total_chunks_used: int

class HealthResponse(BaseModel):
    status: str
    message: str
    vector_store_ready: bool

# Globales para inicialización
llm = None
embeddings = None
collection = None
initialized = False

def initialize_chatbot():
    """Inicializa el chatbot con vector store y LLM"""
    global llm, embeddings, collection, initialized
    
    if initialized:
        return True
    
    try:
        # Verificar que existe el vector store
        persist_directory = "./chroma_db"
        if not Path(persist_directory).exists():
            print("❌ No se encontró el vector store")
            return False
        
        # Cargar vector store desde ChromaDB local
        client = chromadb.PersistentClient(path=persist_directory)
        
        try:
            collection = client.get_collection("luisito_transcripts")
        except:
            print("❌ No se encontró la collection 'luisito_transcripts'")
            return False
        
        # Inicializar embeddings con Azure OpenAI
        azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        azure_api_key = os.getenv('AZURE_OPENAI_API_KEY')
        api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
        
        if not azure_endpoint or not azure_api_key:
            print("❌ Azure OpenAI no configurado correctamente")
            return False
        
        # Inicializar embeddings
        embedding_deployment = os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'text-embedding-ada-002')
        embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=azure_endpoint,
            api_key=azure_api_key,
            api_version=api_version,
            azure_deployment=embedding_deployment
        )
        
        # Inicializar LLM con Azure OpenAI
        chat_deployment = os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT', 'gpt-4o-mini')
        llm = AzureChatOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=azure_api_key,
            api_version=api_version,
            azure_deployment=chat_deployment,
            temperature=0.7,
            max_tokens=1500
        )
        
        initialized = True
        print("✅ Chatbot inicializado correctamente")
        return True
    
    except Exception as e:
        print(f"❌ Error inicializando chatbot: {e}")
        return False

def get_relevant_chunks(query, n_results=5):
    """Busca chunks relevantes en el vector store"""
    query_embedding = embeddings.embed_query(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    
    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    
    return documents, metadatas

def generate_response(query):
    """Genera una respuesta usando RAG"""
    try:
        # Obtener chunks relevantes
        docs, metadatas = get_relevant_chunks(query, n_results=5)
        
        if not docs:
            return "Lo siento, no encontré información relevante en los videos.", []
        
        # Crear contexto de los chunks
        context = "\n\n".join([f"[Fuente {i+1}]\n{doc}" for i, doc in enumerate(docs)])
        
        # System prompt mejorado
        system_prompt = """Eres un asistente amigable que responde preguntas sobre los videos de Luisito Comunica, un creador de contenido de viajes.

Contexto de los videos:
{context}

Instrucciones:
- Responde de manera amigable y conversacional, como lo haría Luisito
- Usa el contexto proporcionado para dar respuestas precisas
- Si no encuentras información relevante, di que no tienes esa información
- Responde en español
- Mantén las respuestas concisas pero informativas (150-300 palabras)
- Puedes mencionar detalles interesantes de los videos"""
        
        system_prompt = system_prompt.format(context=context)
        
        # User prompt
        user_prompt = f"Pregunta: {query}\n\nPor favor, responde basándote en el contexto proporcionado."
        
        # Generar respuesta
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = llm.invoke(messages).content
        
        # Procesar metadatas para fuentes
        sources = []
        for metadata in metadatas:
            source = Source(
                title=metadata.get('title', 'Video de Luisito Comunica'),
                video_id=metadata.get('video_id', ''),
                url=f"https://www.youtube.com/watch?v={metadata.get('video_id', '')}" if metadata.get('video_id') else None
            )
            sources.append(source)
        
        return response, sources
    
    except Exception as e:
        print(f"Error generando respuesta: {e}")
        return f"Lo siento, hubo un error generando la respuesta: {e}", []

@app.on_event("startup")
async def startup_event():
    """Inicializa el chatbot al arrancar el servidor"""
    print("🚀 Iniciando API de Luisito Comunica Chatbot...")
    initialize_chatbot()

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    vector_store_ready = Path("./chroma_db").exists() and initialized
    return HealthResponse(
        status="running",
        message="Luisito Comunica Chatbot API",
        vector_store_ready=vector_store_ready
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    vector_store_ready = Path("./chroma_db").exists() and initialized
    return HealthResponse(
        status="healthy",
        message="API funcionando correctamente",
        vector_store_ready=vector_store_ready
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Endpoint principal para chat"""
    if not initialized:
        raise HTTPException(status_code=503, detail="Chatbot no inicializado")
    
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")
    
    # Generar respuesta
    response, sources = generate_response(request.message)
    
    return ChatResponse(
        response=response,
        sources=sources,
        total_chunks_used=len(sources)
    )

@app.get("/stats")
async def get_stats():
    """Obtiene estadísticas del vector store"""
    if not initialized or not collection:
        raise HTTPException(status_code=503, detail="Chatbot no inicializado")
    
    try:
        # Obtener conteo total de chunks
        count = collection.count()
        
        return {
            "total_chunks": count,
            "status": "ready"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

