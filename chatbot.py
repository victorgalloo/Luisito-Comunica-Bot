"""
Chatbot de Luisito Comunica usando RAG con ChromaDB y OpenAI
Interfaz web con Streamlit
"""
import streamlit as st
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import chromadb
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Configurar la página
st.set_page_config(
    page_title="🎥 Luisito Comunica Chatbot",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado con diseño moderno
st.markdown("""
<style>
    /* Estilos globales */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header mejorado */
    .main-header {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .sub-header {
        text-align: center;
        color: #64748b;
        margin-bottom: 2rem;
        font-size: 1.1rem;
    }
    
    /* Sidebar mejorado */
    .stSidebar {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Info boxes modernos */
    .info-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #667eea30;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .metric-box {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Chat input mejorado */
    .stChatFloatingInputContainer {
        bottom: 20px;
        background-color: white;
        border-top: 1px solid #e2e8f0;
    }
    
    /* Mensajes de usuario */
    [data-testid="stChatMessage-user"] {
        background-color: #667eea;
        color: white;
    }
    
    /* Botones mejorados */
    .stButton > button {
        border-radius: 12px;
        border: 2px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #667eea;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Stats modernas */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    /* Fuentes mejoradas */
    .source-item {
        background-color: #f8fafc;
        padding: 0.75rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 3px solid #667eea;
        transition: all 0.2s ease;
    }
    
    .source-item:hover {
        background-color: #f1f5f9;
        transform: translateX(5px);
    }
    
    /* Scrollbar personalizado */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_chatbot():
    """
    Inicializa el chatbot con el vector store y LLM
    
    Returns:
        Tupla con (llm, memory, get_chunks function, embeddings)
    """
    try:
        # Verificar que existe el vector store
        persist_directory = "./chroma_db"
        if not Path(persist_directory).exists():
            st.error("❌ No se encontró el vector store. Por favor ejecuta primero `build_vectorstore.py`")
            return None, None, None, None
        
        # Cargar vector store desde ChromaDB local
        client = chromadb.PersistentClient(path=persist_directory)
        
        try:
            collection = client.get_collection("luisito_transcripts")
        except:
            st.error("❌ No se encontró la collection 'luisito_transcripts'. Ejecuta `build_vectorstore.py` primero.")
            return None, None, None, None
        
        # Inicializar embeddings con Azure OpenAI
        azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        azure_api_key = os.getenv('AZURE_OPENAI_API_KEY')
        api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
        
        # Validar configuración de Azure OpenAI
        if not azure_endpoint:
            st.error("❌ AZURE_OPENAI_ENDPOINT no está configurado en .env")
            return None, None, None, None
        
        if not azure_api_key:
            st.error("❌ AZURE_OPENAI_API_KEY no está configurado en .env")
            return None, None, None, None
        
        # Inicializar embeddings
        embedding_deployment = os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'text-embedding-ada-002')
        embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=azure_endpoint,
            api_key=azure_api_key,
            api_version=api_version,
            azure_deployment=embedding_deployment
        )
        
        # Inicializar LLM con Azure OpenAI
        chat_deployment = os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT', 'gpt-4o-mini')
        llm = AzureChatOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=azure_api_key,
            api_version=api_version,
            azure_deployment=chat_deployment,
            temperature=0.7,
            max_tokens=1500
        )
        
        # Memoria manejada por Streamlit
        memory = None  # Usaremos st.session_state para la memoria
        
        # Función para obtener chunks relevantes
        def get_relevant_chunks(query, n_results=5):
            """
            Busca chunks relevantes en el vector store
            
            Args:
                query: Pregunta del usuario
                n_results: Número de resultados a retornar
            
            Returns:
                Tupla con (documents, metadatas)
            """
            query_embedding = embeddings.embed_query(query)
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            
            return documents, metadatas
        
        return llm, memory, get_relevant_chunks, embeddings
    
    except Exception as e:
        st.error(f"❌ Error inicializando chatbot: {e}")
        return None, None, None, None

def generate_response(llm, memory, get_relevant_chunks, query):
    """
    Genera una respuesta usando RAG
    
    Args:
        llm: Modelo de lenguaje
        memory: Memoria de conversación
        get_relevant_chunks: Función para obtener chunks relevantes
        query: Pregunta del usuario
    
    Returns:
        Tupla con (response, sources, metadatas)
    """
    # Obtener chunks relevantes
    docs, metadatas = get_relevant_chunks(query)
    
    # Construir contexto
    context = "\n\n".join([
        f"[Video: {meta['title']}]\n{doc}"
        for doc, meta in zip(docs, metadatas)
    ])
    
    # Construir prompt
    system_prompt = """Eres un asistente de IA especializado en el contenido de Luisito Comunica.
Responde las preguntas de los usuarios basándote ÚNICAMENTE en el siguiente contexto de sus videos.
Si la información no está en el contexto, di amablemente que no tienes esa información.

Mantén un tono conversacional y amigable, como si fueras Luisito Comunica."""
    
    user_prompt = f"""Contexto:
{context}

Pregunta del usuario: {query}

Responde de manera natural y conversacional:"""
    
    # Generar respuesta
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = llm.invoke(messages).content
    except Exception as e:
        response = f"Lo siento, hubo un error generando la respuesta: {e}"
    
    # Memoria manejada por Streamlit session_state
    # No necesitamos guardar manualmente
    
    return response, docs, metadatas

def main():
    """
    Interfaz principal del chatbot
    """
    # Header
    st.markdown('<div class="main-header">🎥 Luisito Comunica Chatbot</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Pregunta todo sobre los videos de Luisito!</div>', unsafe_allow_html=True)
    
    # Inicializar chatbot
    llm, memory, get_relevant_chunks, embeddings = initialize_chatbot()
    
    # Verificar si se inicializó correctamente
    if llm is None:
        st.stop()
    
    # Inicializar historial de chat en session_state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar mejorado
    with st.sidebar:
        # Header con logo
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h2 style='margin: 0; color: #667eea;'>🎥</h2>
            <h3 style='margin: 0.5rem 0; color: #1e293b;'>Luisito Comunica</h3>
            <p style='color: #64748b; font-size: 0.9rem; margin: 0;'>Chatbot IA</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Info box mejorado
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("""
        ### 🤖 ¿Cómo funciona?
        
        Este chatbot tiene acceso a **48 videos** de Luisito Comunica y puede responder tus preguntas sobre su contenido.
        
        💡 Usa **IA + RAG** para darte respuestas precisas basadas en los videos reales.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Preguntas sugeridas interactivas
        st.markdown("### 💬 Preguntas sugeridas")
        suggested_questions = [
            "¿De qué trató el video del mercado de solteros en China?",
            "¿Qué lugares visitó en Madagascar?",
            "¿Cuál fue su experiencia en Dubai?",
            "¿Qué opinó sobre Cuba?",
            "¿En qué video habla de comida mexicana?"
        ]
        
        for question in suggested_questions:
            if st.button(question, key=f"suggest_{hash(question)}", use_container_width=True):
                # Agregar pregunta automáticamente al chat
                st.session_state.messages.append({"role": "user", "content": question})
                st.rerun()
        
        st.divider()
        
        # Estadísticas mejoradas
        total_messages = len(st.session_state.messages)
        if total_messages > 0:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.markdown(f"### 📊 Estadísticas")
            st.metric("💬 Mensajes", total_messages)
            st.metric("📹 Videos disponibles", "48")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Botón limpiar con mejor diseño
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Limpiar", use_container_width=True, help="Eliminar historial de chat"):
                st.session_state.messages = []
                st.rerun()
        
        with col2:
            if st.button("🔄 Nuevo chat", use_container_width=True, help="Comenzar conversación nueva"):
                st.session_state.messages = []
                st.rerun()
        
        st.markdown("---")
        
        # Footer con info
        st.markdown("""
        <div style='text-align: center; padding: 1rem; color: #64748b; font-size: 0.8rem;'>
            <p style='margin: 0.5rem 0;'>Powered by</p>
            <p style='margin: 0;'>🤖 GPT-4o-mini</p>
            <p style='margin: 0;'>🧠 ChromaDB</p>
            <p style='margin: 0;'>☁️ Azure OpenAI</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Mostrar mensaje de bienvenida si no hay mensajes
    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div style='text-align: center; padding: 3rem 1rem; background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%); 
                    border-radius: 16px; border: 2px dashed #cbd5e1; margin: 2rem 0;'>
            <h2 style='color: #667eea; margin-bottom: 1rem;'>👋 ¡Hola!</h2>
            <p style='color: #64748b; font-size: 1.1rem; margin-bottom: 1.5rem;'>
                Soy el chatbot de Luisito Comunica. Puedo responder preguntas sobre sus <strong>48 videos</strong>
            </p>
            <p style='color: #94a3b8; font-size: 0.95rem;'>
                💡 Usa las <strong>preguntas sugeridas</strong> en el sidebar o escribe tu propia pregunta
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Mostrar historial de chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Mostrar fuentes mejoradas
            if message["role"] == "assistant" and "sources" in message and message["sources"]:
                with st.expander("📚 Ver fuentes (videos referenciados)", expanded=False):
                    for idx, source in enumerate(message["sources"], 1):
                        st.markdown(f"""
                        <div style='background: #f8fafc; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid #667eea;'>
                            <strong>📹 Fuente {idx}</strong><br>
                            {source['title'][:80] if len(source.get('title', '')) > 80 else source.get('title', 'Sin título')}...
                        </div>
                        """, unsafe_allow_html=True)
    
    # Input del usuario mejorado
    if prompt := st.chat_input("💬 Pregunta algo sobre los videos de Luisito..."):
        # Validar que no esté vacío
        if not prompt.strip():
            st.warning("Por favor escribe una pregunta")
            return
        
        # Agregar mensaje del usuario al historial
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generar respuesta con mejor UI
        with st.chat_message("assistant"):
            with st.spinner("🤔 Pensando en los videos de Luisito..."):
                response, docs, metadatas = generate_response(
                    llm, 
                    memory, 
                    get_relevant_chunks, 
                    prompt
                )
                # Mostrar respuesta con animación
                st.markdown(response)
                
                # Indicador de que se usaron fuentes
                if metadatas and len(metadatas) > 0:
                    st.caption(f"✅ Basado en {len(metadatas)} video(s) de Luisito Comunica")
        
        # Agregar respuesta al historial
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "sources": metadatas
        })
    
    # Footer mejorado
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%); 
                    border-radius: 12px; border: 1px solid #e2e8f0;'>
            <p style='margin: 0; color: #64748b; font-size: 0.85rem;'>
                🤖 Powered by <strong>GPT-4o-mini</strong> | 🧠 <strong>ChromaDB</strong> | ☁️ <strong>Azure OpenAI</strong>
            </p>
            <p style='margin: 0.5rem 0 0 0; color: #94a3b8; font-size: 0.75rem;'>
                Hecho con ❤️ para los fans de Luisito Comunica
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

