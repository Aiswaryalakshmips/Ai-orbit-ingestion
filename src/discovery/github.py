import requests
from uuid import uuid5, NAMESPACE_URL

from src.models import Entity, Source


GITHUB_API_URL = "https://api.github.com/search/repositories"


def search_repositories(query: str, limit: int = 10):
    params = {
        "q": query,
        "per_page": limit,
    }

    response = requests.get(
        GITHUB_API_URL,
        params=params,
        timeout=15,
    )

    response.raise_for_status()

    return response.json().get("items", [])


def convert_to_entities(repositories):
    entities = []

    for repo in repositories:
        entity = Entity(
            id=uuid5(NAMESPACE_URL, repo["html_url"]),
            entity_type="repository",
            name=repo["name"],
            description=repo.get("description") or "",
            url=repo["html_url"],
            categories=["AI", "Open Source", "Repository"],
            source=Source(
                name="GitHub",
                url=repo["html_url"],
            ),
        )

        entities.append(entity)

    return entities


if __name__ == "__main__":
    repositories = search_repositories(
        "artificial intelligence",
        limit=10,
    )

    entities = convert_to_entities(repositories)

    for entity in entities:
        print(entity.model_dump_json(indent=2))