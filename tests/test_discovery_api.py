def test_discovery_endpoints_expose_filter_values(client):
    languages = client.get("/filters/languages")
    mime_types = client.get("/filters/mime-types")
    topics = client.get("/filters/topics?q=child")
    authors = client.get("/filters/authors?q=carroll")
    titles = client.get("/filters/titles?q=alice")
    book_ids = client.get("/filters/book-ids?q=alice")

    assert languages.status_code == 200
    assert languages.get_json()["results"] == ["en", "fr"]
    assert "application/epub+zip" in mime_types.get_json()["results"]
    assert topics.get_json()["subjects"] == ["Child education"]
    assert topics.get_json()["bookshelves"] == ["Children's Literature"]
    assert authors.get_json()["results"][0]["name"] == "Carroll, Lewis"
    assert titles.get_json()["results"][0]["id"] == 11
    assert book_ids.get_json()["results"][0]["id"] == 11


def test_discovery_limit_is_validated(client):
    response = client.get("/filters/authors?limit=101")

    assert response.status_code == 400
    assert response.get_json() == {"error": "limit must be an integer from 1 to 100"}
