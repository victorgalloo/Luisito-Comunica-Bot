"""
Transcripción de videos de Luisito Comunica usando MCP de YouTube
Estrategia: MCP primero, fallback a youtube-transcript-api si falla
"""
import os
import json
import time
import requests
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

load_dotenv()

def get_mcp_transcript(mcp_url, video_url):
    """
    Obtiene transcripción de un video usando el servidor MCP
    
    Args:
        mcp_url: URL del servidor MCP
        video_url: URL completa del video de YouTube
    
    Returns:
        Dict con la transcripción o None si falla
    """
    try:
        # Llamada al endpoint del servidor MCP
        response = requests.post(
            f"{mcp_url}/api/transcript",
            json={"url": video_url},
            timeout=60,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'transcript': data.get('text', ''),
                'transcript_data': data.get('segments', []),
                'language': data.get('language', 'es'),
                'method': 'MCP',
                'status': 'success'
            }
        else:
            print(f"⚠️  Error MCP {response.status_code}: {response.text}")
            return None
    
    except requests.exceptions.ConnectionError:
        print(f"⚠️  No se pudo conectar al servidor MCP en {mcp_url}")
        return None
    except requests.exceptions.Timeout:
        print(f"⚠️  Timeout esperando respuesta del servidor MCP")
        return None
    except Exception as e:
        print(f"⚠️  Error en MCP: {e}")
        return None

def transcribe_with_fallback(video_id, video_url):
    """
    Transcribe usando MCP, fallback a youtube-transcript-api si falla
    
    Args:
        video_id: ID del video de YouTube
        video_url: URL completa del video
    
    Returns:
        Dict con la transcripción o error
    """
    # Intentar con MCP primero
    mcp_url = os.getenv('MCP_URL', 'http://localhost:8080')
    print(f"   Intento 1: MCP en {mcp_url}...")
    result = get_mcp_transcript(mcp_url, video_url)
    
    if result and result['status'] == 'success':
        print(f"   ✅ MCP exitoso")
        result['video_id'] = video_id
        return result
    
    # Fallback a youtube-transcript-api
    print(f"   Intento 2: Fallback a youtube-transcript-api...")
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
        
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        try:
            transcript = transcript_list.find_transcript(['es', 'en'])
            if transcript.language_code != 'es':
                transcript = transcript.translate('es')
        except:
            try:
                transcript = transcript_list.find_generated_transcript(['es', 'en'])
                if transcript.language_code != 'es':
                    transcript = transcript.translate('es')
            except:
                raise NoTranscriptFound(video_id, ['es', 'en'])
        
        transcript_data = transcript.fetch()
        
        result = {
            'video_id': video_id,
            'transcript': ' '.join([item['text'] for item in transcript_data]),
            'transcript_data': transcript_data,
            'language': transcript.language_code,
            'method': 'fallback',
            'status': 'success'
        }
        print(f"   ✅ Fallback exitoso")
        return result
        
    except TranscriptsDisabled:
        return {
            'video_id': video_id,
            'error': 'Los subtítulos están deshabilitados para este video',
            'status': 'error'
        }
    except NoTranscriptFound:
        return {
            'video_id': video_id,
            'error': 'No se encontró transcripción disponible',
            'status': 'error'
        }
    except Exception as e:
        return {
            'video_id': video_id,
            'error': f'Error en fallback: {str(e)}',
            'status': 'error'
        }

def load_video_list(video_list_file='data/video_list.json'):
    """
    Carga la lista de videos a transcribir
    
    Args:
        video_list_file: Ruta al archivo JSON con la lista de videos
    
    Returns:
        Lista de videos o lista de ejemplo si no existe el archivo
    """
    if os.path.exists(video_list_file):
        with open(video_list_file, 'r', encoding='utf-8') as f:
            videos = json.load(f)
        print(f"📋 Cargados {len(videos)} videos desde {video_list_file}")
        return videos
    else:
        print(f"⚠️  No se encontró {video_list_file}")
        print("📝 Creando lista de ejemplo...")
        return get_example_videos()

