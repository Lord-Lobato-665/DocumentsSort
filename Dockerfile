# syntax=docker/dockerfile:1

# Imagen base con Python 3.11
FROM python:3.11-slim AS base

# Variables de entorno para un runtime predecible
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    MPLBACKEND=Agg

# Instala dependencias del sistema mínimas (algunas wheels pueden requerir compilación)
# Nota: Si las wheels muchaslinux están disponibles, esto no compilará casi nada, pero
# mantenemos herramientas de compilación por si lxml/pillow/matplotlib requieren headers.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    gcc g++ make \
    libxml2-dev libxslt1-dev \
    libjpeg-dev zlib1g-dev \
    libfreetype6-dev libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copiamos solo requirements primero para aprovechar cache de Docker
COPY requirements.txt ./

# Instala dependencias de Python
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copia el código del proyecto
COPY . .

# Crea un usuario no-root para ejecutar la app
RUN useradd -ms /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expone el puerto del servicio
EXPOSE 8000

# Comando por defecto: ejecutar el servidor FastAPI con uvicorn
# Importante: usamos host 0.0.0.0 para que sea accesible desde fuera del contenedor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
