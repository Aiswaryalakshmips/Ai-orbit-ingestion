import json
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()


GITHUB_API_URL = "https://api.github.com/search/repositories"
GITHUB_CONTENTS_URL = "https://api.github.com/repos"

OUTPUT_FILE = Path(
    "data/mcp.json"
)


SEARCH_QUERIES = [
    "MCP server",
    "Model Context Protocol",
    "mcp-server",
    "model-context-protocol",
]


# --------------------------------------------------
# GitHub headers
# --------------------------------------------------

def get_headers():
    """Build GitHub API request headers."""

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "AI-Orbit-Ingestion",
    }

    token = os.getenv(
        "GITHUB_TOKEN"
    )

    if token:
        headers["Authorization"] = (
            f"Bearer {token}"
        )

    return headers


# --------------------------------------------------
# GitHub repository search
# --------------------------------------------------

def search_github(query):
    """Search GitHub repositories related to MCP."""

    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": 20,
    }

    try:

        response = requests.get(
            GITHUB_API_URL,
            headers=get_headers(),
            params=params,
            timeout=20,
        )

        response.raise_for_status()

        return response.json().get(
            "items",
            []
        )

    except requests.RequestException as error:

        print(
            f"Warning: GitHub request failed "
            f"for '{query}': {error}"
        )

        return []


# --------------------------------------------------
# README fetching
# --------------------------------------------------

def fetch_readme(owner, repo_name):
    """
    Fetch repository README from GitHub.

    Returns plain README text when available.
    """

    url = (
        f"{GITHUB_CONTENTS_URL}/"
        f"{owner}/{repo_name}/readme"
    )

    try:

        response = requests.get(
            url,
            headers=get_headers(),
            params={
                "ref": "HEAD"
            },
            timeout=15,
        )

        if response.status_code != 200:
            return ""

        data = response.json()

        # GitHub normally returns base64 content.
        content = data.get(
            "content",
            ""
        )

        encoding = data.get(
            "encoding",
            ""
        )

        if (
            encoding == "base64"
            and content
        ):

            import base64

            decoded = base64.b64decode(
                content
            )

            return decoded.decode(
                "utf-8",
                errors="ignore"
            )

        return ""

    except (
        requests.RequestException,
        ValueError,
        UnicodeDecodeError,
    ) as error:

        print(
            f"Warning: README fetch failed "
            f"for {owner}/{repo_name}: {error}"
        )

        return ""


# --------------------------------------------------
# Installation extraction
# --------------------------------------------------

def extract_installation(readme):
    """
    Extract a useful installation section from README.

    We only return information that actually appears
    in the README.
    """

    if not readme:
        return None

    lines = readme.splitlines()

    installation_keywords = (
        "installation",
        "install",
        "getting started",
        "setup",
        "quick start",
    )

    start_index = None

    for index, line in enumerate(lines):

        clean_line = line.strip().lower()

        if (
            clean_line.startswith("#")
            and any(
                keyword in clean_line
                for keyword in installation_keywords
            )
        ):

            start_index = index
            break

    if start_index is None:
        return None

    collected = []

    for line in lines[
        start_index + 1:
        start_index + 25
    ]:

        # Stop at the next markdown heading.
        if (
            line.strip().startswith("#")
            and collected
        ):
            break

        if line.strip():
            collected.append(
                line.rstrip()
            )

    if not collected:
        return None

    text = "\n".join(
        collected
    ).strip()

    # Avoid storing an excessively large README section.
    return text[:2000]


# --------------------------------------------------
# Runtime detection
# --------------------------------------------------

