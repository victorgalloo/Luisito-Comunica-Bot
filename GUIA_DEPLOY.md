# 🚀 Guía Completa de Deploy - Luisito Comunica Chatbot

Esta guía te explica cómo hacer deploy del backend (y frontend) para que funcione **24/7 de manera continua**.

---

## 📋 Índice

1. [Deploy Local (Desarrollo/Pruebas)](#1-deploy-local-desarrollopruebas)
2. [Deploy en la Nube (Producción)](#2-deploy-en-la-nube-producción)
   - [Opción A: Azure Container Apps (Recomendado)](#opción-a-azure-container-apps-recomendado)
   - [Opción B: Railway](#opción-b-railway)
   - [Opción C: Render](#opción-c-render)
   - [Opción D: DigitalOcean App Platform](#opción-d-digitalocean-app-platform)
   - [Opción E: VPS propio (Docker Compose)](#opción-e-vps-propio-docker-compose)
3. [Configuración para Producción](#3-configuración-para-producción)
4. [Persistencia de Datos](#4-persistencia-de-datos)
5. [Monitoreo y Logs](#5-monitoreo-y-logs)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Deploy Local (Desarrollo/Pruebas)

### Opción A: Docker Compose (Recomendado para pruebas)

**Ventajas:**
- ✅ Fácil de configurar
- ✅ Corre todos los servicios juntos
- ✅ Buena para desarrollo

**Desventajas:**
- ❌ Se detiene cuando apagas tu computadora
- ❌ No es accesible desde internet

**Pasos:**

```bash
# 1. Iniciar todos los servicios
docker-compose up -d

# 2. Verificar que todo esté corriendo
docker-compose ps

# Deberías ver:
# - luisito-mcp-youtube (puerto 8080)
# - luisito-api (puerto 8000)
# - luisito-frontend (puerto 3000)

# 3. Ver logs
docker-compose logs -f

# 4. Para detener
docker-compose down
```

**Para que corra automáticamente al reiniciar tu Mac/Linux:**

```bash
# Crear un servicio systemd (Linux) o LaunchDaemon (Mac)
# En Mac, usar launchd (ver abajo)
```

**En macOS con launchd:**

Crea un archivo `~/Library/LaunchAgents/com.luisito.chatbot.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.luisito.chatbot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/docker-compose</string>
        <string>-f</string>
        <string>/Users/victorgallo/LuisitoComunica/docker-compose.yml</string>
        <string>up</string>
        <string>-d</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/victorgallo/LuisitoComunica</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Luego ejecuta:

```bash
launchctl load ~/Library/LaunchAgents/com.luisito.chatbot.plist
```

---

## 2. Deploy en la Nube (Producción)

Para que el backend funcione **24/7 y sea accesible desde internet**, necesitas deployarlo en la nube.

### ⚠️ Consideraciones Importantes

**ChromaDB (Vector Store):**
- El vector store está en `./chroma_db/` (local)
- En producción, necesitas **persistencia** (volúmenes, storage cloud, etc.)
- Opciones:
  1. Usar volúmenes persistentes del hosting
  2. Subir el vector store a Azure Blob Storage y descargarlo al iniciar
  3. Usar ChromaDB Cloud (servicio pago)

---

### Opción A: Azure Container Apps (Recomendado)

**Ventajas:**
- ✅ Gratis hasta cierto uso
- ✅ Escala automáticamente
- ✅ Integración con Azure (ya usas Azure OpenAI)
- ✅ Buena gestión de variables de entorno

**Desventajas:**
- ⚠️ Requiere cuenta de Azure
- ⚠️ Persistencia requiere Azure Files

**Pasos:**

#### 1. Preparar el código

Asegúrate de que los Dockerfiles estén optimizados (ya lo están).

#### 2. Crear Azure Container Registry

```bash
# Instalar Azure CLI si no lo tienes
# brew install azure-cli (Mac)
# https://docs.microsoft.com/cli/azure/install-azure-cli

# Login
az login

# Crear resource group
az group create --name luisito-rg --location eastus

# Crear Container Registry
az acr create --resource-group luisito-rg --name luisitoacr --sku Basic

# Login al registry
az acr login --name luisitoacr
```

#### 3. Construir y subir imágenes

```bash
# Desde el directorio del proyecto
cd /Users/victorgallo/LuisitoComunica

# Construir y subir imagen del backend
az acr build --registry luisitoacr --image luisito-api:latest --file Dockerfile.api .

# Construir y subir imagen del frontend
cd chatbot-frontend
az acr build --registry luisitoacr --image luisito-frontend:latest --file Dockerfile .
cd ..

# Construir y subir imagen MCP
az acr build --registry luisitoacr --image luisito-mcp:latest --file Dockerfile.mcp .
```

#### 4. Crear Container App Environment

```bash
# Crear entorno
az containerapp env create \
  --name luisito-env \
  --resource-group luisito-rg \
  --location eastus
```

#### 5. Desplegar servicios

**Backend API:**

```bash
az containerapp create \
  --name luisito-api \
  --resource-group luisito-rg \
  --environment luisito-env \
  --image luisitoacr.azurecr.io/luisito-api:latest \
  --target-port 8000 \
  --ingress external \
  --registry-server luisitoacr.azurecr.io \
  --env-vars \
    AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
    AZURE_OPENAI_API_KEY="$AZURE_OPENAI_API_KEY" \
    AZURE_OPENAI_API_VERSION="$AZURE_OPENAI_API_VERSION" \
    AZURE_OPENAI_CHAT_DEPLOYMENT="$AZURE_OPENAI_CHAT_DEPLOYMENT" \
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT="$AZURE_OPENAI_EMBEDDING_DEPLOYMENT" \
  --cpu 1.0 --memory 2.0Gi \
  --min-replicas 1 --max-replicas 3
```

**Frontend:**

```bash
# Primero obtener la URL del backend
BACKEND_URL=$(az containerapp show --name luisito-api --resource-group luisito-rg --query properties.configuration.ingress.fqdn -o tsv)

az containerapp create \
  --name luisito-frontend \
  --resource-group luisito-rg \
  --environment luisito-env \
  --image luisitoacr.azurecr.io/luisito-frontend:latest \
  --target-port 3000 \
  --ingress external \
  --registry-server luisitoacr.azurecr.io \
  --env-vars \
    NEXT_PUBLIC_API_URL="https://${BACKEND_URL}" \
  --cpu 0.5 --memory 1.0Gi \
  --min-replicas 1 --max-replicas 2
```

**MCP Server (opcional si lo necesitas):**

```bash
az containerapp create \
  --name luisito-mcp \
  --resource-group luisito-rg \
  --environment luisito-env \
  --image luisitoacr.azurecr.io/luisito-mcp:latest \
  --target-port 8080 \
  --ingress internal \
  --registry-server luisitoacr.azurecr.io \
  --cpu 0.5 --memory 1.0Gi \
  --min-replicas 1 --max-replicas 1
```

#### 6. Persistencia del Vector Store

**Opción 1: Azure Files (Recomendado)**

```bash
# Crear storage account
az storage account create \
  --name luisitostorage \
  --resource-group luisito-rg \
  --location eastus \
  --sku Standard_LRS

# Crear file share
az storage share create \
  --name chromadb \
  --account-name luisitostorage \
  --connection-string "$(az storage account show-connection-string --name luisitostorage --resource-group luisito-rg -o tsv)"

# Montar en el container app (requiere actualizar la app)
# Esto es más complejo, mejor usar Opción 2
```

**Opción 2: Subir ChromaDB a Blob Storage y descargarlo al iniciar**

Modifica `api_server.py` para descargar el vector store de Azure si no existe localmente.

---

### Opción B: Railway

**Ventajas:**
- ✅ Muy fácil de usar
- ✅ Deploy con un click desde GitHub
- ✅ $5 de crédito gratis al mes
- ✅ Variables de entorno fáciles de configurar

**Pasos:**

1. **Sube tu código a GitHub** (si no lo has hecho)

2. **Ve a [Railway.app](https://railway.app)** y conecta tu GitHub

3. **Crea un nuevo proyecto** → "Deploy from GitHub repo"

4. **Selecciona tu repositorio**

5. **Configura el backend:**
   - **Root Directory**: Dejar vacío (o `/`)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
   - **Variables de entorno** (Settings → Variables):
     ```
     AZURE_OPENAI_ENDPOINT=tu_endpoint
     AZURE_OPENAI_API_KEY=tu_key
     AZURE_OPENAI_API_VERSION=2024-02-15-preview
     AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
     AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
     PORT=8000
     ```

6. **Configura el frontend:**
   - Crea otro servicio en el mismo proyecto
   - **Root Directory**: `chatbot-frontend`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`
   - **Variables de entorno**:
     ```
     NEXT_PUBLIC_API_URL=https://tu-backend-url.railway.app
     PORT=3000
     ```

7. **Para persistencia de ChromaDB:**
   - Usa Railway Volumes (en Settings → Volumes)
   - Monta un volumen en `/app/chroma_db`

---

### Opción C: Render

**Ventajas:**
- ✅ Plan gratuito disponible
- ✅ Muy fácil de configurar
- ✅ Auto-deploy desde GitHub

**Pasos:**

1. **Ve a [Render.com](https://render.com)** y conecta GitHub

2. **Crea un Web Service** para el backend:
   - **Environment**: Docker
   - **Build Command**: (dejar vacío, Render usa Dockerfile)
   - **Start Command**: (dejar vacío)
   - **Dockerfile Path**: `Dockerfile.api`
   - **Environment Variables**:
     ```
     AZURE_OPENAI_ENDPOINT=tu_endpoint
     AZURE_OPENAI_API_KEY=tu_key
     AZURE_OPENAI_API_VERSION=2024-02-15-preview
     AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
     AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
     ```

3. **Crea otro Web Service** para el frontend:
   - **Root Directory**: `chatbot-frontend`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`
   - **Environment Variables**:
     ```
     NEXT_PUBLIC_API_URL=https://tu-backend-url.onrender.com
     ```

4. **Persistencia:**
   - Render tiene "Disk" persistente (pero limitado en plan gratis)
   - O sube ChromaDB a Azure Blob Storage

---

### Opción D: DigitalOcean App Platform

**Ventajas:**
- ✅ Plan básico desde $5/mes
- ✅ Buena documentación
- ✅ Persistent Storage incluido

**Pasos:**

1. Ve a [DigitalOcean App Platform](https://www.digitalocean.com/products/app-platform)

2. Crea una nueva app desde GitHub

3. Configura servicios similares a Render

4. Usa "Persistent Storage" para `/app/chroma_db`

---

### Opción E: VPS Propio (Docker Compose)

**Ventajas:**
- ✅ Control total
- ✅ Más barato a largo plazo
- ✅ Sin límites del hosting

**Desventajas:**
- ❌ Requiere configuración manual
- ❌ Necesitas mantener el servidor

**Pasos:**

1. **Renta un VPS** (DigitalOcean, Linode, AWS EC2, etc.)
   - Recomendado: 2GB RAM mínimo
   - Ubuntu 22.04 LTS

2. **Conecta por SSH**

3. **Instala Docker y Docker Compose:**

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
```

4. **Clona tu repositorio:**

```bash
git clone tu-repo-url
cd LuisitoComunica
```

5. **Crea `.env` con tus variables**

6. **Inicia servicios:**

```bash
docker-compose up -d
```

7. **Configura Nginx como reverse proxy** (para HTTPS y dominio):

```nginx
# /etc/nginx/sites-available/luisito
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

8. **Instala Certbot para HTTPS:**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

9. **Configura systemd para auto-start:**

```bash
# Crear servicio
sudo nano /etc/systemd/system/luisito.service
```

```ini
[Unit]
Description=Luisito Comunica Chatbot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/usuario/LuisitoComunica
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=usuario

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable luisito
sudo systemctl start luisito
```

---

## 3. Configuración para Producción

### Mejoras Necesarias en los Dockerfiles

**Dockerfile.api (ya está bien, pero quita `--reload` en producción):**

```dockerfile
# Cambiar la última línea:
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
# (sin --reload)
```

**Dockerfile Frontend (producción):**

Necesita construir la app antes de servirla:

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM node:20-alpine

WORKDIR /app

COPY --from=builder /app/package*.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 3000

CMD ["npm", "start"]
```

### Variables de Entorno Críticas

**Backend:**
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_CHAT_DEPLOYMENT`
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`

**Frontend:**
- `NEXT_PUBLIC_API_URL` (debe ser la URL pública del backend)

### CORS en Producción

Actualiza `api_server.py` para permitir solo tu dominio:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-dominio.com"],  # Solo tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 4. Persistencia de Datos

### ChromaDB Vector Store

**Problema:** En contenedores, el vector store se pierde al reiniciar.

**Soluciones:**

#### Opción 1: Volúmenes Persistentes (Recomendado)

- Azure Container Apps: Azure Files
- Railway: Railway Volumes
- Render: Persistent Disk
- VPS: Volúmenes de Docker

#### Opción 2: Subir a Azure Blob Storage

Modifica `api_server.py` para:

1. Al iniciar, verificar si existe `chroma_db/` local
2. Si no existe, descargar desde Azure Blob Storage
3. Si existe pero es viejo, sincronizar

#### Opción 3: ChromaDB Cloud

Usa ChromaDB Cloud (servicio pago) en lugar de local.

---

## 5. Monitoreo y Logs

### Health Checks

Tu API ya tiene `/health` endpoint. Configura health checks en tu hosting:

- **Railway**: Auto-configurado
- **Render**: Agrega health check path `/health`
- **Azure**: Configura health probe

### Logs

```bash
# Docker Compose
docker-compose logs -f api

# Azure Container Apps
az containerapp logs show --name luisito-api --resource-group luisito-rg --follow

# Railway/Render: Ver en el dashboard
```

### Monitoreo Recomendado

- **Uptime Robot** (gratis): Verifica que el servicio esté online
- **Sentry** (gratis hasta cierto punto): Captura errores
- **Azure Monitor**: Si usas Azure

---

## 6. Troubleshooting

### El backend se cae frecuentemente

**Causa:** Falta de memoria o CPU

**Solución:** 
- Aumenta recursos en tu hosting
- Verifica logs para ver errores específicos

### ChromaDB no persiste

**Causa:** Volumen no montado correctamente

**Solución:**
- Verifica que el volumen esté montado en `/app/chroma_db`
- Usa Azure Blob Storage como respaldo

### CORS errors en producción

**Causa:** Frontend y backend en diferentes dominios sin CORS configurado

**Solución:**
- Actualiza `allow_origins` en `api_server.py` con tu dominio real

### El frontend no encuentra el backend

**Causa:** `NEXT_PUBLIC_API_URL` mal configurado

**Solución:**
- Verifica que la variable tenga la URL completa: `https://tu-backend-url.com`
- **Importante:** Next.js necesita rebuild si cambias `NEXT_PUBLIC_*` variables

---

## 📊 Comparación de Opciones

| Opción | Precio | Facilidad | Escalabilidad | Persistencia |
|--------|--------|-----------|----------------|--------------|
| **Azure Container Apps** | ~$20/mes | Media | ⭐⭐⭐⭐⭐ | Azure Files |
| **Railway** | $5-20/mes | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Volúmenes |
| **Render** | $0-25/mes | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Disco limitado |
| **DigitalOcean** | $5-12/mes | ⭐⭐⭐⭐ | ⭐⭐⭐ | Incluido |
| **VPS Propio** | $5-10/mes | ⭐⭐ | ⭐⭐⭐ | Control total |

---

## ✅ Checklist de Deploy

Antes de hacer deploy:

- [ ] Variables de entorno configuradas
- [ ] Dockerfiles optimizados para producción
- [ ] ChromaDB subido a storage persistente
- [ ] CORS configurado correctamente
- [ ] `NEXT_PUBLIC_API_URL` apunta al backend real
- [ ] Health checks configurados
- [ ] Dominio/configuración de DNS (si aplica)
- [ ] HTTPS configurado (SSL/TLS)
- [ ] Monitoreo básico configurado

---

## 🎉 ¡Listo!

Después de seguir esta guía, tu backend estará corriendo **24/7** y accesible desde internet.

**Próximos pasos:**
1. Configura un dominio personalizado
2. Agrega monitoreo avanzado
3. Configura backups del vector store
4. Optimiza recursos según uso

---

**¿Necesitas ayuda?** Revisa los logs y la documentación de tu proveedor de hosting.

