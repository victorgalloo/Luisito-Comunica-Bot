"""
Script para verificar que toda la configuración esté correcta
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import sys

def print_header(text):
    """Imprime un header formateado"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def check_file_exists(filepath, description):
    """Verifica que un archivo exista"""
    exists = Path(filepath).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def check_env_var(var_name, description):
    """Verifica que una variable de entorno esté configurada"""
    value = os.getenv(var_name)
    has_value = value and value.strip() and not value.startswith("your")
    
    if has_value:
        # Mostrar solo los primeros y últimos 5 caracteres para seguridad
        masked_value = value[:5] + "..." + value[-5:] if len(value) > 10 else value
        print(f"✅ {description}: {masked_value}")
    else:
        print(f"❌ {description}: No configurado")
    
    return has_value

def check_docker():
    """Verifica que Docker esté instalado"""
    import subprocess
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Docker: {version}")
            return True
    except FileNotFoundError:
        print("❌ Docker: No instalado")
        return False

def check_docker_compose():
    """Verifica que Docker Compose esté disponible"""
    import subprocess
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Docker Compose: {version}")
            return True
    except FileNotFoundError:
        print("❌ Docker Compose: No disponible")
        return False

def check_azure_connection():
    """Verifica que se pueda conectar a Azure"""
    azure_conn = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if not azure_conn or not azure_conn.strip():
        return False
    
    try:
        from azure.storage.blob import BlobServiceClient
        client = BlobServiceClient.from_connection_string(azure_conn)
        # Intentar listar contenedores
        containers = list(client.list_containers())
        if containers:  # Si tiene contenedores, está bien
            print("✅ Azure Blob Storage: Conectado correctamente")
        else:
            print("✅ Azure Blob Storage: Conectado (sin contenedores)")
        return True
    except Exception as e:
        print(f"❌ Azure Blob Storage: Error conectando - {str(e)[:100]}")
        return False

def check_azure_openai():
    """Verifica que se pueda conectar a Azure OpenAI"""
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    
    if not endpoint or not api_key or not api_key.strip():
        return False
    
    try:
        import requests
        api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
        # Verificar conectividad usando el endpoint de modelos
        url = f"{endpoint}/openai/models?api-version={api_version}"
        headers = {'api-key': api_key}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            print("✅ Azure OpenAI: Conectado correctamente")
            # Verificar deployments (pero no fallar si no existen)
            deployments_url = f"{endpoint}/openai/deployments?api-version={api_version}"
            deployments_response = requests.get(deployments_url, headers=headers, timeout=5)
            if deployments_response.status_code == 200:
                deployments = deployments_response.json().get('data', [])
                print(f"   📊 Deployments encontrados: {len(deployments)}")
                if len(deployments) == 0:
                    print("   ⚠️  No hay deployments creados. Créalos en Azure AI Studio.")
            return True
        else:
            print(f"❌ Azure OpenAI: Error {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Azure OpenAI: Error conectando - {str(e)[:100]}")
        return False

def check_directories():
    """Verifica que existan los directorios necesarios"""
    dirs = [
        ('data', 'Directorio de datos'),
        ('chroma_db', 'Directorio de vector store'),
    ]
    
    all_exist = True
    for dir_name, description in dirs:
        path = Path(dir_name)
        exists = path.exists()
        if not exists:
            print(f"⚠️  {description}: No existe, será creado automáticamente")
        else:
            print(f"✅ {description}: Existe")
        all_exist = all_exist and exists
    
    return all_exist

def main():
    """Función principal"""
    print_header("VERIFICACIÓN DE CONFIGURACIÓN")
    
    # Cargar variables de entorno
    load_dotenv()
    
    print("\n📋 PRERREQUISITOS DEL SISTEMA")
    docker_ok = check_docker()
    compose_ok = check_docker_compose()
    
    print("\n📁 ARCHIVOS Y DIRECTORIOS")
    file_checks = [
        ('requirements.txt', 'Requirements'),
        ('docker-compose.yml', 'Docker Compose'),
        ('transcribe_mcp.py', 'Script de transcripción'),
        ('chatbot.py', 'Chatbot'),
        ('.env', 'Variables de entorno'),
    ]
    
    for filepath, desc in file_checks:
        check_file_exists(filepath, desc)
    
    check_directories()
    
    print("\n🔐 VARIABLES DE ENTORNO")
    env_checks = [
        ('MCP_URL', 'MCP URL'),
        ('AZURE_STORAGE_CONNECTION_STRING', 'Azure Storage Connection String'),
        ('AZURE_STORAGE_CONTAINER', 'Azure Storage Container'),
        ('AZURE_OPENAI_ENDPOINT', 'Azure OpenAI Endpoint'),
        ('AZURE_OPENAI_API_KEY', 'Azure OpenAI API Key'),
        ('AZURE_OPENAI_CHAT_DEPLOYMENT', 'Azure OpenAI Chat Deployment'),
        ('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'Azure OpenAI Embedding Deployment'),
        ('YOUTUBE_CHANNEL_ID', 'YouTube Channel ID'),
    ]
    
    for var, desc in env_checks:
        check_env_var(var, desc)
    
    print("\n🌐 VERIFICACIÓN DE CONEXIONES")
    
    # Azure Storage
    azure_ok = check_azure_connection()
    
    # Azure OpenAI
    openai_ok = check_azure_openai()
    
    print("\n📊 RESUMEN")
    print("="*60)
    
    issues = []
    if not docker_ok or not compose_ok:
        issues.append("⚠️  Instala Docker y Docker Compose")
    if not azure_ok:
        issues.append("⚠️  Verifica tu conexión a Azure Blob Storage")
    if not openai_ok:
        issues.append("⚠️  Verifica tu configuración de Azure OpenAI o crea los deployments")
    
    if not issues:
        print("\n🎉 ¡TODO LISTO!")
        print("Tu configuración está correcta. Puedes proceder con:")
        print("  1. docker-compose up -d")
        print("  2. docker-compose --profile transcriber up transcriber")
        print("  3. docker-compose --profile chatbot up chatbot")
    else:
        print("\n❌ PROBLEMAS DETECTADOS:")
        for issue in issues:
            print(f"  {issue}")
        print("\nPor favor corrige estos problemas antes de continuar.")
        sys.exit(1)

if __name__ == "__main__":
    main()

