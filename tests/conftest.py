import pytest

from app import create_app
from models import Author, Book, Bookshelf, Format, Language, Subject, db


@pytest.fixture()
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_ENGINE_OPTIONS": {},
        }
    )

    with app.app_context():
        db.create_all()
        seed_books()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def seed_books():
    english = Language(id=1, code="en")
    french = Language(id=2, code="fr")
    carroll = Author(id=1, name="Carroll, Lewis", birth_year=1832, death_year=1898)
    austen = Author(id=2, name="Austen, Jane", birth_year=1775, death_year=1817)
    child_education = Subject(id=1, name="Child education")
    science = Subject(id=2, name="Science")
    childrens_literature = Bookshelf(id=1, name="Children's Literature")

    alice = Book(
        id=1,
        gutenberg_id=11,
        title="Alice's Adventures in Wonderland",
        media_type="Text",
        download_count=1000,
        authors=[carroll],
        languages=[english],
        subjects=[child_education],
        bookshelves=[childrens_literature],
        formats=[
            Format(mime_type="text/plain", url="https://example.test/alice.txt"),
            Format(mime_type="application/epub+zip", url="https://example.test/alice.epub"),
        ],
    )
    pride = Book(
        id=2,
        gutenberg_id=1342,
        title="Pride and Prejudice",
        media_type="Text",
        download_count=900,
        authors=[austen],
        languages=[english, french],
        subjects=[science],
        formats=[Format(mime_type="text/html", url="https://example.test/pride.html")],
    )
    db.session.add_all(
        [
            english,
            french,
            carroll,
            austen,
            child_education,
            science,
            childrens_literature,
            alice,
            pride,
        ]
    )

    for number in range(3, 31):
        db.session.add(
            Book(
                id=number,
                gutenberg_id=10000 + number,
                title=f"Popular book {number}",
                media_type="Text",
                download_count=1000 - number,
                languages=[english],
            )
        )
    db.session.commit()
