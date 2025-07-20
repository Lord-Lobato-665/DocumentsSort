import io
import fitz
from docx import Document

def process_file(file_bytes: bytes, filename: str) -> str:
    filename_lower = filename.lower()

    if filename_lower.endswith(".pdf"):
        text = extract_pdf_text(file_bytes)
    elif filename_lower.endswith(".docx"):
        text = extract_docx_text(file_bytes)
    else:
        # fallback: intenta decodificar por si es .txt u otro legible
        text = file_bytes.decode('utf-8', errors='ignore')
    
    return text.strip()

def extract_pdf_text(file_bytes: bytes) -> str:
    text = ""
    with fitz.open("pdf", file_bytes) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_docx_text(file_bytes: bytes) -> str:
    text = ""
    file_stream = io.BytesIO(file_bytes)
    document = Document(file_stream)
    for para in document.paragraphs:
        text += para.text + "\n"
    return text
