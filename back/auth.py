from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from database import get_db
import models
from fastapi import Request 


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


def get_usuario_logado(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token ausente")

    token = auth_header.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")

        usuario = db.query(models.User).filter(models.User.email == email).first()
        if not usuario:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")

        return usuario
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")


