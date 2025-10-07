# back/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FeedbackCreate(BaseModel):
    aluno_id: int
    texto: str
    video_url: Optional[str] = None

class FeedbackOut(BaseModel):
    id: int
    aluno_id: int
    treinador_id: int
    texto: str
    video_url: Optional[str]
    criado_em: datetime

    class Config:
        orm_mode = True

class NotificacaoOut(BaseModel):
    id: int
    mensagem: str
    lida: bool
    criado_em: datetime

    class Config:
        orm_mode = True