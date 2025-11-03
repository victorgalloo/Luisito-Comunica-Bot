"""
Construye el vector store con ChromaDB usando las transcripciones desde Azure
"""
import os
from pathlib import Path
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
import chromadb
import json

load_dotenv()

def load_transcriptions_from_azure():
    """
    Carga todas las transcripciones desde Azure Blob Storage
    
    Returns:
        Lista de transcripciones
    """
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if not connection_string:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING no está configurada")
    
    container_name = os.getenv('AZURE_STORAGE_CONTAINER', 'luisito-transcripts')
    
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    
    transcriptions = []
    
    print("📥 Cargando transcripciones desde Azure Blob Storage...")
    for blob in container_client.list_blobs(name_starts_with="videos/"):
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=blob.name
        )
        data = blob_client.download_blob().readall()
        transcription = json.loads(data.decode('utf-8'))
        transcriptions.append(transcription)
    
    print(f"✅ {len(transcriptions)} transcripciones cargadas")
    return transcriptions

def load_transcriptions_from_local():
    """
    Carga transcripciones desde archivo local (fallback)
    
    Returns:
        Lista de transcripciones
    """
    transcriptions_dir = Path('data')
    transcription_files = list(transcriptions_dir.glob('transcriptions_*.json'))
    
    if not transcription_files:
        return []
    
    latest_file = sorted(transcription_files)[-1]
    print(f"📥 Cargando desde archivo local: {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        transcriptions = json.load(f)
    
    return transcriptions

def create_vectorstore():
    """
    Crea el vector store usando ChromaDB local con embeddings de OpenAI
    """
    print("\n🧠 CONSTRUYENDO VECTOR STORE")
    print("="*60)
    
    # Inicializar ChromaDB local
    persist_directory = "./chroma_db"
    Path(persist_directory).mkdir(exist_ok=True)
    
    client = chromadb.PersistentClient(path=persist_directory)
    
    # Crear o obtener collection
    collection_name = "luisito_transcripts"
    
    try:
        # Intentar eliminar collection existente para reconstruirla
        client.delete_collection(collection_name)
        print(f"   🗑️  Collection '{collection_name}' eliminada (reconstruyendo)")
    except:
        pass
    
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    
    # Cargar transcripciones (primero intentar Azure, luego local)
    try:
        transcriptions = load_transcriptions_from_azure()
    except:
        print("⚠️  No se pudo cargar desde Azure, intentando local...")
        transcriptions = load_transcriptions_from_local()
    
    if not transcriptions:
        print("❌ No se encontraron transcripciones")
        return
    
    # Filtar solo transcripciones exitosas
    successful_transcriptions = [t for t in transcriptions if t.get('status') == 'success']
    print(f"   📊 Transcripciones exitosas: {len(successful_transcriptions)}")
    
    # Inicializar text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    
    # Inicializar embeddings con Azure OpenAI
    azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    azure_api_key = os.getenv('AZURE_OPENAI_API_KEY')
    api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
    embedding_deployment = os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'text-embedding-ada-002')
    
    if not azure_endpoint or not azure_api_key:
        raise ValueError("AZURE_OPENAI_ENDPOINT y AZURE_OPENAI_API_KEY deben estar configurados")
    
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=azure_endpoint,
        api_key=azure_api_key,
        api_version=api_version,
        azure_deployment=embedding_deployment
    )
    
    # Procesar transcripciones
    print("\n📝 Procesando transcripciones...")
    all_chunks = []
    
    for trans in successful_transcriptions:
        title = trans.get('title', 'Sin título')
        video_id = trans.get('video_id', 'unknown')
        transcript = trans.get('transcript', '')
        published_at = trans.get('published_at', '')
        
        if not transcript:
            continue
        
        # Dividir texto en chunks
        chunks = text_splitter.split_text(transcript)
        
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                'id': f"{video_id}_{i}",
                'text': chunk,
                'metadata': {
                    'video_id': video_id,
                    'title': title,
                    'published_at': str(published_at),
                    'chunk_index': i
                }
            })
    
    print(f"   ✅ {len(all_chunks)} chunks creados")
    
    # Generar embeddings y agregar a ChromaDB
    print(f"\n🧠 Generando embeddings con Azure OpenAI...")
    print(f"   Deployment: {embedding_deployment}")
    print(f"   Esto puede tomar varios minutos dependiendo de la cantidad de chunks")
    
    batch_size = 100
    
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i+batch_size]
        texts = [chunk['text'] for chunk in batch]
        
        # Generar embeddings
        try:
            embedding_list = embeddings.embed_documents(texts)
            
            # Agregar a ChromaDB
            for chunk, embedding in zip(batch, embedding_list):
                collection.add(
                    ids=[chunk['id']],
                    embeddings=[embedding],
                    documents=[chunk['text']],
                    metadatas=[chunk['metadata']]
                )
            
            print(f"   ✅ Procesados {min(i+batch_size, len(all_chunks))}/{len(all_chunks)} chunks")
            
        except Exception as e:
            print(f"   ❌ Error procesando batch {i//batch_size + 1}: {e}")
            continue
    
    # PersistentClient se guarda automáticamente, no necesita persist() explícito
    
    print(f"\n✅ Vector store creado exitosamente!")
    print(f"   📁 Ubicación: {persist_directory}")
    print(f"   📊 Total de chunks: {len(all_chunks)}")
    print(f"   🗂️  Collection: {collection_name}")

def verify_vectorstore():
    """
    Verifica que el vector store se creó correctamente
    """
    persist_directory = "./chroma_db"
    
    if not Path(persist_directory).exists():
        print("❌ Vector store no existe")
        return False
    
    try:
        client = chromadb.PersistentClient(path=persist_directory)
        
        collection = client.get_collection("luisito_transcripts")
        count = collection.count()
        
        print(f"\n✅ Vector store verificado")
        print(f"   📊 Total de documentos: {count}")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando vector store: {e}")
        return False

if __name__ == "__main__":
    create_vectorstore()
    verify_vectorstore()

