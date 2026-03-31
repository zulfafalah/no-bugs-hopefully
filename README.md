# Desent API

A simple REST API built with Django 6 and Django REST Framework. Features JWT authentication and CRUD operations for books with in-memory storage.

## Tech Stack

- Python 3.14
- Django 6.0
- Django REST Framework
- SimpleJWT (authentication)
- drf-spectacular (API docs)

## Getting Started

### Local

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Docker

```bash
docker compose up --build
```

The API will be available at `http://localhost:8006`.

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/ping` | Health check | No |
| POST | `/echo` | Echo request body | No |
| POST | `/auth/token` | Obtain JWT token | No |
| POST | `/auth/token/refresh` | Refresh JWT token | No |
| GET | `/books` | List all books | Yes |
| POST | `/books` | Create a book | Yes |
| GET | `/books/<id>` | Get a book | Yes |
| PUT | `/books/<id>` | Update a book | Yes |
| PATCH | `/books/<id>` | Partial update | Yes |
| DELETE | `/books/<id>` | Delete a book | Yes |

## API Documentation

- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI Schema: `/api/schema/`
