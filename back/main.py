from fastapi import FastAPI, Request, Form, Body, Path
import shutil
from fastapi import File, UploadFile
import os
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
from sqlalchemy import func
from datetime import datetime, timedelta


UPLOAD_DIRECTORY = "./uploads/dietas" #Variável referente a dieta
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# Cria tabelas se não existirem
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Servindo arquivos estáticos
app.mount("/static", StaticFiles(directory="front/static"), name="static")

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

# Logout
@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_id")
    return response

