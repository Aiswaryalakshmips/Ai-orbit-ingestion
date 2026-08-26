# AI Orbit Ingestion Pipeline

A modular Python-based data ingestion pipeline for discovering, cleaning, normalizing, deduplicating, classifying, validating, sampling, and mapping relationships across the global AI ecosystem.

## Overview

The AI Orbit Ingestion Pipeline follows an API-first, modular architecture designed to produce a high-quality representative dataset rather than relying on large-scale scraping.

The pipeline currently discovers data from:

* GitHub
* Hugging Face
* News / RSS
* YouTube
* MCP ecosystem
* AI companies
* AI tools

## Pipeline Architecture

```text
Discovery
   ↓
Extraction
   ↓
Cleaning
   ↓
Normalization
   ↓
Deduplication
   ↓
Classification
   ↓
Relationship Mapping
   ↓
Validation
   ↓
Relationship-aware Sampling
```

Each stage is implemented as a separate reusable module under `src/`.

## Data Sources

### GitHub

Discovers open-source AI repositories and extracts repository metadata such as:

* Stars
* Primary programming language
* Last updated timestamp
* Repository owner

### Hugging Face

Discovers AI/ML models and extracts metadata including:

* Provider
* Downloads
* Likes
* Pipeline/task information
* Library
* License
* Modalities

When an upstream source does not provide a value, the pipeline preserves the missing value instead of inventing metadata.

### News / RSS

Collects AI-related announcements and industry news through RSS feeds and sanitizes extracted text.

### YouTube

Collects AI-related technical videos, tutorials, demonstrations, and reviews.

### MCP

Discovers MCP ecosystem entities and captures metadata such as:

* Installation methods
* Runtime requirements
* Repository information
* Stars
* Programming language
* Last updated timestamp

### Companies

Discovers AI companies and captures:

* Founding year
* Industry sector
* Headquarters

### AI Tools

Collects AI application/tool entities for ecosystem analysis and relationship mapping.

## Common Entity Schema

Entities follow a common structure:

```json
{
  "id": "stable-generated-uuid",
  "entity_type": "string",
  "name": "string",
  "description": "string",
  "url": "string",
  "categories": ["string"],
  "source": {
    "name": "string",
    "url": "string"
  },
  "metadata": {}
}
```

The `metadata` object contains domain-specific fields where applicable.

## Supported Entity Types

The pipeline currently handles:

* Company
* Repository
* Model
* Tool
* MCP
* News
* Video
* Creative
* Personal
* Robot

The architecture is extensible and can support additional entity types such as Tasks, Devices, Collections, and newly added entities when suitable source data is available.

## Entity Resolution and Deduplication

The pipeline performs entity resolution before producing the cleaned dataset.

Deduplication uses normalized entity information and stable identifiers to reduce duplicate records caused by:

* Name variations
* URL variations
* Repeated source records
* Cross-source overlap

The goal is to retain one canonical representation of an entity.

## URL Normalization

URLs are normalized during processing so that equivalent source references can be compared consistently.

Validation additionally ensures that entity and source URLs use valid HTTP/HTTPS structures.

## Sanitization and Cleaning

Text from external sources is cleaned before entering the final dataset.

The cleaning stage handles incomplete or unusable records and removes unnecessary formatting from extracted content.

## Relationship Extraction

Relationships are stored in:

```text
data/relationships.json
```

The mapper currently identifies the following relationships:

```text
Company → develops → Tool
Company → develops → Model

Repository → implements → Model

MCP → integrates_with → Tool
MCP → integrates_with → Repository
```

The relationship extractor uses explicit metadata and conservative matching logic to reduce false-positive connections.

The current dataset contains:

* 48 `develops` relationships
* 2 `implements` relationships
* 90 `integrates_with` relationships

Total:

```text
140 relationships
```

All relationship source and target IDs were verified against the cleaned entity dataset.

### Relationship Coverage

The specification also defines:

```text
Tool → solves → Task
Device → runs → Model
```

The current source collection does not contain dedicated Task or Device records, so these relationship types are not fabricated. Consequently, the current dataset contains:

```text
solves = 0
runs   = 0
```

This is intentional data-integrity behavior: relationships are only created when supported by actual source entities and evidence.

## Validation

The validation module checks:

