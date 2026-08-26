"""
AI company discovery for the AI Orbit ingestion pipeline.

Uses public company/product pages as the discovery source.
"""

import json
import re
from pathlib import Path
from uuid import uuid5, NAMESPACE_URL

import requests
from bs4 import BeautifulSoup


OUTPUT_FILE = Path("data/companies.json")


COMPANY_PAGES = [
    {
        "name": "OpenAI",
        "url": "https://openai.com/",
        "industry": "Artificial Intelligence",
        "headquarters": "San Francisco, California, USA",
        "founded": 2015,
        "fallback_description": (
            "OpenAI is an artificial intelligence research "
            "and deployment company."
        ),
    },
    {
        "name": "Anthropic",
        "url": "https://www.anthropic.com/",
        "industry": "Artificial Intelligence",
        "headquarters": "San Francisco, California, USA",
        "founded": 2021,
    },
    {
        "name": "Hugging Face",
        "url": "https://huggingface.co/",
        "industry": "AI / Machine Learning",
        "headquarters": "New York, USA",
        "founded": 2016,
    },
    {
        "name": "Google DeepMind",
        "url": "https://deepmind.google/",
        "industry": "Artificial Intelligence Research",
        "headquarters": "London, UK",
        "founded": 2010,
    },
    {
        "name": "Mistral AI",
        "url": "https://mistral.ai/",
        "industry": "Artificial Intelligence",
        "headquarters": "Paris, France",
        "founded": 2023,
    },
    {
        "name": "Cohere",
        "url": "https://cohere.com/",
        "industry": "Artificial Intelligence",
        "headquarters": "Toronto, Canada",
        "founded": 2019,
    },
    {
        "name": "Perplexity",
        "url": "https://www.perplexity.ai/",
        "industry": "AI Search",
        "headquarters": "San Francisco, California, USA",
        "founded": 2022,
        "fallback_description": (
            "Perplexity is an AI-powered search "
            "and answer engine."
        ),
    },
    {
        "name": "Runway",
        "url": "https://runwayml.com/",
        "industry": "Generative AI",
        "headquarters": "New York, USA",
        "founded": 2018,
    },
    {
        "name": "Scale AI",
        "url": "https://scale.com/",
        "industry": "AI Data Infrastructure",
        "headquarters": "San Francisco, California, USA",
        "founded": 2016,
    },
    {
        "name": "Stability AI",
        "url": "https://stability.ai/",
        "industry": "Generative AI",
        "headquarters": "London, UK",
        "founded": 2019,
    },
]


def clean_text(text):
    """Clean extracted text."""

    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def fetch_description(url):
    """
    Fetch a short description from the company's
    public homepage metadata.
    """

    try:
        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(AI Orbit ingestion pipeline)"
                )
            },
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        description = ""

        meta_description = soup.find(
            "meta",
            attrs={"name": "description"},
        )

        if meta_description:
            description = meta_description.get(
                "content",
                "",
            )

        if not description:
            og_description = soup.find(
                "meta",
                attrs={
                    "property": "og:description"
                },
            )

            if og_description:
                description = og_description.get(
                    "content",
                    "",
                )

        return clean_text(description)

    except requests.RequestException as error:
        print(
            f"Warning: Failed to fetch {url}: "
            f"{error}"
        )

        return ""


def create_entity(company):
    """Convert company information into an entity."""

    url = company["url"]

    description = fetch_description(url)

    # Use fallback description if website metadata
    # does not provide a description.
    if not description:
        description = company.get(
            "fallback_description",
            "",
        )

    entity_id = str(
        uuid5(
            NAMESPACE_URL,
            url,
        )
    )

    return {
        "id": entity_id,
        "entity_type": "company",
        "name": company["name"],
        "description": description,
        "url": url,
        "categories": [
            "ai company",
            company["industry"].lower(),
        ],
        "source": {
            "name": "Official Company Website",
            "url": url,
        },
        "metadata": {
            "founding_year": company["founded"],
            "industry_sector": company["industry"],
            "headquarters": company["headquarters"],
        },
    }


def discover_companies():
    """Discover AI companies."""

    print(
        "Starting AI company discovery..."
    )

    companies = []

    for company in COMPANY_PAGES:

        print(
            f"Fetching: {company['name']}"
        )

        try:

            entity = create_entity(
                company
            )

            companies.append(entity)

        except Exception as error:

            print(
                f"Warning: Failed to process "
                f"{company['name']}: {error}"
            )

    return companies


def save_entities(entities):
    """Save discovered companies."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            entities,
            file,
            indent=2,
            ensure_ascii=False,
        )


def main():

    companies = discover_companies()

    print(
        f"Unique companies discovered: "
        f"{len(companies)}"
    )

    save_entities(companies)

    print(
        f"Saved {len(companies)} company entities "
        f"to {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()