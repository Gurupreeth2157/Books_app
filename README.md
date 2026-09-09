# Books API

Flask + SQLAlchemy API over the Gutendex dump in `gutendex.sql`.

## Setup

1. Create a database and load the dump (preferably using mysql workbench) 


2. Create a local `.env` file and set `DATABASE_URL`. For a local MySQL
   database, use the SQLAlchemy/PyMySQL form:

```text
DATABASE_URL=mysql+pymysql://root:your_password@127.0.0.1:3306/gutendex?charset=utf8mb4
```

3. Install and run:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open **Swagger UI** at `http://127.0.0.1:5000/docs` to inspect and try the endpoints.


## Tests

The test suite uses an isolated in-memory SQLite database, so MySQL does not
need to be running.

```powershell
pip install -r requirements-dev.txt
pytest
```

## Endpoints

- `GET /docs` — Swagger UI
- `GET /openapi.json` — OpenAPI spec
- `GET /` — usage notes
- `GET /books` — filtered, paginated book list (25 per page)
- `GET /filters/` — get filter options through series of filter APIs

### Query parameters

| Param | Example | Notes |
|---|---|---|
| `ids` | `ids=11,84` | Project Gutenberg IDs |
| `language` | `language=en,fr` | Language codes |
| `mime_type` | `mime_type=text/plain` | Matches exact type or `type;charset=...` |
| `topic` | `topic=child,infant` | Partial match on subject **or** bookshelf |
| `author` | `author=carroll` | Case-insensitive partial match |
| `title` | `title=alice` | Case-insensitive partial match |
| `page` | `page=2` | 25 books per page |

