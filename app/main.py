import random
import string
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from . import models, schemas
from .database import SessionLocal, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        models.Base.metadata.create_all(bind=engine)
    except OperationalError as exc:
        print(f"Database startup error: {exc}")
    yield


app = FastAPI(lifespan=lifespan)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_code(length=6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


@app.post("/shorten", response_model=schemas.URLResponse)
def shorten_url(url: schemas.URLCreate, db: Session = Depends(get_db)):
    try:
        models.Base.metadata.create_all(bind=engine)

        code = generate_code()
        while db.query(models.URL).filter(models.URL.short_code == code).first():
            code = generate_code()

        new_url = models.URL(
            original_url=url.original_url,
            short_code=code
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