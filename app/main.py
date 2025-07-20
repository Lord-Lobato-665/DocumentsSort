from fastapi import FastAPI
from app.api.endpoints import upload, train

app = FastAPI(title="Document Classifier API")

app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(train.router, prefix="/train", tags=["Train"])
