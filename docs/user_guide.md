# User Guide

## Introduction

Welcome to the AI Research Assistant MCP User Guide. This guide will help you get started with using the AI Research Assistant for your research needs.

## Getting Started

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/ai-research-assistant-mcp.git
cd ai-research-assistant-mcp
```

2. Run the setup script:
```bash
./scripts/setup.sh
```

3. Download required models:
```bash
./scripts/download_models.sh
```

### Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your settings:
```env
HOST=localhost
PORT=8000
WORKERS=4
LOG_LEVEL=info
```

## Basic Usage

### Starting the Server

```bash
./scripts/start_server.sh
```

The server will be available at `http://localhost:8000`.

### Making Your First Request

Using Python:
```python
from research_assistant import ResearchAssistant

# Initialize client
client = ResearchAssistant()

# Perform a search
results = client.search(
    query="quantum computing applications",
    max_results=10
)

# Extract content from a result
content = client.extract(
    url=results[0]["url"],
    type="web"
)

# Generate a summary
summary = client.analyze(
    content=content["text"],
    analysis_type="summarize"
)
```

## Features

### 1. Multi-Source Web Search

The AI Research Assistant can search across multiple sources:

```python
results = client.search(
    query="your search query",
    sources=["duckduckgo", "searx", "academic"],
    filters={
        "date_range": {
            "start": "2024-01-01",
            "end": "2024-12-31"
        }
    }
)
```

### 2. Content Extraction

Extract content from various sources:

```python
# Web content
web_content = client.extract(
    url="https://example.com",
    type="web",
    options={"clean_html": True}
)

# PDF documents
pdf_content = client.extract(
    url="path/to/document.pdf",
    type="pdf"
)

# Academic papers
paper_content = client.extract(
    paper_id="arxiv:1234.5678",
    type="academic"
)
```

### 3. Content Analysis

Perform various types of analysis:

```python
# Summarization
summary = client.analyze(
    content=text,
    analysis_type="summarize",
    options={"max_length": 200}
)

# Insight extraction
insights = client.analyze(
    content=text,
    analysis_type="insights",
    options={"focus_areas": ["key_points", "conclusions"]}
)

# Fact checking
fact_check = client.analyze(
    content=text,
    analysis_type="fact_check",
    options={"confidence_threshold": 0.8}
)
```

### 4. Knowledge Graph Generation

Create knowledge graphs from research findings:

```python
graph = client.build_graph(
    topic="artificial intelligence",
    sources=["academic", "news"],
    options={
        "depth": 2,
        "include_metadata": True
    }
)

# Visualize the graph
visualization = client.visualize_graph(graph)
```

### 5. Report Generation

Generate research reports:

```python
report = client.generate_report(
    research_data=results,
    template="academic",
    format="pdf",
    options={
        "include_visualizations": True,
        "include_citations": True
    }
)
```

## Advanced Features

### Real-time Updates

Use WebSocket for real-time updates:

```python
client = ResearchAssistant(use_websocket=True)

# Subscribe to events
client.on("search_progress", lambda data: print(f"Progress: {data['progress']}"))
client.on("analysis_progress", lambda data: print(f"Analysis: {data['progress']}"))

# Start a long-running task
client.search(
    query="complex query",
    max_results=100,
    real_time=True
)
```

### Custom Analysis Templates

Create custom analysis templates:

```python
template = {
    "name": "custom_analysis",
    "prompt": "Analyze the following text focusing on {focus_areas}: {text}",
    "parameters": {
        "focus_areas": ["technical", "business", "social"]
    }
}

client.register_template(template)

results = client.analyze(
    content=text,
    analysis_type="custom_analysis",
    options={"focus_areas": ["technical", "business"]}
)
```

### Batch Processing

Process multiple items in batch:

```python
urls = ["https://example1.com", "https://example2.com"]

# Batch content extraction
contents = client.batch_extract(
    urls=urls,
    type="web",
    options={"clean_html": True}
)

# Batch analysis
analyses = client.batch_analyze(
    contents=contents,
    analysis_type="summarize"
)
```

## Best Practices

1. **Error Handling**
```python
try:
    results = client.search(query="your query")
except ResearchAssistantError as e:
    print(f"Error: {e.message}")
    print(f"Details: {e.details}")
```

2. **Rate Limiting**
```python
# Use rate limiting decorator
@client.rate_limit(requests=100, period=60)
def process_large_dataset():
    # Your code here
    pass
```

3. **Caching**
```python
# Enable caching for repeated queries
client.enable_caching(ttl=3600)  # Cache for 1 hour
```

4. **Session Management**
```python
# Create a research session
session = client.create_session(
    name="My Research",
    description="Research on quantum computing"
)

# Add items to session
session.add_search_results(results)
session.add_analysis(analysis)

# Save session
session.save()
```

## Troubleshooting

### Common Issues

1. **Server Connection Issues**
   - Check if the server is running
   - Verify your `.env` configuration
   - Check network connectivity

2. **Model Loading Issues**
   - Ensure models are downloaded
   - Check available disk space
   - Verify model compatibility

3. **Performance Issues**
   - Adjust worker count in `.env`
   - Enable caching for repeated queries
   - Use batch processing for large datasets

### Getting Help

- Check the [Troubleshooting Guide](troubleshooting.md)
- Visit our [GitHub Issues](https://github.com/your-org/ai-research-assistant-mcp/issues)
- Join our [Discord Community](https://discord.gg/your-community)

## Updates and Maintenance

### Checking for Updates

```bash
git pull origin main
./scripts/setup.sh
```

### Updating Models

```bash
./scripts/download_models.sh --update
```

### Backup and Restore

```bash
# Backup
./scripts/backup.sh

# Restore
./scripts/restore.sh backup_file.tar.gz
```

## Security

### API Key Management

1. Generate a new API key:
```bash
./scripts/generate_api_key.sh
```

2. Rotate API keys regularly:
```bash
./scripts/rotate_api_key.sh
```

### Data Privacy

- All data is processed locally
- No data is sent to external servers
- Use encryption for sensitive data

## Support

- Documentation: [docs/](docs/)
- Examples: [examples/](examples/)
- Community: [Discord](https://discord.gg/your-community)
- Issues: [GitHub Issues](https://github.com/your-org/ai-research-assistant-mcp/issues) 