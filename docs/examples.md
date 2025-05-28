# Examples

This document provides examples of how to use the AI Research Assistant MCP for various research tasks.

## Basic Usage

### Simple Search and Analysis

```python
from research_assistant import ResearchAssistant

# Initialize the assistant
assistant = ResearchAssistant()

# Perform a search
results = assistant.search(
    query="quantum computing applications",
    max_results=5
)

# Extract content from the first result
content = assistant.extract_content(results[0]["url"])

# Analyze the content
analysis = assistant.analyze(
    content=content["text"],
    analysis_type="summarization"
)

print(f"Summary: {analysis['summary']}")
```

### Multi-Source Search

```python
from research_assistant import ResearchAssistant
from research_assistant.search import SearchSource

# Initialize with specific sources
assistant = ResearchAssistant(
    search_sources=[
        SearchSource.DUCKDUCKGO,
        SearchSource.SEARX,
        SearchSource.ACADEMIC
    ]
)

# Perform parallel search
results = assistant.search(
    query="machine learning in healthcare",
    max_results=10,
    parallel=True
)

# Combine and rank results
ranked_results = assistant.rank_results(results)
```

## Academic Research

### Literature Review

```python
from research_assistant import ResearchAssistant
from research_assistant.analysis import AnalysisType

# Initialize for academic research
assistant = ResearchAssistant(
    analysis_type=AnalysisType.ACADEMIC
)

# Search academic papers
papers = assistant.search(
    query="deep learning in natural language processing",
    source_type="academic",
    year_range=(2020, 2023)
)

# Extract and analyze papers
for paper in papers:
    content = assistant.extract_content(paper["url"])
    analysis = assistant.analyze(
        content=content["text"],
        analysis_type="academic_review"
    )
    
    # Generate citation
    citation = assistant.generate_citation(paper)
    
    print(f"Title: {paper['title']}")
    print(f"Citation: {citation}")
    print(f"Key Findings: {analysis['key_findings']}")
```

### Research Gap Analysis

```python
from research_assistant import ResearchAssistant

# Initialize the assistant
assistant = ResearchAssistant()

# Search for recent papers
papers = assistant.search(
    query="quantum machine learning",
    source_type="academic",
    year_range=(2022, 2023)
)

# Analyze research gaps
gaps = assistant.analyze_research_gaps(papers)

# Generate report
report = assistant.generate_report(
    title="Research Gaps in Quantum Machine Learning",
    content=gaps,
    format="academic"
)

# Save report
report.save("quantum_ml_gaps.pdf")
```

## Market Research

### Competitor Analysis

```python
from research_assistant import ResearchAssistant
from research_assistant.analysis import AnalysisType

# Initialize for market research
assistant = ResearchAssistant(
    analysis_type=AnalysisType.MARKET
)

# Search for competitor information
competitors = assistant.search(
    query="AI companies in healthcare",
    source_type="web",
    max_results=10
)

# Analyze each competitor
for competitor in competitors:
    content = assistant.extract_content(competitor["url"])
    analysis = assistant.analyze(
        content=content["text"],
        analysis_type="competitor_analysis"
    )
    
    print(f"Company: {competitor['title']}")
    print(f"Market Position: {analysis['market_position']}")
    print(f"Key Strengths: {analysis['strengths']}")
    print(f"Key Weaknesses: {analysis['weaknesses']}")
```

### Market Trend Analysis

```python
from research_assistant import ResearchAssistant

# Initialize the assistant
assistant = ResearchAssistant()

# Search for market trends
trends = assistant.search(
    query="artificial intelligence market trends 2024",
    source_type="web",
    max_results=20
)

# Analyze trends
analysis = assistant.analyze_market_trends(trends)

# Generate visualization
visualization = assistant.generate_visualization(
    data=analysis,
    type="trend_analysis"
)

# Save report
report = assistant.generate_report(
    title="AI Market Trends 2024",
    content=analysis,
    visualization=visualization,
    format="market_research"
)
report.save("ai_market_trends.pdf")
```

## Fact Checking

### Claim Verification

```python
from research_assistant import ResearchAssistant
from research_assistant.analysis import AnalysisType

# Initialize for fact checking
assistant = ResearchAssistant(
    analysis_type=AnalysisType.FACT_CHECK
)

# Define claims to verify
claims = [
    "Quantum computers can solve any problem instantly",
    "AI will replace all human jobs by 2030",
    "Machine learning models are always biased"
]

# Verify each claim
for claim in claims:
    verification = assistant.verify_claim(
        claim=claim,
        confidence_threshold=0.8
    )
    
    print(f"Claim: {claim}")
    print(f"Verdict: {verification['verdict']}")
    print(f"Confidence: {verification['confidence']}")
    print(f"Sources: {verification['sources']}")
```

### Source Reliability Check

