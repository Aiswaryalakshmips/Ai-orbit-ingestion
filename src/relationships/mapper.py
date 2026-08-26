"""
Relationship extraction for the AI Orbit ingestion pipeline.

Supported relationships:
- Company -> develops -> Tool / Model
- Repository -> implements -> Model
- MCP -> integrates_with -> Tool / Repository
- Device -> runs -> Model
- Tool -> solves -> Task

The mapper uses explicit metadata and conservative text matching
to reduce false-positive relationships.
"""

import json
import re
from pathlib import Path


INPUT_FILE = Path("data/entities_clean.json")
OUTPUT_FILE = Path("data/relationships.json")


# --------------------------------------------------
# Load entities
# --------------------------------------------------

def load_entities():
    """Load cleaned entities from JSON."""

    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return []

    try:
        with INPUT_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            print("Warning: entities_clean.json must contain a list.")
            return []

        return data

    except json.JSONDecodeError as error:
        print(f"Invalid JSON: {error}")
        return []

    except OSError as error:
        print(f"Could not read {INPUT_FILE}: {error}")
        return []


# --------------------------------------------------
# Text helpers
# --------------------------------------------------

def normalize(text):
    """Normalize text for reliable matching."""

    if not text:
        return ""

    text = str(text).lower()
    text = re.sub(r"[-_/.,:;(){}\[\]]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def tokenize(text):
    """Return meaningful normalized tokens."""

    stop_words = {
        "the",
        "and",
        "for",
        "with",
        "from",
        "this",
        "that",
        "into",
        "using",
        "based",
        "official",
        "project",
        "repository",
        "github",
        "model",
        "models",
        "tool",
        "tools",
        "ai",
        "open",
    }

    return {
        token
        for token in normalize(text).split()
        if len(token) >= 3
        and token not in stop_words
    }


def entity_text(entity):
    """Build searchable text from an entity."""

    metadata = entity.get("metadata") or {}

    values = [
        entity.get("name", ""),
        entity.get("description", ""),
        entity.get("url", ""),
    ]

    categories = entity.get("categories") or []
    values.extend(categories)

    if isinstance(metadata, dict):
        for key in (
            "owner",
            "provider",
            "organization",
            "company",
            "author",
            "developer",
            "publisher",
            "creator",
            "manufacturer",
            "framework",
            "base_model",
            "pipeline_tag",
            "task",
        ):
            values.append(metadata.get(key, ""))

    return normalize(
        " ".join(
            str(value)
            for value in values
            if value
        )
    )


def get_metadata(entity):
    """Safely return entity metadata."""

    metadata = entity.get("metadata")

    if isinstance(metadata, dict):
        return metadata

    return {}


def names_match(name_a, name_b):
    """
    Conservative name matching.

    Requires either:
    - exact normalized names, or
    - strong token overlap.
    """

    a = normalize(name_a)
    b = normalize(name_b)

    if not a or not b:
        return False

    if a == b:
        return True

    tokens_a = tokenize(a)
    tokens_b = tokenize(b)

    if not tokens_a or not tokens_b:
        return False

    intersection = tokens_a & tokens_b
    smaller = min(
        len(tokens_a),
        len(tokens_b),
    )

    if smaller == 0:
        return False

    return (
        len(intersection) >= smaller
        and len(intersection) >= 2
    )


def explicit_entity_reference(entity, target):
    """
    Check whether an entity explicitly references another entity
    through metadata.
    """

    target_name = normalize(
        target.get("name", "")
    )

    if not target_name:
        return False

    metadata = get_metadata(entity)

    explicit_fields = [
        "owner",
        "provider",
        "organization",
        "company",
        "developer",
        "publisher",
        "creator",
        "manufacturer",
        "author",
        "maintainer",
        "base_model",
        "framework",
        "tool",
        "tools",
        "model",
        "models",
        "integrates_with",
        "integrations",
        "supports",
        "supported_models",
    ]

    for field in explicit_fields:

        value = metadata.get(field)

        if isinstance(value, list):

            for item in value:

                if names_match(
                    item,
                    target_name,
                ):
                    return True

        elif isinstance(value, dict):

            for item in value.values():

                if names_match(
                    item,
                    target_name,
                ):
                    return True

        elif value:

            if names_match(
                value,
                target_name,
            ):
                return True

    return False


def text_contains_entity(text, entity):
    """
    Check whether an entity name appears as a meaningful phrase
    in text.
    """

    text = normalize(text)
    name = normalize(
        entity.get("name", "")
    )

    if not text or not name:
        return False

    return bool(
        re.search(
            rf"\b{re.escape(name)}\b",
            text,
        )
    )


# --------------------------------------------------
# Relationship creation
# --------------------------------------------------

def create_relationship(
    source,
    target,
    relationship_type,
    evidence=None,
):
    """Create a relationship record."""

    relationship = {
        "source_id": str(source["id"]),
        "source_name": source["name"],
        "source_type": source["entity_type"],
        "relationship": relationship_type,
        "target_id": str(target["id"]),
        "target_name": target["name"],
        "target_type": target["entity_type"],
    }

    if evidence:
        relationship["evidence"] = evidence

    return relationship


# --------------------------------------------------
# Company relationships
# --------------------------------------------------

def map_company_relationships(
    companies,
    tools,
    models,
):
    """
    Map Company -> develops -> Tool / Model.

    A company is not assumed to develop every model hosted
    on its platform.
    """

    relationships = []

    for company in companies:

        company_name = normalize(
            company.get("name", "")
        )

        company_metadata = get_metadata(
            company
        )

        aliases = {
            company_name,
            normalize(
                company_metadata.get(
                    "legal_name"
                )
            ),
            normalize(
                company_metadata.get(
                    "slug"
                )
            ),
        }

        aliases = {
            alias
            for alias in aliases
            if alias
        }

        for target in tools + models:

            target_metadata = get_metadata(
                target
            )

            explicit_values = {
                normalize(
                    target_metadata.get(
                        "provider"
                    )
                ),
                normalize(
                    target_metadata.get(
                        "company"
                    )
                ),
                normalize(
                    target_metadata.get(
                        "developer"
                    )
                ),
                normalize(
                    target_metadata.get(
                        "owner"
                    )
                ),
                normalize(
                    target_metadata.get(
                        "organization"
                    )
                ),
            }

            explicit_values.discard("")

            if aliases & explicit_values:

                relationships.append(
                    create_relationship(
                        company,
                        target,
                        "develops",
                        "explicit metadata reference",
                    )
                )

                continue

            if target.get(
                "entity_type"
            ) == "tool":

                target_text = entity_text(
                    target
                )

                if any(
                    alias in target_text
                    for alias in aliases
                    if len(alias) >= 4
                ):

                    relationships.append(
                        create_relationship(
                            company,
                            target,
                            "develops",
                            "company name referenced in tool metadata/text",
                        )
                    )

    return relationships


# --------------------------------------------------
# Repository -> Model
# --------------------------------------------------

def map_repository_model_relationships(
    repositories,
    models,
):
    """
    Map Repository -> implements -> Model.

    Uses explicit metadata first, then conservative model-name
    matching.
    """

    relationships = []

    for repository in repositories:

        repo_text = entity_text(
            repository
        )

        for model in models:

            if explicit_entity_reference(
                repository,
                model,
            ):

                relationships.append(
                    create_relationship(
                        repository,
                        model,
                        "implements",
                        "explicit repository metadata reference",
                    )
                )

                continue

            model_name = normalize(
                model.get("name", "")
            )

            if not model_name:
                continue

            if text_contains_entity(
                repo_text,
                model,
            ):

                relationships.append(
                    create_relationship(
                        repository,
                        model,
                        "implements",
                        "model name explicitly referenced",
                    )
                )

                continue

            model_parts = [
                part
                for part in model_name.split()
                if len(part) >= 4
            ]

            if len(model_parts) >= 2:

                matched = sum(
                    1
                    for part in model_parts
                    if re.search(
                        rf"\b{re.escape(part)}\b",
                        repo_text,
                    )
                )

                if matched >= 2:

                    relationships.append(
                        create_relationship(
                            repository,
                            model,
                            "implements",
                            "strong model-name overlap",
                        )
                    )

    return relationships


# --------------------------------------------------
# MCP relationships
# --------------------------------------------------

def map_mcp_relationships(
    mcp_servers,
    tools,
    repositories,
):
    """
    Map MCP -> integrates_with -> Tool / Repository.
    """

    relationships = []

    for mcp in mcp_servers:

        mcp_text = entity_text(mcp)

        # MCP -> Tool
        for tool in tools:

            if explicit_entity_reference(
                mcp,
                tool,
            ):

                relationships.append(
                    create_relationship(
                        mcp,
                        tool,
                        "integrates_with",
                        "explicit MCP integration metadata",
                    )
                )

                continue

            if text_contains_entity(
                mcp_text,
                tool,
            ):

                relationships.append(
                    create_relationship(
                        mcp,
                        tool,
                        "integrates_with",
                        "tool name explicitly referenced",
                    )
                )

        # MCP -> Repository
        for repository in repositories:

            if explicit_entity_reference(
                mcp,
                repository,
            ):

                relationships.append(
                    create_relationship(
                        mcp,
                        repository,
                        "integrates_with",
                        "explicit MCP repository reference",
                    )
                )

                continue

            if text_contains_entity(
                mcp_text,
                repository,
            ):

                if normalize(
                    repository.get("name", "")
                ) == normalize(
                    mcp.get("name", "")
                ):
                    continue

                relationships.append(
                    create_relationship(
                        mcp,
                        repository,
                        "integrates_with",
                        "repository name explicitly referenced",
                    )
                )

    return relationships


# --------------------------------------------------
# Device -> Model
# --------------------------------------------------

def map_device_model_relationships(
    devices,
    models,
):
    """Map Device -> runs -> Model."""

    relationships = []

    for device in devices:

        device_text = entity_text(
            device
        )

        for model in models:

            if explicit_entity_reference(
                device,
                model,
            ):

                relationships.append(
                    create_relationship(
                        device,
                        model,
                        "runs",
                        "explicit device/model metadata",
                    )
                )

                continue

            if text_contains_entity(
                device_text,
                model,
            ):

                relationships.append(
                    create_relationship(
                        device,
                        model,
                        "runs",
                        "model explicitly referenced",
                    )
                )

    return relationships


# --------------------------------------------------
# Tool -> Task
# --------------------------------------------------

def map_tool_task_relationships(
    tools,
    tasks,
):
    """Map Tool -> solves -> Task."""

    relationships = []

    for tool in tools:

        tool_text = entity_text(
            tool
        )

        for task in tasks:

            task_name = normalize(
                task.get("name", "")
            )

            if not task_name:
                continue

            if explicit_entity_reference(
                tool,
                task,
            ):

                relationships.append(
                    create_relationship(
                        tool,
                        task,
                        "solves",
                        "explicit tool/task metadata",
                    )
                )

                continue

            if text_contains_entity(
                tool_text,
                task,
            ):

                relationships.append(
                    create_relationship(
                        tool,
                        task,
                        "solves",
                        "task explicitly referenced",
                    )
                )

    return relationships


# --------------------------------------------------
# Main relationship extraction
# --------------------------------------------------

def extract_relationships(entities):
    """Extract all supported ecosystem relationships."""

    companies = [
        entity
        for entity in entities
        if entity.get("entity_type")
        == "company"
    ]

    tools = [
        entity
        for entity in entities
        if entity.get("entity_type")
        == "tool"
    ]

    models = [
        entity
        for entity in entities
        if entity.get("entity_type")
        == "model"
    ]

    repositories = [
        entity
        for entity in entities
        if entity.get("entity_type")
        == "repository"
    ]

    mcp_servers = [
        entity
        for entity in entities
        if entity.get("entity_type")
        == "mcp"
    ]

    devices = [
        entity
        for entity in entities
        if entity.get("entity_type")
        == "device"
    ]

    tasks = [
        entity
        for entity in entities
        if entity.get("entity_type")
        == "task"
    ]

    relationships = []

    relationships.extend(
        map_company_relationships(
            companies,
            tools,
            models,
        )
    )

    relationships.extend(
        map_repository_model_relationships(
            repositories,
            models,
        )
    )

    relationships.extend(
        map_mcp_relationships(
            mcp_servers,
            tools,
            repositories,
        )
    )

    relationships.extend(
        map_device_model_relationships(
            devices,
            models,
        )
    )

    relationships.extend(
        map_tool_task_relationships(
            tools,
            tasks,
        )
    )

    # --------------------------------------------------
    # Deduplicate relationships
    # --------------------------------------------------

    unique = {}

    for relationship in relationships:

        key = (
            str(relationship["source_id"]),
            relationship["relationship"],
            str(relationship["target_id"]),
        )

        unique[key] = relationship

    return list(unique.values())


# --------------------------------------------------
# Save
# --------------------------------------------------

def save_relationships(relationships):
    """Save relationships to JSON."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            relationships,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"Saved {len(relationships)} relationships "
        f"to {OUTPUT_FILE}"
    )


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print(
        "Starting relationship extraction..."
    )

    entities = load_entities()

    print(
        f"Loaded {len(entities)} entities."
    )

    relationships = extract_relationships(
        entities
    )

    print(
        f"Relationships found: "
        f"{len(relationships)}"
    )

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    relationship_counts = {}

    for relationship in relationships:

        relationship_type = relationship[
            "relationship"
        ]

        relationship_counts[
            relationship_type
        ] = relationship_counts.get(
            relationship_type,
            0,
        ) + 1

    print(
        "\nRelationship summary:"
    )

    expected_types = [
        "develops",
        "implements",
        "integrates_with",
        "runs",
        "solves",
    ]

    for relationship_type in expected_types:

        print(
            f"- {relationship_type}: "
            f"{relationship_counts.get(relationship_type, 0)}"
        )

    save_relationships(
        relationships
    )


if __name__ == "__main__":
    main()