def detect_runtime(
    repo,
    readme
):
    """
    Detect runtime/language from reliable repository data.

    Runtime is only assigned when there is evidence.
    """

    language = (
        repo.get("language")
        or ""
    ).lower()

    text = (
        readme or ""
    ).lower()

    runtimes = []

    # Python
    if (
        language == "python"
        or "python" in text
        or "pip install" in text
        or "uv run" in text
    ):
        runtimes.append(
            "Python"
        )

    # Node.js / TypeScript
    if (
        language in {
            "javascript",
            "typescript",
        }
        or "npm install" in text
        or "npx " in text
        or "node " in text
    ):
        runtimes.append(
            "Node.js"
        )

    # Go
    if (
        language == "go"
        or "go run" in text
        or "go install" in text
    ):
        runtimes.append(
            "Go"
        )

    # Rust
    if (
        language == "rust"
        or "cargo run" in text
        or "cargo install" in text
    ):
        runtimes.append(
            "Rust"
        )

    # Java
    if (
        language == "java"
        or "mvn " in text
        or "gradle" in text
    ):
        runtimes.append(
            "Java"
        )

    # Remove duplicates.
    runtimes = list(
        dict.fromkeys(runtimes)
    )

    if not runtimes:
        return None

    return runtimes


# --------------------------------------------------
# MCP metadata enrichment
# --------------------------------------------------

def enrich_mcp_metadata(
    repo,
    owner_login
):
    """
    Add MCP-specific metadata from the repository README.
    """

    repo_name = repo.get(
        "name",
        ""
    )

    readme = fetch_readme(
        owner_login,
        repo_name
    )

    installation = extract_installation(
        readme
    )

    runtime = detect_runtime(
        repo,
        readme
    )

    return {
        "installation": installation,
        "runtime": runtime,
    }


# --------------------------------------------------
# Entity builder
# --------------------------------------------------

def build_entity(repo):
    """Convert a GitHub repository into an MCP entity."""

    owner = repo.get(
        "owner",
        {}
    )

    owner_login = owner.get(
        "login",
        ""
    )

    metadata = {
        "stars": repo.get(
            "stargazers_count",
            0
        ),

        "primary_language": repo.get(
            "language"
        ),

        "last_updated": repo.get(
            "updated_at"
        ),

        "owner": owner_login,

        "forks": repo.get(
            "forks_count",
            0
        ),
    }

    # --------------------------------------------------
    # MCP-specific metadata
    # --------------------------------------------------

    print(
        f"Enriching MCP metadata: "
        f"{repo.get('full_name', repo.get('name', ''))}"
    )

    enriched_metadata = enrich_mcp_metadata(
        repo,
        owner_login
    )

    metadata.update(
        enriched_metadata
    )

    return {
        "id": repo.get(
            "id"
        ),

        "entity_type": "mcp",

        "name": repo.get(
            "full_name",
            repo.get("name", "")
        ),

        "description": repo.get(
            "description"
        ) or "",

        "url": repo.get(
            "html_url",
            ""
        ),

        "categories": [
            "mcp",
            "model-context-protocol",
            "developer-tool",
        ],

        "source": {
            "name": "GitHub",
            "url": repo.get(
                "html_url",
                ""
            ),
        },

        "metadata": metadata,
    }


# --------------------------------------------------
# Deduplication
# --------------------------------------------------

def deduplicate_entities(
    entities
):
    """Remove duplicate MCP repositories by URL."""

    unique = {}

    for entity in entities:

        url = (
            entity.get(
                "url",
                ""
            )
            .rstrip("/")
        )

        if url:
            unique[url] = entity

    return list(
        unique.values()
    )


# --------------------------------------------------
# Save
# --------------------------------------------------

def save_entities(
    entities
):
    """Save MCP entities to JSON."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            entities,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Saved {len(entities)} MCP entities "
        f"to {OUTPUT_FILE}"
    )


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    """Run MCP discovery."""

    print(
        "Starting MCP discovery..."
    )

    entities = []

    for query in SEARCH_QUERIES:

        print(
            f"Searching GitHub MCP: {query}"
        )

        repositories = search_github(
            query
        )

        for repo in repositories:

            entity = build_entity(
                repo
            )

            entities.append(
                entity
            )

    entities = deduplicate_entities(
        entities
    )

    print(
        f"Unique MCP entities discovered: "
        f"{len(entities)}"
    )

    save_entities(
        entities
    )

    print(
        "MCP discovery completed successfully."
    )


if __name__ == "__main__":
    main()