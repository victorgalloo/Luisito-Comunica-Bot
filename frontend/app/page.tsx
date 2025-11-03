'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Film, Trash2, RotateCcw } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{
    title: string;
    video_id: string;
    chunk_id: string;
  }>;
}

const SUGGESTED_QUESTIONS = [
  "¿De qué trató el video del mercado de solteros en China?",
  "¿Qué lugares visitó en Madagascar?",
  "¿Cuál fue su experiencia en Dubai?",
  "¿Qué opinó sobre Cuba?",
  "¿En qué video habla de comida mexicana?",
];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ total_chunks: 0 });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Cargar stats al iniciar
    fetch('http://localhost:8000/api/stats')
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(err => console.error('Error loading stats:', err));
  }, []);

  const sendMessage = async (messageText?: string) => {
    const text = messageText || input.trim();
    if (!text) return;

    // Agregar mensaje del usuario
    const userMessage: Message = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: text,
          conversation_id: 'default',
        }),
      });

      const data = await response.json();
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        sources: data.sources,
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Lo siento, hubo un error al generar la respuesta. Por favor intenta de nuevo.',
      };
      setMessages(prev => [...prev, errorMessage]);
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  const handleSuggestedQuestion = (question: string) => {
    sendMessage(question);
  };

  return (
    <div className="flex min-h-screen bg-gradient-to-br from-slate-50 to-purple-50">
      {/* Sidebar */}
      <aside className="w-80 bg-white/80 backdrop-blur-sm border-r border-purple-100 flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-purple-100">
          <div className="text-center">
            <div className="text-4xl mb-2">🎥</div>
            <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
              Luisito Comunica
            </h2>
            <p className="text-sm text-gray-500 mt-1">Chatbot IA</p>
          </div>
        </div>

        {/* Info Box */}
        <div className="p-6 border-b border-purple-100">
          <div className="bg-gradient-to-br from-purple-50 to-indigo-50 p-4 rounded-xl border border-purple-200">
            <h3 className="font-semibold text-purple-900 mb-2">🤖 ¿Cómo funciona?</h3>
            <p className="text-sm text-gray-700 leading-relaxed">
              Este chatbot tiene acceso a <strong>48 videos</strong> de Luisito Comunica y puede responder tus preguntas sobre su contenido.
            </p>
            <p className="text-sm text-purple-700 mt-2">
              💡 Usa <strong>IA + RAG</strong> para respuestas precisas basadas en los videos reales.
            </p>
          </div>
        </div>

        {/* Suggested Questions */}
        <div className="flex-1 overflow-y-auto p-6">
          <h3 className="font-semibold text-gray-800 mb-3">💬 Preguntas sugeridas</h3>
          <div className="space-y-2">
            {SUGGESTED_QUESTIONS.map((question, idx) => (
              <button
                key={idx}
                onClick={() => handleSuggestedQuestion(question)}
                className="w-full text-left p-3 text-sm bg-white rounded-lg border border-purple-200 hover:border-purple-400 hover:bg-purple-50 transition-all duration-200 text-gray-700"
              >
                {question}
              </button>
            ))}
          </div>
        </div>

        {/* Stats */}
        {messages.length > 0 && (
          <div className="p-6 border-t border-purple-100">
            <div className="bg-white rounded-xl p-4 border border-gray-200">
              <h3 className="font-semibold text-gray-800 mb-3 text-center">📊 Estadísticas</h3>
              <div className="text-center space-y-2">
                <div>
                  <div className="text-3xl font-bold text-purple-600">{messages.length}</div>
                  <div className="text-xs text-gray-500">Mensajes</div>
                </div>
                <div className="border-t pt-2">
                  <div className="text-xl font-bold text-indigo-600">{stats.total_chunks || 48}</div>
                  <div className="text-xs text-gray-500">Videos disponibles</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="p-6 border-t border-purple-100 space-y-2">
          <button
            onClick={clearChat}
            className="w-full flex items-center justify-center gap-2 p-3 bg-white border border-red-200 rounded-lg hover:bg-red-50 hover:border-red-400 transition-all duration-200 text-red-600 font-medium"
          >
            <Trash2 size={16} />
            Limpiar
          </button>
          <button
            onClick={clearChat}
            className="w-full flex items-center justify-center gap-2 p-3 bg-white border border-purple-200 rounded-lg hover:bg-purple-50 hover:border-purple-400 transition-all duration-200 text-purple-600 font-medium"
          >
            <RotateCcw size={16} />
            Nuevo chat
          </button>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-purple-100 text-center">
          <p className="text-xs text-gray-500 mb-2">Powered by</p>
          <div className="text-xs text-gray-600 space-y-1">
            <p>🤖 GPT-4o-mini</p>
            <p>🧠 ChromaDB</p>
            <p>☁️ Azure OpenAI</p>
          </div>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white/80 backdrop-blur-sm border-b border-purple-100 p-6">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-4xl font-black bg-gradient-to-r from-purple-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent mb-2">
              🎥 Luisito Comunica Chatbot
            </h1>
            <p className="text-gray-600">Pregunta todo sobre los videos de Luisito</p>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.length === 0 && (
              <div className="text-center py-12 px-6 bg-gradient-to-br from-purple-50 to-indigo-50 rounded-2xl border-2 border-dashed border-purple-200">
                <h2 className="text-3xl font-bold text-purple-600 mb-4">👋 ¡Hola!</h2>
                <p className="text-lg text-gray-700 mb-6">
                  Soy el chatbot de Luisito Comunica. Puedo responder preguntas sobre sus{' '}
                  <strong className="text-purple-600">48 videos</strong>
                </p>
                <p className="text-gray-600">
                  💡 Usa las <strong className="text-purple-600">preguntas sugeridas</strong> en el sidebar o escribe tu propia pregunta
                </p>
              </div>
            )}

            {messages.map((message, idx) => (
              <div
                key={idx}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-2xl rounded-2xl p-4 ${
                    message.role === 'user'
                      ? 'bg-purple-600 text-white'
                      : 'bg-white border border-purple-100 text-gray-800'
                  }`}
                >
                  <div className="prose prose-sm max-w-none">
                    {message.content.split('\n').map((line, i) => (
                      <p key={i}>{line}</p>
                    ))}
                  </div>
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-purple-200">
                      <details className="text-xs">
                        <summary className="cursor-pointer text-purple-600 hover:text-purple-700 font-medium">
                          📚 Ver fuentes ({message.sources.length} video{message.sources.length > 1 ? 's' : ''})
                        </summary>
                        <div className="mt-2 space-y-2">
                          {message.sources.map((source, i) => (
                            <div
                              key={i}
                              className="bg-gray-50 p-2 rounded-lg border-l-2 border-purple-400 hover:bg-gray-100 transition-colors"
                            >
                              <strong className="text-purple-600">📹 Fuente {i + 1}</strong>
                              <p className="text-gray-700 mt-1">{source.title}</p>
                            </div>
                          ))}
                        </div>
                      </details>
                    </div>
                  )}
                  {message.role === 'assistant' && message.sources && message.sources.length > 0 && (
                    <p className="text-xs text-gray-500 mt-2">
                      ✅ Basado en {message.sources.length} video{message.sources.length > 1 ? 's' : ''} de Luisito Comunica
                    </p>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-white border border-purple-100 rounded-2xl p-4">
                  <div className="flex items-center gap-2 text-gray-600">
                    <Sparkles className="animate-pulse" size={20} />
                    <span>🤔 Pensando en los videos de Luisito...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input */}
        <div className="bg-white/80 backdrop-blur-sm border-t border-purple-100 p-6">
          <div className="max-w-4xl mx-auto">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                sendMessage();
              }}
              className="flex gap-4"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="💬 Pregunta algo sobre los videos de Luisito..."
                className="flex-1 px-4 py-3 border border-purple-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2 font-medium"
              >
                <Send size={20} />
                Enviar
              </button>
            </form>
          </div>
        </div>

        {/* Footer */}
        <footer className="bg-gradient-to-r from-purple-50 to-indigo-50 border-t border-purple-100 p-6">
          <div className="max-w-4xl mx-auto text-center">
            <p className="text-sm text-gray-600">
              🤖 Powered by <strong>GPT-4o-mini</strong> | 🧠 <strong>ChromaDB</strong> | ☁️{' '}
              <strong>Azure OpenAI</strong>
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Hecho con ❤️ para los fans de Luisito Comunica
            </p>
          </div>
        </footer>
      </main>
    </div>
  );
}
