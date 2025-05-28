# AI Research Assistant MCP

An AI-powered research assistant using MCP (Model Context Protocol) for advanced research capabilities. 

## 1. Introduction

### 1.1 Purpose
The AI-Powered Research Assistant MCP Server is designed to provide intelligent web research capabilities through the Model Context Protocol (MCP). It combines web scraping, document processing, and local LLM analysis to deliver comprehensive research insights without requiring external API costs.

### 1.2 Scope
This system will enable users to:
- Conduct intelligent web searches across multiple sources
- Extract and analyze content from web pages and documents
- Generate summaries and insights using local LLMs
- Create knowledge graphs from research findings
- Perform fact-checking across multiple sources
- Generate research reports and recommendations

## 2. System Overview

### 2.1 System Description
The AI Research Assistant MCP Server is a comprehensive research tool that leverages multiple free and open-source technologies to provide intelligent web research capabilities. The system integrates web search engines, document processors, and local AI models to deliver accurate, comprehensive research results.

### 2.2 Key Features
- **Multi-Source Web Search**: Aggregates results from DuckDuckGo, SearX, and academic databases
- **Intelligent Content Extraction**: Processes web pages, PDFs, and academic papers
- **AI-Powered Analysis**: Uses local LLMs for summarization and insight extraction
- **Knowledge Graph Generation**: Creates visual representations of research relationships
- **Fact-Checking**: Cross-references information across multiple sources
- **Research Report Generation**: Compiles findings into structured reports

## Project Structure

ai_research_assistant_mcp/
├── README.md
├── LICENSE
├── requirements.txt
├── setup.py
├── pyproject.toml
├── docker-compose.yml
├── .env.example
├── .gitignore
│
├── src/
│   └── research_assistant/
│       ├── __init__.py
│       ├── main.py
│       ├── server.py                    # Main MCP server entry point
│       ├── config.py                    # Configuration management
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── mcp_server.py           # MCP protocol implementation
│       │   ├── tool_registry.py        # Tool registration and management
│       │   └── error_handler.py        # Global error handling
│       │
│       ├── search/
│       │   ├── __init__.py
│       │   ├── base_searcher.py        # Abstract search interface
│       │   ├── duckduckgo_search.py    # DuckDuckGo implementation
│       │   ├── searx_search.py         # SearX implementation
│       │   ├── selenium_search.py      # Selenium-based search
│       │   ├── academic_search.py      # Academic paper search
│       │   ├── search_aggregator.py    # Multi-source aggregation
│       │   └── search_utils.py         # Search utilities
│       │
│       ├── extraction/
│       │   ├── __init__.py
│       │   ├── base_extractor.py       # Abstract extractor interface
│       │   ├── web_extractor.py        # Web content extraction
│       │   ├── pdf_extractor.py        # PDF processing
│       │   ├── document_extractor.py   # Word/PowerPoint processing
│       │   ├── content_cleaner.py      # Text cleaning and preprocessing
│       │   └── extraction_utils.py     # Extraction utilities
│       │
│       ├── analysis/
│       │   ├── __init__.py
│       │   ├── base_analyzer.py        # Abstract analyzer interface
│       │   ├── summarizer.py           # Content summarization
│       │   ├── insight_extractor.py    # Key insight identification
│       │   ├── fact_checker.py         # Cross-reference verification
│       │   ├── sentiment_analyzer.py   # Sentiment analysis
│       │   ├── topic_modeler.py        # Topic modeling
│       │   └── analysis_utils.py       # Analysis utilities
│       │
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── ollama_client.py        # Ollama integration
│       │   ├── langchain_chains.py     # LangChain workflows
│       │   ├── prompt_templates.py     # Prompt management
│       │   ├── model_manager.py        # Model loading and management
│       │   └── llm_utils.py           # LLM utilities
│       │
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── vector_store.py         # ChromaDB integration
│       │   ├── cache_manager.py        # Result caching
│       │   ├── knowledge_graph.py      # Graph storage and retrieval
│       │   ├── session_manager.py      # Session data management
│       │   └── storage_utils.py        # Storage utilities
│       │
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── research_tools.py       # Core research MCP tools
│       │   ├── analysis_tools.py       # Analysis MCP tools
│       │   ├── export_tools.py         # Export and reporting tools
│       │   ├── utility_tools.py        # Utility MCP tools
│       │   └── tool_schemas.py         # Tool input/output schemas
│       │
│       ├── reports/
│       │   ├── __init__.py
│       │   ├── report_generator.py     # Report compilation
│       │   ├── template_manager.py     # Report templates
│       │   ├── export_formats.py       # Multiple export formats
│       │   └── visualization.py        # Charts and graphs
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── research_models.py      # Research data models
│       │   ├── content_models.py       # Content data models
│       │   ├── analysis_models.py      # Analysis result models
│       │   └── response_models.py      # API response models
│       │
│       └── utils/
│           ├── __init__.py
│           ├── logger.py               # Logging configuration
│           ├── validators.py           # Input validation
│           ├── decorators.py           # Common decorators
│           ├── constants.py            # System constants
│           └── helpers.py              # Helper functions
│
├── config/
│   ├── models.yaml                     # Ollama model configurations
│   ├── search_sources.yaml             # Search engine configurations
│   ├── extraction_rules.yaml           # Content extraction rules
│   ├── analysis_templates.yaml         # Analysis prompt templates
│   └── logging.yaml                    # Logging configuration
│
├── data/
│   ├── models/                         # Downloaded models
│   ├── cache/                          # Cached search results
│   ├── vector_store/                   # ChromaDB data
│   └── knowledge_graphs/               # Generated knowledge graphs
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                     # Pytest configuration
│   ├── unit/
│   │   ├── test_search/
│   │   ├── test_extraction/
│   │   ├── test_analysis/
│   │   └── test_tools/
│   ├── integration/
│   │   ├── test_search_flow.py
│   │   ├── test_analysis_flow.py
│   │   └── test_mcp_integration.py
│   └── e2e/
│       ├── test_research_workflow.py
│       └── test_complete_pipeline.py
│
├── docs/
│   ├── README.md
│   ├── installation.md
│   ├── configuration.md
│   ├── api_reference.md
│   ├── user_guide.md
│   ├── developer_guide.md
│   ├── troubleshooting.md
│   └── examples/
│       ├── basic_research.md
│       ├── academic_research.md
│       └── business_analysis.md
│
├── scripts/
│   ├── setup.sh                       # Initial setup script
│   ├── download_models.sh              # Model download script
│   ├── start_server.sh                 # Server startup script
│   └── run_tests.sh                    # Test execution script
│
└── examples/
    ├── basic_usage.py
    ├── academic_research.py
    ├── market_research.py
    ├── fact_checking.py
    └── knowledge_graph_demo.py

