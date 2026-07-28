# URL Shortener

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.1+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)

Simple URL shortening API built with FastAPI, SQLAlchemy, and PostgreSQL, with a lightweight server-rendered landing page.

The project generates a random short code for each URL submitted (via the landing page form or the `POST /shorten` endpoint) and persists the data in the database.

**Note:** This documentation is also available in Portuguese.  
[Ler em Português 🇧🇷](./README.pt-br.md)

## Overview

The application currently delivers:

- a landing page with a form to shorten URLs, rendered server-side with Jinja2;
- short link creation via REST API;
- redirection of short links to their original URL, with click tracking;
- persistence in PostgreSQL;
- automatic interactive documentation with Swagger UI;
- local execution with Docker Compose.

## Stack

| Layer | Technology |
| --- | --- |
| API | FastAPI |
| ASGI Server | Uvicorn |
| Templating | Jinja2 |
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
|   |-- schemas.py
|   |-- templates/
|   |   `-- index.html
|   `-- static/
|       `-- style.css
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

- Landing page: [http://localhost:8000](http://localhost:8000)
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

## Available endpoints

### `GET /`

Renders the landing page with the URL-shortening form.

### `POST /shorten-form`

Handles the landing page form submission (`application/x-www-form-urlencoded`). Renders the result back on the same page as HTML. Intended for browser use, not for API integration.

### `POST /shorten`

Creates a new short code for the given URL. Intended for programmatic/API use.

#### Request

```json
{
  "original_url": "https://example.com"
}
```

#### Response

```json
{
  "id": 1,
  "original_url": "https://example.com",
  "short_code": "DfP6vK",
  "clicks": 0,
  "created_at": "2026-07-27T22:13:20.331705"
}
```

#### cURL example

```bash
curl --request POST "http://localhost:8000/shorten" \
  --header "Content-Type: application/json" \
  --data "{\"original_url\":\"https://example.com\"}"
```

### `GET /urls`

Lists the most recent short URLs. Accepts an optional `limit` query parameter (default `10`, max `100`).

### `GET /urls/{short_code}`

Returns the details of a single short URL by its code.

### `GET /{short_code}`

Redirects to the original URL and increments the `clicks` counter.

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

Landing page (`GET /`, `POST /shorten-form`) validated locally on `2026-07-27`:

- form submission creates a record and renders the short URL on the page;
- invalid URLs are rejected with an inline error message;
- the JSON API (`POST /shorten`, `GET /urls`) continues to work unchanged.

## Important notes

- The short code is randomly generated with 6 alphanumeric characters.
- Table creation is handled automatically on API startup.
- The landing page and the JSON API share the same URL-creation logic, so both stay consistent with each other.

## Future improvements

- write automated tests;
- validate URL format with stricter rules;
- add health check endpoint;
- add pagination to `GET /urls`;
- optional JS-enhanced UX on the landing page (submit without full page reload).

## Live demo

The API is hosted and publicly accessible at:
👉 **[https://shortenerurl.duckdns.org/](https://shortenerurl.duckdns.org/)**

Swagger UI: [https://shortenerurl.duckdns.org/docs](https://shortenerurl.duckdns.org/docs)

## Author

Project prepared for publication by Ruan Gama.