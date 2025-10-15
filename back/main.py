from fastapi import FastAPI, Request, Form, Body, Path
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models


# Cria tabelas se não existirem
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Servindo arquivos estáticos
app.mount("/static", StaticFiles(directory="front/static"), name="static")

# Templates (HTML com Jinja2)
templates = Jinja2Templates(directory="front/templates")

# Função para popular usuários
def seed_users():
    db = SessionLocal()
    users_exist = db.query(models.User).count() > 0
    if not users_exist:
        users = [
            models.User(nome="Ana Mendonça", email="ana.mendonca@if.com", senha="123", tipo=models.UserType.aluno),
            models.User(nome="Pedro Silva", email="pedro.silva@if.com", senha="123", tipo=models.UserType.aluno),
            models.User(nome="Carolina Rodrigues", email="carolina.rodrigues@if.com", senha="123", tipo=models.UserType.aluno),
            models.User(nome="Treinador Master", email="treinador@if.com", senha="123", tipo=models.UserType.treinador),
        ]
        db.add_all(users)
        db.commit()
    db.close()

# Popula usuários
seed_users()

def seed_desempenhos():
    db = SessionLocal()
    if db.query(models.Desempenho).count() == 0:
        alunos = db.query(models.User).filter(models.User.tipo == models.UserType.aluno).all()
        for aluno in alunos:
            db.add_all([
                models.Desempenho(atleta_id=aluno.id, treino="Natação 50m", tempo=35.2, distancia=50),
                models.Desempenho(atleta_id=aluno.id, treino="Natação 100m", tempo=80.5, distancia=100),
            ])
        db.commit()
    db.close()

seed_desempenhos()


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
    treinador = db.query(models.User).filter(models.User.id == treinador_id).first()
    alunos = db.query(models.User).filter(models.User.tipo == models.UserType.aluno).all()
    db.close()

    return templates.TemplateResponse(
        "pages/dashboard.html",
        {
            "request": request,
            "treinador": treinador,
            "alunos": alunos
        }
    )

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

# Logout
@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_id")
    return response

