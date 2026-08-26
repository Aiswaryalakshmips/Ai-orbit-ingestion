from pathlib import Path
import json

from fastapi import FastAPI

app = FastAPI(
    title="AI Orbit Data Ingestion Pipeline",
    description="AI ecosystem data ingestion pipeline and processed dataset API.",
    version="1.0.0",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def load_json(filename):
    path = DATA_DIR / filename

    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


@app.get("/")
def root():
    return {
        "project": "AI Orbit Data Ingestion Pipeline",
        "status": "running",
        "message": "AI Orbit ingestion pipeline is deployed successfully.",
        "endpoints": {
            "health": "/health",
            "entities": "/entities",
            "relationships": "/relationships",
            "sampled": "/entities/sampled",
            "docs": "/docs",
        },
    }


@app.get("/health")
def health():
    entities = load_json("entities_clean.json") or []
    relationships = load_json("relationships.json") or []
    sampled = load_json("entities_sampled.json") or []

    return {
        "status": "healthy",
        "entities": len(entities),
        "relationships": len(relationships),
        "sampled_entities": len(sampled),
    }


@app.get("/entities")
def entities():
    return load_json("entities_clean.json") or []


@app.get("/relationships")
def relationships():
    return load_json("relationships.json") or []


@app.get("/entities/sampled")
def sampled_entities():
    return load_json("entities_sampled.json") or []