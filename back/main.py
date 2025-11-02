from fastapi import FastAPI, Request, Form, Body, Path, Depends, HTTPException
import shutil
from fastapi import File, UploadFile
import os
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, relationship, joinedload
from database import SessionLocal, engine, Base, get_db
import models
from sqlalchemy import func
from datetime import datetime, timedelta, date, time
from typing import List, Optional
from pydantic import BaseModel
from schema import FeedbackCreate, FeedbackOut
from auth import criar_token_acesso, get_usuario_logado
from fastapi import APIRouter, Depends


UPLOAD_DIRECTORY = "./uploads/dietas" #Variável referente a dieta
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

VIDEO_UPLOAD_DIRECTORY = "./uploads/videos" #Variável referente aos vídeos
os.makedirs(VIDEO_UPLOAD_DIRECTORY, exist_ok=True)

class VideoUpdate(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    aluno_id: Optional[int] = None

# Cria tabelas se não existirem
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Servindo arquivos estáticos
app.mount("/static", StaticFiles(directory="front/static"), name="static")
app.mount("/uploads", StaticFiles(directory="./uploads"), name="uploads")

# Templates (HTML com Jinja2)
templates = Jinja2Templates(directory="front/templates")

# Função para popular usuários
@app.on_event("startup")
def startup_event():
    """
    Função executada apenas uma vez na inicialização do servidor.
    """
    db = SessionLocal()
    try:
        # Lógica da seed_users
        users_exist = db.query(models.User).count() > 0
        if not users_exist:
            print("--- BANCO DE DADOS VAZIO: Populando usuários iniciais... ---")
            users = [
                models.User(nome="Ana Mendonça", email="ana.mendonca@if.com", senha="123", tipo=models.UserType.aluno),
                models.User(nome="Pedro Silva", email="pedro.silva@if.com", senha="123", tipo=models.UserType.aluno),
                models.User(nome="Carolina Rodrigues", email="carolina.rodrigues@if.com", senha="123", tipo=models.UserType.aluno),
                models.User(nome="Treinador Master", email="treinador@if.com", senha="123", tipo=models.UserType.treinador),
            ]
            db.add_all(users)
            db.commit()

        # Lógica da seed_desempenhos
        if db.query(models.Desempenho).count() == 0:
            print("--- BANCO DE DADOS VAZIO: Populando desempenhos iniciais... ---")
            alunos = db.query(models.User).filter(models.User.tipo == models.UserType.aluno).all()
            for aluno in alunos:
                db.add_all([
                    models.Desempenho(atleta_id=aluno.id, treino="Natação 50m", tempo=35.2, distancia=50),
                    models.Desempenho(atleta_id=aluno.id, treino="Natação 100m", tempo=80.5, distancia=100),
                ])
            db.commit()
    finally:
        db.close()


# Função auxiliar para buscar usuário por email
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# Página de login
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Rota de login
@app.post("/login")
async def login(request: Request, email: str = Form(...), senha: str = Form(...)):
    db = SessionLocal()
    user = get_user_by_email(db, email)
    db.close()

    if not user or user.senha != senha:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "Credenciais inválidas!"}
        )

    if user.tipo.value == "aluno":
        return RedirectResponse(url=f"/aluno/dashboard/{user.id}", status_code=303)
    else:
        return RedirectResponse(url=f"/treinador/dashboard/{user.id}", status_code=303)




    #ALUNOS

# Dashboard do aluno (simplificado)
@app.get("/aluno/dashboard/{aluno_id}", response_class=HTMLResponse)
async def aluno_dashboard(request: Request, aluno_id: int):
    db = SessionLocal()
    aluno = db.query(models.User).filter(models.User.id == aluno_id).first()
    db.close()

    return templates.TemplateResponse(
        "pages_aluno/dashboard.html",
        {
            "request": request,
            "aluno": aluno
        }
    )


