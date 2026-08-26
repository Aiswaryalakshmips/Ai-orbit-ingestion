from typing import List, Dict
from rapidfuzz import fuzz


def normalize_name(name: str) -> str:
    """
    Create a normalized version of an entity name
    for comparison.
    """

    if not name:
        return ""

    return "".join(
        char.lower()
        for char in name
        if char.isalnum()
    )


def are_duplicates(
    entity_a: dict,
    entity_b: dict,
    threshold: int = 90,
) -> bool:
    """
    Determine whether two entities represent
    the same real-world entity.
    """

    # Strongest signal: same URL
    url_a = entity_a.get("url", "")
    url_b = entity_b.get("url", "")

    if url_a and url_b and url_a == url_b:
        return True

    # Compare normalized names
    name_a = normalize_name(
        entity_a.get("name", "")
    )
    name_b = normalize_name(
        entity_b.get("name", "")
    )

    if not name_a or not name_b:
        return False

    similarity = fuzz.ratio(
        name_a,
        name_b
    )

    return similarity >= threshold


def deduplicate_entities(
    entities: List[dict],
) -> List[dict]:
    """
    Remove duplicate entities while preserving
    the first occurrence.
    """

    unique_entities = []

    for entity in entities:
        duplicate_found = False

        for existing in unique_entities:
            if are_duplicates(
                entity,
                existing
            ):
                duplicate_found = True
                break

        if not duplicate_found:
            unique_entities.append(entity)

    return unique_entities


if __name__ == "__main__":
    test_entities = [
        {
            "name": "OpenAI",
            "url": "https://openai.com",
        },
        {
            "name": "Open AI",
            "url": "https://openai.com/",
        },
        {
            "name": "Anthropic",
            "url": "https://anthropic.com",
        },
    ]

    result = deduplicate_entities(
        test_entities
    )

    print(
        f"Input entities: {len(test_entities)}"
    )

    print(
        f"Unique entities: {len(result)}"
    )

    for entity in result:
        print(entity["name"])