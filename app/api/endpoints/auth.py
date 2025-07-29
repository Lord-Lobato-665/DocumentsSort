# app/api/endpoints/auth.py
from fastapi import APIRouter, HTTPException
from app.models.user import UserIn
from app.db.mongodb import get_collection
from app.core.security import hash_password
from datetime import datetime
from fastapi import Depends
from app.core.security import verify_password
from app.core.jwt import create_access_token

router = APIRouter()

@router.post("/register")
async def register_user(user: UserIn):
    users = await get_collection("users")
    if await users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    hashed_pwd = hash_password(user.password)
    new_user = {
        "username": user.username,
        "email": user.email,
        "password": hashed_pwd,
        "created_at": datetime.utcnow()
    }
    await users.insert_one(new_user)
    return {"message": "Usuario registrado con éxito"}


@router.post("/login")
async def login_user(user: UserIn):
    users = await get_collection("users")
    found = await users.find_one({"email": user.email})
    
    if not found or not verify_password(user.password, found["password"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    token = create_access_token({"sub": found["email"]})
    return {"access_token": token, "token_type": "bearer"}