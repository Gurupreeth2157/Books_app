from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

book_authors = db.Table(
    "books_book_authors",
    db.Column("id", db.Integer, primary_key=True),
    db.Column("book_id", db.Integer, db.ForeignKey("books_book.id"), nullable=False),
    db.Column("author_id", db.Integer, db.ForeignKey("books_author.id"), nullable=False),
)

book_bookshelves = db.Table(
    "books_book_bookshelves",
    db.Column("id", db.Integer, primary_key=True),
    db.Column("book_id", db.Integer, db.ForeignKey("books_book.id"), nullable=False),
    db.Column(
        "bookshelf_id",
        db.Integer,
        db.ForeignKey("books_bookshelf.id"),
        nullable=False,
    ),
)

book_languages = db.Table(
    "books_book_languages",
    db.Column("id", db.Integer, primary_key=True),
    db.Column("book_id", db.Integer, db.ForeignKey("books_book.id"), nullable=False),
    db.Column(
        "language_id",
        db.Integer,
        db.ForeignKey("books_language.id"),
        nullable=False,
    ),
)

book_subjects = db.Table(
    "books_book_subjects",
    db.Column("id", db.Integer, primary_key=True),
    db.Column("book_id", db.Integer, db.ForeignKey("books_book.id"), nullable=False),
    db.Column("subject_id", db.Integer, db.ForeignKey("books_subject.id"), nullable=False),
)


class Author(db.Model):
    __tablename__ = "books_author"

    id = db.Column(db.Integer, primary_key=True)
    birth_year = db.Column(db.SmallInteger)
    death_year = db.Column(db.SmallInteger)
    name = db.Column(db.String(128), nullable=False)

    def to_dict(self):
        return {
            "name": self.name,
            "birth_year": self.birth_year,
            "death_year": self.death_year,
        }


class Language(db.Model):
    __tablename__ = "books_language"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4), nullable=False)


class Subject(db.Model):
    __tablename__ = "books_subject"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)


class Bookshelf(db.Model):
    __tablename__ = "books_bookshelf"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)


class Format(db.Model):
    __tablename__ = "books_format"

    id = db.Column(db.Integer, primary_key=True)
    mime_type = db.Column(db.String(32), nullable=False)
    url = db.Column(db.Text, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books_book.id"), nullable=False)


class Book(db.Model):
    __tablename__ = "books_book"

    id = db.Column(db.Integer, primary_key=True)
    download_count = db.Column(db.Integer)
    gutenberg_id = db.Column(db.Integer, nullable=False)
    media_type = db.Column(db.String(16), nullable=False)
    title = db.Column(db.Text)

    authors = db.relationship(Author, secondary=book_authors, lazy="selectin")
    languages = db.relationship(Language, secondary=book_languages, lazy="selectin")
    subjects = db.relationship(Subject, secondary=book_subjects, lazy="selectin")
    bookshelves = db.relationship(
        Bookshelf, secondary=book_bookshelves, lazy="selectin"
    )
    formats = db.relationship(Format, lazy="selectin")

    def to_dict(self):
        subject_names = [subject.name for subject in self.subjects]
        return {
            "id": self.gutenberg_id,
            "title": self.title,
            "authors": [author.to_dict() for author in self.authors],
            "languages": [language.code for language in self.languages],
            "subjects": subject_names,
            "genre": subject_names,
            "bookshelves": [shelf.name for shelf in self.bookshelves],
            "formats": [
                {"mime_type": fmt.mime_type, "url": fmt.url}
                for fmt in sorted(self.formats, key=lambda fmt: fmt.mime_type)
            ],
            "media_type": self.media_type,
            "download_count": self.download_count or 0,
        }
