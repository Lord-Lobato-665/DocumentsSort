# Usa una imagen base de Python 3.11
FROM python:3.11-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo de dependencias
COPY requirements.txt .

# Instala las dependencias del sistema necesarias para PyMuPDF y otros paquetes
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código de la aplicación
COPY . .

# Crea los directorios necesarios para la aplicación
RUN mkdir -p models temp graphics/text Documentos

# Expone el puerto 8000 para la API
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
