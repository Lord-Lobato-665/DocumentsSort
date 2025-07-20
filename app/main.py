from fastapi import FastAPI
from app.api.endpoints import upload, train, predict, graphics
from app.ml.model import load_model
import os

app = FastAPI(title="Document Classifier API Avanzado")

model = None
vectorizer = None

@app.on_event("startup")
async def startup_event():
    global model, vectorizer
    model_path = "models/model.pkl"
    vectorizer_path = "models/vectorizer.pkl"
    
    if os.path.exists(model_path) and os.path.exists(vectorizer_path):
        model, vectorizer = load_model(model_path, vectorizer_path)
        predict.model = model
        predict.vectorizer = vectorizer
        print("[INFO] Modelo y vectorizador cargados correctamente.")
    else:
        print("[WARNING] Modelos no encontrados, inicia con entrenamiento.")

app.include_router(upload, prefix="/upload", tags=["Data"])
app.include_router(train, prefix="/train", tags=["Train"])
#app.include_router(predict, prefix="/predict", tags=["Predict"])
app.include_router(graphics, prefix="/text/graph", tags=["Graphics"])
