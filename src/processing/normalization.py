from urllib.parse import urlparse, urlunparse


def normalize_url(url: str) -> str:
    """
    Normalize URLs by:
    - Removing surrounding whitespace
    - Converting scheme and hostname to lowercase
    - Removing fragments
    - Removing trailing slash from paths
    """

    if not url:
        return ""

    url = url.strip()

    parsed = urlparse(url)

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/").lower()

    normalized = urlunparse(
        (
            scheme,
            netloc,
            path,
            "",
            parsed.query,
            "",
        )
    )

    return normalized


def normalize_entity_url(entity: dict) -> dict:
    """
    Normalize the main URL and source URL of an entity.
    """

    if entity.get("url"):
        entity["url"] = normalize_url(entity["url"])

    source = entity.get("source")

    if source and source.get("url"):
        source["url"] = normalize_url(source["url"])

    return entity


if __name__ == "__main__":
    test_urls = [
        "HTTPS://GitHub.COM/OpenAI/Test/",
        "https://github.com/OpenAI/Test/#readme",
        " https://github.com/openai/test/ ",
    ]

    for url in test_urls:
        print(normalize_url(url))