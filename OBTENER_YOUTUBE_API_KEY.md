# 🔑 Cómo Obtener YouTube API Key

## 📝 Instrucciones Paso a Paso

### Paso 1: Ir a Google Cloud Console

1. Ve a: **https://console.cloud.google.com/**
2. Inicia sesión con tu cuenta de Google

### Paso 2: Crear o Seleccionar Proyecto

1. En la parte superior, haz clic en el selector de proyectos
2. Haz clic en "**NUEVO PROYECTO**"
3. Nombra tu proyecto (ej: "Luisito Comunica Bot")
4. Haz clic en "**CREAR**"
5. Espera a que se cree el proyecto (puede tomar unos segundos)

### Paso 3: Habilitar YouTube Data API v3

1. En el menú lateral izquierdo, ve a **"APIs y Servicios"** → **"Biblioteca"**
2. En el buscador, escribe: **"YouTube Data API v3"**
3. Selecciona **"YouTube Data API v3"**
4. Haz clic en **"HABILITAR"**

### Paso 4: Crear Credenciales (API Key)

1. Ve a **"APIs y Servicios"** → **"Credenciales"**
2. En la parte superior, haz clic en **"CREAR CREDENCIALES"**
3. Selecciona **"Clave de API"**
4. Se creará una clave API automáticamente
5. **¡COPIA LA CLAVE INMEDIATAMENTE!** No podrás verla después

### Paso 5: Configurar Restricciones (Opcional pero Recomendado)

1. Haz clic en tu API Key para editarla
2. En "Restricciones de API":
   - Selecciona **"Restringir clave"**
   - Elige **"YouTube Data API v3"**
3. En "Restricciones de aplicación":
   - Puedes dejarlo sin restricciones o agregar IPs específicas
4. Haz clic en **"GUARDAR"**

### Paso 6: Agregar al Proyecto

Agrega la API Key a tu archivo `.env`:

```bash
# Editar .env
nano .env
```

Agrega esta línea:
```env
YOUTUBE_API_KEY=TU_API_KEY_AQUI
```

---

## ⚡ Método Rápido: Solo la API Key

Si solo necesitas la API Key y ya tienes un proyecto de Google Cloud:

1. Ve a: **https://console.cloud.google.com/apis/credentials**
2. Haz clic en **"CREAR CREDENCIALES"** → **"Clave de API"**
3. Copia la clave
4. Agrega a `.env`:
```bash
echo "YOUTUBE_API_KEY=TU_CLAVE_AQUI" >> .env
```

---

## 🆓 Límites de Cuota

YouTube Data API v3 tiene límites **Gratuitos**:
- **10,000 unidades por día** (renovables)
- Cada `search.list` usa **100 unidades**
- Cada `video.list` usa **1 unidad**
- Cada `channels.list` usa **1 unidad**

**Para un canal con 1000 videos:**
- Obtener lista de videos: ~100 unidades
- Transcribir videos: No usa cuota (usa youtube-transcript-api)

**Conclusión**: La cuota gratis es más que suficiente para este proyecto.

---

## ✅ Verificar que Funciona

```bash
# Cargar la API key
source .env

# Probar que funciona
python get_video_list_example.py
```

---

## 🚨 Troubleshooting

### "API key not valid"
- Verifica que copiaste bien la clave
- Asegúrate de haber habilitado YouTube Data API v3
- Revisa las restricciones de la clave

### "Quota exceeded"
- Has alcanzado el límite diario
- Espera 24 horas o solicita mayor cuota en Google Cloud Console

### "Access not configured"
- No habilitaste YouTube Data API v3
- Ve a "APIs y Servicios" → "Biblioteca" y habilítala

---

## 🎯 Próximo Paso

Una vez que tengas la API Key:
```bash
python get_video_list_example.py
```

Esto descargará todos los videos de Luisito Comunica y los guardará en `data/video_list.json`.