## Functional Requirements

### 4.1 Core Research Tools

#### FR-001: Multi-Source Web Search
- **Description**: Aggregate search results from multiple free search engines
- **Input**: Search query, result count, source preferences
- **Output**: Ranked search results with metadata
- **Priority**: High
- **Dependencies**: DuckDuckGo API, SearX instances

#### FR-002: Content Extraction and Processing
- **Description**: Extract and clean content from web pages and documents
- **Input**: URLs, file paths, extraction parameters
- **Output**: Cleaned text content with metadata
- **Priority**: High
- **Dependencies**: BeautifulSoup, PyMuPDF, Selenium

#### FR-003: AI-Powered Content Summarization
- **Description**: Generate intelligent summaries using local LLMs
- **Input**: Text content, summary length, focus areas
- **Output**: Structured summaries with key points
- **Priority**: High
- **Dependencies**: Ollama, LangChain

#### FR-004: Academic Paper Analysis
- **Description**: Search and analyze academic papers from multiple sources
- **Input**: Research query, publication filters
- **Output**: Paper summaries with citations and relevance scores
- **Priority**: Medium
- **Dependencies**: arXiv API, Semantic Scholar API

#### FR-005: Knowledge Graph Generation
- **Description**: Create visual knowledge graphs from research findings
- **Input**: Research results, relationship parameters
- **Output**: Interactive knowledge graph data
- **Priority**: Medium
- **Dependencies**: NetworkX, Graph visualization libraries

#### FR-006: Cross-Source Fact Checking
- **Description**: Verify claims across multiple reliable sources
- **Input**: Claims/statements, verification depth
- **Output**: Fact-check results with source citations
- **Priority**: Medium
- **Dependencies**: Multiple search sources, NLP analysis

#### FR-007: Research Report Generation
- **Description**: Compile findings into structured research reports
- **Input**: Research session data, report template
- **Output**: Formatted research report (multiple formats)
- **Priority**: Medium
- **Dependencies**: Report templates, Export libraries