@app.get("/api/atletas/{atleta_id}/desempenho", response_class=JSONResponse)
async def api_desempenho(atleta_id: int):
    db = SessionLocal()
    atleta = db.query(models.User).filter(
        models.User.id == atleta_id,
        models.User.tipo == models.UserType.aluno
    ).first()
    
    if not atleta:
        db.close()
        return JSONResponse(status_code=404, content={"error": "Atleta não encontrado"})
    
    registros = []
    for d in atleta.desempenhos:
        registros.append({
            "id": d.id,
            "treino": d.treino,
            "tempo": d.tempo,
            "distancia": d.distancia
        })
    
    db.close()
    return {"atleta": {"id": atleta.id, "nome": atleta.nome}, "desempenho": registros}

# TREINADOR

# Dashboard do treinador (simplificado)
@app.get("/treinador/dashboard/{treinador_id}", response_class=HTMLResponse)
async def treinador_dashboard(request: Request, treinador_id: int):
    db = SessionLocal()
    
    try:
        treinador = db.query(models.User).filter(models.User.id == treinador_id).first()

        if not treinador:
            return templates.TemplateResponse(
                "pages/404_error.html", # Exemplo de página de erro
                {"request": request},
                status_code=404
            )

        alunos = db.query(models.User).filter(models.User.tipo == models.UserType.aluno).all()
        total_alunos = db.query(models.User).filter(models.User.tipo == models.UserType.aluno).count()

        return templates.TemplateResponse(
            "pages/dashboard.html",
            {
                "request": request,
                "treinador": treinador,
                "alunos": alunos,
                "total_alunos": total_alunos
            }
        )
    finally:
        db.close()
     
@app.get("/api/comparativo")
async def comparar_periodos():
    db = SessionLocal()
    try:
        hoje = datetime.now()
        # Definição dos intervalos
        inicio_30 = hoje - timedelta(days=30)
        inicio_60 = hoje - timedelta(days=60)

        # Contagem de cadastros nos últimos 30 dias
        bloco_A = db.query(models.User).filter(models.User.data_cadastro >= inicio_30).count()

        # Contagem de cadastros entre 30 e 60 dias atrás
        bloco_B = db.query(models.User).filter(
            models.User.data_cadastro >= inicio_60,
            models.User.data_cadastro < inicio_30
        ).count()

        # Evita divisão por zero
        if bloco_B == 0:
            if bloco_A == 0:
                return {"mensagem": "Sem dados suficientes para comparação."}
            else:
                return {"mensagem": "Aumento de 100% (nenhum dado no mês anterior)."}

        # Calcula a variação percentual
        variacao = ((bloco_A - bloco_B) / bloco_B) * 100

        # Monta a mensagem adequada
        if variacao > 0:
            mensagem = f"{variacao:.1f}% a mais do que no mês passado."
        elif variacao < 0:
            mensagem = f"{abs(variacao):.1f}% a menos do que no mês passado."
        else:
            mensagem = "Mesma quantidade do mês passado."

        return {
            "mensagem": mensagem,
            "periodo_atual": bloco_A,
            "periodo_anterior": bloco_B,
            "variacao_percentual": round(variacao, 1)
        }

    finally:
        db.close()

# Motor de pesquisa da página de Dashboard 
@app.get("/api/search/alunos/") 
async def search_alunos(q: str | None = None):

    if not q or len(q) < 2:
        return []

    db = SessionLocal()
    try:
        search_term = f"%{q.lower()}%"

        alunos_encontrados = db.query(models.User).filter(
            models.User.tipo == "aluno",
            func.lower(models.User.nome).like(search_term)
        ).limit(10).all()

        sugestoes = [
            {"id": aluno.id, "nome": aluno.nome}
            for aluno in alunos_encontrados
        ]
        
        return sugestoes
    finally:
        db.close()
        
# Página de Dados Gerais
@app.get("/treinador/dados/{treinador_id}", response_class=HTMLResponse)
async def dados_gerais(request: Request, treinador_id: int):
    db = SessionLocal()
    treinador = db.query(models.User).filter(models.User.id == treinador_id).first()
    alunos = db.query(models.User).filter(models.User.tipo == models.UserType.aluno).all()
    db.close()
    
    return templates.TemplateResponse(
        "pages/dados_gerais.html", 
        {
            "request": request, 
            "treinador": treinador,
            "alunos": alunos
        }
    )

