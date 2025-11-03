"""
Ejemplo de cómo obtener la lista de videos de un canal de YouTube
Usando YouTube Data API v3
"""
import os
from googleapiclient.discovery import build
from dotenv import load_dotenv
import json

load_dotenv()

def get_all_videos_from_channel(channel_id, api_key):
    """
    Obtiene todos los videos de un canal de YouTube
    
    Args:
        channel_id: ID del canal de YouTube (ej: UCECJDeK0MNapZbpaOzxrUPA)
        api_key: API Key de YouTube Data API v3
    
    Returns:
        Lista de diccionarios con información de cada video
    """
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    videos = []
    next_page_token = None
    
    while True:
        # Buscar videos del canal
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=50,  # Máximo permitido por request
            order="date",
            type="video",
            pageToken=next_page_token
        )
        response = request.execute()
        
        # Procesar resultados
        for item in response['items']:
            videos.append({
                'video_id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'published_at': item['snippet']['publishedAt'],
                'description': item['snippet']['description'][:200],  # Primeros 200 chars
                'channel_id': channel_id
            })
        
        # Verificar si hay más páginas
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
    
    return videos

def save_video_list(videos, filename='data/video_list.json'):
    """
    Guarda la lista de videos en un archivo JSON
    
    Args:
        videos: Lista de videos
        filename: Nombre del archivo de salida
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Guardados {len(videos)} videos en {filename}")

def main():
    """
    Función principal
    """
    print("📺 OBTENER LISTA DE VIDEOS DE YOUTUBE")
    print("="*60)
    
    # Configuración
    channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
    api_key = os.getenv('YOUTUBE_API_KEY')  # Necesitas obtener esto
    
    if not channel_id:
        print("❌ YOUTUBE_CHANNEL_ID no está configurado en .env")
        return
    
    if not api_key:
        print("❌ YOUTUBE_API_KEY no está configurado en .env")
        print("\nPara obtener una API key:")
        print("1. Ve a https://console.cloud.google.com/")
        print("2. Crea un proyecto o selecciona uno existente")
        print("3. Habilita YouTube Data API v3")
        print("4. Crea credenciales (API Key)")
        return
    
    # Obtener videos
    print(f"\n📥 Obteniendo videos del canal: {channel_id}")
    print("   Esto puede tomar varios minutos...")
    
    try:
        videos = get_all_videos_from_channel(channel_id, api_key)
    except Exception as e:
        print(f"❌ Error obteniendo videos: {e}")
        return
    
    # Guardar en archivo
    os.makedirs('data', exist_ok=True)
    save_video_list(videos)
    
    # Estadísticas
    print(f"\n📊 RESUMEN")
    print(f"   Total de videos: {len(videos)}")
    print(f"   Guardado en: data/video_list.json")
    print("\n✅ Listo para transcribir!")

if __name__ == "__main__":
    main()