#### FR-008: Research Session Management
- **Description**: Manage research sessions and maintain context
- **Input**: Session parameters, research history
- **Output**: Persistent research sessions
- **Priority**: Low
- **Dependencies**: Session storage, Context management

### 4.2 Analysis and Intelligence Tools

#### FR-009: Sentiment Analysis
- **Description**: Analyze sentiment of research content
- **Input**: Text content, analysis scope
- **Output**: Sentiment scores and emotional indicators
- **Priority**: Low
- **Dependencies**: NLP libraries, Sentiment models

#### FR-010: Topic Modeling
- **Description**: Identify and categorize topics in research content
- **Input**: Document collection, topic count
- **Output**: Topic clusters with representative keywords
- **Priority**: Low
- **Dependencies**: Topic modeling algorithms

#### FR-011: Research Question Generation
- **Description**: Generate relevant research questions from content
- **Input**: Research domain, content context
- **Output**: Prioritized research questions
- **Priority**: Medium
- **Dependencies**: LLM analysis, Question templates

#### FR-012: Citation and Reference Management
- **Description**: Extract and format citations from research sources
- **Input**: Academic content, citation style
- **Output**: Properly formatted citations
- **Priority**: Medium
- **Dependencies**: Citation parsing libraries

#### FR-013: Trend Analysis
- **Description**: Identify trends and patterns in research data
- **Input**: Time-series research data, analysis parameters
- **Output**: Trend reports with visualizations
- **Priority**: Low
- **Dependencies**: Statistical analysis libraries

#### FR-014: Research Recommendation Engine
- **Description**: Suggest related research areas and sources
- **Input**: Current research context, user preferences
- **Output**: Recommended research directions
- **Priority**: Low
- **Dependencies**: Machine learning models, Content similarity

## System Architecture

### 7.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Client Layer                         │
│              (Claude, VSCode, etc.)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ MCP Protocol
┌─────────────────────▼───────────────────────────────────────┐
│                MCP Server Core                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │Tool Registry│ │Error Handler│ │Config Mgr   │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Research Tools Layer                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │Search Tools │ │Analysis Tools│ │Export Tools │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────┬───────────────┬───────────────┬─────────────────────────┘
      │               │               │
┌─────▼─────┐ ┌───────▼───────┐ ┌─────▼─────┐
│Search     │ │Analysis       │ │Storage    │
│Engine     │ │Engine         │ │Engine     │
│Layer      │ │Layer          │ │Layer      │
└───────────┘ └───────────────┘ └───────────┘
```

### 7.2 Web Search Architecture

#### 7.2.1 Multi-Source Search Flow

```
Search Query
    │
    ▼
┌─────────────────┐
│Search Aggregator│
└─────────────────┘
    │
    ├─── DuckDuckGo Search ──┐
    │                        │
    ├─── SearX Search ────────┤
    │                        │
    ├─── Academic Search ─────┤
    │                        │
    └─── Selenium Search ─────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │Result Normalizer│
                    └─────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │Relevance Scorer │
                    └─────────────────┘
                             │
                             ▼
                      Ranked Results
```

### 7.3 Content Extraction Architecture

#### 7.3.1 Multi-Format Extraction Pipeline

```
Content URL/File
    │
    ▼
┌─────────────────┐
│Content Detector │ ── Detect: HTML, PDF, DOC, etc.
└─────────────────┘
    │
    ├─── Web Extractor ────── BeautifulSoup + trafilatura
    │
    ├─── PDF Extractor ────── PyMuPDF
    │
    ├─── DOC Extractor ────── python-docx
    │
    └─── JS-heavy Sites ───── Selenium
                │
                ▼
        ┌─────────────────┐
        │Content Cleaner  │ ── Remove ads, nav, boilerplate
        └─────────────────┘
                │
                ▼
        ┌─────────────────┐
        │Text Normalizer  │ ── Clean encoding, format
        └─────────────────┘
                │
                ▼
          Clean Text Output
```

### 7.4 AI Analysis Architecture

#### 7.4.1 Local LLM Processing Flow

```
Research Content
    │
    ▼
┌─────────────────┐
│Content Chunker  │ ── Split large content
└─────────────────┘
    │
    ▼
