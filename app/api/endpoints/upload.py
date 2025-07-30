# app/api/endpoints/upload.py

import os
from fastapi import APIRouter, UploadFile, File, Form
from app.db.mongodb import get_collection
from app.utils.file_utils import process_file
from app.ml.model import train_model_from_db, predict_category
from datetime import datetime
import uuid
from uuid import uuid4
from app.core.ml import train_model
from fastapi.responses import FileResponse
import zipfile
from fastapi import HTTPException
from fastapi import Query
from fastapi import APIRouter, HTTPException
from app.db.mongodb import mongodb
from app.models.document import Document
from typing import List
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.db.mongodb import get_collection
from zoneinfo import ZoneInfo


router = APIRouter()

CANCUN_TZ = ZoneInfo("America/Cancun")
DOCUMENT_ROOT = os.getenv("DOCUMENT_ROOT", "./storage")  # Ruta base para guardar documentos

@router.post("/")
async def upload_document(
    file: UploadFile = File(...),
    username: str = Query(..., description="Usuario que sube el archivo")
):
    contents = await file.read()
    processed_text = process_file(contents, file.filename)

    predicted_category = predict_category(processed_text)
    folder_path = os.path.join(DOCUMENT_ROOT, predicted_category)
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, file.filename)
    with open(file_path, "wb") as f:
        f.write(contents)

    doc = {
        "filename": file.filename,
        "content": processed_text,
        "created_at": datetime.now(CANCUN_TZ).isoformat(),
        "uuid": str(uuid4()),
        "categories": [predicted_category],
        "filepath": file_path
    }

    documents_collection = await get_collection("documents")
    result = await documents_collection.insert_one(doc)

    audit_collection = await get_collection("audit_logs")
    audit_entry = {
        "timestamp": datetime.now(CANCUN_TZ).isoformat(),
        "username": username,
        "operation": "Subida de documento",
        "document_id": str(result.inserted_id),
        "document_filename": file.filename,
        "category": predicted_category,
        "filepath": file_path
    }
    await audit_collection.insert_one(audit_entry)

    await train_model_from_db()  # Reentrenar modelo

    return {
        "message": f"{file.filename} subido y modelo actualizado con categoría '{predicted_category}'",
        "saved_path": file_path
    }

@router.get("/documents", response_model=List[Document])
async def get_all_documents():
    try:
        documents = await mongodb.db.documents.find().to_list(length=None)
        for doc in documents:
            doc["_id"] = str(doc["_id"])  # convertir ObjectId a str
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los documentos: {str(e)}")

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

@router.delete("/documents/{doc_id}", status_code=204)
async def delete_document(doc_id: str, username: str = Query(..., description="Usuario que elimina el archivo")):
    if not ObjectId.is_valid(doc_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    try:
        collection = await get_collection("documents")
        document = await collection.find_one({"_id": ObjectId(doc_id)})
        if not document:
            raise HTTPException(status_code=404, detail="Documento no encontrado")

        filepath = document.get("filepath")
        if filepath:
            relative_path = filepath.replace("\\", os.sep).replace("/", os.sep)
            if os.path.exists(relative_path):
                os.remove(relative_path)
            else:
                raise HTTPException(status_code=404, detail=f"Archivo físico no encontrado en: {relative_path}")

        result = await collection.delete_one({"_id": ObjectId(doc_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="No se pudo eliminar de la base de datos")

        audit_collection = await get_collection("audit_logs")
        audit_entry = {
            "timestamp": datetime.now(CANCUN_TZ).isoformat(),
            "username": username,
            "operation": "Eliminación de documento",
            "document_id": doc_id,
            "document_filename": document.get("filename"),
            "category": document.get("categories", ["Desconocida"])[0],
            "filepath": filepath
        }
        await audit_collection.insert_one(audit_entry)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno al eliminar documento: {str(e)}")

    return  # 204 No Content

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
