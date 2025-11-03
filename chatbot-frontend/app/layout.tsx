import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Luisito Comunica Chatbot',
  description: 'Chatbot interactivo sobre los videos de Luisito Comunica usando IA',
  viewport: 'width=device-width, initial-scale=1, maximum-scale=1',
  themeColor: '#000000',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body className="font-sans antialiased">
        {children}
      </body>
    </html>
  )
}

