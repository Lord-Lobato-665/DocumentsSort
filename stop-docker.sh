#!/bin/bash

echo "🛑 Deteniendo DocumentSort..."
echo ""

# Detener los contenedores
docker-compose down

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Servicios detenidos correctamente"
    echo ""
    echo "💡 Opciones adicionales:"
    echo "   - Eliminar también los volúmenes (datos): docker-compose down -v"
    echo "   - Ver estado de contenedores: docker-compose ps"
else
    echo ""
    echo "❌ Error al detener los servicios"
    exit 1
fi
