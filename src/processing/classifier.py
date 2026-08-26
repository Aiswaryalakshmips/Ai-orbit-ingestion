"""
Rule-based entity classification for the AI Orbit ingestion pipeline.
"""

from typing import Dict


def classify_entity(entity: Dict) -> Dict:
    """
    Classify an entity based on its existing fields,
    source information, categories, and metadata.
    """

    entity = dict(entity)

    name = str(entity.get("name", "")).lower()
    description = str(
        entity.get("description", "")
    ).lower()

    url = str(
        entity.get("url", "")
    ).lower()

    categories = [
        str(category).lower()
        for category in entity.get(
            "categories", []
        )
    ]

    text = " ".join(
        [
            name,
            description,
            url,
            " ".join(categories),
        ]
    )

    current_type = entity.get(
        "entity_type",
        ""
    ).lower()

    # --------------------------------------------------
    # Preserve strong source-specific classifications
    # --------------------------------------------------

    if current_type in {
        "repository",
        "model",
        "news",
        "video",
    }:
        entity["entity_type"] = current_type
        return entity

    # --------------------------------------------------
    # MCP
    # --------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "mcp server",
            "model context protocol",
            "mcp-server",
        ]
    ):
        entity["entity_type"] = "mcp"
        return entity

    # --------------------------------------------------
    # Robots
    # --------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "robot",
            "robotics",
            "humanoid",
            "autonomous robot",
        ]
    ):
        entity["entity_type"] = "robot"
        return entity

    # --------------------------------------------------
    # Devices / Hardware
    # --------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "ai hardware",
            "ai device",
            "gpu",
            "edge device",
            "ai chip",
            "ai computer",
        ]
    ):
        entity["entity_type"] = "device"
        return entity

    # --------------------------------------------------
    # Companies
    # --------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "company",
            "startup",
            "headquarters",
            "founded",
            "inc.",
            "incorporated",
        ]
    ):
        entity["entity_type"] = "company"
        return entity

    # --------------------------------------------------
    # Creative AI
    # --------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "image generation",
            "video generation",
            "music generation",
            "creative ai",
            "generative art",
        ]
    ):
        entity["entity_type"] = "creative"
        return entity

    # --------------------------------------------------
    # Personal AI assistants
    # --------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "personal ai",
            "ai assistant",
            "personal assistant",
            "virtual assistant",
        ]
    ):
        entity["entity_type"] = "personal"
        return entity

    # --------------------------------------------------
    # Tools / Applications
    # --------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "ai tool",
            "ai application",
            "ai platform",
            "ai software",
            "developer tool",
        ]
    ):
        entity["entity_type"] = "tool"
        return entity

    # --------------------------------------------------
    # Tasks
    # --------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "task",
            "summarization",
            "translation",
            "classification",
            "object detection",
            "text generation",
            "image generation",
        ]
    ):
        entity["entity_type"] = "task"
        return entity

    # --------------------------------------------------
    # Collections
    # --------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "collection",
            "curated list",
            "awesome list",
            "directory",
        ]
    ):
        entity["entity_type"] = "collection"
        return entity

    # --------------------------------------------------
    # Default classification
    # --------------------------------------------------

    if current_type:
        entity["entity_type"] = current_type
    else:
        entity["entity_type"] = "tool"

    return entity