from app.db.mongodb import get_collection
from app.models.document import Document
from bson import ObjectId
import os
from datetime import datetime

async def insert_document(filename, category, content, path):
    collection = await get_collection("documents")
    file_stats = os.stat(path)
    size_bytes = file_stats.st_size
    length_chars = len(content)
    created_at = datetime.utcnow()  # o extrae fecha si tienes metadata real

    doc = {
        "filename": filename,
        "category": category,
        "content": content,
        "path": path,
        "size_bytes": size_bytes,
        "length_chars": length_chars,
        "created_at": created_at,
    }
    result = await collection.insert_one(doc)
    return result.inserted_id
