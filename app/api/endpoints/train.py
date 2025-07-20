from fastapi import APIRouter
from app.core.ml import train_model, cluster_documents

router = APIRouter()

@router.post("/")
async def train_and_classify():
    result = await train_model()
    clusters = await cluster_documents()
    return {"message": "Modelo entrenado y documentos agrupados", "clusters": clusters}
