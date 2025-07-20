from app.db.mongodb import get_collection
from app.models.document import Document
from bson import ObjectId

async def insert_document(filename, category, content, path):
    collection = await get_collection("documents")
    result = await collection.insert_one({
        "filename": filename,
        "category": category,
        "content": content,
        "path": path
    })
    return result.inserted_id
