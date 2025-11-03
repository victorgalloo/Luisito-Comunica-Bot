'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, Loader2, Youtube, Menu, X } from 'lucide-react'
import axios from 'axios'
import Image from 'next/image'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
}

interface Source {
  title: string
  video_id?: string
  url?: string
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const suggestedQuestions = [
  "¿De qué trató el video del mercado de solteros en China?",
  "¿Qué lugares visitó en Madagascar?",
  "¿Cuál fue su experiencia en Dubai?",
  "¿Qué opinó sobre Cuba?",
  "¿En qué video habla de comida mexicana?"
]

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false) // Cerrado por defecto en móvil
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (messageText?: string) => {
    const text = messageText || input.trim()
    if (!text || loading) return

    const userMessage: Message = { role: 'user', content: text }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: text,
        history: []
      })

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response,
        sources: response.data.sources
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Lo siento, hubo un error al procesar tu mensaje. Por favor intenta de nuevo.'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const clearChat = () => {
    setMessages([])
  }

  return (
    <div className="flex h-screen bg-black">
      {/* Overlay para móvil */}
      {sidebarOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black/50 z-30"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 lg:w-80 lg:static fixed inset-y-0 left-0 z-40 transition-transform duration-300 ease-in-out border-r border-zinc-900 flex flex-col overflow-hidden bg-black w-80`}>
        <div className="p-4 lg:p-6 border-b border-zinc-900">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center">
                <Bot className="w-5 h-5 text-black" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">Chatbot</h2>
                <p className="text-xs text-zinc-500">Luisito Comunica</p>
              </div>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-1.5 hover:bg-zinc-900 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-zinc-400" />
            </button>
          </div>

          {/* Imagen de Luisito */}
          <div className="relative w-full h-32 rounded-lg overflow-hidden border border-zinc-900">
            <Image
              src="/luisito.jpeg"
              alt="Luisito Comunica"
              fill
              className="object-cover"
              priority
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar p-3 lg:p-4">
          <div className="bg-zinc-950 border border-zinc-900 rounded-lg p-3 lg:p-4 mb-4">
            <h3 className="font-medium text-xs lg:text-sm text-white mb-2">¿Cómo funciona?</h3>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Acceso a <span className="text-white">48 videos</span> con <span className="text-white">IA + RAG</span> para respuestas precisas.
            </p>
          </div>

          <h3 className="font-medium text-xs lg:text-sm text-white mb-2">Preguntas sugeridas</h3>
          <div className="space-y-1.5 mb-4 lg:mb-6">
            {suggestedQuestions.map((question, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(question)}
                disabled={loading}
                className="w-full text-left px-3 py-2 bg-zinc-950 hover:bg-zinc-900 border border-zinc-900 hover:border-zinc-800 rounded-lg transition-colors text-xs text-zinc-400 hover:text-white disabled:opacity-50"
              >
                {question}
              </button>
            ))}
          </div>

          {messages.length > 0 && (
            <div className="bg-zinc-950 border border-zinc-900 rounded-lg p-3 lg:p-4 mb-4">
              <h3 className="font-medium text-xs lg:text-sm text-white mb-3">Estadísticas</h3>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between items-center">
                  <span className="text-zinc-400">Mensajes</span>
                  <span className="font-semibold text-white">{messages.length}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-zinc-400">Videos</span>
                  <span className="font-semibold text-white">48</span>
                </div>
              </div>
            </div>
          )}

          <button
            onClick={clearChat}
            disabled={messages.length === 0}
            className="w-full btn-secondary disabled:opacity-50 text-sm"
          >
            Limpiar chat
          </button>

          <div className="mt-4 lg:mt-6 pt-3 lg:pt-4 border-t border-zinc-900">
            <div className="flex flex-col items-center space-y-1 text-xs text-zinc-500">
              <p>Powered by</p>
              <p className="text-zinc-400 text-[10px] lg:text-xs">GPT-4o-mini • ChromaDB • Azure</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="border-b border-zinc-900 px-4 lg:px-6 py-4 flex items-center justify-between bg-black sticky top-0 z-30">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden p-1.5 hover:bg-zinc-900 rounded-lg transition-colors"
          >
            <Menu className="w-5 h-5 text-zinc-400" />
          </button>
          <h1 className="text-base lg:text-xl font-semibold text-white truncate">
            Luisito Comunica Chatbot
          </h1>
          <div className="w-10"></div>
        </header>

        <div className="flex-1 overflow-y-auto custom-scrollbar p-4 lg:p-6">
          {messages.length === 0 && (
            <div className="flex items-center justify-center h-full px-4">
              <div className="text-center max-w-md w-full">
                <div className="w-20 h-20 lg:w-24 lg:h-24 mx-auto mb-4 lg:mb-6 rounded-full overflow-hidden border-4 border-white ring-4 ring-white/10">
                  <Image
                    src="/luisito.jpeg"
                    alt="Luisito Comunica"
                    width={96}
                    height={96}
                    className="object-cover w-full h-full"
                    priority
                  />
                </div>
                <h2 className="text-xl lg:text-2xl font-semibold text-white mb-2">
                  ¡Hola! 👋
                </h2>
                <p className="text-zinc-400 text-xs lg:text-sm mb-1">
                  Soy el chatbot de Luisito Comunica
                </p>
                <p className="text-zinc-500 text-xs">
                  Pregúntame sobre sus 48 videos
                </p>
              </div>
            </div>
          )}

          <div className="space-y-4">
            {messages.map((message, idx) => (
              <div
                key={idx}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`message-bubble ${message.role === 'user' ? 'message-user' : 'message-assistant'}`}>
                  {message.role === 'assistant' && (
                    <div className="flex items-center mb-2">
                      <Bot className="w-4 h-4 text-zinc-500 mr-2" />
                    </div>
                  )}
                  <p className="whitespace-pre-wrap">{message.content}</p>
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-zinc-800">
                      <p className="text-xs text-zinc-500 mb-2">
                        Basado en {message.sources.length} video(s)
                      </p>
                      <div className="space-y-1.5">
                        {message.sources.map((source, sidx) => (
                          <a
                            key={sidx}
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-start space-x-2 p-2 bg-zinc-950 hover:bg-zinc-900 rounded-lg transition-colors group border border-zinc-900"
                          >
                            <Youtube className="w-3.5 h-3.5 text-red-500 mt-0.5 flex-shrink-0" />
                            <p className="text-xs text-zinc-400 group-hover:text-white truncate">
                              {sidx + 1}. {source.title}
                            </p>
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="message-bubble message-assistant">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="w-4 h-4 text-zinc-500 animate-spin" />
                    <span className="text-zinc-400">Pensando...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div ref={messagesEndRef} />
        </div>

        <div className="border-t border-zinc-900 p-3 lg:p-4 bg-black sticky bottom-0">
          <div className="flex items-end space-x-2 lg:space-x-3 max-w-4xl mx-auto">
            <div className="flex-1 relative min-w-0">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Escribe un mensaje..."
                className="w-full px-3 lg:px-4 py-2.5 lg:py-3 bg-zinc-950 border border-zinc-800 rounded-lg focus:ring-2 focus:ring-white focus:border-transparent resize-none custom-scrollbar text-white placeholder:text-zinc-600 text-sm"
                rows={1}
                style={{ maxHeight: '120px' }}
              />
            </div>
            <button
              onClick={() => handleSend()}
              disabled={loading || !input.trim()}
              className="btn-primary flex items-center space-x-2 shrink-0 px-4 lg:px-6"
            >
              <Send className="w-4 h-4" />
              <span className="hidden sm:inline">Enviar</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
