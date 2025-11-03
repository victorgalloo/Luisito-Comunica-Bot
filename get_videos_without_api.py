"""
Obtener lista de videos sin YouTube API
Usando yt-dlp como alternativa
"""
import subprocess
import json
import os
from dotenv import load_dotenv

load_dotenv()

def get_videos_with_ytdlp(channel_url):
    """
    Obtiene lista de videos usando yt-dlp
    
    Args:
        channel_url: URL del canal (ej: @LuisitoComunica o UCECJDeK0MNapZbpaOzxrUPA)
    
    Returns:
        Lista de diccionarios con información de videos
    """
    try:
        # Intentar usar yt-dlp
        cmd = [
            'yt-dlp',
            '--flat-playlist',
            '--dump-json',
            '--playlist-end', '50',  # Limitar a primeros 50 videos
            f'https://www.youtube.com/{channel_url}/videos'
        ]
        
        print("📥 Descargando información de videos con yt-dlp...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"⚠️  yt-dlp no está instalado: {result.stderr}")
            return None
        
        # Parsear salida JSON
        videos = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    video_data = json.loads(line)
                    videos.append({
                        'video_id': video_data.get('id'),
                        'title': video_data.get('title'),
                        'duration': video_data.get('duration'),
                        'view_count': video_data.get('view_count'),
                        'published_at': video_data.get('upload_date', '')[:10] if video_data.get('upload_date') else None,
                        'url': video_data.get('url', f"https://www.youtube.com/watch?v={video_data.get('id')}")
                    })
                except:
                    continue
        
        return videos
    
    except FileNotFoundError:
        print("❌ yt-dlp no está instalado")
        print("\nPara instalar yt-dlp:")
        print("  brew install yt-dlp  # macOS")
        print("  pip install yt-dlp   # Python")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def save_video_list(videos, filename='data/video_list.json'):
    """Guardar lista de videos en JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)
    print(f"✅ Guardados {len(videos)} videos en {filename}")

def main():
    """Función principal"""
    print("📺 OBTENER VIDEOS SIN YOUTUBE API")
    print("="*60)
    
    channel_id = os.getenv('YOUTUBE_CHANNEL_ID', 'UCECJDeK0MNapZbpaOzxrUPA')
    channel_url = f"channel/{channel_id}"
    
    print(f"Canal: {channel_id}")
    print("Usando yt-dlp (sin API key necesario)\n")
    
    videos = get_videos_with_ytdlp(channel_url)
    
    if videos:
        os.makedirs('data', exist_ok=True)
        save_video_list(videos)
        print(f"\n📊 Total: {len(videos)} videos")
        print("\n✅ ¡Listo para transcribir!")
    else:
        print("\n⚠️  No se pudieron obtener videos")
        print("\nOpción alternativa:")
        print("1. Instala yt-dlp: brew install yt-dlp")
        print("2. O usa YouTube API Key (ver OBTENER_YOUTUBE_API_KEY.md)")

if __name__ == "__main__":
    main()