```python
from research_assistant import ResearchAssistant

# Initialize the assistant
assistant = ResearchAssistant()

# Define sources to check
sources = [
    "https://example.com/article1",
    "https://example.com/article2",
    "https://example.com/article3"
]

# Check each source
for source in sources:
    reliability = assistant.check_source_reliability(source)
    
    print(f"Source: {source}")
    print(f"Reliability Score: {reliability['score']}")
    print(f"Factors: {reliability['factors']}")
    print(f"Recommendation: {reliability['recommendation']}")
```

## Knowledge Graph Generation

### Building a Knowledge Graph

```python
from research_assistant import ResearchAssistant

# Initialize the assistant
assistant = ResearchAssistant()

# Search for related content
results = assistant.search(
    query="artificial intelligence ethics",
    max_results=15
)

# Extract content
contents = []
for result in results:
    content = assistant.extract_content(result["url"])
    contents.append(content)

# Generate knowledge graph
graph = assistant.generate_knowledge_graph(
    contents=contents,
    min_confidence=0.7
)

# Visualize graph
visualization = assistant.visualize_knowledge_graph(graph)

# Save graph
graph.save("ai_ethics_graph.json")
visualization.save("ai_ethics_graph.png")
```

### Querying Knowledge Graph

```python
from research_assistant import ResearchAssistant

# Initialize the assistant
assistant = ResearchAssistant()

# Load existing knowledge graph
graph = assistant.load_knowledge_graph("ai_ethics_graph.json")

# Query the graph
results = graph.query(
    query="What are the main ethical concerns in AI?",
    max_results=5
)

# Display results
for result in results:
    print(f"Concept: {result['concept']}")
    print(f"Relations: {result['relations']}")
    print(f"Confidence: {result['confidence']}")
```

## Report Generation

### Research Report

```python
from research_assistant import ResearchAssistant
from research_assistant.reports import ReportFormat

# Initialize the assistant
assistant = ResearchAssistant()

# Search and analyze content
results = assistant.search(
    query="sustainable energy solutions",
    max_results=20
)

# Extract and analyze content
contents = []
for result in results:
    content = assistant.extract_content(result["url"])
    analysis = assistant.analyze(
        content=content["text"],
        analysis_type="comprehensive"
    )
    contents.append({
        "content": content,
        "analysis": analysis
    })

# Generate report
report = assistant.generate_report(
    title="Sustainable Energy Solutions: A Comprehensive Review",
    content=contents,
    format=ReportFormat.ACADEMIC,
    include_visualizations=True
)

# Save report
report.save("sustainable_energy_report.pdf")
```

### Executive Summary

```python
from research_assistant import ResearchAssistant

# Initialize the assistant
assistant = ResearchAssistant()

# Generate executive summary
summary = assistant.generate_executive_summary(
    report_path="sustainable_energy_report.pdf",
    max_length=1000,
    include_key_points=True,
    include_recommendations=True
)

# Save summary
summary.save("sustainable_energy_summary.pdf")
```

## Advanced Features

### Custom Analysis Template

```python
from research_assistant import ResearchAssistant
from research_assistant.analysis import AnalysisTemplate

# Define custom template
template = AnalysisTemplate(
    name="custom_analysis",
    template="""
    Analyze the following text focusing on:
    1. Main arguments
    2. Supporting evidence
    3. Potential biases
    4. Recommendations
    
    Text: {text}
    """,
    parameters={
        "max_length": 500,
        "include_citations": True
    }
)

# Initialize with custom template
assistant = ResearchAssistant(
    custom_templates=[template]
)

# Use custom analysis
analysis = assistant.analyze(
    content="Your text here",
    analysis_type="custom_analysis"
)
```

### Batch Processing

```python
from research_assistant import ResearchAssistant
from concurrent.futures import ThreadPoolExecutor

# Initialize the assistant
assistant = ResearchAssistant()

# Define batch of queries
queries = [
    "AI in healthcare",
    "Machine learning applications",
    "Deep learning frameworks",
    "Natural language processing"
]

# Process batch
def process_query(query):
    results = assistant.search(query)
    content = assistant.extract_content(results[0]["url"])
    analysis = assistant.analyze(content["text"])
    return {
        "query": query,
        "analysis": analysis
    }

# Execute batch processing
with ThreadPoolExecutor() as executor:
    results = list(executor.map(process_query, queries))

# Save results
assistant.save_batch_results(results, "batch_analysis.json")
```

### Real-time Updates

```python
from research_assistant import ResearchAssistant
import asyncio

# Initialize the assistant
assistant = ResearchAssistant()

# Define callback for real-time updates
async def handle_update(update):
    print(f"Received update: {update['type']}")
    print(f"Progress: {update['progress']}%")
    if update['type'] == 'complete':
        print(f"Results: {update['results']}")

# Perform search with real-time updates
async def search_with_updates():
    await assistant.search(
        query="quantum computing",
        max_results=10,
        callback=handle_update
    )

# Run the search
asyncio.run(search_with_updates())
```

