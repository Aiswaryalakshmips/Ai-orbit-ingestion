import json
from pathlib import Path

from src.processing.cleaning import clean_entity
from src.processing.normalization import normalize_entity_url
from src.processing.classifier import classify_entity
from src.processing.deduplication import deduplicate_entities
from src.validation.validator import validate_entities


# --------------------------------------------------
# Input files
# --------------------------------------------------

GITHUB_INPUT_FILE = Path(
    "data/entities.json"
)

HUGGINGFACE_INPUT_FILE = Path(
    "data/huggingface_models.json"
)

NEWS_INPUT_FILE = Path(
    "data/news.json"
)

YOUTUBE_INPUT_FILE = Path(
    "data/youtube.json"
)

MCP_INPUT_FILE = Path(
    "data/mcp.json"
)

COMPANY_INPUT_FILE = Path(
    "data/companies.json"
)

TOOLS_INPUT_FILE = Path(
    "data/tools.json"
)


# --------------------------------------------------
# Output file
# --------------------------------------------------

OUTPUT_FILE = Path(
    "data/entities_clean.json"
)


def load_entities(path: Path):
    """Load entities from a JSON file."""

    if not path.exists():

        print(
            f"Warning: Input file not found: {path}"
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
            f"Warning: Invalid JSON in {path}: "
            f"{error}"
        )

        return []

    except OSError as error:

        print(
            f"Warning: Could not read {path}: "
            f"{error}"
        )

        return []


def save_entities(
    entities,
    path: Path
):
    """Save processed entities to JSON."""

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            entities,
            file,
            indent=2,
            ensure_ascii=False
        )


def load_all_entities():
    """
    Load entities from all supported
    discovery sources.
    """

    # --------------------------------------------------
    # GitHub
    # --------------------------------------------------

    github_entities = load_entities(
        GITHUB_INPUT_FILE
    )

    print(
        f"GitHub entities: "
        f"{len(github_entities)}"
    )


    # --------------------------------------------------
    # Hugging Face
    # --------------------------------------------------

    huggingface_entities = load_entities(
        HUGGINGFACE_INPUT_FILE
    )

    print(
        f"Hugging Face models: "
        f"{len(huggingface_entities)}"
    )


    # --------------------------------------------------
    # News / RSS
    # --------------------------------------------------

    news_entities = load_entities(
        NEWS_INPUT_FILE
    )

    print(
        f"News entities: "
        f"{len(news_entities)}"
    )


    # --------------------------------------------------
    # YouTube
    # --------------------------------------------------

    youtube_entities = load_entities(
        YOUTUBE_INPUT_FILE
    )

    print(
        f"YouTube entities: "
        f"{len(youtube_entities)}"
    )


    # --------------------------------------------------
    # MCP
    # --------------------------------------------------

    mcp_entities = load_entities(
        MCP_INPUT_FILE
    )

    print(
        f"MCP entities: "
        f"{len(mcp_entities)}"
    )


    # --------------------------------------------------
    # Companies
    # --------------------------------------------------

    company_entities = load_entities(
        COMPANY_INPUT_FILE
    )

    print(
        f"Company entities: "
        f"{len(company_entities)}"
    )


    # --------------------------------------------------
    # AI Tools
    # --------------------------------------------------

    tool_entities = load_entities(
        TOOLS_INPUT_FILE
    )

    print(
        f"AI Tool entities: "
        f"{len(tool_entities)}"
    )


    # --------------------------------------------------
    # Combine all sources
    # --------------------------------------------------

    all_entities = (
        github_entities
        + huggingface_entities
        + news_entities
        + youtube_entities
        + mcp_entities
        + company_entities
        + tool_entities
    )

    print(
        f"Total discovered entities: "
        f"{len(all_entities)}"
    )

    return all_entities


def process_entities(entities):
    """
    Run the core processing pipeline:

    Cleaning
    → URL Normalization
    → Classification
    → Deduplication
    """

    processed_entities = []

    for entity in entities:

        try:

            # --------------------------------------------------
            # 1. Cleaning
            # --------------------------------------------------

            entity = clean_entity(
                entity
            )


            # --------------------------------------------------
            # 2. URL normalization
            # --------------------------------------------------

            entity = normalize_entity_url(
                entity
            )


            # --------------------------------------------------
            # 3. Classification
            # --------------------------------------------------

            entity = classify_entity(
                entity
            )


            # --------------------------------------------------
            # Add processed entity
            # --------------------------------------------------

            processed_entities.append(
                entity
            )

        except Exception as error:

            name = entity.get(
                "name",
                "Unknown"
            )

            print(
                f"Processing failed for "
                f"{name}: {error}"
            )


    # --------------------------------------------------
    # 4. Deduplication
    # --------------------------------------------------

    unique_entities = deduplicate_entities(
        processed_entities
    )

    return unique_entities


def main():
    """Run the complete AI Orbit ingestion pipeline."""

    print(
        "Starting AI Orbit ingestion pipeline..."
    )


    # --------------------------------------------------
    # 1. Load data
    # --------------------------------------------------

    entities = load_all_entities()


    # --------------------------------------------------
    # 2. Processing
    # --------------------------------------------------

    processed_entities = process_entities(
        entities
    )

    print(
        f"After deduplication: "
        f"{len(processed_entities)} entities."
    )


    # --------------------------------------------------
    # 3. Validation
    # --------------------------------------------------

    validation_result = validate_entities(
        processed_entities
    )

    valid_count = validation_result[
        "valid"
    ]

    invalid_count = validation_result[
        "invalid"
    ]

    print(
        f"Validation: "
        f"{valid_count} valid, "
        f"{invalid_count} invalid."
    )


    # --------------------------------------------------
    # 4. Report validation errors
    # --------------------------------------------------

    if invalid_count > 0:

        print(
            "\nValidation errors:"
        )

        for item in validation_result[
            "invalid_entities"
        ]:

            entity = item["entity"]

            name = entity.get(
                "name",
                "Unknown"
            )

            errors = item["errors"]

            print(
                f"- {name}: "
                f"{', '.join(errors)}"
            )


    # --------------------------------------------------
    # 5. Save valid entities
    # --------------------------------------------------

    save_entities(
        validation_result[
            "valid_entities"
        ],
        OUTPUT_FILE
    )

    print(
        f"Saved processed data to "
        f"{OUTPUT_FILE}"
    )

    print(
        "Pipeline completed successfully."
    )


if __name__ == "__main__":
    main()