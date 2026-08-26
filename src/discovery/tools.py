"""
AI Tool discovery for the AI Orbit ingestion pipeline.

Discovers representative AI applications/tools from
public GitHub repositories using the GitHub Search API.
"""

import json
import os
import time
import uuid
from pathlib import Path

import requests


OUTPUT_FILE = Path("data/tools.json")

GITHUB_API_URL = "https://api.github.com/search/repositories"

SEARCH_QUERIES = [
    "AI productivity tool",
    "AI developer tool",
    "AI automation tool",
    "AI assistant tool",
    "generative AI application",
    "AI image generation tool",
    "AI video generation tool",
    "AI coding assistant",
]


def github_headers():
    """Build GitHub API headers."""

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "AI-Orbit-Ingestion-Pipeline",
    }

    token = os.getenv("GITHUB_TOKEN")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def normalize_name(name):
    """Normalize names for deduplication."""

    return (
        str(name)
        .lower()
        .strip()
        .replace("-", " ")
        .replace("_", " ")
    )


def search_github(query, per_page=10):
    """Search GitHub repositories."""

    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": per_page,
    }

    try:
        response = requests.get(
            GITHUB_API_URL,
            headers=github_headers(),
            params=params,
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()

        return data.get("items", [])

    except requests.RequestException as error:

        print(
            f"Warning: GitHub search failed "
            f"for '{query}': {error}"
        )

        return []


def create_tool_entity(repository):
    """Convert a GitHub repository into an AI tool entity."""

    owner = repository.get("owner", {}) or {}

    return {
        "id": str(uuid.uuid5(
            uuid.NAMESPACE_URL,
            repository.get(
                "html_url",
                repository.get("full_name", "")
            ),
        )),
        "entity_type": "tool",
        "name": repository.get(
            "name",
            repository.get("full_name", "Unknown Tool"),
        ),
        "description": (
            repository.get("description")
            or "AI tool or application."
        ),
        "url": repository.get(
            "html_url",
            "",
        ),
        "categories": [
            "ai",
            "tool",
            "application",
        ],
        "source": {
            "name": "GitHub",
            "url": repository.get(
                "html_url",
                "",
            ),
        },
        "metadata": {
            "stars": repository.get(
                "stargazers_count",
                0,
            ),
            "forks": repository.get(
                "forks_count",
                0,
            ),
            "primary_language": repository.get(
                "language"
            ),
            "last_updated": repository.get(
                "updated_at"
            ),
            "owner": owner.get(
                "login"
            ),
        },
    }


def discover_tools():
    """Discover AI tools from GitHub."""

    print(
        "Starting AI tool discovery..."
    )

    discovered = []
    seen = set()

    for query in SEARCH_QUERIES:

        print(
            f"Searching GitHub tools: {query}"
        )

        repositories = search_github(
            query
        )

        for repository in repositories:

            html_url = repository.get(
                "html_url"
            )

            name = repository.get(
                "full_name"
            )

            if not html_url or not name:
                continue

            key = normalize_name(
                name
            )

            if key in seen:
                continue

            seen.add(key)

            entity = create_tool_entity(
                repository
            )

            discovered.append(
                entity
            )

        time.sleep(0.5)

    print(
        f"Unique AI tools discovered: "
        f"{len(discovered)}"
    )

    return discovered


def save_tools(tools):
    """Save discovered tools to JSON."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            tools,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"Saved {len(tools)} AI tool entities "
        f"to {OUTPUT_FILE}"
    )


def main():
    """Run AI tool discovery."""

    tools = discover_tools()

    save_tools(tools)


if __name__ == "__main__":
    main()