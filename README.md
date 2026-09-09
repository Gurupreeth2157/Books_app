# Books API

Flask + SQLAlchemy API over the Gutendex dump in `gutendex.sql`.

## Setup

1. Create a database and load the dump (this file is large and can take several minutes):

```powershell
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS gutendex CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
Get-Content gutendex.sql | mysql -u root -p gutendex
```

2. Copy `.env.example` to `.env` and set your MySQL password.

3. Install and run:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The API listens on `http://127.0.0.1:5000`.

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

Filters are combined with AND. Multiple values for one filter are OR.

### Example

`http://127.0.0.1:5000/books?language=en,fr&topic=child&author=carroll`

Response includes `count`, `next`, `previous`, and `results` with title, authors, languages, subjects/genre, bookshelves, and download links by mime-type. Books are ordered by `download_count` descending.
