import json
from pathlib import Path
from typing import List, Dict
from urllib.parse import urlparse


INPUT_FILE = Path("data/entities_clean.json")


REQUIRED_FIELDS = [
    "id",
    "entity_type",
    "name",
    "url",
    "source",
]


def is_valid_url(url: str) -> bool:
    """Check whether a URL has a valid HTTP/HTTPS structure."""

    if not url:
        return False

    try:
        parsed = urlparse(str(url))

        return parsed.scheme in (
            "http",
            "https",
        ) and bool(parsed.netloc)

    except Exception:
        return False


def validate_entity(entity: Dict) -> List[str]:
    """
    Validate a single entity.

    Returns a list of validation errors.
    An empty list means the entity is valid.
    """

    errors = []

    # Required fields
    for field in REQUIRED_FIELDS:
        if not entity.get(field):
            errors.append(
                f"Missing required field: {field}"
            )

    # Name validation
    if entity.get("name"):
        if not isinstance(entity["name"], str):
            errors.append(
                "Entity name must be a string"
            )
        elif not entity["name"].strip():
            errors.append(
                "Entity name is empty"
            )

    # URL validation
    if entity.get("url"):
        if not is_valid_url(entity["url"]):
            errors.append(
                "Invalid entity URL"
            )

    # Source validation
    source = entity.get("source")

    if source:
        if not isinstance(source, dict):
            errors.append(
                "Source must be an object"
            )
        else:
            if not source.get("name"):
                errors.append(
                    "Missing source name"
                )

            if not is_valid_url(
                source.get("url", "")
            ):
                errors.append(
                    "Invalid source URL"
                )

    return errors


def validate_entities(
    entities: List[Dict],
) -> Dict:
    """
    Validate all entities and return a summary.
    """

    valid_entities = []
    invalid_entities = []

    seen_ids = set()

    for entity in entities:

        entity_id = entity.get("id")

        errors = validate_entity(entity)

        # Duplicate ID detection
        if entity_id in seen_ids:
            errors.append(
                "Duplicate entity ID"
            )

        if entity_id:
            seen_ids.add(entity_id)

        if errors:
            invalid_entities.append(
                {
                    "entity": entity,
                    "errors": errors,
                }
            )
        else:
            valid_entities.append(entity)

    return {
        "total": len(entities),
        "valid": len(valid_entities),
        "invalid": len(invalid_entities),
        "valid_entities": valid_entities,
        "invalid_entities": invalid_entities,
    }


def load_entities():
    """Load entities from the cleaned dataset."""

    if not INPUT_FILE.exists():
        print(
            f"Input file not found: {INPUT_FILE}"
        )
        return []

    try:
        with INPUT_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(data, list):
            print(
                "Error: entities_clean.json must contain a list."
            )
            return []

        return data

    except json.JSONDecodeError as error:
        print(
            f"Invalid JSON: {error}"
        )
        return []

    except OSError as error:
        print(
            f"Could not read {INPUT_FILE}: {error}"
        )
        return []


def main():
    """Validate the cleaned entity dataset."""

    print(
        "Starting entity validation..."
    )

    entities = load_entities()

    if not entities:
        print(
            "No entities found."
        )
        return

    result = validate_entities(
        entities
    )

    print(
        f"Total: {result['total']}"
    )

    print(
        f"Valid: {result['valid']}"
    )

    print(
        f"Invalid: {result['invalid']}"
    )

    # Show invalid entities and their errors
    if result["invalid_entities"]:

        print(
            "\nInvalid entities:"
        )

        for item in result[
            "invalid_entities"
        ]:

            entity = item["entity"]

            print(
                f"\n- {entity.get('name', '<unnamed>')}"
            )

            print(
                f"  ID: {entity.get('id', '<missing>')}"
            )

            for error in item["errors"]:
                print(
                    f"  Error: {error}"
                )

    else:
        print(
            "\nAll entities passed validation."
        )


if __name__ == "__main__":
    main()