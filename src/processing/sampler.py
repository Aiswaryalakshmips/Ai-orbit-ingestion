"""
Relationship-aware dataset sampler for the AI Orbit ingestion pipeline.

Reduces the dataset to a representative 250-300 record range while
prioritizing entities that participate in relationships.
"""

import json
from pathlib import Path
from collections import defaultdict


ENTITIES_FILE = Path(
    "data/entities_clean.json"
)

RELATIONSHIPS_FILE = Path(
    "data/relationships.json"
)

OUTPUT_FILE = Path(
    "data/entities_sampled.json"
)


# --------------------------------------------------
# Target distribution
# --------------------------------------------------

TARGET_COUNTS = {
    "repository": 55,
    "video": 45,
    "mcp": 40,
    "model": 40,
    "tool": 40,
    "news": 20,
    "company": 11,
    "creative": 11,
    "personal": 6,
    "robot": 3,
}


# --------------------------------------------------
# Load JSON
# --------------------------------------------------

def load_json(path):
    """Load a JSON file safely."""

    if not path.exists():

        print(
            f"Input file not found: {path}"
        )

        return []

    try:

        with path.open(
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if not isinstance(data, list):

                print(
                    f"Warning: Expected a list in "
                    f"{path}"
                )

                return []

            return data

    except json.JSONDecodeError as error:

        print(
            f"Invalid JSON in {path}: {error}"
        )

        return []


# --------------------------------------------------
# Relationship indexing
# --------------------------------------------------

def build_relationship_index(relationships):
    """
    Count how many relationships each entity participates in.
    """

    relationship_score = defaultdict(int)

    for relationship in relationships:

        source_id = str(
            relationship.get("source_id")
        )

        target_id = str(
            relationship.get("target_id")
        )

        if source_id:
            relationship_score[source_id] += 1

        if target_id:
            relationship_score[target_id] += 1

    return relationship_score


# --------------------------------------------------
# Sampling
# --------------------------------------------------

def sample_entities(
    entities,
    relationships
):
    """
    Select a representative dataset.

    Entities participating in relationships receive
    higher priority than isolated entities.
    """

    relationship_score = (
        build_relationship_index(
            relationships
        )
    )

    grouped = defaultdict(list)

    for entity in entities:

        entity_type = entity.get(
            "entity_type",
            "unknown"
        )

        grouped[entity_type].append(
            entity
        )

    selected = []

    for entity_type, target_count in TARGET_COUNTS.items():

        candidates = grouped.get(
            entity_type,
            []
        )

        if not candidates:
            continue

        # --------------------------------------------------
        # Sort by relationship participation.
        # Higher relationship count = higher priority.
        # --------------------------------------------------

        candidates = sorted(
            candidates,
            key=lambda entity: (
                relationship_score.get(
                    str(entity.get("id")),
                    0
                ),
                str(
                    entity.get(
                        "name",
                        ""
                    )
                ).lower()
            ),
            reverse=True
        )

        selected_count = min(
            target_count,
            len(candidates)
        )

        selected.extend(
            candidates[:selected_count]
        )

        print(
            f"{entity_type}: "
            f"{len(candidates)} available → "
            f"{selected_count} selected"
        )

    # --------------------------------------------------
    # Preserve unexpected categories
    # --------------------------------------------------

    selected_types = set(
        TARGET_COUNTS.keys()
    )

    for entity_type, candidates in grouped.items():

        if entity_type in selected_types:
            continue

        # Keep small unknown categories instead of
        # silently deleting them.

        selected.extend(
            candidates
        )

        print(
            f"{entity_type}: "
            f"{len(candidates)} preserved"
        )

    # --------------------------------------------------
    # Remove duplicate IDs
    # --------------------------------------------------

    unique = {}

    for entity in selected:

        entity_id = str(
            entity.get("id")
        )

        if entity_id:
            unique[entity_id] = entity

    return list(
        unique.values()
    )


# --------------------------------------------------
# Save
# --------------------------------------------------

def save_entities(entities):

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
        f"\nSaved {len(entities)} sampled "
        f"entities to {OUTPUT_FILE}"
    )


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print(
        "Starting relationship-aware dataset sampling..."
    )

    entities = load_json(
        ENTITIES_FILE
    )

    relationships = load_json(
        RELATIONSHIPS_FILE
    )

    print(
        f"Loaded {len(entities)} entities."
    )

    print(
        f"Loaded {len(relationships)} relationships."
    )

    sampled = sample_entities(
        entities,
        relationships
    )

    save_entities(
        sampled
    )

    print(
        "Sampling completed successfully."
    )


if __name__ == "__main__":
    main()