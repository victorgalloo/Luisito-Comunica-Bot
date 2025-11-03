"""
Sube transcripciones a Azure Blob Storage
"""
import os
import json
from datetime import datetime
from azure.storage.blob import BlobServiceClient, BlobClient
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

def create_blob_client():
    """
    Crea un cliente de Azure Blob Storage
    
    Returns:
        BlobServiceClient configurado
    """
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if not connection_string:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING no está configurada")
    
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    return blob_service_client

def create_container_if_not_exists(blob_service_client, container_name):
    """
    Crea el contenedor si no existe
    
    Args:
        blob_service_client: Cliente de Azure Blob
        container_name: Nombre del contenedor
    """
    try:
        blob_service_client.create_container(container_name)
        print(f"   ✅ Contenedor '{container_name}' creado")
    except Exception as e:
        if 'ContainerAlreadyExists' in str(e):
            print(f"   ✅ Contenedor '{container_name}' ya existe")
        else:
            raise

def upload_transcription_file(blob_service_client, container_name, file_path):
    """
    Sube el archivo JSON completo de transcripciones
    
    Args:
        blob_service_client: Cliente de Azure Blob
        container_name: Nombre del contenedor
        file_path: Ruta al archivo de transcripciones
    """
    blob_name = f"transcriptions/{os.path.basename(file_path)}"
    
    container_client = blob_service_client.get_container_client(container_name)
    
    with open(file_path, 'rb') as data:
        blob_client = container_client.upload_blob(
            name=blob_name,
            data=data,
            overwrite=True
        )
    
    print(f"   ✅ Archivo completo subido: {blob_name}")

def upload_individual_transcriptions(blob_service_client, container_name, transcriptions):
    """
    Sube cada transcripción individualmente como blob separado
    
    Args:
        blob_service_client: Cliente de Azure Blob
        container_name: Nombre del contenedor
        transcriptions: Lista de transcripciones
    """
    uploaded = 0
    
    for trans in transcriptions:
        if trans['status'] == 'success':
            blob_name = f"videos/{trans['video_id']}.json"
            json_data = json.dumps(trans, ensure_ascii=False, indent=2)
            
            container_client = blob_service_client.get_container_client(container_name)
            container_client.upload_blob(
                name=blob_name,
                data=json_data.encode('utf-8'),
                overwrite=True
            )
            uploaded += 1
            print(f"   ✅ {trans.get('title', 'Sin título')[:60]}...")
    
    print(f"\n   📦 {uploaded} transcripciones individuales subidas")

def upload_transcriptions(transcriptions_file='data/transcriptions_latest.json'):
    """
    Función principal para subir transcripciones a Azure
    
    Args:
        transcriptions_file: Ruta al archivo de transcripciones
    """
    print("\n📤 UPLOAD A AZURE BLOB STORAGE")
    print("="*60)
    
    # Verificar archivo
    if not os.path.exists(transcriptions_file):
        # Buscar el archivo más reciente
        transcriptions_dir = Path('data')
        transcription_files = list(transcriptions_dir.glob('transcriptions_*.json'))
        
        if not transcription_files:
            print("❌ No se encontró archivo de transcripciones")
            return
        
        transcriptions_file = sorted(transcription_files)[-1]
        print(f"📋 Usando archivo más reciente: {transcriptions_file}")
    
    # Cargar transcripciones
    with open(transcriptions_file, 'r', encoding='utf-8') as f:
        transcriptions = json.load(f)
    
    print(f"   📊 Total de transcripciones: {len(transcriptions)}")
    
    # Crear cliente
    blob_service_client = create_blob_client()
    container_name = os.getenv('AZURE_STORAGE_CONTAINER', 'luisito-transcripts')
    
    # Crear contenedor
    create_container_if_not_exists(blob_service_client, container_name)
    
    # Subir archivo completo
    print(f"\n📦 Subiendo archivo completo...")
    upload_transcription_file(blob_service_client, container_name, transcriptions_file)
    
    # Subir transcripciones individuales
    print(f"\n📦 Subiendo transcripciones individuales...")
    upload_individual_transcriptions(blob_service_client, container_name, transcriptions)
    
    print("\n✅ Upload completado!")

def download_transcriptions(container_name=None):
    """
    Descarga todas las transcripciones desde Azure Blob Storage
    
    Args:
        container_name: Nombre del contenedor (opcional)
    
    Returns:
        Lista de transcripciones
    """
    blob_service_client = create_blob_client()
    
    if not container_name:
        container_name = os.getenv('AZURE_STORAGE_CONTAINER', 'luisito-transcripts')
    
    container_client = blob_service_client.get_container_client(container_name)
    transcriptions = []
    
    print(f"📥 Descargando transcripciones desde Azure...")
    for blob in container_client.list_blobs(name_starts_with="videos/"):
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=blob.name
        )
        data = blob_client.download_blob().readall()
        transcription = json.loads(data.decode('utf-8'))
        transcriptions.append(transcription)
        print(f"   ✅ {transcription.get('title', 'Sin título')[:60]}...")
    
    print(f"\n✅ {len(transcriptions)} transcripciones descargadas")
    return transcriptions

if __name__ == "__main__":
    # Subir transcripciones
    upload_transcriptions()
    
    # Opcional: Verificar descarga
    # print("\n📥 Verificando descarga...")
    # transcripts = download_transcriptions()