┌─────────────────┐
│Ollama LLM       │ ── Local models (Llama2, Mistral)
│Processing       │
└─────────────────┘
    │
    ├─── Summarization ───┐
    │                     │
    ├─── Insight Extract ─┤
    │                     │
    ├─── Fact Checking ───┤
    │                     │
    └─── Q&A Generation ──┘
                          │
                          ▼
                 ┌─────────────────┐
                 │Result Aggregator│
                 └─────────────────┘
                          │
                          ▼
                   Analysis Results
```

### 7.5 Data Flow Architecture

```
Search Query → Search Aggregator → Multiple Search Sources
     ↓
Content URLs → Content Extractor → Clean Text Content
     ↓
Text Content → AI Analyzer → Insights & Summaries
     ↓
Analysis Results → Knowledge Graph → Visual Representation
     ↓
Final Results → Report Generator → Formatted Output
```

## User Stories

### 10.1 Researcher User Stories

#### US-001: Basic Web Research
**As a researcher**  
I want to search multiple sources simultaneously  
So that I can get comprehensive results without manually checking each source

**Acceptance Criteria:**
- Can search DuckDuckGo, SearX, and academic sources in one query
- Results are aggregated and ranked by relevance
- Search completes within 10 seconds for standard queries
- Duplicate results are automatically filtered

#### US-002: Academic Paper Analysis
**As an academic researcher**  
I want to analyze academic papers from arXiv and Semantic Scholar  
So that I can quickly understand key findings and methodologies

**Acceptance Criteria:**
- Can search academic databases with subject filters
- Papers are automatically summarized with key points
- Citations are extracted and formatted correctly
- Related papers are suggested based on content similarity

#### US-003: Content Summarization
**As a content analyst**  
I want to get AI-generated summaries of web articles and documents  
So that I can quickly understand large volumes of content

**Acceptance Criteria:**
- Can summarize web pages, PDFs, and documents
- Multiple summary types available (brief, detailed, executive)
- Key insights and trends are highlighted
- Summary accuracy is validated against source content

#### US-004: Fact Verification
**As a journalist**  
I want to verify claims across multiple reliable sources  
So that I can ensure information accuracy in my reporting

**Acceptance Criteria:**
- Can fact-check specific claims or statements
- Results show verification status with confidence scores
- Source citations are provided for all verifications
- Contradictory information is clearly highlighted

#### US-005: Knowledge Graph Creation
**As a data analyst**  
I want to visualize relationships between research entities  
So that I can understand complex topic interconnections

**Acceptance Criteria:**
- Can generate interactive knowledge graphs from research content
- Entities and relationships are automatically extracted
- Graph can be exported in multiple formats
- Interactive exploration features are available

### 10.2 Student User Stories

#### US-006: Literature Review Assistance
**As a graduate student**  
I want to compile research from multiple sources for literature reviews  
So that I can efficiently gather relevant academic sources

**Acceptance Criteria:**
- Can search across academic databases and web sources
- Results are categorized by research themes
- Citation formats are automatically generated
- Research gaps and opportunities are identified

#### US-007: Research Question Generation
**As an undergraduate student**  
I want to generate research questions from topic exploration  
So that I can develop focused research proposals

**Acceptance Criteria:**
- Can analyze topic content to suggest research questions
- Questions are ranked by feasibility and originality
- Background context is provided for each question
- Related research areas are suggested

### 10.3 Business Analyst User Stories

#### US-008: Market Research Analysis
**As a business analyst**  
I want to research market trends and competitor information  
So that I can provide data-driven business recommendations

**Acceptance Criteria:**
- Can search for industry reports and market data
- Trend analysis is performed on collected data
- Competitor information is automatically categorized
- Business insights are extracted and prioritized

#### US-009: Research Report Generation
**As a consultant**  
I want to generate professional research reports from my findings  
So that I can deliver comprehensive analysis to clients

**Acceptance Criteria:**
- Can compile research sessions into formatted reports
- Multiple report templates are available
- Charts and visualizations are automatically generated
- Reports can be exported in various formats (PDF, HTML, Word)

### 10.4 Developer User Stories

#### US-010: MCP Integration
**As a developer**  
I want to integrate research capabilities into my AI assistant  
So that my application can provide intelligent research features

**Acceptance Criteria:**
- MCP server can be easily configured and deployed
- All tools are accessible through MCP protocol
- Comprehensive API documentation is available
- Error handling provides clear feedback

## Examples