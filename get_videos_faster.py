"""
Obtener videos de YouTube de forma más eficiente
Usa channels.list y luego busca con search cada vez que sea necesario
"""
import os
from googleapiclient.discovery import build
from dotenv import load_dotenv
import json
import time

load_dotenv()

def get_videos_efficient(channel_id, api_key, max_videos=100):
    """
    Obtiene videos de forma más eficiente
    """
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    videos = []
    next_page_token = None
    page = 0
    
    print(f"📥 Obteniendo hasta {max_videos} videos...")
    
    while len(videos) < max_videos:
        page += 1
        print(f"   Página {page}...")
        
        try:
            request = youtube.search().list(
                part="snippet",
                channelId=channel_id,
                maxResults=min(50, max_videos - len(videos)),
                order="date",
                type="video",
                pageToken=next_page_token
            )
            response = request.execute()
            
            # Procesar resultados
            for item in response['items']:
                if len(videos) >= max_videos:
                    break
                videos.append({
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'published_at': item['snippet']['publishedAt'],
                    'description': item['snippet'].get('description', '')[:200],
                    'channel_id': channel_id
                })
            
            # Verificar si hay más páginas
            next_page_token = response.get('nextPageToken')
            if not next_page_token or len(videos) >= max_videos:
                break
            
            # Rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   ⚠️  Error en página {page}: {e}")
            if "quotaExceeded" in str(e):
                print("   ❌ Cuota excedida")
                break
            time.sleep(2)
            continue
    
    return videos

def save_video_list(videos, filename='data/video_list.json'):
    """Guardar lista de videos"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)
    print(f"✅ Guardados {len(videos)} videos en {filename}")

def main():
    print("📺 OBTENER VIDEOS DE YOUTUBE (EFICIENTE)")
    print("="*60)
    
    channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not channel_id or not api_key:
        print("❌ Configura YOUTUBE_CHANNEL_ID y YOUTUBE_API_KEY en .env")
        return
    
    # Obtener videos
    videos = get_videos_efficient(channel_id, api_key, max_videos=200)
    
    if videos:
        os.makedirs('data', exist_ok=True)
        save_video_list(videos)
        print(f"\n📊 Total: {len(videos)} videos")
        print("\n✅ ¡Listo para transcribir!")
    else:
        print("\n❌ No se pudieron obtener videos")

if __name__ == "__main__":
    main()

