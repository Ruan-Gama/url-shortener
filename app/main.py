import secrets
import string
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from . import models, schemas
from .database import SessionLocal, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Cria as tabelas quando a aplicação inicia
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


def get_db():
    # Abre uma sessão com o banco
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_code(length: int = 6) -> str:
    # Gera um código curto aleatório
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_unique_code(db: Session, length: int = 6) -> str:
    # Gera um código e garante que ele não exista no banco
    while True:
        code = generate_code(length)
        existing_url = db.query(models.URL).filter(models.URL.short_code == code).first()
        if not existing_url:
            return code


@app.get("/")
def read_root():
    return {"message": "URL Shortener API funcionando."}


@app.post("/shorten", response_model=schemas.URLResponse, status_code=201)
def shorten_url(url: schemas.URLCreate, db: Session = Depends(get_db)):
    try:
        code = generate_unique_code(db)

        new_url = models.URL(
            original_url=str(url.original_url),
            short_code=code,
        )

        db.add(new_url)
        db.commit()
        db.refresh(new_url)

        return new_url

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
    try:
        url = db.query(models.URL).filter(models.URL.short_code == short_code).first()

        if not url:
            raise HTTPException(status_code=404, detail="URL nao encontrada.")

        # Soma um clique toda vez que alguém acessa o link curto
        url.clicks += 1
        db.commit()

        return RedirectResponse(url=url.original_url, status_code=307)

    except OperationalError as exc:
        raise HTTPException(
            status_code=503,
            detail="Banco de dados indisponivel no momento.",
        ) from exc