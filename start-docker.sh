#!/bin/bash

echo "🐳 Iniciando DocumentSort con Docker Compose..."
echo ""

# Verifica si Docker está corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker no está corriendo"
    echo "Por favor, inicia Docker Desktop e intenta de nuevo"
    exit 1
fi

# Verifica si docker-compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose no está instalado"
    echo "Instalalo con: sudo apt install docker-compose"
    exit 1
fi

echo "📦 Construyendo contenedores..."
docker-compose build

if [ $? -ne 0 ]; then
    echo "❌ Error al construir los contenedores"
    exit 1
fi

echo ""
echo "🚀 Levantando servicios..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Error al iniciar los servicios"
    exit 1
fi

echo ""
echo "⏳ Esperando que los servicios estén listos..."
sleep 5

echo ""
echo "✅ Aplicación iniciada correctamente!"
echo ""
echo "📊 Servicios disponibles:"
echo "   - API: http://localhost:8000"
echo "   - Documentación: http://localhost:8000/docs"
echo "   - MongoDB: mongodb://localhost:27017"
echo ""
echo "📝 Ver logs en tiempo real:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Detener los servicios:"
echo "   docker-compose down"
echo ""
echo "🗑️  Detener y eliminar volúmenes:"
echo "   docker-compose down -v"
echo ""
