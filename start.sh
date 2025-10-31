#!/bin/bash

# Script para construir y levantar la aplicación Document Classifier en Docker

set -e

echo "🐳 Document Classifier - Docker Setup"
echo "======================================"

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Nombre de la imagen y contenedor
IMAGE_NAME="document-classifier"
CONTAINER_NAME="document-classifier-app"
PORT=8000

# Verificar si existe el archivo .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No se encontró el archivo .env${NC}"
    echo "Creando .env desde .env.example..."
    
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ Archivo .env creado. Por favor, edita las variables según tu configuración.${NC}"
        echo -e "${YELLOW}⚠️  IMPORTANTE: Configura MONGO_URI con tu conexión a MongoDB${NC}"
        read -p "Presiona Enter para continuar después de configurar el .env..."
    else
        echo -e "${RED}❌ No se encontró .env.example${NC}"
        exit 1
    fi
fi

# Detener y eliminar contenedor existente si está corriendo
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo -e "${YELLOW}🛑 Deteniendo contenedor existente...${NC}"
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
fi

# Construir la imagen Docker
echo -e "${GREEN}🔨 Construyendo la imagen Docker...${NC}"
docker build -t $IMAGE_NAME .

# Verificar si la construcción fue exitosa
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Imagen construida exitosamente${NC}"
else
    echo -e "${RED}❌ Error al construir la imagen${NC}"
    exit 1
fi

# Crear volúmenes para persistencia de datos
echo -e "${GREEN}📦 Creando volúmenes...${NC}"
docker volume create document-classifier-models 2>/dev/null || true
docker volume create document-classifier-documents 2>/dev/null || true

# Levantar el contenedor
echo -e "${GREEN}🚀 Levantando el contenedor...${NC}"
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:8000 \
    --env-file .env \
    -v document-classifier-models:/app/models \
    -v document-classifier-documents:/app/Documentos \
    -v "$(pwd)/temp:/app/temp" \
    --restart unless-stopped \
    $IMAGE_NAME

# Verificar si el contenedor está corriendo
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo -e "${GREEN}✅ Contenedor levantado exitosamente${NC}"
    echo ""
    echo "======================================"
    echo -e "${GREEN}🎉 Aplicación corriendo en:${NC}"
    echo -e "   📍 http://localhost:$PORT"
    echo -e "   📚 API Docs: http://localhost:$PORT/docs"
    echo ""
    echo -e "${YELLOW}Comandos útiles:${NC}"
    echo "   Ver logs:       docker logs -f $CONTAINER_NAME"
    echo "   Detener:        docker stop $CONTAINER_NAME"
    echo "   Reiniciar:      docker restart $CONTAINER_NAME"
    echo "   Eliminar:       docker rm -f $CONTAINER_NAME"
    echo "======================================"
else
    echo -e "${RED}❌ Error al levantar el contenedor${NC}"
    docker logs $CONTAINER_NAME
    exit 1
fi
