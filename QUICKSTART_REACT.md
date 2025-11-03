# 🚀 Quick Start - React + Next.js

## ⚡ Inicio Rápido en 3 Pasos

### 1️⃣ Construir los servicios

```bash
# Construir solo API + Frontend
docker-compose build api frontend
```

### 2️⃣ Ejecutar

```bash
# Ejecutar API + Frontend
docker-compose up api frontend
```

### 3️⃣ Abrir en el navegador

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000

---

## 🎯 Desarrollo Local (Sin Docker)

### Backend

```bash
# Terminal 1: API
pip install -r requirements.txt
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
# Terminal 2: Frontend
cd chatbot-frontend
npm install
npm run dev
```

---

## ✅ Verificar que Funciona

### 1. API Health Check

```bash
curl http://localhost:8000/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "message": "API funcionando correctamente",
  "vector_store_ready": true
}
```

### 2. Estadísticas

```bash
curl http://localhost:8000/stats
```

**Respuesta esperada:**
```json
{
  "total_chunks": 1328,
  "status": "ready"
}
```

### 3. Chat Test

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿De qué trata el video de Japón?"}'
```

---

## 🐛 Problemas Comunes

### "Error connecting to API"

**Solución:**
```bash
# Verificar que la API está corriendo
docker-compose ps api

# Ver logs
docker-compose logs api
```

### "CORS error"

La API ya tiene CORS configurado. Si ves errores:

1. Verifica que `NEXT_PUBLIC_API_URL=http://localhost:8000` en `.env.local`
2. Reinicia el frontend

### "Vector store not found"

**Solución:**
```bash
# Asegúrate de que chroma_db existe
ls -la chroma_db/

# Si no existe, construye el vector store
python build_vectorstore.py
```

---

## 📦 Comandos Útiles

```bash
# Construir todo
docker-compose build

# Ejecutar todo (con transcripciones)
docker-compose --profile transcriber up

# Solo API + Frontend
docker-compose up api frontend

# Ver logs
docker-compose logs -f api frontend

# Detener todo
docker-compose down

# Limpiar volúmenes
docker-compose down -v
```

---

## 🎨 Customización

### Cambiar colores

Editar `chatbot-frontend/tailwind.config.js`:

```js
colors: {
  primary: {
    // Cambiar estos valores
    500: '#667eea',
    600: '#764ba2',
  },
}
```

### Agregar nuevas preguntas

Editar `chatbot-frontend/app/page.tsx`:

```tsx
const suggestedQuestions = [
  "Tu nueva pregunta aquí",
  // ...
]
```

---

## 🚀 Deploy

### Vercel (Frontend)

```bash
cd chatbot-frontend
vercel deploy
```

### Azure Container Apps (Backend)

```bash
az containerapp create \
  --name luisito-api \
  --image tu-registry.azurecr.io/luisito-api:latest \
  --resource-group luisito-rg \
  --target-port 8000
```

---

## 📚 Próximos Pasos

1. Lee `MIGRACION_REACT.md` para detalles completos
2. Agrega autenticación
3. Implementa analytics
4. Configura CI/CD
5. Deploy a producción

---

**¡Ya tienes un chatbot moderno con React + Next.js funcionando!** 🎉

