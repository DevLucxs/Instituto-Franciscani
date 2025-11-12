from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from database import get_db
import models
from fastapi import Request, Cookie, Header
from typing import Optional
from models import User

# Carregar variáveis do .env
load_dotenv()
SECRET_KEY = os.getenv("APP_SECRET_KEY")
ALGORITHM = "HS256"
EXPIRATION_MINUTES = 200

if not SECRET_KEY:
    raise RuntimeError("APP_SECRET_KEY não foi definido no .env")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def criar_token_acesso(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_usuario_logado(
    jwt_token: Optional[str] = Cookie(default=None),
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db)
):
    # Tenta pegar o token do cookie
    token = jwt_token

    # Se não tiver no cookie, tenta pegar do header Authorization
    if not token and authorization:
        if authorization.startswith("Bearer "):
            token = authorization[7:]  # remove "Bearer "

    if not token:
        raise HTTPException(status_code=401, detail="Token ausente")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        usuario = db.query(User).filter(User.email == email).first()
        if not usuario:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        return usuario
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

