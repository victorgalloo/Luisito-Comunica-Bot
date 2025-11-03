"""
API REST para el chatbot de Luisito Comunica usando FastAPI
Reemplaza la interfaz Streamlit con una API moderna
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

# Configurar FastAPI
app = FastAPI(
    title="🎥 Luisito Comunica Chatbot API",
    description="API REST para el chatbot de Luisito Comunica",
    version="1.0.0"
)

# CORS middleware para permitir requests del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class ChatMessage(BaseModel):
    role: str  # "user" o "assistant"
    content: str
    
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    
class ChatResponse(BaseModel):
    response: str
    sources: List[dict]
    conversation_id: str

# Variables globales para el chatbot
llm = None
embeddings = None
get_relevant_chunks_fn = None

def initialize_chatbot():
    """
    Inicializa el chatbot con el vector store y LLM
    """
    global llm, embeddings, get_relevant_chunks_fn
    
    try:
        # Verificar que existe el vector store
        persist_directory = "./chroma_db"
        if not Path(persist_directory).exists():
            print("❌ No se encontró el vector store. Ejecuta build_vectorstore.py primero.")
            return False
        
        # Cargar vector store desde ChromaDB local
        client = chromadb.PersistentClient(path=persist_directory)
        
        try:
            collection = client.get_collection("luisito_transcripts")
        except:
            print("❌ No se encontró la collection 'luisito_transcripts'. Ejecuta build_vectorstore.py primero.")
            return False
        
        # Inicializar embeddings con Azure OpenAI
        azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        azure_api_key = os.getenv('AZURE_OPENAI_API_KEY')
        api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')
        
        # Validar configuración de Azure OpenAI
        if not azure_endpoint:
            print("❌ AZURE_OPENAI_ENDPOINT no está configurado en .env")
            return False
        
        if not azure_api_key:
            print("❌ AZURE_OPENAI_API_KEY no está configurado en .env")
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
        
        # Función para obtener chunks relevantes
        def get_relevant_chunks(query, n_results=5):
            """
            Busca chunks relevantes en el vector store
            """
            query_embedding = embeddings.embed_query(query)
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            
            return documents, metadatas
        
        get_relevant_chunks_fn = get_relevant_chunks
        
        print("✅ Chatbot inicializado correctamente")
        return True
    
    except Exception as e:
        print(f"❌ Error inicializando chatbot: {e}")
        return False

# Inicializar al startup
@app.on_event("startup")
async def startup_event():
    initialize_chatbot()

# Endpoints
@app.get("/")
async def root():
    """Endpoint de salud"""
    return {
        "message": "🎥 Luisito Comunica Chatbot API",
        "status": "operational",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check para Docker"""
    if llm is None or embeddings is None:
        return {"status": "unhealthy", "error": "Chatbot not initialized"}
    return {"status": "healthy"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint principal para chatear con el bot
    """
    if llm is None or get_relevant_chunks_fn is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    try:
        # Obtener chunks relevantes
        docs, metadatas = get_relevant_chunks_fn(request.message)
        
        # Construir contexto
        context = "\n\n".join([
            f"[Video: {meta.get('title', 'Sin título')}]\n{doc}"
            for doc, meta in zip(docs, metadatas)
        ])
        
        # Construir prompt
        system_prompt = """Eres un asistente de IA especializado en el contenido de Luisito Comunica.
Responde las preguntas de los usuarios basándote ÚNICAMENTE en el siguiente contexto de sus videos.
Si la información no está en el contexto, di amablemente que no tienes esa información.

Mantén un tono conversacional y amigable, como si fueras Luisito Comunica."""
        
        user_prompt = f"""Contexto:
{context}

Pregunta del usuario: {request.message}

Responde de manera natural y conversacional:"""
        
        # Generar respuesta
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = llm.invoke(messages).content
        
        # Preparar metadatas para el frontend
        sources = [
            {
                "title": meta.get('title', 'Sin título'),
                "video_id": meta.get('video_id', ''),
                "chunk_id": meta.get('chunk_id', '')
            }
            for meta in metadatas
        ]
        
        return ChatResponse(
            response=response,
            sources=sources,
            conversation_id=request.conversation_id or "default"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando respuesta: {str(e)}")

@app.get("/api/stats")
async def get_stats():
    """Obtener estadísticas del vector store"""
    try:
        persist_directory = "./chroma_db"
        client = chromadb.PersistentClient(path=persist_directory)
        collection = client.get_collection("luisito_transcripts")
        
        count = collection.count()
        
        return {
            "total_chunks": count,
            "status": "ready"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "not_ready"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