## Error Handling

### Graceful Error Handling

```python
from research_assistant import ResearchAssistant
from research_assistant.exceptions import ResearchAssistantError

# Initialize the assistant
assistant = ResearchAssistant()

try:
    # Perform search
    results = assistant.search(
        query="complex query",
        max_results=5
    )
    
    # Extract content
    content = assistant.extract_content(results[0]["url"])
    
    # Analyze content
    analysis = assistant.analyze(content["text"])
    
except ResearchAssistantError as e:
    print(f"Error occurred: {e.message}")
    print(f"Error code: {e.code}")
    print(f"Details: {e.details}")
    
    # Handle specific error types
    if e.code == "SEARCH_FAILED":
        # Retry with different parameters
        results = assistant.search(
            query="simplified query",
            max_results=3
        )
    elif e.code == "EXTRACTION_FAILED":
        # Try alternative extraction method
        content = assistant.extract_content_alternative(results[0]["url"])
```

### Retry Logic

```python
from research_assistant import ResearchAssistant
from research_assistant.utils import retry

# Initialize the assistant
assistant = ResearchAssistant()

# Define retryable function
@retry(max_attempts=3, delay=1)
def search_with_retry(query):
    return assistant.search(query)

# Use retryable function
try:
    results = search_with_retry("complex query")
except Exception as e:
    print(f"Failed after retries: {e}")
```

## Best Practices

### Efficient Resource Usage

```python
from research_assistant import ResearchAssistant
from research_assistant.config import Config

# Configure resource limits
config = Config(
    max_memory_usage="4GB",
    max_cpu_usage=80,
    cache_size="1GB"
)

# Initialize with configuration
assistant = ResearchAssistant(config=config)

# Use resource monitoring
with assistant.monitor_resources():
    # Perform resource-intensive operations
    results = assistant.search(
        query="complex query",
        max_results=20
    )
    
    # Process results
    for result in results:
        content = assistant.extract_content(result["url"])
        analysis = assistant.analyze(content["text"])
```

### Caching Results

```python
from research_assistant import ResearchAssistant
from research_assistant.cache import Cache

# Initialize cache
cache = Cache(
    ttl=3600,  # 1 hour
    max_size="1GB"
)

# Initialize assistant with cache
assistant = ResearchAssistant(cache=cache)

# Use cached results
results = assistant.search(
    query="frequently used query",
    use_cache=True
)

# Clear cache when needed
assistant.clear_cache()
```

### Logging and Monitoring

```python
from research_assistant import ResearchAssistant
from research_assistant.logging import Logger

# Initialize logger
logger = Logger(
    level="DEBUG",
    file="research.log"
)

# Initialize assistant with logger
assistant = ResearchAssistant(logger=logger)

# Use logging
with logger.context("search_operation"):
    results = assistant.search(
        query="complex query",
        max_results=10
    )
    logger.info(f"Found {len(results)} results")
    
    for result in results:
        with logger.context("extraction"):
            content = assistant.extract_content(result["url"])
            logger.debug(f"Extracted {len(content['text'])} characters")
```

## Integration Examples

### Web Application Integration

```python
from flask import Flask, request, jsonify
from research_assistant import ResearchAssistant

app = Flask(__name__)
assistant = ResearchAssistant()

@app.route("/search", methods=["POST"])
def search():
    data = request.json
    query = data.get("query")
    max_results = data.get("max_results", 5)
    
    try:
        results = assistant.search(
            query=query,
            max_results=max_results
        )
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    content = data.get("content")
    analysis_type = data.get("analysis_type", "general")
    
    try:
        analysis = assistant.analyze(
            content=content,
            analysis_type=analysis_type
        )
        return jsonify({"analysis": analysis})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
```

### Command Line Interface

```python
import click
from research_assistant import ResearchAssistant

@click.group()
def cli():
    pass

@cli.command()
@click.argument("query")
@click.option("--max-results", default=5, help="Maximum number of results")
def search(query, max_results):
    assistant = ResearchAssistant()
    results = assistant.search(query, max_results=max_results)
    for result in results:
        click.echo(f"Title: {result['title']}")
        click.echo(f"URL: {result['url']}")
        click.echo("---")

@cli.command()
@click.argument("url")
def extract(url):
    assistant = ResearchAssistant()
    content = assistant.extract_content(url)
    click.echo(f"Extracted {len(content['text'])} characters")

@cli.command()
@click.argument("content")
@click.option("--type", default="general", help="Analysis type")
def analyze(content, type):
    assistant = ResearchAssistant()
    analysis = assistant.analyze(content, analysis_type=type)
    click.echo(f"Analysis: {analysis}")

if __name__ == "__main__":
    cli()
``` 