# app/api/endpoints
from fastapi import APIRouter, HTTPException
from app.schemas.training_example import TrainingExample
from app.db.mongodb import get_collection
from app.ml.model import train_model_from_db
from typing import List

router = APIRouter()

@router.post("/training-new-example", status_code=201)
async def add_training_example(example: TrainingExample):
    collection = await get_collection("training_examples")
    result = await collection.insert_one(example.dict())
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="No se pudo insertar el ejemplo")
    return {"message": "Ejemplo agregado correctamente", "id": str(result.inserted_id)}

@router.post("/train-model")
async def train_model():
    try:
        result = await train_model_from_db()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante el entrenamiento: {str(e)}")
    
@router.get("/categories", response_model=List[str])
async def get_categories():
    collection = await get_collection("training_examples")
    categories = await collection.distinct("category")
    if not categories:
        raise HTTPException(status_code=404, detail="No categories found")
    return categories

@router.get("/texts/{category}", response_model=List[str])
async def get_texts_by_category(category: str):
    collection = await get_collection("training_examples")
    cursor = collection.find({"category": category}, {"_id": 0, "text": 1})
    texts = [doc["text"] async for doc in cursor]
    if not texts:
        raise HTTPException(status_code=404, detail=f"No texts found for category '{category}'")
    return texts