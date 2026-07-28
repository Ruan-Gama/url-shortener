"""
Configuração de conexão com o banco de dados PostgreSQL.

Centraliza a criação do engine SQLAlchemy e da factory de sessões
(`SessionLocal`), usados via injeção de dependência nas rotas da API.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Carrega as variáveis do arquivo .env (override=True garante que valores
# do .env tenham prioridade sobre variáveis já definidas no ambiente)
load_dotenv(override=True)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# URL de conexão com o Postgres, montada a partir das variáveis de ambiente
DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Engine de conexão: gerencia o pool de conexões com o banco
engine = create_engine(DATABASE_URL)

# Factory de sessões: cada request cria e fecha a sua própria sessão
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Classe base da qual todos os modelos ORM (ex: models.URL) herdam
Base = declarative_base()