# app/core/audit.py
from datetime import datetime
from app.db.mongodb import get_collection

async def log_action(username: str, action: str, category: str, doc_id: str):
    audit = await get_collection("audit_logs")
    await audit.insert_one({
        "username": username,
        "action": action,
        "category": category,
        "document_id": doc_id,
        "timestamp": datetime.utcnow()
    })
