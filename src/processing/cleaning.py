import re
from typing import Optional


def clean_text(text: Optional[str]) -> str:
    """
    Clean text by:
    - Handling missing values
    - Removing HTML tags
    - Removing excessive whitespace
    - Normalizing line breaks
    """

    if not text:
        return ""

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Replace line breaks and tabs with spaces
    text = re.sub(r"[\r\n\t]+", " ", text)

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def clean_entity(entity: dict) -> dict:
    """
    Clean text fields in a single entity.
    """

    entity["name"] = clean_text(entity.get("name"))
    entity["description"] = clean_text(
        entity.get("description")
    )

    return entity

if __name__ == "__main__":
    test_text = """
        <p>Artificial Intelligence</p>
        is    changing
        the world.
    """

    print(clean_text(test_text))