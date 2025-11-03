# 🐳 Instrucciones: Docker + MCP

## ✅ Estado Actual

**¡MCP funcionando con Docker!** 🎉

```
✅ Docker instalado y funcionando
✅ MCP Server personalizado creado
✅ Docker Compose configurado
✅ Imagen construida exitosamente
✅ Servidor corriendo en http://localhost:8080
✅ Health check funcionando
```

---

## 🚀 Cómo Usar

### Iniciar MCP

```bash
docker-compose up -d mcp-youtube-transcript
```

### Verificar que esté funcionando

```bash
# Ver logs
docker-compose logs -f mcp-youtube-transcript

# Verificar health
curl http://localhost:8080/health

# Ver información del servicio
curl http://localhost:8080/
```

### Detener MCP

```bash
docker-compose down mcp-youtube-transcript
```

---

## 📋 Transcribir Videos

### Opción A: Con Docker Compose (Recomendado)

```bash
# 1. Asegúrate que MCP está corriendo
docker-compose up -d mcp-youtube-transcript

# 2. Construir transcriber si es necesario
docker-compose build transcriber

# 3. Transcribir videos
docker-compose --profile transcriber up transcriber
```

### Opción B: Directamente (Más Rápido)

```bash
# 1. Asegúrate que MCP está corriendo
docker-compose up -d mcp-youtube-transcript

# 2. Configurar MCP_URL apuntando a localhost
export MCP_URL=http://localhost:8080

# 3. Transcribir
python transcribe_mcp.py
```

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────┐
│  docker-compose up                      │
└─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
   ┌────▼─────┐          ┌──────▼────────┐
   │ MCP      │◄─────────┤ Transcriber   │
   │ Server   │  HTTP    │ Service       │
   │ :8080    │          │ (profile)     │
   └──────────┘          └───────────────┘
        │
        └──────────► YouTube Transcript API
```

**Flujo:**
1. MCP Server escucha en puerto 8080
2. Transcriber se conecta a MCP via HTTP
3. MCP usa `youtube-transcript-api` para obtener transcripciones
4. Transcriber guarda resultados en Azure Blob Storage

---

## 🔧 Archivos MCP

- **`mcp_server.py`**: Servidor HTTP simple que expone API de transcripción
- **`Dockerfile.mcp`**: Dockerfile para construir imagen del servidor MCP
- **`docker-compose.yml`**: Configuración actualizada para usar nuestro MCP

---

## 🧪 Probar MCP Manualmente

```bash
# Transcribir un video directamente
curl -X POST http://localhost:8080/api/transcript \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

---

## ⚠️ Notas Importantes

### Rate Limiting de YouTube

Si encuentras errores "Too Many Requests":
- YouTube limita las solicitudes de transcripciones
- Espera unos minutos entre transcripciones
- Usa videos que definitivamente tienen captions

### MCP vs Directo

- **Con MCP**: Usa contenedor Docker, más escalable
- **Directo**: Usa Python directamente, más rápido para desarrollo

### Hostname

Desde dentro de Docker:
```
MCP_URL=http://mcp-youtube-transcript:8080
```

Desde fuera de Docker:
```
MCP_URL=http://localhost:8080
```

---

## 🎉 ¡Todo Listo!

Ahora tienes:
- ✅ MCP Server personalizado funcionando
- ✅ Docker Compose configurado
- ✅ Opción de transcripción con y sin Docker
- ✅ Sistema completamente funcional

**Próximo paso**: Agrega más videos a `data/video_list.json` y transcríbelos!

