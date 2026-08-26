import json
from pathlib import Path
from uuid import uuid5, NAMESPACE_URL

import requests

from src.models import Entity, Source


HUGGINGFACE_API_URL = "https://huggingface.co/api/models"

SEARCH_QUERIES = [
    "text-generation",
    "text-to-image",
    "image-classification",
    "text-classification",
    "automatic-speech-recognition",
]


def search_models(query: str, limit: int = 10):
    """Fetch models from Hugging Face."""

    params = {
        "search": query,
        "limit": limit,
        "sort": "downloads",
        "direction": -1,
    }

    response = requests.get(
        HUGGINGFACE_API_URL,
        params=params,
        timeout=20,
    )

    response.raise_for_status()

    return response.json()


def get_model_details(model_id: str):
    """
    Fetch detailed metadata for a Hugging Face model.

    Missing metadata is handled gracefully.
    """

    url = (
        f"https://huggingface.co/api/models/"
        f"{model_id}"
    )

    try:
        response = requests.get(
            url,
            timeout=15,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:
        print(
            f"Metadata request failed for "
            f"{model_id}: {error}"
        )

        return {}


def extract_modalities(model: dict):
    """
    Extract model modalities from available metadata.

    Hugging Face may expose different metadata
    depending on the model.
    """

    modalities = []

    pipeline_tag = model.get(
        "pipeline_tag"
    )

    if pipeline_tag:
        modality_map = {
            "text-generation": "text",
            "text-classification": "text",
            "text2text-generation": "text",
            "fill-mask": "text",
            "question-answering": "text",
            "translation": "text",
            "summarization": "text",

            "text-to-image": "text-to-image",
            "image-to-text": "image-to-text",
            "image-classification": "image",
            "object-detection": "image",
            "image-segmentation": "image",

            "automatic-speech-recognition": "audio",
            "audio-classification": "audio",
            "text-to-speech": "audio",
        }

        modality = modality_map.get(
            pipeline_tag
        )

        if modality:
            modalities.append(modality)

    # Remove duplicates while preserving order
    return list(dict.fromkeys(modalities))


def build_metadata(model: dict):
    """Build normalized model metadata."""

    metadata = {
        "provider": "Hugging Face",
        "downloads": model.get(
            "downloads",
            0
        ),
        "likes": model.get(
            "likes",
            0
        ),
        "pipeline_tag": model.get(
            "pipeline_tag"
        ),
        "library_name": model.get(
            "library_name"
        ),
        "license": model.get(
            "license"
        ),
        "modalities": extract_modalities(
            model
        ),
    }

    return metadata


def convert_to_entities(models):
    """Convert Hugging Face models into Orbit entities."""

    entities = []

    for index, model in enumerate(models):

        model_id = model.get("id")

        if not model_id:
            continue

        print(
            f"Enriching model "
            f"{index + 1}/{len(models)}: "
            f"{model_id}"
        )

        # Fetch detailed model metadata
        details = get_model_details(
            model_id
        )

        # Merge list metadata with detailed metadata
        enriched_model = {
            **model,
            **details,
        }

        model_url = (
            f"https://huggingface.co/{model_id}"
        )

        metadata = build_metadata(
            enriched_model
        )

        entity = Entity(
            id=uuid5(
                NAMESPACE_URL,
                model_url
            ),
            entity_type="model",
            name=model_id,
            description=(
                enriched_model.get(
                    "description"
                )
                or
                f"Hugging Face model: "
                f"{model_id}"
            ),
            url=model_url,
            categories=[
                "AI",
                "Machine Learning",
                "Model",
            ],
            source=Source(
                name="Hugging Face",
                url=model_url,
            ),
            metadata=metadata,
        )

        entities.append(entity)

    return entities


def save_entities(
    entities,
    output_path="data/huggingface_models.json"
):
    """Save Hugging Face entities."""

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    data = [
        entity.model_dump(mode="json")
        for entity in entities
    ]

    with path.open(
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
        f"Saved {len(data)} models to {path}"
    )


def main():

    print(
        "Starting Hugging Face discovery..."
    )

    all_models = {}

    for query in SEARCH_QUERIES:

        print(
            f"Searching Hugging Face: "
            f"{query}"
        )

        try:
            models = search_models(
                query,
                limit=10
            )

            for model in models:

                model_id = model.get("id")

                if model_id:
                    all_models[
                        model_id
                    ] = model

        except requests.RequestException as error:

            print(
                f"Request failed for "
                f"'{query}': {error}"
            )

    print(
        f"Unique models discovered: "
        f"{len(all_models)}"
    )

    entities = convert_to_entities(
        list(all_models.values())
    )

    save_entities(entities)


if __name__ == "__main__":
    main()