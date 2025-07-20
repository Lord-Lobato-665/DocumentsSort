# app/api/endpoints/upload.py

import os
from fastapi import APIRouter, UploadFile, File, Form
from app.db.mongodb import get_collection
from app.utils.file_utils import process_file
from app.ml.model import train_and_save_model, predict_category
from datetime import datetime
import uuid
from uuid import uuid4
from app.core.ml import train_model
from fastapi.responses import FileResponse
import zipfile
from fastapi import HTTPException
from fastapi import Query

router = APIRouter()

# Asegúrate que en tu run.py o main.py haces load_dotenv()
DOCUMENT_ROOT = os.getenv("DOCUMENT_ROOT", "./storage")  # Ruta base para guardar documentos

@router.post("/")
async def upload_document(file: UploadFile = File(...)):
    contents = await file.read()
    processed_text = process_file(contents, file.filename)

    # Predicción de categoría
    predicted_category = predict_category(processed_text)

    # Construir ruta de carpeta y crearla si no existe
    folder_path = os.path.join(DOCUMENT_ROOT, predicted_category)
    os.makedirs(folder_path, exist_ok=True)

    # Ruta completa del archivo
    file_path = os.path.join(folder_path, file.filename)

    # Guardar el archivo físico
    with open(file_path, "wb") as f:
        f.write(contents)

    # Preparar documento para guardar en MongoDB
    doc = {
        "filename": file.filename,
        "content": processed_text,
        "created_at": datetime.utcnow(),
        "uuid": str(uuid.uuid4()),
        "categories": [predicted_category],
        "filepath": file_path  # Guarda la ruta para referencia
    }

    # Insertar en la colección
    documents_collection = await get_collection("documents")
    await documents_collection.insert_one(doc)

    # Entrenar el modelo con los documentos actuales
    all_docs = await documents_collection.find({}).to_list(None)
    filtered_docs = [d for d in all_docs if "content" in d and "categories" in d and d["categories"]]

    texts = [d["content"] for d in filtered_docs]
    labels = [d["categories"][0] for d in filtered_docs]

    if texts and labels:
        train_and_save_model(texts, labels)

    return {
        "message": f"{file.filename} subido y modelo actualizado con categoría '{predicted_category}'",
        "saved_path": file_path
    }

@router.get("/by-category/{category}")
async def get_documents_by_category(category: str, limit: int = 100):
    """
    Retorna los documentos filtrados por categoría, sin incluir el texto procesado.
    """
    collection = await get_collection("documents")
    
    docs = await collection.find(
        {"categories": category},
        {
            "content": 0  # Excluye el texto completo
        }
    ).limit(limit).to_list(length=None)

    # Transformar ObjectId a string para compatibilidad
    for doc in docs:
        doc["id"] = str(doc["_id"])
        del doc["_id"]

    return {"category": category, "total": len(docs), "documents": docs}

# DESCARGAS DE ARCHIVOS

@router.get("/download/file/")
async def download_file_by_name(
    filename: str = Query(..., description="Nombre del archivo con extensión"),
    category: str = Query(..., description="Categoría donde está el archivo")
):
    # Construimos la ruta del archivo esperando que esté dentro de la carpeta de la categoría
    file_path = os.path.join("./Documentos", category, filename)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado en la categoría especificada")

    return FileResponse(file_path, media_type="application/octet-stream", filename=filename)

@router.get("/download/zip/{category}")
async def download_category_zip(category: str):
    folder_path = os.path.join("./Documentos", category)
    if not os.path.isdir(folder_path):
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    zip_path = f"./temp/{category}.zip"
    os.makedirs("./temp", exist_ok=True)
    
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, folder_path)
                zipf.write(full_path, arcname=arcname)

    return FileResponse(zip_path, media_type="application/zip", filename=f"{category}.zip")

@router.get("/download/all")
async def download_all_documents():
    folder_path = "./Documentos"
    if not os.path.isdir(folder_path):
        raise HTTPException(status_code=404, detail="Carpeta de documentos no encontrada")

    zip_path = "./temp/Documentos_completo.zip"
    os.makedirs("./temp", exist_ok=True)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, folder_path)
                zipf.write(full_path, arcname=arcname)

    return FileResponse(zip_path, media_type="application/zip", filename="Documentos_completo.zip")
