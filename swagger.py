OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Books API",
        "version": "1.0.0",
        "description": (
            "Filter Project Gutenberg books by ID, language, mime-type, topic, "
            "author, and title. Results are ordered by download count (descending) "
            "and returned 25 at a time.\n\n"
            "Multiple filters are combined with **AND**. Multiple values for the "
            "same filter (comma-separated) are combined with **OR**.\n\n"
            "Topic matches **subject** or **bookshelf** with a case-insensitive "
            "partial match (for example `topic=child`)."
        ),
    },
    "servers": [{"url": "/", "description": "Current host"}],
    "tags": [
        {"name": "Books", "description": "Search and list books"},
        {
            "name": "Filter discovery",
            "description": "Browse real values to use with the book filters",
        },
        {"name": "Meta", "description": "API information"},
    ],
    "paths": {
        "/": {
            "get": {
                "tags": ["Meta"],
                "summary": "API overview",
                "operationId": "getOverview",
                "responses": {
                    "200": {
                        "description": "Short description of available endpoints",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Overview"}
                            }
                        },
                    }
                },
            }
        },
        "/books": {
            "get": {
                "tags": ["Books"],
                "summary": "List books",
                "description": (
                    "Returns matching books with a total count and pagination links. "
                    "Use `page` to fetch the next set of 25 results."
                ),
                "operationId": "listBooks",
                "parameters": [
                    {
                        "name": "ids",
                        "in": "query",
                        "required": False,
                        "description": "Project Gutenberg IDs, comma-separated.",
                        "schema": {"type": "string", "example": "11,84"},
                    },
                    {
                        "name": "language",
                        "in": "query",
                        "required": False,
                        "description": "Language codes, comma-separated.",
                        "schema": {"type": "string", "example": "en,fr"},
                    },
                    {
                        "name": "mime_type",
                        "in": "query",
                        "required": False,
                        "description": (
                            "Mime-type filter. Matches the exact type or a type "
                            "with extra parameters such as `text/plain; charset=utf-8`."
                        ),
                        "schema": {"type": "string", "example": "text/plain"},
                    },
                    {
                        "name": "topic",
                        "in": "query",
                        "required": False,
                        "description": (
                            "Case-insensitive partial match on subject or bookshelf."
                        ),
                        "schema": {"type": "string", "example": "child,infant"},
                    },
                    {
                        "name": "author",
                        "in": "query",
                        "required": False,
                        "description": "Case-insensitive partial match on author name.",
                        "schema": {"type": "string", "example": "carroll"},
                    },
                    {
                        "name": "title",
                        "in": "query",
                        "required": False,
                        "description": "Case-insensitive partial match on title.",
                        "schema": {"type": "string", "example": "alice"},
                    },
                    {
                        "name": "page",
                        "in": "query",
                        "required": False,
                        "description": "1-based page number. Each page has at most 25 books.",
                        "schema": {
                            "type": "integer",
                            "minimum": 1,
                            "default": 1,
                            "example": 1,
                        },
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Paginated list of matching books",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/BookList"}
                            }
                        },
                    },
                    "400": {
                        "description": "Invalid page parameter",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                },
            }
        },
        "/filters/book-ids": {
            "get": {
                "tags": ["Filter discovery"],
                "summary": "Discover Project Gutenberg IDs",
                "description": "Lists popular books and their IDs. `q` partially matches a title.",
                "parameters": [
                    {"$ref": "#/components/parameters/DiscoveryQuery"},
                    {"$ref": "#/components/parameters/DiscoveryLimit"},
                ],
                "responses": {"200": {"description": "Available book IDs"}, "400": {"description": "Invalid limit"}},
            }
        },
        "/filters/languages": {
            "get": {
                "tags": ["Filter discovery"],
                "summary": "List available languages",
                "responses": {"200": {"description": "Available language codes"}},
            }
        },
        "/filters/mime-types": {
            "get": {
                "tags": ["Filter discovery"],
                "summary": "List available MIME types",
                "responses": {"200": {"description": "Available MIME types"}},
            }
        },
        "/filters/topics": {
            "get": {
                "tags": ["Filter discovery"],
                "summary": "Discover subjects and bookshelves",
                "description": "Returns values accepted by the `topic` filter. `q` partially matches a subject or bookshelf.",
                "parameters": [
                    {"$ref": "#/components/parameters/DiscoveryQuery"},
                    {"$ref": "#/components/parameters/DiscoveryLimit"},
                ],
                "responses": {"200": {"description": "Available topics"}, "400": {"description": "Invalid limit"}},
            }
        },
        "/filters/authors": {
            "get": {
                "tags": ["Filter discovery"],
                "summary": "Discover authors",
                "description": "Lists authors. `q` partially matches an author name.",
                "parameters": [
                    {"$ref": "#/components/parameters/DiscoveryQuery"},
                    {"$ref": "#/components/parameters/DiscoveryLimit"},
                ],
                "responses": {"200": {"description": "Available authors"}, "400": {"description": "Invalid limit"}},
            }
        },
        "/filters/titles": {
            "get": {
                "tags": ["Filter discovery"],
                "summary": "Discover titles",
                "description": "Lists popular books and titles. `q` partially matches a title.",
                "parameters": [
                    {"$ref": "#/components/parameters/DiscoveryQuery"},
                    {"$ref": "#/components/parameters/DiscoveryLimit"},
                ],
                "responses": {"200": {"description": "Available titles"}, "400": {"description": "Invalid limit"}},
            }
        },
    },
    "components": {
        "parameters": {
            "DiscoveryQuery": {
                "name": "q",
                "in": "query",
                "required": False,
                "description": "Optional case-insensitive partial search term.",
                "schema": {"type": "string", "example": "carroll"},
            },
            "DiscoveryLimit": {
                "name": "limit",
                "in": "query",
                "required": False,
                "description": "Maximum values returned (1–100; default 25).",
                "schema": {"type": "integer", "minimum": 1, "maximum": 100, "default": 25},
            },
        },
        "schemas": {
            "Overview": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "endpoint": {"type": "string"},
                    "docs": {"type": "string"},
                    "filters": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "pagination": {"type": "string"},
                    "example": {"type": "string"},
                },
            },
            "Error": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "page must be a positive integer"}
                },
            },
            "Author": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "example": "Carroll, Lewis"},
                    "birth_year": {
                        "type": "integer",
                        "nullable": True,
                        "example": 1832,
                    },
                    "death_year": {
                        "type": "integer",
                        "nullable": True,
                        "example": 1898,
                    },
                },
            },
            "Book": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "Project Gutenberg ID",
                        "example": 11,
                    },
                    "title": {
                        "type": "string",
                        "example": "Alice's Adventures in Wonderland",
                    },
                    "authors": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/Author"},
                    },
                    "languages": {
                        "type": "array",
                        "items": {"type": "string", "example": "en"},
                    },
                    "subjects": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "genre": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Same values as subjects (no separate genre field in the dump).",
                    },
                    "bookshelves": {
                        "type": "array",
                        "items": {"type": "string", "example": "Children's Literature"},
                    },
                    "formats": {
                        "type": "array",
                        "description": "Download links, each paired with its MIME type.",
                        "items": {
                            "type": "object",
                            "required": ["mime_type", "url"],
                            "properties": {
                                "mime_type": {
                                    "type": "string",
                                    "example": "application/epub+zip",
                                },
                                "url": {"type": "string", "format": "uri"},
                            },
                        },
                        "example": [
                            {
                                "mime_type": "text/html",
                                "url": "https://www.gutenberg.org/ebooks/11.html.images",
                            },
                            {
                                "mime_type": "application/epub+zip",
                                "url": "https://www.gutenberg.org/ebooks/11.epub.images",
                            },
                        ],
                    },
                    "media_type": {"type": "string", "example": "Text"},
                    "download_count": {"type": "integer", "example": 15000},
                },
            },
            "BookList": {
                "type": "object",
                "properties": {
                    "count": {
                        "type": "integer",
                        "description": "Total books matching the filters",
                        "example": 431,
                    },
                    "next": {
                        "type": "string",
                        "format": "uri",
                        "nullable": True,
                    },
                    "previous": {
                        "type": "string",
                        "format": "uri",
                        "nullable": True,
                    },
                    "results": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/Book"},
                    },
                },
            },
        }
    },
}
