# URL Shortener

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.1+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)

API simples para encurtamento de URLs construída com FastAPI, SQLAlchemy e PostgreSQL.

O projeto cria um código curto aleatório para cada URL enviada ao endpoint `POST /shorten` e persiste os dados no banco.

## Visão geral

Atualmente a aplicação entrega:

- criação de links curtos via API REST;
- persistência em PostgreSQL;
- documentação interativa automática com Swagger UI;
- execução local com Docker Compose.

## Stack utilizada

| Camada | Tecnologia |
| --- | --- |
| API | FastAPI |
| Servidor ASGI | Uvicorn |
| ORM | SQLAlchemy |
| Banco de dados | PostgreSQL 15 |
| Ambiente | Docker + Docker Compose |

## Estrutura do projeto

```text
url-shortener/
|-- app/
|   |-- database.py
|   |-- main.py
|   |-- models.py
|   `-- schemas.py
|-- .dockerignore
|-- .env.example
|-- .gitignore
|-- docker-compose.yml
|-- Dockerfile
|-- README.md
`-- requirements-app.txt
```

## Requisitos

Para rodar o projeto com o fluxo principal:

- Docker
- Docker Compose

Para rodar manualmente:

- Python 3.12+
- PostgreSQL

## Como executar com Docker

1. Crie o arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

No Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

2. Suba os serviços:

```bash
docker compose up --build
```

3. Acesse:

- API: [http://localhost:8000](http://localhost:8000)
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

## Como executar manualmente

1. Crie e ative um ambiente virtual.
2. Instale as dependências:

```bash
pip install -r requirements-app.txt
```

3. Garanta que o PostgreSQL esteja rodando.
4. Configure o `.env`.

Se for rodar sem Docker Compose, ajuste o host do banco para `localhost`:

```env
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=urlshortener
DB_HOST=localhost
DB_PORT=5432
```

5. Inicie a aplicação:

```bash
uvicorn app.main:app --reload
```

## Variáveis de ambiente

| Variável | Descrição | Exemplo |
| --- | --- | --- |
| `DB_USER` | usuário do banco | `postgres` |
| `DB_PASSWORD` | senha do banco | `postgres` |
| `DB_NAME` | nome do banco | `urlshortener` |
| `DB_HOST` | host do banco | `db` ou `localhost` |
| `DB_PORT` | porta do banco | `5432` |

## Endpoint disponível

### `POST /shorten`

Cria um novo código curto para a URL enviada.

#### Request

```json
{
  "original_url": "https://example.com"
}
```

#### Response

```json
{
  "original_url": "https://example.com",
  "short_code": "DfP6vK"
}
```

#### Exemplo com cURL

```bash
curl --request POST "http://localhost:8000/shorten" \
  --header "Content-Type: application/json" \
  --data "{\"original_url\":\"https://example.com\"}"
```

## Modelo de dados

A tabela `urls` armazena:

- `id`
- `original_url`
- `short_code`
- `clicks`
- `created_at`

## Testes e validação realizados

Validação executada localmente em `2026-04-15`:

- `docker compose build api`
- `docker compose up -d`
- acesso confirmado em `http://127.0.0.1:8000/docs`
- smoke test aprovado no endpoint `POST /shorten`

Resposta observada no teste:

```json
{
  "original_url": "https://example.com",
  "short_code": "DfP6vK"
}
```

## Observações importantes

- O projeto atual implementa o encurtamento da URL, mas ainda não possui rota de redirecionamento como `GET /{short_code}`.
- O código curto é gerado aleatoriamente com 6 caracteres alfanuméricos.
- A criação das tabelas é feita automaticamente na inicialização da API.

## Melhorias futuras

- adicionar rota de redirecionamento;
- contabilizar cliques no acesso ao link curto;
- criar testes automatizados;
- validar formato de URL com regras mais rígidas;
- adicionar endpoint de health check.

## Autor

Projeto preparado para publicação por Ruan Gama.
