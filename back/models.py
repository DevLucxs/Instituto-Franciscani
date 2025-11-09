from sqlalchemy import Column, Integer, String, Enum, Float, ForeignKey, func, DateTime, Text, Table, Date, Time, Boolean
from sqlalchemy.orm import declarative_base, relationship
import enum
from database import Base
from datetime import datetime
from datetime import timezone


class UserType(enum.Enum):
    aluno = "aluno"
    treinador = "treinador"

evento_alunos_association = Table(
    'evento_alunos', Base.metadata,
    Column('evento_id', Integer, ForeignKey('eventos.id'), primary_key=True),
    Column('aluno_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
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
    foco = Column(String(255), nullable=True)  
    ano_ingresso = Column(Integer, nullable=True)  
    # Eventos que este usuário (treinador) criou
    eventos_criados = relationship("Evento", back_populates="criador", foreign_keys="Evento.treinador_id")
    
    # Eventos que este usuário (aluno) está participando
    eventos_participantes = relationship(
        "Evento",
        secondary=evento_alunos_association,
        back_populates="participantes")

    desempenhos = relationship("Desempenho", back_populates="atleta")


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    aluno_id = Column(Integer, ForeignKey("users.id"))
    treinador_id = Column(Integer, ForeignKey("users.id"))
    texto = Column(Text, nullable=False)
    video_url = Column(String, nullable=True)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    aluno = relationship("User", foreign_keys=[aluno_id])
    treinador = relationship("User", foreign_keys=[treinador_id])

class Desempenho(Base):
    __tablename__ = "desempenhos"

    id = Column(Integer, primary_key=True)
    atleta_id = Column(Integer, ForeignKey("users.id"))
    treino = Column(String)
    tempo = Column(Float)
    distancia = Column(Integer)
    data_atualizacao = Column(DateTime, default=datetime.utcnow)
    tempo_esperado = Column(Float)

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

class Evento(Base):
    __tablename__ = "eventos"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    data = Column(Date, nullable=False)
    hora = Column(Time, nullable=True)
    local = Column(String(255), nullable=True)
    tipo = Column(String(50), nullable=True)
    descricao = Column(String(1024), nullable=True)
    
    # Relação com o Treinador (Criador)
    treinador_id = Column(Integer, ForeignKey("users.id"))
    criador = relationship("User", back_populates="eventos_criados")

    participantes = relationship(
        "User",
        secondary=evento_alunos_association,
        back_populates="eventos_participantes"
    )

User.videos = relationship("Video", back_populates="aluno")

Video.aluno = relationship("User", back_populates="videos")

# Adicionar no User o relacionamento inverso
User.desempenhos = relationship("Desempenho", back_populates="atleta")

class Treinamento(Base):
    __tablename__ = "treinamentos"

    id = Column(Integer, primary_key=True, index=True)
    atleta_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Associação com o atleta (aluno)
    tipo = Column(String(50), nullable=False)  # Ex: "Técnico", "Aeróbico", etc.
    data = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    carga = Column(Float, default=0.0)  # Carga em horas ou minutos, como no seu front
    deadline = Column(Date, nullable=True)  # Prazo para conclusão
    completed = Column(Boolean, default=False)  # Se foi concluído
    descricao = Column(String(1024), nullable=True)  # Descrição técnica, se aplicável

    # Relacionamento com o User (atleta)
    atleta = relationship("User", back_populates="treinamentos")

# Adicione o relacionamento inverso no User (depois da classe User existente)
User.treinamentos = relationship("Treinamento", back_populates="atleta")