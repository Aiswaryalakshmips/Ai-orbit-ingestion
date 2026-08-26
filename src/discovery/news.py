import json
from pathlib import Path
from uuid import uuid5, NAMESPACE_URL

import feedparser

from src.models import Entity, Source


RSS_FEEDS = [
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
    },
]


OUTPUT_FILE = Path("data/news.json")


def fetch_feed(feed):
    """Fetch and parse an RSS feed."""

    parsed = feedparser.parse(feed["url"])

    if parsed.bozo:
        print(
            f"Warning: RSS feed may have parsing issues: "
            f"{feed['name']}"
        )

    return parsed.entries


def convert_to_entities(entries, source_name, source_url):
    """Convert RSS articles into Orbit entities."""

    entities = []

    for entry in entries:

        title = entry.get("title", "").strip()
        url = entry.get("link", "").strip()

        if not title or not url:
            continue

        description = (
            entry.get("summary")
            or entry.get("description")
            or ""
        )

        entity = Entity(
            id=uuid5(
                NAMESPACE_URL,
                url
            ),
            entity_type="news",
            name=title,
            description=description,
            url=url,
            categories=[
                "AI",
                "News",
            ],
            source=Source(
                name=source_name,
                url=source_url,
            ),
            metadata={
                "published": entry.get(
                    "published",
                    None
                ),
            },
        )

        entities.append(entity)

    return entities


def save_entities(entities):
    """Save news entities to JSON."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    data = [
        entity.model_dump(mode="json")
        for entity in entities
    ]

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Saved {len(data)} news entities "
        f"to {OUTPUT_FILE}"
    )


def main():

    print(
        "Starting News/RSS discovery..."
    )

    all_entities = {}
    
    for feed in RSS_FEEDS:

        print(
            f"Fetching: {feed['name']}"
        )

        try:

            entries = fetch_feed(feed)

            entities = convert_to_entities(
                entries,
                feed["name"],
                feed["url"],
            )

            for entity in entities:
                all_entities[str(entity.id)] = entity

        except Exception as error:

            print(
                f"Failed to fetch "
                f"{feed['name']}: {error}"
            )

    entities = list(
        all_entities.values()
    )

    print(
        f"Unique news discovered: "
        f"{len(entities)}"
    )

    save_entities(entities)


if __name__ == "__main__":
    main()