# Luisito Comunica Chatbot Frontend

Frontend moderno con React y Next.js para el chatbot de Luisito Comunica.

## 🚀 Características

- ⚛️ **React + Next.js 14**: Framework moderno con App Router
- 🎨 **Tailwind CSS**: Diseño responsive y moderno
- 💬 **Chat en tiempo real**: Interfaz de chat fluida
- 📱 **Responsive**: Funciona en desktop, tablet y móvil
- 🎯 **Preguntas sugeridas**: Botones interactivos
- 📊 **Estadísticas**: Métricas en tiempo real
- 🔗 **Enlaces a videos**: Links directos a YouTube

## 🛠️ Instalación

```bash
# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev

# Build para producción
npm run build

# Ejecutar producción
npm start
```

## 🌐 Configuración

Crea un archivo `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📦 Uso con Docker

El frontend se incluye automáticamente en el `docker-compose.yml` del proyecto principal.

## 🎨 Tecnologías

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Lucide Icons
- Axios

## 📝 Scripts

- `npm run dev`: Desarrollo
- `npm run build`: Build producción
- `npm start`: Ejecutar producción
- `npm run lint`: Linter

## 🔌 API

El frontend consume la API REST de FastAPI en `http://localhost:8000`.

Endpoints:
- `POST /chat`: Enviar mensaje
- `GET /health`: Health check
- `GET /stats`: Estadísticas