# Página de Treinamentos
@app.get("/treinador/treinamentos/{treinador_id}", response_class=HTMLResponse)
async def treinamentos(request: Request, treinador_id: int):
    db = SessionLocal()
    treinador = db.query(models.User).filter(models.User.id == treinador_id).first()
    db.close()
    return templates.TemplateResponse(
        "pages/treinamentos.html", 
        {"request": request, "treinador": treinador}
    )

# Página de Calendário
@app.get("/treinador/calendario/{treinador_id}", response_class=HTMLResponse)
async def calendario(request: Request, treinador_id: int):
    db = SessionLocal()
    treinador = db.query(models.User).filter(models.User.id == treinador_id).first()
    db.close()
    return templates.TemplateResponse(
        "pages/calendario.html", 
        {"request": request, "treinador": treinador}
    )


@app.post("/api/feedbacks")
async def criar_feedback(feedback: FeedbackCreate, usuario: models.User = Depends(get_usuario_logado)):
    try:
        db = SessionLocal()
        novo_feedback = models.Feedback(
            texto=feedback.texto,
            video_url=feedback.video_url,
            treinador_id=usuario.id,
            aluno_id=feedback.aluno_id
        )
        db.add(novo_feedback)
        db.commit()
        db.refresh(novo_feedback)
        db.close()
        return {"sucesso": True, "mensagem": "Feedback criado com sucesso"}
    except Exception as e:
        db.rollback()
        db.close()
        raise HTTPException(status_code=500, detail=f"Erro ao criar feedback: {str(e)}")


@app.get("/api/alunos/{aluno_id}/feedbacks")
def listar_feedbacks(aluno_id: int, db: Session = Depends(get_db)):
    feedbacks = db.query(models.Feedback).filter(models.Feedback.aluno_id == aluno_id).all()
    
    resultado = []
    for f in feedbacks:
        resultado.append({
            "id": f.id,
            "aluno_id": f.aluno_id,
            "treinador_id": f.treinador_id,
            "treinador_nome": f.treinador.nome if f.treinador else "Treinador",
            "texto": f.texto,
            "video_url": f.video_url,
            "criado_em": f.criado_em
        })
    return {"feedbacks": resultado}




# Criar atleta
@app.post("/api/alunos", response_class=JSONResponse)
async def criar_aluno(aluno: dict = Body(...)):
    db = SessionLocal()
    novo_aluno = models.User(
        nome=aluno.get("nome"),
        email=aluno.get("email"),
        senha="123",
        tipo=models.UserType.aluno,
        modalidade=aluno.get("modalidade"),
        idade=aluno.get("idade"),
        status=aluno.get("status"),
        telefone=aluno.get("telefone"),
        endereco=aluno.get("endereco"),
        
    )
    db.add(novo_aluno)
    db.commit()
    db.refresh(novo_aluno)
    db.close()
    return {
        "id": novo_aluno.id,
        "nome": novo_aluno.nome,
        "email": novo_aluno.email,
        "modalidade": novo_aluno.modalidade,
        "idade": novo_aluno.idade,
        "status": novo_aluno.status,
        "telefone": novo_aluno.telefone,
        "endereco": novo_aluno.endereco,
        
    }

# Editar atleta
@app.put("/api/alunos/{atleta_id}", response_class=JSONResponse)
async def atualizar_aluno(atleta_id: int = Path(...), dados: dict = Body(...)):
    db = SessionLocal()
    atleta = db.query(models.User).filter(models.User.id == atleta_id, models.User.tipo == models.UserType.aluno).first()
    if not atleta:
        db.close()
        return JSONResponse(status_code=404, content={"error": "Atleta não encontrado"})

    atleta.nome = dados.get("nome", atleta.nome)
    atleta.email = dados.get("email", atleta.email)
    atleta.modalidade = dados.get("modalidade", atleta.modalidade)
    atleta.idade = dados.get("idade", atleta.idade)
    atleta.status = dados.get("status", atleta.status)
    atleta.telefone = dados.get("telefone", atleta.telefone)
    atleta.endereco = dados.get("endereco", atleta.endereco)
    

    db.commit()
    db.refresh(atleta)
    db.close()

    return {
        "id": atleta.id,
        "nome": atleta.nome,
        "email": atleta.email,
        "modalidade": atleta.modalidade,
        "idade": atleta.idade,
        "status": atleta.status,
        "telefone": atleta.telefone,
        "endereco": atleta.endereco,
        
    }

