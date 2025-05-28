import pytest
from unittest.mock import Mock, patch
from research_assistant.knowledge_graph.graph_manager import GraphManager
from research_assistant.knowledge_graph.builders.concept_builder import ConceptBuilder
from research_assistant.knowledge_graph.builders.relationship_builder import RelationshipBuilder

class TestGraphManager:
    @pytest.fixture
    def graph_manager(self):
        return GraphManager()

    def test_initialize_builders(self, graph_manager):
        """Test initialization of graph builders."""
        assert isinstance(graph_manager.concept_builder, ConceptBuilder)
        assert isinstance(graph_manager.relationship_builder, RelationshipBuilder)

    @patch("research_assistant.knowledge_graph.builders.concept_builder.ConceptBuilder.build")
    @patch("research_assistant.knowledge_graph.builders.relationship_builder.RelationshipBuilder.build")
    async def test_build_graph(self, mock_relationship, mock_concept, graph_manager, mock_graph_request):
        """Test knowledge graph building."""
        mock_concept.return_value = [
            {"id": "1", "label": "Concept 1", "type": "concept"},
            {"id": "2", "label": "Concept 2", "type": "concept"}
        ]
        mock_relationship.return_value = [
            {
                "source": "1",
                "target": "2",
                "label": "related_to",
                "weight": 0.8
            }
        ]

        result = await graph_manager.build_graph(mock_graph_request)
        
        assert "nodes" in result
        assert "edges" in result
        assert len(result["nodes"]) == 2
        assert len(result["edges"]) == 1
        mock_concept.assert_called_once()
        mock_relationship.assert_called_once()

    @patch("research_assistant.knowledge_graph.builders.concept_builder.ConceptBuilder.build")
    async def test_build_graph_with_depth(self, mock_concept, graph_manager, mock_graph_request):
        """Test graph building with depth limit."""
        mock_concept.return_value = [
            {"id": "1", "label": "Concept 1", "type": "concept"},
            {"id": "2", "label": "Concept 2", "type": "concept"},
            {"id": "3", "label": "Concept 3", "type": "concept"}
        ]

        mock_graph_request["options"]["depth"] = 1
        result = await graph_manager.build_graph(mock_graph_request)
        
        assert len(result["nodes"]) <= 2  # Should respect depth limit
        mock_concept.assert_called_once()

    @patch("research_assistant.knowledge_graph.builders.concept_builder.ConceptBuilder.build")
    async def test_build_graph_with_confidence(self, mock_concept, graph_manager, mock_graph_request):
        """Test graph building with confidence threshold."""
        mock_concept.return_value = [
            {"id": "1", "label": "Concept 1", "type": "concept", "confidence": 0.9},
            {"id": "2", "label": "Concept 2", "type": "concept", "confidence": 0.5}
        ]

        mock_graph_request["options"]["min_confidence"] = 0.8
        result = await graph_manager.build_graph(mock_graph_request)
        
        assert len(result["nodes"]) == 1  # Only high confidence concepts
        assert result["nodes"][0]["confidence"] >= 0.8
        mock_concept.assert_called_once()

    async def test_build_graph_invalid_request(self, graph_manager, mock_graph_request):
        """Test graph building with invalid request."""
        del mock_graph_request["topic"]
        
        with pytest.raises(ValueError, match="Invalid graph request"):
            await graph_manager.build_graph(mock_graph_request)

    @patch("research_assistant.knowledge_graph.builders.concept_builder.ConceptBuilder.build")
    async def test_build_graph_timeout(self, mock_concept, graph_manager, mock_graph_request):
        """Test graph building timeout handling."""
        mock_concept.side_effect = TimeoutError("Graph building timed out")
        
        with pytest.raises(TimeoutError, match="Graph building timed out"):
            await graph_manager.build_graph(mock_graph_request)

    def test_validate_graph_request(self, graph_manager, mock_graph_request):
        """Test graph request validation."""
        # Test valid request
        assert graph_manager.validate_graph_request(mock_graph_request) is True

        # Test invalid request (missing required field)
        invalid_request = mock_graph_request.copy()
        del invalid_request["topic"]
        assert graph_manager.validate_graph_request(invalid_request) is False

        # Test invalid request (invalid depth)
        invalid_request = mock_graph_request.copy()
        invalid_request["options"]["depth"] = -1
        assert graph_manager.validate_graph_request(invalid_request) is False

    @patch("research_assistant.knowledge_graph.builders.concept_builder.ConceptBuilder.build")
    async def test_build_graph_with_metadata(self, mock_concept, graph_manager, mock_graph_request):
        """Test graph building with metadata."""
        mock_concept.return_value = [
            {
                "id": "1",
                "label": "Concept 1",
                "type": "concept",
                "metadata": {
                    "source": "source1",
                    "timestamp": "2024-03-15"
                }
            }
        ]

        mock_graph_request["options"]["include_metadata"] = True
        result = await graph_manager.build_graph(mock_graph_request)
        
        assert "metadata" in result["nodes"][0]
        assert "source" in result["nodes"][0]["metadata"]
        mock_concept.assert_called_once()

    @patch("research_assistant.knowledge_graph.builders.concept_builder.ConceptBuilder.build")
    async def test_build_graph_with_circular_references(self, mock_concept, graph_manager, mock_graph_request):
        """Test graph building with circular references."""
        mock_concept.return_value = [
            {"id": "1", "label": "Concept 1", "type": "concept"},
            {"id": "2", "label": "Concept 2", "type": "concept"},
            {"id": "1", "label": "Concept 1", "type": "concept"}  # Duplicate
        ]

        result = await graph_manager.build_graph(mock_graph_request)
        
        assert len(result["nodes"]) == 2  # Duplicates should be removed
        mock_concept.assert_called_once()

    @patch("research_assistant.knowledge_graph.builders.concept_builder.ConceptBuilder.build")
    async def test_build_graph_with_hierarchical_structure(self, mock_concept, graph_manager, mock_graph_request):
        """Test graph building with hierarchical structure."""
        mock_concept.return_value = [
            {"id": "1", "label": "Parent", "type": "concept"},
            {"id": "2", "label": "Child 1", "type": "concept"},
            {"id": "3", "label": "Child 2", "type": "concept"}
        ]

        result = await graph_manager.build_graph(mock_graph_request)
        
        assert len(result["nodes"]) == 3
        assert any(node["label"] == "Parent" for node in result["nodes"])
        mock_concept.assert_called_once() 