import os
from urllib.parse import urlencode

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint
from sqlalchemy import false, func, or_
from werkzeug.middleware.proxy_fix import ProxyFix

from models import Author, Book, Bookshelf, Format, Language, Subject, db
from swagger import OPENAPI_SPEC

load_dotenv()

PAGE_SIZE = 25
DISCOVERY_DEFAULT_LIMIT = 25
DISCOVERY_MAX_LIMIT = 100


def database_uri():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL must be set.")
    return database_url


def create_app(test_config=None):
    app = Flask(__name__)
    # Render terminates HTTPS at a reverse proxy. Trust its forwarded host and
    # protocol headers so generated pagination URLs use the public HTTPS URL.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1, x_proto=1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 5,
        "pool_recycle": 280,
    }
    if test_config:
        app.config.update(test_config)
    db.init_app(app)
    register_swagger(app)
    register_routes(app)
    return app


def register_swagger(app):
    swagger_ui = get_swaggerui_blueprint(
        "/docs",
        "/openapi.json",
        config={
            "app_name": "Books API",
            "tryItOutEnabled": True,
            "supportedSubmitMethods": ["get"],
        },
    )
    app.register_blueprint(swagger_ui, url_prefix="/docs")


def parse_values(*names):
    seen = set()
    values = []
    for name in names:
        for raw in request.args.getlist(name):
            for part in raw.split(","):
                part = part.strip()
                if part and part not in seen:
                    seen.add(part)
                    values.append(part)
    return values


def like_term(value):
    escaped = (
        value.replace("!", "!!").replace("%", "!%").replace("_", "!_")
    )
    return f"%{escaped}%"


def discovery_limit():
    """Return a bounded result size for filter-discovery endpoints."""
    raw_limit = request.args.get("limit", DISCOVERY_DEFAULT_LIMIT)
    try:
        limit = int(raw_limit)
    except (TypeError, ValueError):
        return None
    if not 1 <= limit <= DISCOVERY_MAX_LIMIT:
        return None
    return limit


def query_term():
    """Return an optional, trimmed discovery search term."""
    return request.args.get("q", "").strip()


def apply_filters(query):
    ids = parse_values("ids", "id")
    if ids:
        parsed_ids = []
        for value in ids:
            try:
                parsed_ids.append(int(value))
            except ValueError:
                continue
        if parsed_ids:
            query = query.filter(Book.gutenberg_id.in_(parsed_ids))
        else:
            query = query.filter(false())

    languages = parse_values("language", "languages")
    if languages:
        query = query.filter(Book.languages.any(Language.code.in_(languages)))

    mime_types = parse_values("mime_type", "mime-type", "mime")
    if mime_types:
        mime_clauses = [
            Book.formats.any(
                or_(
                    Format.mime_type == mime,
                    Format.mime_type.like(f"{mime};%"),
                )
            )
            for mime in mime_types
        ]
        query = query.filter(or_(*mime_clauses))

    topics = parse_values("topic")
    if topics:
        topic_clauses = [
            or_(
                Book.subjects.any(Subject.name.ilike(like_term(topic), escape="!")),
                Book.bookshelves.any(
                    Bookshelf.name.ilike(like_term(topic), escape="!")
                ),
            )
            for topic in topics
        ]
        query = query.filter(or_(*topic_clauses))

    authors = parse_values("author")
    if authors:
        author_clauses = [
            Book.authors.any(Author.name.ilike(like_term(author), escape="!"))
            for author in authors
        ]
        query = query.filter(or_(*author_clauses))

    titles = parse_values("title")
    if titles:
        title_clauses = [
            Book.title.ilike(like_term(title), escape="!") for title in titles
        ]
        query = query.filter(or_(*title_clauses))

    return query


def page_link(page):
    args = request.args.to_dict(flat=False)
    args["page"] = [str(page)]
    query = urlencode(args, doseq=True)
    return request.base_url + ("?" + query if query else "")


