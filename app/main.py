"""
Aplicação principal: API de encurtamento de URLs + landing page.

Expõe:
- Landing page (GET /) com formulário de encurtamento renderizado via Jinja2
- API JSON para integração programática (POST /shorten, GET /urls, etc.)
- Redirecionamento dos links curtos (GET /{short_code})
"""

import secrets
import string
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from . import models, schemas
from .database import SessionLocal, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cria as tabelas do banco na inicialização da aplicação."""
    try:
        models.Base.metadata.create_all(bind=engine)
    except OperationalError as exc:
        print(f"Database startup error: {exc}")
    yield


app = FastAPI(
    title="URL Shortener",
    description="API simples para encurtar URLs",
    version="1.0.0",
    lifespan=lifespan,
)

# --- Configuração da landing page (templates Jinja2 + arquivos estáticos) ---
# BASE_DIR aponta para a pasta app/, garantindo que os caminhos funcionem
# independente de onde o uvicorn for iniciado (local, Docker, etc.)
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


def get_db():
    """Dependency que abre e garante o fechamento de uma sessão do banco."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_code(length: int = 6) -> str:
    """Gera um código curto aleatório (letras e dígitos)."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_unique_code(db: Session, length: int = 6) -> str:
    """Gera um código curto garantindo que ele ainda não exista no banco."""
    while True:
        code = generate_code(length)
        existing_url = db.query(models.URL).filter(models.URL.short_code == code).first()
        if not existing_url:
            return code


def criar_url_encurtada(db: Session, original_url: str) -> models.URL:
    """
    Cria e persiste uma nova URL encurtada.

    Lógica compartilhada entre o endpoint JSON (/shorten) e o formulário
    da landing page (/shorten-form), evitando duplicação.
    """
    code = generate_unique_code(db)
    new_url = models.URL(original_url=original_url, short_code=code)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)
    return new_url


# --- Landing page ---

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Renderiza a landing page com o formulário de encurtamento."""
    return templates.TemplateResponse(
        request,
        "index.html",
        {"resultado": None, "erro": None},
    )


@app.post("/shorten-form", response_class=HTMLResponse)
def shorten_form(
    request: Request,
    original_url: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Processa o envio do formulário da landing page.

    Diferente de POST /shorten (que recebe JSON e é pensado para
    integração via API), este endpoint recebe form data e devolve HTML
    renderizado com o resultado, para uso direto no navegador.
    """
    # Reaproveita o schema da API para validar a URL informada no formulário
    try:
        dados = schemas.URLCreate(original_url=original_url)
    except ValidationError:
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "resultado": None,
                "erro": "URL inválida. Use o formato https://exemplo.com/...",
                "url_digitada": original_url,
            },
        )

    try:
        nova_url = criar_url_encurtada(db, str(dados.original_url))
    except OperationalError:
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "resultado": None,
                "erro": "Banco de dados indisponível no momento. Tente novamente.",
                "url_digitada": original_url,
            },
        )

    # Monta a URL curta a partir do host da própria requisição, funcionando
    # automaticamente em qualquer ambiente (local, staging, produção)
    url_curta = f"{str(request.base_url).rstrip('/')}/{nova_url.short_code}"

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "resultado": {
                "url_curta": url_curta,
                "url_longa": nova_url.original_url,
                "criado_em": nova_url.created_at.strftime("%d/%m/%Y %H:%M"),
            },
            "erro": None,
        },
    )


# --- API JSON ---

@app.post("/shorten", response_model=schemas.URLResponse, status_code=201)
def shorten_url(url: schemas.URLCreate, db: Session = Depends(get_db)):
    """Cria uma nova URL encurtada a partir de um payload JSON."""
    try:
        return criar_url_encurtada(db, str(url.original_url))

    except OperationalError as exc:
        raise HTTPException(
            status_code=503,
            detail="Banco de dados indisponivel no momento.",
        ) from exc

    except ProgrammingError as exc:
        raise HTTPException(
            status_code=500,
            detail="Estrutura do banco ainda nao foi criada corretamente.",
        ) from exc


@app.get("/urls", response_model=list[schemas.URLResponse])
def list_urls(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Lista as URLs mais recentes, com limite configurável."""
    try:
        urls = db.query(models.URL).order_by(models.URL.id.desc()).limit(limit).all()
        return urls

    except OperationalError as exc:
        raise HTTPException(
            status_code=503,
            detail="Banco de dados indisponivel no momento.",
        ) from exc


@app.get("/urls/{short_code}", response_model=schemas.URLResponse)
def get_url_by_code(short_code: str, db: Session = Depends(get_db)):
    """Busca os detalhes de uma URL encurtada pelo seu código."""
    try:
        url = db.query(models.URL).filter(models.URL.short_code == short_code).first()

        if not url:
            raise HTTPException(status_code=404, detail="URL nao encontrada.")

        return url

    except OperationalError as exc:
        raise HTTPException(
            status_code=503,
            detail="Banco de dados indisponivel no momento.",
        ) from exc


@app.get("/{short_code}")
def redirect_url(short_code: str, db: Session = Depends(get_db)):
    """Redireciona um código curto para a URL original e soma um clique."""
    try:
        url = db.query(models.URL).filter(models.URL.short_code == short_code).first()

        if not url:
            raise HTTPException(status_code=404, detail="URL nao encontrada.")

        url.clicks += 1
        db.commit()

        return RedirectResponse(url=url.original_url, status_code=307)

    except OperationalError as exc:
        raise HTTPException(
            status_code=503,
            detail="Banco de dados indisponivel no momento.",
        ) from exc