@app.get("/api/alunos", response_class=JSONResponse)
async def listar_alunos():
    db = SessionLocal()
    alunos = db.query(models.User).filter(models.User.tipo == models.UserType.aluno).all()
    db.close()
    result = []
    for a in alunos:
        result.append({
        "id": a.id,
        "nome": a.nome,
        "email": a.email,
        "modalidade": a.modalidade,
        "idade": a.idade,
        "status": a.status,
        "telefone": a.telefone,
        "endereco": a.endereco,
})
    return result

@app.delete("/api/alunos/{atleta_id}", response_class=JSONResponse)
async def deletar_aluno(atleta_id: int = Path(...)):
    db = SessionLocal()
    atleta = db.query(models.User).filter(models.User.id == atleta_id, models.User.tipo == models.UserType.aluno).first()
    
    if not atleta:
        db.close()
        return JSONResponse(status_code=404, content={"error": "Atleta não encontrado"})

    db.delete(atleta)
    db.commit()
    db.close()

    return JSONResponse(status_code=200, content={"message": "Atleta excluído com sucesso"})


@app.post("/api/desempenho", response_class=JSONResponse)
async def adicionar_desempenho(desempenho: dict = Body(...)):
    db = SessionLocal()
    
    # ⚠️ Certifique-se de que o atleta_id seja enviado no body do request!
    novo_desempenho = models.Desempenho(
        atleta_id=desempenho.get("atleta_id"),
        treino=desempenho.get("treino"),
        tempo=desempenho.get("tempo"),
        distancia=desempenho.get("distancia"),
    )
    
    db.add(novo_desempenho)
    db.commit()
    db.refresh(novo_desempenho)
    db.close()
    
    return {
        "id": novo_desempenho.id,
        "atleta_id": novo_desempenho.atleta_id,
        "treino": novo_desempenho.treino,
        "tempo": novo_desempenho.tempo,
        "distancia": novo_desempenho.distancia,
    }

# Diretório para salvar as dietas enviadas aos atletas
@app.post("/api/dieta/{atleta_id}")
async def upload_dieta(atleta_id: int, file: UploadFile = File(...)):
    db = SessionLocal()
    atleta = db.query(models.User).filter(models.User.id == atleta_id).first()
    
    if not atleta:
        db.close()
        return JSONResponse(status_code=404, content={"message": "Atleta não encontrado"})

    # Define um caminho único para o arquivo
    file_path = os.path.join(UPLOAD_DIRECTORY, f"dieta_{atleta_id}_{file.filename}")
    
    # Salva o arquivo no servidor
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Atualiza o caminho do arquivo no banco de dados do atleta
    atleta.dieta_filepath = file_path
    db.commit()
    
    return JSONResponse(status_code=200, content={"message": f"Dieta enviada para {atleta.nome} com sucesso!", "filepath": file_path})
    # Não está sendo enviado ao aluno ainda..
    db.close()


