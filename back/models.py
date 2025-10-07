from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import declarative_base
import enum
from database import Base

class UserType(enum.Enum):
    aluno = "aluno"
    treinador = "treinador"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    senha = Column(String(255), nullable=False)
    tipo = Column(Enum(UserType, native_enum=False), nullable=False)
    nome = Column(String(255), nullable=False)