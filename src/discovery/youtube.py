import json
import os
from pathlib import Path
from uuid import uuid5, NAMESPACE_URL

import requests
from dotenv import load_dotenv


# --------------------------------------------------
# Configuration
# --------------------------------------------------

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

YOUTUBE_API_URL = (
    "https://www.googleapis.com/youtube/v3/search"
)

OUTPUT_FILE = Path("data/youtube.json")

SEARCH_QUERIES = [
    "artificial intelligence",
    "generative AI",
    "machine learning",
    "large language models",
    "AI agents",
    "MCP server",
    "computer vision",
    "natural language processing",
]


# --------------------------------------------------
# YouTube API
# --------------------------------------------------

def search_videos(query: str, limit: int = 10):
    """Search YouTube for AI-related videos."""

    if not YOUTUBE_API_KEY:
        raise ValueError(
            "YOUTUBE_API_KEY is not set in .env"
        )

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": limit,
        "order": "relevance",
        "key": YOUTUBE_API_KEY,
    }

    response = requests.get(
        YOUTUBE_API_URL,
        params=params,
        timeout=20,
    )

    response.raise_for_status()

    data = response.json()

    return data.get("items", [])


# --------------------------------------------------
# Entity Conversion
# --------------------------------------------------

def convert_to_entities(videos):
    """Convert YouTube videos into Orbit entities."""

    entities = []

    for video in videos:

        video_id = (
            video
            .get("id", {})
            .get("videoId")
        )

        snippet = video.get(
            "snippet",
            {}
        )

        if not video_id:
            continue

        title = snippet.get(
            "title",
            "Unknown YouTube Video"
        )

        description = snippet.get(
            "description",
            ""
        )

        channel_title = snippet.get(
            "channelTitle",
            ""
        )

        published_at = snippet.get(
            "publishedAt"
        )

        video_url = (
            f"https://www.youtube.com/watch?v={video_id}"
        )

        metadata = {
            "platform": "YouTube",
            "video_id": video_id,
            "channel": channel_title,
            "published_at": published_at,
        }

        entity = {
            "id": str(
                uuid5(
                    NAMESPACE_URL,
                    video_url
                )
            ),
            "entity_type": "video",
            "name": title,
            "description": description,
            "url": video_url,
            "categories": [
                "AI",
                "Video",
                "Technology",
            ],
            "source": {
                "name": "YouTube",
                "url": video_url,
            },
            "metadata": metadata,
        }

        entities.append(entity)

    return entities


# --------------------------------------------------
# Save
# --------------------------------------------------

def save_entities(entities):
    """Save YouTube entities to JSON."""

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
        f"Saved {len(entities)} YouTube entities "
        f"to {OUTPUT_FILE}"
    )


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print(
        "Starting YouTube discovery..."
    )

    if not YOUTUBE_API_KEY:

        print(
            "Error: YOUTUBE_API_KEY is missing "
            "from .env"
        )

        return

    all_videos = {}

    for query in SEARCH_QUERIES:

        print(
            f"Searching YouTube: {query}"
        )

        try:

            videos = search_videos(
                query,
                limit=10
            )

            for video in videos:

                video_id = (
                    video
                    .get("id", {})
                    .get("videoId")
                )

                if video_id:
                    all_videos[
                        video_id
                    ] = video

        except requests.RequestException as error:

            print(
                f"Request failed for "
                f"'{query}': {error}"
            )

        except Exception as error:

            print(
                f"Search failed for "
                f"'{query}': {error}"
            )

    print(
        f"Unique videos discovered: "
        f"{len(all_videos)}"
    )

    entities = convert_to_entities(
        list(all_videos.values())
    )

    save_entities(entities)


if __name__ == "__main__":
    main()