def register_routes(app):
    @app.get("/openapi.json")
    def openapi_spec():
        return jsonify(OPENAPI_SPEC)

    @app.get("/")
    def index():
        return jsonify(
            {
                "message": "Gutendex-style books API",
                "endpoint": "/books",
                "docs": "/docs",
                "filters": [
                    "ids",
                    "language",
                    "mime_type",
                    "topic",
                    "author",
                    "title",
                ],
                "filter_discovery": {
                    "book_ids": "/filters/book-ids",
                    "languages": "/filters/languages",
                    "mime_types": "/filters/mime-types",
                    "topics": "/filters/topics",
                    "authors": "/filters/authors",
                    "titles": "/filters/titles",
                },
                "pagination": "page (25 books per page)",
                "example": "/books?language=en,fr&topic=child&page=1",
            }
        )

    @app.get("/filters/book-ids")
    def discover_book_ids():
        limit = discovery_limit()
        if limit is None:
            return jsonify({"error": "limit must be an integer from 1 to 100"}), 400

        query = db.session.query(Book)
        term = query_term()
        if term:
            query = query.filter(Book.title.ilike(like_term(term), escape="!"))

        books = (
            query.order_by(Book.download_count.desc(), Book.gutenberg_id.asc())
            .limit(limit)
            .all()
        )
        return jsonify(
            {
                "results": [
                    {
                        "id": book.gutenberg_id,
                        "title": book.title,
                        "download_count": book.download_count or 0,
                    }
                    for book in books
                ]
            }
        )

    @app.get("/filters/languages")
    def discover_languages():
        languages = db.session.query(Language).order_by(Language.code.asc()).all()
        return jsonify({"results": [language.code for language in languages]})

    @app.get("/filters/mime-types")
    def discover_mime_types():
        mime_types = (
            db.session.query(Format.mime_type)
            .distinct()
            .order_by(Format.mime_type.asc())
            .all()
        )
        return jsonify({"results": [mime_type for (mime_type,) in mime_types]})

    @app.get("/filters/topics")
    def discover_topics():
        limit = discovery_limit()
        if limit is None:
            return jsonify({"error": "limit must be an integer from 1 to 100"}), 400

        term = query_term()
        subject_query = db.session.query(Subject.name)
        bookshelf_query = db.session.query(Bookshelf.name)
        if term:
            pattern = like_term(term)
            subject_query = subject_query.filter(Subject.name.ilike(pattern, escape="!"))
            bookshelf_query = bookshelf_query.filter(
                Bookshelf.name.ilike(pattern, escape="!")
            )

        subjects = subject_query.order_by(Subject.name.asc()).limit(limit).all()
        bookshelves = bookshelf_query.order_by(Bookshelf.name.asc()).limit(limit).all()
        return jsonify(
            {
                "subjects": [name for (name,) in subjects],
                "bookshelves": [name for (name,) in bookshelves],
            }
        )

    @app.get("/filters/authors")
    def discover_authors():
        limit = discovery_limit()
        if limit is None:
            return jsonify({"error": "limit must be an integer from 1 to 100"}), 400

        query = db.session.query(Author)
        term = query_term()
        if term:
            query = query.filter(Author.name.ilike(like_term(term), escape="!"))
        authors = query.order_by(Author.name.asc()).limit(limit).all()
        return jsonify({"results": [author.to_dict() for author in authors]})

    @app.get("/filters/titles")
    def discover_titles():
        limit = discovery_limit()
        if limit is None:
            return jsonify({"error": "limit must be an integer from 1 to 100"}), 400

        query = db.session.query(Book)
        term = query_term()
        if term:
            query = query.filter(Book.title.ilike(like_term(term), escape="!"))
        books = (
            query.order_by(Book.download_count.desc(), Book.gutenberg_id.asc())
            .limit(limit)
            .all()
        )
        return jsonify(
            {
                "results": [
                    {
                        "id": book.gutenberg_id,
                        "title": book.title,
                        "download_count": book.download_count or 0,
                    }
                    for book in books
                ]
            }
        )

    @app.get("/books")
    def list_books():
        try:
            page = int(request.args.get("page", 1))
        except (TypeError, ValueError):
            return jsonify({"error": "page must be a positive integer"}), 400

        if page < 1:
            return jsonify({"error": "page must be a positive integer"}), 400

        offset = (page - 1) * PAGE_SIZE
        filtered = apply_filters(db.session.query(Book))
        total = filtered.with_entities(func.count(Book.id)).scalar() or 0
        books = (
            filtered.order_by(Book.download_count.desc(), Book.gutenberg_id.asc())
            .offset(offset)
            .limit(PAGE_SIZE)
            .all()
        )

        next_url = page_link(page + 1) if offset + len(books) < total else None
        previous_url = page_link(page - 1) if page > 1 else None

        return jsonify(
            {
                "count": total,
                "next": next_url,
                "previous": previous_url,
                "results": [book.to_dict() for book in books],
            }
        )


app = create_app()


if __name__ == "__main__":
    app.run(
        debug=os.getenv("FLASK_DEBUG", "false").lower()
        in {"1", "true", "yes", "on"},
        host="127.0.0.1",
        port=int(os.getenv("PORT", "5000")),
    )
