from fastapi import APIRouter, File, UploadFile, Form
from app.services.file_handler import save_document
from app.crud.document import insert_document

router = APIRouter()

@router.post("/")
async def upload_document(file: UploadFile = File(...), category: str = Form(...)):
    doc_path, content = await save_document(file, category)
    doc_id = await insert_document(file.filename, category, content, doc_path)
    return {"message": "Documento guardado", "id": str(doc_id)}
