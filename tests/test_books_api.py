from app import like_term


def test_list_books_returns_25_popular_books_and_pagination(client):
    response = client.get("/books")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["count"] == 30
    assert len(payload["results"]) == 25
    assert payload["results"][0]["id"] == 11
    assert payload["results"][0]["download_count"] == 1000
    assert "page=2" in payload["next"]
    assert payload["previous"] is None


def test_second_page_returns_remaining_books(client):
    response = client.get("/books?page=2")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["count"] == 30
    assert len(payload["results"]) == 5
    assert payload["next"] is None
    assert "page=1" in payload["previous"]


def test_filters_accept_multiple_values_and_combine_with_and(client):
    response = client.get(
        "/books?ids=11,1342&language=en,fr&topic=child&author=carroll&title=alice&mime_type=text/plain"
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["count"] == 1
    assert [book["id"] for book in payload["results"]] == [11]
    book = payload["results"][0]
    assert book["authors"][0]["name"] == "Carroll, Lewis"
    assert book["formats"] == [
        {
            "mime_type": "application/epub+zip",
            "url": "https://example.test/alice.epub",
        },
        {"mime_type": "text/plain", "url": "https://example.test/alice.txt"},
    ]


def test_topic_matches_subject_or_bookshelf_case_insensitively(client):
    response = client.get("/books?topic=CHILDREN")

    assert response.status_code == 200
    assert [book["id"] for book in response.get_json()["results"]] == [11]


def test_invalid_page_returns_400(client):
    response = client.get("/books?page=0")

    assert response.status_code == 400
    assert response.get_json() == {"error": "page must be a positive integer"}


def test_like_term_escapes_sql_wildcards():
    assert like_term("a!b%c_d") == "%a!!b!%c!_d%"
