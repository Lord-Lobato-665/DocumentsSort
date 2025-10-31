# Document Classifier API

Sistema de clasificación automática de documentos usando FastAPI, MongoDB y Machine Learning.

## 🚀 Inicio Rápido con Docker (Recomendado)

### Requisitos previos

- Docker y Docker Compose instalados
- Nada más! MongoDB se incluye en el setup

### Iniciar la aplicación

```bash
./start-docker.sh
```

El script automáticamente:

- Construye las imágenes Docker
- Levanta MongoDB en un contenedor
- Levanta la aplicación FastAPI
- Configura la red entre contenedores

### Acceder a la aplicación

- **API:** http://localhost:8000
- **Documentación Swagger:** http://localhost:8000/docs
- **MongoDB:** localhost:27017

### Comandos útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver solo logs de la aplicación
docker-compose logs -f app

# Detener servicios
./stop-docker.sh
# o manualmente:
docker-compose down

# Reiniciar servicios
docker-compose restart

# Reconstruir después de cambios en el código
docker-compose build
docker-compose up -d
```

---

## 🐍 Ejecución Local (Sin Docker)

### 1. Activar el entorno virtual

**Windows:**

```bash
.\.venv\Scripts\activate
```

**Linux/Mac:**

```bash
source .venv/bin/activate
```

### 2. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
MONGO_URI=mongodb://localhost:27017
DB_NAME=document_classifier
DOCUMENT_ROOT=./Documentos
SECRET_KEY=tu_clave_secreta_super_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Entrenar el modelo (opcional, primera vez)

```bash
python train_manual.py
```

### 5. Ejecutar la aplicación

```bash
python run.py
```

---

## 📂 Categorías Soportadas

- Actas y Acuerdos
- Contratos y Convenios
- Oficios y Comunicaciones Oficiales
- Expedientes Técnicos y Proyectos
- Informes y Reportes
- Documentación Financiera y Presupuestaria

---

## 🏗️ Estructura del Proyecto

```
DocumentsSort/
├── app/                      # Código principal de la aplicación
│   ├── api/endpoints/       # Endpoints de la API
│   ├── core/                # Configuración y utilidades core
│   ├── ml/                  # Modelos de Machine Learning
│   ├── models/              # Modelos de datos
│   └── services/            # Servicios de negocio
├── models/                  # Modelos entrenados (.pkl)
├── Documentos/              # Almacenamiento de documentos
├── temp/                    # Archivos temporales
├── Dockerfile               # Configuración Docker
├── docker-compose.yml       # Orquestación de servicios
├── start-docker.sh          # Script de inicio
├── stop-docker.sh           # Script de detención
└── requirements.txt         # Dependencias Python
```

---

## 🔧 Tecnologías

- **FastAPI**: Framework web moderno y rápido
- **MongoDB**: Base de datos NoSQL
- **Scikit-learn**: Machine Learning
- **PyMuPDF**: Procesamiento de PDFs
- **python-docx**: Procesamiento de documentos Word
- **Docker**: Contenedorización

---

## 📝 Notas

- Los modelos ML se entrenan automáticamente al subir documentos
- Los documentos se clasifican automáticamente al subirlos
- La aplicación soporta archivos PDF, DOCX y TXT
- Los volúmenes de Docker persisten los datos entre reinicios
