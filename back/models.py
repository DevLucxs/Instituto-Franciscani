from sqlalchemy import Column, Integer, String, Enum, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
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

class Desempenho(Base):
    __tablename__ = "desempenhos"
    
    id = Column(Integer, primary_key=True, index=True)
    atleta_id = Column(Integer, ForeignKey("users.id"))
    treino = Column(String(255), nullable=False)
    tempo = Column(Float)      # tempo em segundos
    distancia = Column(Float)  # distância em metros
    
    atleta = relationship("User", back_populates="desempenhos")


# Adicionar no User o relacionamento inverso
User.desempenhos = relationship("Desempenho", back_populates="atleta")