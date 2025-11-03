"""
Sube ChromaDB a Azure Blob Storage como archivo comprimido
"""
import os
import tarfile
import shutil
from pathlib import Path
from azure.storage.blob import BlobClient
from dotenv import load_dotenv

load_dotenv()

def upload_chromadb_to_azure():
    """
    Comprime y sube el vector store de ChromaDB a Azure Blob Storage
    
    Returns:
        bool: True si subió exitosamente, False si falló
    """
    persist_directory = "./chroma_db"
    
    # Verificar que existe
    if not Path(persist_directory).exists():
        print("❌ ChromaDB no existe localmente")
        return False
    
    # Verificar que tiene datos
    try:
        import chromadb
        client = chromadb.PersistentClient(path=persist_directory)
        try:
            collection = client.get_collection("luisito_transcripts")
            count = collection.count()
            if count == 0:
                print("⚠️  ChromaDB está vacío")
                return False
            print(f"📊 ChromaDB tiene {count} documentos")
        except Exception as e:
            print(f"⚠️  Error verificando collection: {e}")
            return False
    except Exception as e:
        print(f"⚠️  Error verificando ChromaDB: {e}")
        return False
    
    # Intentar subir a Azure
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if not connection_string:
        print("⚠️  AZURE_STORAGE_CONNECTION_STRING no configurada")
        return False
    
    container_name = os.getenv('AZURE_STORAGE_CONTAINER', 'luisito-transcripts')
    blob_name = "chroma_db/chromadb.tar.gz"
    
    try:
        print("📦 Comprimiendo ChromaDB...")
        
        # Crear archivo temporal
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tar.gz') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Comprimir contenido del directorio directamente (sin directorio padre)
            with tarfile.open(temp_path, "w:gz") as tar:
                for root, dirs, files in os.walk(persist_directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, persist_directory)
                        tar.add(file_path, arcname=arcname)
            
            # Subir a Azure
            print("📤 Subiendo ChromaDB a Azure Blob Storage...")
            blob_client = BlobClient.from_connection_string(
                connection_string,
                container_name=container_name,
                blob_name=blob_name
            )
            
            with open(temp_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        print("✅ ChromaDB subido exitosamente a Azure")
        return True
        
    except Exception as e:
        print(f"❌ Error subiendo ChromaDB a Azure: {e}")
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        return False

if __name__ == "__main__":
    upload_chromadb_to_azure()

