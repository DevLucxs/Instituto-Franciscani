from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from database import get_db
import models

# Carregar variáveis do .env
load_dotenv()
SECRET_KEY = os.getenv("APP_SECRET_KEY")
ALGORITHM = "HS256"
EXPIRATION_MINUTES = 60

if not SECRET_KEY:
    raise RuntimeError("APP_SECRET_KEY não foi definido no .env")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def criar_token_acesso(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=EXPIRATION_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_usuario_logado(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    usuario = db.query(models.User).filter(models.User.email == email).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return usuario
