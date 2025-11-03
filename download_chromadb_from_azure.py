"""
Descarga ChromaDB desde Azure Blob Storage si no existe localmente
"""
import os
import shutil
import tarfile
from pathlib import Path
from azure.storage.blob import BlobClient
from dotenv import load_dotenv

load_dotenv()

def download_chromadb_from_azure():
    """
    Descarga el vector store de ChromaDB desde Azure Blob Storage
    si no existe localmente
    
    Returns:
        bool: True si descargó exitosamente o ya existe, False si falló
    """
    persist_directory = "./chroma_db"
    
    # Verificar si ya existe y tiene datos
    if Path(persist_directory).exists():
        # Verificar que tenga la collection
        try:
            import chromadb
            client = chromadb.PersistentClient(path=persist_directory)
            try:
                collection = client.get_collection("luisito_transcripts")
                count = collection.count()
                if count > 0:
                    print(f"✅ ChromaDB ya existe localmente con {count} documentos")
                    return True
            except:
                # Collection no existe, continuar con descarga
                pass
        except Exception as e:
            print(f"⚠️  Error verificando ChromaDB local: {e}")
    
    # Intentar descargar desde Azure
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if not connection_string:
        print("⚠️  AZURE_STORAGE_CONNECTION_STRING no configurada")
        return False
    
    container_name = os.getenv('AZURE_STORAGE_CONTAINER', 'luisito-transcripts')
    blob_name = "chroma_db/chromadb.tar.gz"  # El archivo comprimido del vector store
    
    try:
        print("📥 Descargando ChromaDB desde Azure Blob Storage...")
        
        # Crear directorio si no existe
        Path(persist_directory).mkdir(exist_ok=True)
        
        # Descargar blob
        blob_client = BlobClient.from_connection_string(
            connection_string,
            container_name=container_name,
            blob_name=blob_name
        )
        
        # Verificar si existe
        if not blob_client.exists():
            print("⚠️  ChromaDB no encontrado en Azure Blob Storage")
            return False
        
        # Descargar a archivo temporal
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tar.gz') as temp_file:
            temp_file.write(blob_client.download_blob().readall())
            temp_path = temp_file.name
        
        try:
            # Extraer
            print("📦 Extrayendo ChromaDB...")
            with tarfile.open(temp_path, "r:gz") as tar:
                tar.extractall(path=persist_directory)
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        print("✅ ChromaDB descargado exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error descargando ChromaDB desde Azure: {e}")
        return False

if __name__ == "__main__":
    download_chromadb_from_azure()

