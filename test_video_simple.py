"""
Script simple para probar transcripciones de YouTube
"""
import sys

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    
    # Probar con el video del usuario
    video_id = sys.argv[1] if len(sys.argv) > 1 else 'eGa2qQFgJJE'
    print(f'🎬 Transcribiendo: {video_id}')
    
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    
    print('\n📋 Idiomas disponibles:')
    for t in transcript_list:
        print(f'  - {t.language} ({t.language_code}): Manual={not t.is_generated}')
    
    # Intentar obtener transcripción
    try:
        transcript = transcript_list.find_manually_created_transcript(['es', 'en'])
        print(f'\n✅ Transcripción manual encontrada: {transcript.language}')
    except:
        transcript = transcript_list.find_generated_transcript(['es', 'en'])
        print(f'\n✅ Transcripción generada encontrada: {transcript.language}')
    
    # Si no está en español, traducir
    if transcript.language_code != 'es':
        print(f'🔄 Traduciendo de {transcript.language_code} a español...')
        transcript = transcript.translate('es')
    
    data = transcript.fetch()
    print(f'\n✅ Transcripción obtenida: {len(data)} segmentos')
    
    # Mostrar muestra
    text = ' '.join([item['text'] for item in data[:20]])
    print(f'\n📝 Muestra (primeros 500 caracteres):')
    print(text[:500])
    print('\n✅ ¡Éxito!')
    
except Exception as e:
    print(f'\n❌ Error: {e}')
    import traceback
    traceback.print_exc()

