from fastapi import APIRouter, HTTPException
from app.db.mongodb import get_collection
from typing import List
from datetime import datetime

router = APIRouter()

@router.get("/audit-logs")
async def get_all_audit_logs():
    collection = await get_collection("audit_logs")
    try:
        logs = await collection.find().sort("timestamp", -1).to_list(length=1000)
        for log in logs:
            log["_id"] = str(log["_id"])
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los logs: {str(e)}")


@router.get("/audit-logs/by-operation/{operation}")
async def get_logs_by_operation(operation: str):
    collection = await get_collection("audit_logs")
    try:
        logs = await collection.find({"operation": operation}).sort("timestamp", -1).to_list(length=500)
        if not logs:
            raise HTTPException(status_code=404, detail=f"No se encontraron logs con operación: '{operation}'")
        for log in logs:
            log["_id"] = str(log["_id"])
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al filtrar logs por operación: {str(e)}")


@router.get("/audit-logs/by-user/{username}")
async def get_logs_by_user(username: str):
    collection = await get_collection("audit_logs")
    try:
        logs = await collection.find({"username": username}).sort("timestamp", -1).to_list(length=500)
        if not logs:
            raise HTTPException(status_code=404, detail=f"No se encontraron logs para el usuario: '{username}'")
        for log in logs:
            log["_id"] = str(log["_id"])
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al filtrar logs por usuario: {str(e)}")