@app.post("/api/videos")
async def upload_video(
    titulo: str = Form(...),
    descricao: str = Form(None),
    aluno_id: int = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    try:
        # Define um caminho para o arquivo de vídeo
        video_path = os.path.join(VIDEO_UPLOAD_DIRECTORY, file.filename)

        # Salva o arquivo no servidor
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        url_path = f"/uploads/videos/{file.filename}"

        # Cria a nova entrada de vídeo no banco de dados
        novo_video = models.Video(
            titulo=titulo,
            descricao=descricao,
            filepath=url_path,
            aluno_id=aluno_id
        )
        db.add(novo_video)
        db.commit()
        db.refresh(novo_video)

        return JSONResponse(status_code=200, content={"message": "Vídeo postado com sucesso!"})

    except Exception as e:
        print(f"Erro ao postar vídeo: {e}")
        db.rollback()
        return JSONResponse(status_code=500, content={"message": "Erro interno ao processar o vídeo."})
    
    finally:
        db.close()

# RETORNA VÍDEOS
@app.get("/api/treinador/videos")
async def get_videos(db: Session = Depends(get_db)):
    try:
        videos = db.query(models.Video).options(joinedload(models.Video.aluno)).all()
        
        videos_list = []
        for v in videos:
            url_video_path = v.filepath 
            
            if url_video_path: 
                url_video_path = url_video_path.replace("\\", "/")
                if url_video_path.startswith("./"):
                    url_video_path = url_video_path[1:]
            videos_list.append({
                "id": v.id,
                "titulo": v.titulo,
                "descricao": v.descricao,
                "url_video": v.filepath, 
                "data_upload": v.data_upload.isoformat(),
                "atleta_id": v.aluno_id,
                "atleta_nome": v.aluno.nome if v.aluno else "Sem atleta"
            })
            
        
        return {"sucesso": True, "videos": videos_list}
        
    except Exception as e:
        print(f"Erro ao buscar vídeos: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar vídeos")

#ROTA DE DELEÇÃO DE VÍDEOS
@app.delete("/api/treinador/videos/{video_id}", status_code=200)
async def delete_video_route(video_id: int, db: Session = Depends(get_db)):
    try:
        # 1. Encontra o vídeo no banco de dados
        video = db.query(models.Video).filter(models.Video.id == video_id).first()
        
        if not video:
            raise HTTPException(status_code=404, detail="Vídeo não encontrado")

        # 2. Pega o caminho do arquivo (ex: "./uploads/videos/file.mp4" ou "/uploads/videos/file.mp4")
        file_path = video.filepath
        
        # 3. Deleta o registro do banco de dados
        db.delete(video)
        db.commit()
        
        # 4. Deleta o arquivo físico do servidor
        # (Adiciona uma verificação para garantir que o caminho existe)
        
        # Limpa o caminho para o formato do OS (caso esteja como /uploads/...)
        if file_path.startswith('/'):
            file_path = "." + file_path # Converte "/uploads/..." para "./uploads/..."
            
        file_path = os.path.normpath(file_path) # Garante que o OS entenda o caminho

        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Arquivo físico excluído: {file_path}")
        else:
            print(f"Aviso: Arquivo físico não encontrado em {file_path}, mas o registro do banco foi excluído.")

        
        
        return {"sucesso": True, "message": "Vídeo excluído com sucesso"}

    except Exception as e:
        db.rollback()
        print(f"Erro ao excluir vídeo: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao excluir o vídeo.")

# ROTA DE ATUALIZAÇÃO DE VÍDEOS
@app.put("/api/treinador/videos/{video_id}")
async def update_video(
    video_id: int, 
    video_update: VideoUpdate, 
    db: Session = Depends(get_db)
):
    try:
        # 1. Encontrar o vídeo no banco
        video = db.query(models.Video).filter(models.Video.id == video_id).first()
        
        if not video:
            raise HTTPException(status_code=404, detail="Vídeo não encontrado")
        
        # 2. Atualizar os campos com os dados recebidos
        video.titulo = video_update.titulo
        video.descricao = video_update.descricao
        video.aluno_id = video_update.aluno_id # No frontend é 'atleta_id', mas no DB é 'aluno_id'
        
        # 3. Salvar as mudanças
        db.commit()
        db.refresh(video)
        
        return {"sucesso": True, "message": "Vídeo atualizado com sucesso!"}

    except Exception as e:
        db.rollback()
        print(f"Erro ao atualizar vídeo: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao atualizar o vídeo.")

# Buscar todos os eventos
@app.get("/api/eventos")
async def get_eventos(db: Session = Depends(get_db)):
        
        eventos = db.query(models.Evento).options(joinedload(models.Evento.participantes)).all()
        
        # Converte para um formato JSON seguro
        eventos_list = []
        for ev in eventos:
            eventos_list.append({
                "id": ev.id,
                "title": ev.titulo,
                "date": ev.data.isoformat(),
                "time": ev.hora.isoformat() if ev.hora else None,
                "location": ev.local,
                "type": ev.tipo,
                "description": ev.descricao,
                "treinador_id": ev.treinador_id,
                "alunos_ids": [p.id for p in ev.participantes] # Lista de IDs de alunos
            })
        return eventos_list

# Este é o schema que valida os dados que chegam do JavaScript para criar o evento na rota seguinte
class EventoCreate(BaseModel):
    title: str
    date: date
    time: Optional[str] = None
    location: Optional[str] = None
    type: str
    description: Optional[str] = None
    alunos_ids: List[int] = []
    treinador_id: int

@app.post("/api/CriarEventos")  #Está lançando no banco de dados, falta assimilar ao aluno
async def create_evento(evento_data: EventoCreate, db: Session = Depends(get_db)):
    
    # 1. Buscar os alunos (participantes) no banco
    participantes = []
    if evento_data.alunos_ids:
        participantes = db.query(models.User).filter(
            models.User.id.in_(evento_data.alunos_ids)
        ).all()

    # 2. Criar o novo objeto Evento
    novo_evento = models.Evento(
        titulo=evento_data.title,
        data=evento_data.date,
        hora=evento_data.time,
        local=evento_data.location,
        tipo=evento_data.type,
        descricao=evento_data.description,
        treinador_id=evento_data.treinador_id,
        participantes=participantes  # Associa os alunos encontrados
    )
    
    # 3. Adicionar e salvar no banco
    db.add(novo_evento)
    db.commit()
    db.refresh(novo_evento) # Pega o ID e outros dados gerados pelo banco

    return {
        "title": novo_evento.titulo,       
        "date": novo_evento.data.isoformat(),
        "time": novo_evento.hora.isoformat() if novo_evento.hora else None,
        "location": novo_evento.local,     
        "type": novo_evento.tipo,
        "description": novo_evento.descricao, 
        "treinador_id": novo_evento.treinador_id,
        "alunos": [{"id": p.id, "nome": p.nome} for p in participantes] 
    }


#Deletar eventeos
@app.delete("/api/DeletarEventos/{evento_id}", status_code=200)
async def deletar_evento(evento_id: int, db: Session = Depends(get_db)):
    
    # 1. Encontra o evento no banco de dados
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    
    # 2. Se o evento não for encontrado, retorna um erro 404
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # 3. Se o evento for encontrado, deleta
    try:
        db.delete(evento)
        db.commit()
        # Retorna uma mensagem de sucesso
        return {"message": "Evento deletado com sucesso", "id": evento_id}
    except Exception as e:
        # Em caso de erro no banco, desfaz a operação
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar evento: {str(e)}")

#Editar/Atualizar eventos
@app.put("/api/eventos/{evento_id}")
async def update_evento(evento_id: int, evento_data: EventoCreate, db: Session = Depends(get_db)):
    
    # 1. Encontra o evento existente no banco
    db_evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    
    if not db_evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    # 2. Atualiza os campos simples
    db_evento.titulo = evento_data.title
    db_evento.data = evento_data.date
    db_evento.hora = evento_data.time
    db_evento.local = evento_data.location
    db_evento.tipo = evento_data.type
    db_evento.descricao = evento_data.description
    db_evento.treinador_id = evento_data.treinador_id

    # 3. Atualiza os participantes (relação Many-to-Many)
    participantes = []
    if evento_data.alunos_ids:
        participantes = db.query(models.User).filter(
            models.User.id.in_(evento_data.alunos_ids)
        ).all()
    
    db_evento.participantes = participantes # O SQLAlchemy atualiza a tabela de associação

    # 4. Salva as mudanças
    try:
        db.commit()
        db.refresh(db_evento)
        
        # 5. Retorna o evento atualizado para o frontend
        return {
            "id": db_evento.id, # Inclui o ID
            "title": db_evento.titulo,
            "date": db_evento.data.isoformat(),
            "time": db_evento.hora.isoformat() if db_evento.hora else None,
            "location": db_evento.local,
            "type": db_evento.tipo,
            "description": db_evento.descricao,
            "treinador_id": db_evento.treinador_id,
            # Retorna a lista completa de objetos de alunos
            "alunos": [{"id": p.id, "nome": p.nome} for p in db_evento.participantes] 
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar evento: {str(e)}")

# Logout
@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_id")
    return response

