from fastapi import APIRouter
from app.schemas.predict import PredictRequest
from app.ml.model import predict_category

router = APIRouter()

# Recibir modelos desde main
model = None
vectorizer = None

from app.ml.model import load_model, predict_category

model, vectorizer = load_model()  # cargar solo una vez, preferiblemente global o en startup

@router.post("/")
async def predict_endpoint(request: PredictRequest):
    prediction = predict_category(model, vectorizer, request.document_text)
    return {"prediction": prediction}