* Required entity fields
* Entity names
* Entity URLs
* Source names
* Source URLs
* Duplicate entity IDs

Latest validation result:

```text
Total: 349
Valid: 349
Invalid: 0
```

## Relationship-aware Sampling

The project produces a representative submission dataset in:

```text
data/entities_sampled.json
```

The sampling stage considers relationship participation while maintaining category coverage.

Latest sampling result:

```text
Total sampled entities: 271
```

This is within the required representative dataset range of 250–300 records.

Current distribution:

```text
Repository : 55
Video      : 45
MCP        : 40
Model      : 40
Tool       : 40
News       : 20
Company    : 11
Creative   : 11
Personal   : 6
Robot      : 3
```

The sampled dataset was additionally checked for:

```text
Duplicate IDs: 0
Missing IDs: 0
Missing names: 0
Missing descriptions: 0
Missing URLs: 0
Missing sources: 0
```

## Latest Pipeline Results

A successful end-to-end execution produced:

```text
GitHub entities: 100
Hugging Face models: 49
News entities: 20
YouTube entities: 76
MCP entities: 49
Company entities: 10
AI Tool entities: 75

Total discovered entities: 379
After deduplication: 349

Validated entities: 349
Invalid entities: 0

Relationships: 140

Sampled entities: 271
```

## Project Structure

```text
Ai-orbit-ingestion/
│
├── data/
│   ├── entities.json
│   ├── entities_clean.json
│   ├── entities_sampled.json
│   ├── relationships.json
│   ├── companies.json
│   ├── huggingface_models.json
│   ├── mcp.json
│   ├── news.json
│   ├── tools.json
│   └── youtube.json
│
├── src/
│   ├── models.py
│   │
│   ├── discovery/
│   │   ├── github.py
│   │   ├── huggingface.py
│   │   ├── news.py
│   │   ├── youtube.py
│   │   ├── mcp.py
│   │   ├── company.py
│   │   └── tools.py
│   │
│   ├── processing/
│   │   ├── cleaning.py
│   │   ├── normalization.py
│   │   ├── deduplication.py
│   │   ├── classifier.py
│   │   └── sampler.py
│   │
│   ├── relationships/
│   │   └── mapper.py
│   │
│   └── validation/
│       └── validator.py
│
├── run.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

### 1. Clone the repository

```powershell
git clone https://github.com/Aiswaryalakshmips/Ai-orbit-ingestion.git
cd Ai-orbit-ingestion
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the virtual environment

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file and add the required API credentials.

Example:

```text
YOUTUBE_API_KEY=your_api_key_here
```

Secrets are excluded from Git through `.gitignore`.

## Running the Pipeline

Run the complete ingestion pipeline:

```powershell
python run.py
```

Run relationship extraction separately:

```powershell
python -m src.relationships.mapper
```

Run relationship-aware sampling:

```powershell
python -m src.processing.sampler
```

Run validation:

```powershell
python -m src.validation.validator
```

## Output Files

The main outputs are:

```text
data/entities_clean.json
data/entities_sampled.json
data/relationships.json
```

`entities_clean.json` contains the validated full cleaned dataset.

`entities_sampled.json` contains the representative 250–300 range submission dataset.

`relationships.json` contains the extracted entity relationships.

## Engineering Principles

The implementation prioritizes:

* API-first discovery
* Modular architecture
* Stable entity identifiers
* Entity resolution
* URL normalization
* Data sanitization
* Deduplication
* Conservative relationship extraction
* Schema validation
* Relationship-aware sampling
* Graceful handling of missing upstream metadata
* Reproducible pipeline execution

## Data Integrity Philosophy

The pipeline does not fabricate unavailable metadata or relationships.

If a source does not provide a field, the pipeline preserves the missing value rather than generating unsupported information.

Similarly, relationships are only created when there is sufficient evidence from the available entity metadata.

This approach prioritizes precision and traceability over artificially increasing dataset completeness.

## Final Deliverables

The repository contains:

* Modular ingestion source code under `src/`
* Raw and processed JSON datasets under `data/`
* End-to-end execution script `run.py`
* Dependency specification `requirements.txt`
* Technical documentation in `README.md`
* Git-based version control
* Representative dataset of 271 entities
* 140 extracted relationships
* Validated entity dataset with zero invalid records
