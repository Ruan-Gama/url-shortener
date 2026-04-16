# URL Shortener

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.1+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)

Simple URL shortening API built with FastAPI, SQLAlchemy, and PostgreSQL.

The project generates a random short code for each URL submitted to the `POST /shorten` endpoint and persists the data in the database.

**Note:** This documentation is also available in Portuguese.  
[Ler em Português 🇧🇷](./README.pt-br.md)

## Overview

The application currently delivers:

- short link creation via REST API;
- persistence in PostgreSQL;
- automatic interactive documentation with Swagger UI;
- local execution with Docker Compose.

## Stack

| Layer | Technology |
| --- | --- |
| API | FastAPI |
| ASGI Server | Uvicorn |
| ORM | SQLAlchemy |
| Database | PostgreSQL 15 |
| Environment | Docker + Docker Compose |

## Project structure

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
|-- README.pt-br.md
`-- requirements-app.txt
```

## Requirements

To run the project with the main flow:

- Docker
- Docker Compose

To run manually:

- Python 3.12+
- PostgreSQL

## Running with Docker

1. Create the `.env` file from the example:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

2. Start the services:

```bash
docker compose up --build
```

3. Access:

- API: [http://localhost:8000](http://localhost:8000)
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

## Running manually

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements-app.txt
```

3. Make sure PostgreSQL is running.
4. Configure the `.env` file.

If running without Docker Compose, set the database host to `localhost`:

```env
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=urlshortener
DB_HOST=localhost
DB_PORT=5432
```

5. Start the application:

```bash
uvicorn app.main:app --reload
```

## Environment variables

| Variable | Description | Example |
| --- | --- | --- |
| `DB_USER` | database user | `postgres` |
| `DB_PASSWORD` | database password | `postgres` |
| `DB_NAME` | database name | `urlshortener` |
| `DB_HOST` | database host | `db` or `localhost` |
| `DB_PORT` | database port | `5432` |

## Available endpoint

### `POST /shorten`

Creates a new short code for the given URL.

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

#### cURL example

```bash
curl --request POST "http://localhost:8000/shorten" \
  --header "Content-Type: application/json" \
  --data "{\"original_url\":\"https://example.com\"}"
```

## Data model

The `urls` table stores:

- `id`
- `original_url`
- `short_code`
- `clicks`
- `created_at`

## Testing and validation

Validation performed locally on `2026-04-15`:

- `docker compose build api`
- `docker compose up -d`
- access confirmed at `http://127.0.0.1:8000/docs`
- smoke test passed on `POST /shorten`

Observed response during testing:

```json
{
  "original_url": "https://example.com",
  "short_code": "DfP6vK"
}
```

## Important notes

- The project currently implements URL shortening, but does not yet have a redirect route like `GET /{short_code}`.
- The short code is randomly generated with 6 alphanumeric characters.
- Table creation is handled automatically on API startup.

## Future improvements

- add redirect route;
- track clicks on short link access;
- write automated tests;
- validate URL format with stricter rules;
- add health check endpoint.

## Author

Project prepared for publication by Ruan Gama.