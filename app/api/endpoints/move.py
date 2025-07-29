from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import shutil
from app.db.mongodb import mongodb
from datetime import datetime

router = APIRouter()

class MoveRequest(BaseModel):
    filename: str
    source_folder: str
    target_folder: str

@router.post("/move")
async def move_file(req: MoveRequest):
    collection = mongodb.db["documents"]
    base_path = Path("./Documentos")
    
    source_path = base_path / req.source_folder / req.filename
    target_dir = base_path / req.target_folder
    target_path = target_dir / req.filename

    if not source_path.exists():
        raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {source_path}")
    
    try:
        # Crear carpeta destino si no existe
        target_dir.mkdir(parents=True, exist_ok=True)

        # Mover archivo
        shutil.move(str(source_path), str(target_path))

        # Buscar documento por nombre exacto
        doc = await collection.find_one({"filename": req.filename})
        if not doc:
            raise HTTPException(status_code=404, detail=f"No se encontró ningún documento con filename exacto: '{req.filename}'")

        # Categoría anterior y nueva
        current_category = doc.get("categories", ["Desconocida"])[0]
        new_category = req.target_folder

        # Obtener nueva ruta relativa desde /Documentos
        relative_filepath = str(target_path.relative_to(base_path.parent))

        # Actualizar documento
        await collection.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "filepath": relative_filepath,
                    "categories": [new_category]
                }
            }
        )

        return {
            "message": "Archivo movido y documento actualizado correctamente.",
            "new_filepath": relative_filepath,
            "advertencia": f"Estás moviendo el documento desde la categoría '{current_category}' (asignada por el modelo) a '{new_category}', lo cual podría romper la coherencia de la clasificación automática."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al mover o actualizar: {e}")
