# ⚡ Deploy Rápido - Luisito Comunica Chatbot

## 🚀 Opción Más Rápida: Deploy Local (Para Probar)

```bash
# 1. Verificar que tienes .env configurado
cat .env

# 2. Iniciar todo con un comando
./deploy.sh local

# 3. Verificar que está corriendo
./deploy.sh status

# 4. Acceder:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - Health check: http://localhost:8000/health
```

## 🌐 Para Producción (24/7 en Internet)

### Opción 1: Railway (Más Fácil) ⭐ RECOMENDADO

1. **Sube tu código a GitHub**

2. **Ve a [railway.app](https://railway.app)** y conecta GitHub

3. **Crea dos servicios:**

   **Backend:**
   - Deploy desde `Dockerfile.api`
   - Variables de entorno:
     ```
     AZURE_OPENAI_ENDPOINT=tu_endpoint
     AZURE_OPENAI_API_KEY=tu_key
     AZURE_OPENAI_API_VERSION=2024-02-15-preview
     AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
     AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
     ```

   **Frontend:**
   - Root: `chatbot-frontend`
   - Build: `npm install && npm run build`
   - Start: `npm start`
   - Variables:
     ```
     NEXT_PUBLIC_API_URL=https://tu-backend.railway.app
     ```

4. **Listo!** Tu app estará online en ~5 minutos

**Costo:** $5/mes (con $5 gratis al mes)

---

### Opción 2: Render (Gratis para empezar)

1. Ve a [render.com](https://render.com)

2. Crea dos Web Services similares a Railway

3. Configura igual que Railway

**Costo:** Gratis (con límites) o $7/mes

---

### Opción 3: VPS DigitalOcean ($5/mes)

```bash
# 1. Renta un VPS (2GB RAM mínimo)
# 2. Conecta por SSH
# 3. Instala Docker:
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 4. Clona tu repo
git clone tu-repo
cd LuisitoComunica

# 5. Crea .env
nano .env

# 6. Inicia
docker-compose up -d

# 7. Configura dominio y HTTPS (opcional)
```

---

## 📝 Checklist Rápido

Antes de deployar:

- [ ] Archivo `.env` configurado con todas las variables
- [ ] ChromaDB existe en `./chroma_db/` (o está en Azure Blob Storage)
- [ ] Variables de Azure OpenAI funcionando
- [ ] `NEXT_PUBLIC_API_URL` apunta al backend correcto (en producción)

---

## 🆘 Problemas Comunes

### "Backend no responde"
```bash
# Ver logs
docker-compose logs api

# Reiniciar
docker-compose restart api
```

### "ChromaDB no encontrado"
```bash
# Verificar que existe
ls -la chroma_db/

# Si no existe, necesitas construirlo primero:
python build_vectorstore.py
```

### "CORS errors"
- Actualiza `allow_origins` en `api_server.py` con tu dominio real

---

## 📚 Documentación Completa

Para instrucciones detalladas, revisa **GUIA_DEPLOY.md**

---

**¿Dudas?** Revisa los logs: `docker-compose logs -f`

