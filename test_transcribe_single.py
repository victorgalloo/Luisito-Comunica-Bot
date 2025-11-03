"""
Test transcripción de un solo video con delays apropiados
"""
import os
import time
from dotenv import load_dotenv
load_dotenv()

from transcribe_mcp import transcribe_with_fallback
import json

# Test con el primer video
test_video = {
    "video_id": "eGa2qQFgJJE",
    "title": "Buscando pareja en el mercado de solteros de CHINA",
}

print("🧪 TEST: Transcripción Individual")
print("="*60)
print(f"Video: {test_video['title']}")
print(f"ID: {test_video['video_id']}")
print()

video_url = f"https://www.youtube.com/watch?v={test_video['video_id']}"

# Transcribir
print("⏳ Iniciando transcripción...")
result = transcribe_with_fallback(test_video['video_id'], video_url)

# Mostrar resultado
print()
print("="*60)
print("RESULTADO:")
print("="*60)

if result.get('status') == 'success':
    transcript = result.get('transcript', '')
    print(f"✅ Éxito!")
    print(f"Método: {result.get('method')}")
    print(f"Idioma: {result.get('language')}")
    print(f"Caracteres: {len(transcript)}")
    print(f"\nPrimeros 500 caracteres:")
    print("-"*60)
    print(transcript[:500])
    print("-"*60)
else:
    print(f"❌ Error: {result.get('error', 'Error desconocido')}")

print()
print("="*60)

