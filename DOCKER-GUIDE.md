# 🐳 DocumentSort - Guía de Docker

## ✅ ¡La aplicación está funcionando!

Tu proyecto DocumentSort ahora está completamente contenerizado y corriendo.

## 📦 Archivos creados

1. **Dockerfile** - Definición de la imagen de la aplicación
2. **docker-compose.yml** - Orquestación de servicios (App + MongoDB)
3. **start-docker.sh** - Script para iniciar todo
4. **stop-docker.sh** - Script para detener todo
5. **.env.example** - Plantilla de variables de entorno
6. **.env.docker** - Variables para Docker (opcional)
7. **.dockerignore** - Archivos excluidos del contenedor

## 🚀 Comandos principales

### Iniciar la aplicación

```bash
./start-docker.sh
```

### Detener la aplicación

```bash
./stop-docker.sh
```

### Ver logs en tiempo real

```bash
docker-compose logs -f
```

### Ver solo logs de la app

```bash
docker-compose logs -f app
```

### Ver solo logs de MongoDB

```bash
docker-compose logs -f mongodb
```

### Reiniciar después de cambios en el código

```bash
docker-compose build
docker-compose up -d
```

### Detener y eliminar todo (incluye volúmenes/datos)

```bash
docker-compose down -v
```

## 🌐 URLs de acceso

- **API:** http://localhost:8000
- **Documentación interactiva (Swagger):** http://localhost:8000/docs
- **MongoDB:** mongodb://localhost:27017

## 📝 Cambios realizados en el código

Se modificaron los siguientes archivos para soportar variables de entorno de Docker:

1. **app/db/mongodb.py** - Ahora lee `MONGO_URI` y `DB_NAME` de variables de entorno
2. **app/services/file_handler.py** - Ahora lee `DOCUMENT_ROOT` de variables de entorno
3. **app/core/jwt.py** - Ahora lee `SECRET_KEY`, `ALGORITHM` y `ACCESS_TOKEN_EXPIRE_MINUTES` de variables de entorno

Estos cambios son compatibles con ejecución local (usando archivo .env) y con Docker (usando variables de entorno del sistema).

## 🔧 Configuración

Las variables de entorno se configuran automáticamente en `docker-compose.yml`:

```yaml
environment:
  - MONGO_URI=mongodb://mongodb:27017
  - DB_NAME=document_classifier
  - DOCUMENT_ROOT=/app/Documentos
  - SECRET_KEY=tu_clave_secreta_super_segura_cambiala
  - ALGORITHM=HS256
  - ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 💾 Persistencia de datos

Los siguientes directorios se montan como volúmenes para persistir datos:

- `./Documentos` → `/app/Documentos` (documentos clasificados)
- `./models` → `/app/models` (modelos ML entrenados)
- `./graphics` → `/app/graphics` (gráficas generadas)
- `./temp` → `/app/temp` (archivos temporales)
- `mongodb_data` → `/data/db` (base de datos MongoDB)

## 🎉 ¡Listo para usar!

Tu aplicación está completamente funcional y lista para clasificar documentos.

Puedes:

1. Acceder a http://localhost:8000/docs
2. Subir documentos usando la interfaz Swagger
3. Ver los documentos clasificados automáticamente
4. Entrenar el modelo con ejemplos personalizados

## 🐛 Solución de problemas

### Puerto 8000 ya está en uso

```bash
# Ver qué proceso usa el puerto
sudo lsof -i :8000

# Detener contenedores que usen el puerto
docker ps -a | grep 8000
docker stop <container_id>
```

### Contenedor no inicia

```bash
# Ver logs detallados
docker-compose logs app

# Reconstruir desde cero
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### MongoDB no conecta

```bash
# Verificar que MongoDB esté corriendo
docker-compose ps

# Ver logs de MongoDB
docker-compose logs mongodb

# Reiniciar solo MongoDB
docker-compose restart mongodb
```

## 📚 Recursos adicionales

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MongoDB Docker Image](https://hub.docker.com/_/mongo)
