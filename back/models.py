from sqlalchemy import Column, Integer, String, Enum, Float, ForeignKey, func, DateTime
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
    cargos = Column(String(255), nullable=True)
    modalidade = Column(String(50), nullable=True)
    idade = Column(String(10), nullable=True)
    status = Column(String(20), nullable=True)
    telefone = Column(String(20), nullable=True)
    endereco = Column(String(100), nullable=True)
    data_cadastro = Column(DateTime(timezone=True), server_default=func.now())
    dieta_filepath = Column(String(255), nullable=True)

class Desempenho(Base):
    __tablename__ = "desempenhos"
    
    id = Column(Integer, primary_key=True, index=True)
    atleta_id = Column(Integer, ForeignKey("users.id"))
    treino = Column(String(255), nullable=False)
    tempo = Column(Float)      # tempo em segundos
    distancia = Column(Float)  # dist�ncia em metros
    
    atleta = relationship("User", back_populates="desempenhos")

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    descricao = Column(String(1024), nullable=True) # Usando String com tamanho maior para descrição
    filepath = Column(String(255), nullable=False)
    data_upload = Column(DateTime(timezone=True), server_default=func.now())
    
    aluno_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relacionamento opcional com o User
    aluno = relationship("User")

User.videos = relationship("Video", back_populates="aluno")

Video.aluno = relationship("User", back_populates="videos")

# Adicionar no User o relacionamento inverso
User.desempenhos = relationship("Desempenho", back_populates="atleta")