# API Reference

## Overview

The AI Research Assistant MCP provides a comprehensive API for research automation and analysis. This document details all available endpoints, request/response formats, and usage examples.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All API endpoints require authentication using a Bearer token:

```http
Authorization: Bearer <your_token>
```

## Endpoints

### Search Endpoints

#### POST /search
Perform a multi-source web search.

**Request Body:**
```json
{
    "query": "string",
    "max_results": 10,
    "sources": ["duckduckgo", "searx", "academic"],
    "filters": {
        "date_range": {
            "start": "2024-01-01",
            "end": "2024-12-31"
        },
        "min_relevance": 0.7
    }
}
```

**Response:**
```json
{
    "results": [
        {
            "title": "string",
            "url": "string",
            "snippet": "string",
            "source": "string",
            "relevance_score": 0.95,
            "metadata": {
                "date": "2024-03-15",
                "author": "string"
            }
        }
    ],
    "total_results": 100,
    "search_time": 1.5
}
```

### Content Extraction Endpoints

#### POST /extract
Extract content from web pages or documents.

**Request Body:**
```json
{
    "url": "string",
    "type": "web|pdf|document",
    "options": {
        "clean_html": true,
        "remove_ads": true,
        "extract_metadata": true
    }
}
```

**Response:**
```json
{
    "content": "string",
    "metadata": {
        "title": "string",
        "author": "string",
        "date": "string",
        "word_count": 1000
    },
    "extraction_time": 0.5
}
```

### Analysis Endpoints

#### POST /analyze
Perform content analysis using local LLMs.

**Request Body:**
```json
{
    "content": "string",
    "analysis_type": "summarize|insights|fact_check",
    "options": {
        "max_length": 200,
        "focus_areas": ["key_points", "conclusions"],
        "confidence_threshold": 0.8
    }
}
```

**Response:**
```json
{
    "summary": "string",
    "key_points": ["string"],
    "confidence_score": 0.95,
    "analysis_time": 2.0
}
```

### Knowledge Graph Endpoints

#### POST /graph/build
Build a knowledge graph from research findings.

**Request Body:**
```json
{
    "topic": "string",
    "sources": ["string"],
    "options": {
        "depth": 2,
        "include_metadata": true,
        "min_confidence": 0.7
    }
}
```

**Response:**
```json
{
    "graph": {
        "nodes": [
            {
                "id": "string",
                "label": "string",
                "type": "string",
                "metadata": {}
            }
        ],
        "edges": [
            {
                "source": "string",
                "target": "string",
                "label": "string",
                "weight": 0.8
            }
        ]
    },
    "metadata": {
        "node_count": 100,
        "edge_count": 150
    }
}
```

### Report Generation Endpoints

#### POST /reports/generate
Generate a research report.

**Request Body:**
```json
{
    "research_data": {},
    "template": "academic|business|technical",
    "format": "pdf|html|markdown",
    "options": {
        "include_visualizations": true,
        "include_citations": true
    }
}
```

**Response:**
```json
{
    "report_url": "string",
    "metadata": {
        "page_count": 10,
        "generation_time": 5.0
    }
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
    "error": "string",
    "details": "string"
}
```

### 401 Unauthorized
```json
{
    "error": "Authentication required"
}
```

### 403 Forbidden
```json
{
    "error": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
    "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
    "error": "Internal server error",
    "request_id": "string"
}
```

## Rate Limiting

API requests are limited to:
- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated users

Rate limit headers are included in all responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1615834800
```

## WebSocket API

### WebSocket Endpoint
```
ws://localhost:8000/api/v1/ws
```

### Real-time Events
- `search_progress`: Search progress updates
- `analysis_progress`: Analysis progress updates
- `report_progress`: Report generation progress

### Example WebSocket Message
```json
{
    "type": "search_progress",
    "data": {
        "progress": 0.5,
        "current_source": "duckduckgo",
        "results_so_far": 5
    }
}
```

## SDK Examples

### Python
```python
from research_assistant import ResearchAssistant

client = ResearchAssistant(api_key="your_api_key")

# Perform search
results = client.search(
    query="quantum computing",
    max_results=10,
    sources=["academic", "news"]
)

# Extract content
content = client.extract(
    url="https://example.com",
    type="web",
    options={"clean_html": True}
)

# Generate report
report = client.generate_report(
    research_data=results,
    template="academic",
    format="pdf"
)
```

### JavaScript
```javascript
const { ResearchAssistant } = require('research-assistant');

const client = new ResearchAssistant('your_api_key');

// Perform search
const results = await client.search({
    query: 'quantum computing',
    maxResults: 10,
    sources: ['academic', 'news']
});

// Extract content
const content = await client.extract({
    url: 'https://example.com',
    type: 'web',
    options: { cleanHtml: true }
});

// Generate report
const report = await client.generateReport({
    researchData: results,
    template: 'academic',
    format: 'pdf'
});
```

## Versioning

The API is versioned using the URL path. The current version is v1. Future versions will be released as v2, v3, etc.

## Changelog

### v1.0.0 (2024-03-15)
- Initial release
- Basic search and analysis endpoints
- Knowledge graph generation
- Report generation

### v1.1.0 (2024-04-01)
- Added WebSocket support
- Enhanced error handling
- Improved rate limiting
- Added SDK support 