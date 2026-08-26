# AI Orbit Ingestion Pipeline

An automated AI ecosystem data ingestion pipeline that discovers, normalizes, deduplicates, classifies, validates, samples, and maps relationships between AI ecosystem entities.

## Overview

The AI Orbit Ingestion Pipeline collects structured data from multiple sources and transforms it into a clean, validated dataset suitable for downstream AI ecosystem intelligence and graph-based analysis.

The pipeline currently supports discovery from:

- GitHub
- Hugging Face
- News
- YouTube
- MCP ecosystem
- AI companies
- AI tools

## Pipeline Architecture

The ingestion workflow follows these stages:

1. **Discovery**
   - Collect entities from multiple data sources.

2. **Deduplication**
   - Remove duplicate entities using normalized identifiers and entity information.

3. **Cleaning**
   - Remove incomplete or unusable records.

4. **Normalization**
   - Standardize entity fields and metadata.

5. **Classification**
   - Assign entities to supported ecosystem types.

6. **Validation**
   - Verify required fields, URLs, source information, and entity IDs.

7. **Relationship Extraction**
   - Identify meaningful relationships between entities.

8. **Relationship-aware Sampling**
   - Create a representative dataset while prioritizing entities participating in relationships.

## Supported Entity Types

The pipeline handles multiple entity categories, including:

- Company
- Repository
- Model
- Tool
- MCP
- Device
- Task
- News
- YouTube / Video
- Creative
- Personal
- Robot

## Supported Relationships

The relationship mapper currently supports:

- `Company -> develops -> Tool / Model`
- `Repository -> implements -> Model`
- `MCP -> integrates_with -> Tool / Repository`
- `Device -> runs -> Model`
- `Tool -> solves -> Task`

Relationship extraction uses explicit metadata and conservative text matching to reduce false-positive relationships.

## Current Pipeline Results

Latest successful pipeline execution:

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
Missing relationship IDs: 0

Sampled entities: 271
Duplicate sampled IDs: 0
Missing sampled IDs: 0


Project Structure

AI-orbit-ingestion/
│
├── data/
│   ├── entities.json
│   ├── entities_clean.json
│   ├── entities_sampled.json
│   ├── relationships.json
│   └── companies.json
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
├── .env
├── .gitignore
└── README.md