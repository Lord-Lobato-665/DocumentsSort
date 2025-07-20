from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import os

router = APIRouter()

@router.get("/text/graph", response_class=StreamingResponse)
def get_text_cluster_graph():
    path = "graphics/text/clusters.png"
    if not os.path.exists(path):
        return {"error": "La gráfica aún no ha sido generada. Ejecuta el entrenamiento primero."}
    
    file = open(path, "rb")
    return StreamingResponse(file, media_type="image/png")

