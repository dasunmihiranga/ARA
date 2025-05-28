import pytest
import os
import sys
from pathlib import Path
import yaml
import logging
from unittest.mock import Mock, patch

# Add src directory to Python path
src_path = str(Path(__file__).parent.parent / "src")
sys.path.append(src_path)

from research_assistant import ResearchAssistant
from research_assistant.core.tool_registry import ToolRegistry
from research_assistant.storage.vector_store import VectorStore
from research_assistant.llm.ollama_client import OllamaClient

# Test configuration
TEST_CONFIG = {
    "logging": {
        "level": "DEBUG",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "handlers": ["console"]
    },
    "search": {
        "timeout": 10,
        "max_results": 5,
        "sources": ["duckduckgo", "searx"]
    },
    "extraction": {
        "timeout": 30,
        "clean_html": True,
        "remove_ads": True
    },
    "analysis": {
        "timeout": 60,
        "max_length": 200,
        "confidence_threshold": 0.8
    },
    "storage": {
        "vector_store": {
            "type": "chroma",
            "path": "tests/data/vector_store"
        },
        "cache": {
            "type": "memory",
            "ttl": 3600
        }
    }
}

@pytest.fixture(scope="session")
def test_config():
    """Fixture for test configuration."""
    return TEST_CONFIG

@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture for test data directory."""
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir

@pytest.fixture(scope="session")
def vector_store():
    """Fixture for VectorStore instance."""
    store = VectorStore()
    yield store
    # Cleanup
    store.clear()

@pytest.fixture(scope="session")
def ollama_client():
    """Fixture for OllamaClient instance."""
    return OllamaClient()

@pytest.fixture(scope="session")
def tool_registry():
    """Fixture for ToolRegistry instance."""
    return ToolRegistry()

@pytest.fixture(scope="session")
def research_assistant():
    """Fixture for ResearchAssistant instance."""
    assistant = ResearchAssistant()
    yield assistant
    # Cleanup
    assistant.close()

@pytest.fixture
def mock_search_results():
    """Fixture for mock search results."""
    return [
        {
            "title": "Test Result 1",
            "url": "https://example.com/1",
            "snippet": "This is a test result",
            "source": "duckduckgo",
            "relevance_score": 0.9
        },
        {
            "title": "Test Result 2",
            "url": "https://example.com/2",
            "snippet": "Another test result",
            "source": "searx",
            "relevance_score": 0.8
        }
    ]

@pytest.fixture
def mock_content():
    """Fixture for mock content."""
    return {
        "text": "This is a test content for analysis.",
        "metadata": {
            "title": "Test Content",
            "author": "Test Author",
            "date": "2024-03-15"
        }
    }

@pytest.fixture
def mock_analysis_result():
    """Fixture for mock analysis result."""
    return {
        "summary": "Test summary",
        "key_points": ["Point 1", "Point 2"],
        "confidence_score": 0.95
    }

@pytest.fixture
def mock_knowledge_graph():
    """Fixture for mock knowledge graph."""
    return {
        "nodes": [
            {"id": "1", "label": "Concept 1", "type": "concept"},
            {"id": "2", "label": "Concept 2", "type": "concept"}
        ],
        "edges": [
            {
                "source": "1",
                "target": "2",
                "label": "related_to",
                "weight": 0.8
            }
        ]
    }

@pytest.fixture
def mock_report():
    """Fixture for mock report."""
    return {
        "title": "Test Report",
        "content": "This is a test report content",
        "sections": [
            {"title": "Section 1", "content": "Content 1"},
            {"title": "Section 2", "content": "Content 2"}
        ],
        "metadata": {
            "generated_at": "2024-03-15",
            "page_count": 2
        }
    }

@pytest.fixture
def mock_search_query():
    """Fixture for mock search query."""
    return {
        "query": "test query",
        "max_results": 5,
        "sources": ["duckduckgo", "searx"],
        "filters": {
            "date_range": {
                "start": "2024-01-01",
                "end": "2024-12-31"
            }
        }
    }

@pytest.fixture
def mock_extraction_request():
    """Fixture for mock extraction request."""
    return {
        "url": "https://example.com/test",
        "type": "web",
        "options": {
            "clean_html": True,
            "remove_ads": True,
            "extract_metadata": True
        }
    }

@pytest.fixture
def mock_analysis_request():
    """Fixture for mock analysis request."""
    return {
        "content": "Test content for analysis",
        "analysis_type": "summarize",
        "options": {
            "max_length": 200,
            "focus_areas": ["key_points", "conclusions"],
            "confidence_threshold": 0.8
        }
    }

@pytest.fixture
def mock_graph_request():
    """Fixture for mock graph request."""
    return {
        "topic": "test topic",
        "sources": ["source1", "source2"],
        "options": {
            "depth": 2,
            "include_metadata": True,
            "min_confidence": 0.7
        }
    }

@pytest.fixture
def mock_report_request():
    """Fixture for mock report request."""
    return {
        "research_data": {
            "title": "Test Research",
            "content": "Test content"
        },
        "template": "academic",
        "format": "pdf",
        "options": {
            "include_visualizations": True,
            "include_citations": True
        }
    }

@pytest.fixture
def mock_error_response():
    """Fixture for mock error response."""
    return {
        "error": "Test error",
        "details": "This is a test error message",
        "code": "TEST_ERROR"
    }

@pytest.fixture
def mock_success_response():
    """Fixture for mock success response."""
    return {
        "status": "success",
        "data": {
            "message": "Operation completed successfully"
        }
    }

@pytest.fixture(autouse=True)
def setup_logging():
    """Setup logging for tests."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

@pytest.fixture(autouse=True)
def cleanup_test_data(test_data_dir):
    """Cleanup test data after each test."""
    yield
    # Cleanup test data directory
    for file in test_data_dir.glob("*"):
        if file.is_file():
            file.unlink() 