def get_example_videos():
    """
    Retorna una lista de ejemplo de videos famosos de Luisito Comunica
    El usuario deberá actualizar esta lista con los videos reales
    """
    return [
        {
            "video_id": "example1",
            "title": "Video de ejemplo 1 - Actualizar con video real",
            "published_at": "2024-01-01T00:00:00Z"
        }
    ]

def transcribe_all_videos(video_list_file='data/video_list.json'):
    """
    Transcribe todos los videos usando MCP o fallback
    
    Args:
        video_list_file: Ruta al archivo con la lista de videos
    
    Returns:
        Ruta al archivo de transcripciones generado
    """
    # Cargar lista de videos
    videos = load_video_list(video_list_file)
    
    if not videos:
        print("❌ No hay videos para transcribir")
        return None
    
    print(f"\n🎬 Iniciando transcripción de {len(videos)} videos\n")
    
    transcriptions = []
    mcp_count = 0
    fallback_count = 0
    error_count = 0
    
    for i, video in enumerate(videos, 1):
        video_id = video['video_id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        print(f"[{i}/{len(videos)}] {video['title'][:60]}...")
        
        result = transcribe_with_fallback(video_id, video_url)
        result.update(video)
        transcriptions.append(result)
        
        if result['status'] == 'success':
            if result.get('method') == 'MCP':
                mcp_count += 1
            else:
                fallback_count += 1
        else:
            error_count += 1
        
        # Rate limiting para no saturar APIs (aumentar si hay problemas)
        time.sleep(10)
    
    # Guardar resultados
    output_file = f"data/transcriptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(transcriptions, f, indent=2, ensure_ascii=False)
    
    # Estadísticas
    print(f"\n{'='*60}")
    print(f"📊 RESUMEN DE TRANSCRIPCIONES")
    print(f"{'='*60}")
    print(f"   Total procesados:     {len(transcriptions)}")
    print(f"   ✅ Exitosos:          {mcp_count + fallback_count}")
    print(f"      - Con MCP:         {mcp_count}")
    print(f"      - Con fallback:    {fallback_count}")
    print(f"   ❌ Errores:           {error_count}")
    print(f"   💾 Archivo:           {output_file}")
    print(f"{'='*60}\n")
    
    return output_file

def check_mcp_server(mcp_url=None):
    """
    Verifica si el servidor MCP está disponible
    
    Args:
        mcp_url: URL del servidor MCP (opcional)
    
    Returns:
        Boolean indicando si el servidor está disponible
    """
    if not mcp_url:
        mcp_url = os.getenv('MCP_URL', 'http://localhost:8080')
    
    try:
        response = requests.get(f"{mcp_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Servidor MCP disponible en {mcp_url}")
            return True
    except:
        pass
    
    print(f"⚠️  Servidor MCP no disponible en {mcp_url}")
    return False

def main():
    """Función principal"""
    print("🎥 SISTEMA DE TRANSCRIPCIÓN DE LUISITO COMUNICA")
    print("="*60)
    
    # Crear directorio de datos
    Path("data").mkdir(exist_ok=True)
    Path("chroma_db").mkdir(exist_ok=True)
    
    # Verificar servidor MCP
    mcp_available = check_mcp_server()
    if not mcp_available:
        print("\n⚠️  El servidor MCP no está disponible.")
        print("   Se usará youtube-transcript-api como fallback.")
    
    # Transcribir videos
    transcriptions_file = transcribe_all_videos()
    
    if not transcriptions_file:
        print("❌ No se generaron transcripciones")
        return
    
    # Upload a Azure si está configurado
    azure_conn_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if azure_conn_str and azure_conn_str.strip():
        print("\n📤 Subiendo transcripciones a Azure Blob Storage...")
        try:
            from upload_to_azure import upload_transcriptions
            upload_transcriptions(transcriptions_file)
            
            print("\n🧠 Construyendo vector store con ChromaDB...")
            from build_vectorstore import create_vectorstore
            create_vectorstore()
            
            print("\n✅ Pipeline completo finalizado!")
        except Exception as e:
            print(f"\n⚠️  Error en upload/vectorstore: {e}")
    else:
        print("\n⚠️  Azure no configurado. Skipping upload y vector store.")
    
    print("\n🎉 Proceso completado!")

if __name__ == "__main__":
    main()

