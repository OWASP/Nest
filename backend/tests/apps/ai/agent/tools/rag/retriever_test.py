"""Tests for the RAG Retriever."""

import os
from unittest.mock import MagicMock, patch

import openai
import pytest

from apps.ai.agent.tools.rag.retriever import Retriever


class TestRetriever:
    """Test cases for the Retriever class."""

    def test_init_success(self):
        """Test successful initialization with API key."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            retriever = Retriever(embedding_model="custom-model")

            assert retriever.embedding_model == "custom-model"
            assert retriever.openai_client == mock_client
            mock_openai.assert_called_once_with(api_key="test-key")

    def test_init_no_api_key(self):
        """Test initialization fails when API key is not set."""
        with (
            patch.dict(os.environ, {}, clear=True),
            pytest.raises(
                ValueError,
                match="DJANGO_OPEN_AI_SECRET_KEY environment variable not set",
            ),
        ):
            Retriever()

    def test_init_default_model(self):
        """Test initialization with default embedding model."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI"),
        ):
            retriever = Retriever()
            assert retriever.embedding_model == "text-embedding-3-small"

    def test_get_query_embedding_success(self):
        """Test successful query embedding generation."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client

            retriever = Retriever()
            result = retriever.get_query_embedding("test query")

            assert result == [0.1, 0.2, 0.3]
            mock_client.embeddings.create.assert_called_once_with(
                input=["test query"], model="text-embedding-3-small"
            )

    def test_get_query_embedding_openai_error(self):
        """Test query embedding with OpenAI API error."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_client.embeddings.create.side_effect = openai.OpenAIError("API Error")
            mock_openai.return_value = mock_client

            retriever = Retriever()

            with pytest.raises(openai.OpenAIError):
                retriever.get_query_embedding("test query")

    def test_get_query_embedding_unexpected_error(self):
        """Test query embedding with unexpected error."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_client.embeddings.create.side_effect = Exception("Unexpected error")
            mock_openai.return_value = mock_client

            retriever = Retriever()

            with pytest.raises(Exception, match="Unexpected error"):
                retriever.get_query_embedding("test query")

    def test_get_source_name_with_name(self):
        """Test getting source name when object has name attribute."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI"),
        ):
            retriever = Retriever()

            entity = MagicMock()
            entity.name = "Test Name"
            entity.title = "Test Title"

            result = retriever.get_source_name(entity)
            assert result == "Test Name"

    def test_get_source_name_with_title(self):
        """Test getting source name when object has title but no name."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI"),
        ):
            retriever = Retriever()

            entity = MagicMock()
            entity.name = None
            entity.title = "Test Title"
            entity.login = "test_login"

            result = retriever.get_source_name(entity)
            assert result == "Test Title"

    def test_get_source_name_with_login(self):
        """Test getting source name when object has login but no name/title."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI"),
        ):
            retriever = Retriever()

            entity = MagicMock()
            entity.name = None
            entity.title = None
            entity.login = "test_login"
            entity.key = "test_key"

            result = retriever.get_source_name(entity)
            assert result == "test_login"

    def test_get_source_name_fallback_to_str(self):
        """Test getting source name falls back to string representation."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI"),
        ):
            retriever = Retriever()

            entity = MagicMock()
            entity.name = None
            entity.title = None
            entity.login = None
            entity.key = None
            entity.summary = None
            entity.__str__ = MagicMock(return_value="String representation")

            result = retriever.get_source_name(entity)
            assert result == "String representation"

    def test_get_additional_context_chapter(self):
        """Test getting additional context for chapter content type."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI"),
        ):
            retriever = Retriever()

            content_object = MagicMock()
            content_object.__class__.__name__ = "Chapter"
            content_object.suggested_location = "New York"
            content_object.region = "North America"
            content_object.country = "USA"
            content_object.postal_code = "10001"
            content_object.currency = "USD"
            content_object.meetup_group = "OWASP NYC"
            content_object.tags = ["security", "web"]
            content_object.topics = ["OWASP Top 10"]
            content_object.leaders_raw = ["John Doe", "Jane Smith"]
            content_object.related_urls = ["https://example.com"]
            content_object.is_active = True
            content_object.url = "https://owasp.org/chapter"

            result = retriever.get_additional_context(content_object)

            expected_keys = [
                "location",
                "region",
                "country",
                "postal_code",
                "currency",
                "meetup_group",
                "tags",
                "topics",
                "leaders",
                "related_urls",
                "is_active",
                "url",
            ]
            for key in expected_keys:
                assert key in result

    def test_get_additional_context_project(self):
        """Test getting additional context for project content type."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI"),
        ):
            retriever = Retriever()

            content_object = MagicMock()
            content_object.__class__.__name__ = "Project"
            content_object.level = "flagship"
            content_object.type = "tool"
            content_object.languages = ["python"]
            content_object.topics = ["security"]
            content_object.licenses = ["MIT"]
            content_object.tags = ["web"]
            content_object.custom_tags = ["api"]
            content_object.stars_count = 100
            content_object.forks_count = 20
            content_object.contributors_count = 5
            content_object.releases_count = 3
            content_object.open_issues_count = 2
            content_object.leaders_raw = ["Alice"]
            content_object.related_urls = ["https://project.example.com"]
            content_object.created_at = "2023-01-01"
            content_object.updated_at = "2023-01-02"
            content_object.released_at = "2023-01-03"
            content_object.health_score = 85.5
            content_object.is_active = True
            content_object.track_issues = True
            content_object.url = "https://owasp.org/project"

            result = retriever.get_additional_context(content_object)

            expected_keys = [
                "level",
                "project_type",
                "languages",
                "topics",
                "licenses",
                "tags",
                "custom_tags",
                "stars_count",
                "forks_count",
                "contributors_count",
                "releases_count",
                "open_issues_count",
                "leaders",
                "related_urls",
                "created_at",
                "updated_at",
                "released_at",
                "health_score",
                "is_active",
                "track_issues",
                "url",
            ]
            for key in expected_keys:
                assert key in result

    def test_get_additional_context_event(self):
        """Test getting additional context for event content type."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI"),
        ):
            retriever = Retriever()

            content_object = MagicMock()
            content_object.__class__.__name__ = "Event"
            content_object.start_date = "2023-01-01"
            content_object.end_date = "2023-01-02"
            content_object.suggested_location = "San Francisco"
            content_object.category = "conference"
            content_object.latitude = 37.7749
            content_object.longitude = -122.4194
            content_object.url = "https://event.example.com"
            content_object.description = "Test event description"
            content_object.summary = "Test event summary"

            result = retriever.get_additional_context(content_object)

            expected_keys = [
                "start_date",
                "end_date",
                "location",
                "category",
                "latitude",
                "longitude",
                "url",
                "description",
                "summary",
            ]
            for key in expected_keys:
                assert key in result

    def test_get_additional_context_committee(self):
        """Test getting additional context for committee content type."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI"),
        ):
            retriever = Retriever()

            content_object = MagicMock()
            content_object.__class__.__name__ = "Committee"
            content_object.is_active = True
            content_object.leaders = ["John Doe", "Jane Smith"]
            content_object.url = "https://committee.example.com"
            content_object.description = "Test committee description"
            content_object.summary = "Test committee summary"
            content_object.tags = ["security", "governance"]
            content_object.topics = ["policy", "standards"]
            content_object.related_urls = ["https://related.example.com"]

            result = retriever.get_additional_context(content_object)

            expected_keys = [
                "is_active",
                "leaders",
                "url",
                "description",
                "summary",
                "tags",
                "topics",
                "related_urls",
            ]
            for key in expected_keys:
                assert key in result

    def test_get_additional_context_message_with_conversation_but_no_attributes(self):
        """Test additional context for message with conversation lacking slack_channel_id."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI"),
        ):
            retriever = Retriever()
            conversation = MagicMock(spec=[])
            parent_message = MagicMock(spec=[])
            author = MagicMock(spec=[])
            content_object = MagicMock()
            content_object.__class__.__name__ = "Message"
            content_object.conversation = conversation
            content_object.parent_message = parent_message
            content_object.ts = "1234567891.123456"
            content_object.author = author

            result = retriever.get_additional_context(content_object)

            assert "channel" not in result or result.get("channel") is None
            assert "thread_ts" not in result or result.get("thread_ts") is None
            assert "user" not in result or result.get("user") is None

    def test_get_additional_context_message_with_falsy_conversation(self):
        """Test getting additional context for message when conversation evaluates to False."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI"),
        ):
            retriever = Retriever()

            content_object = MagicMock()
            content_object.__class__.__name__ = "Message"
            content_object.conversation = 0
            content_object.parent_message = False
            content_object.author = ""
            content_object.ts = "1234567891.123456"

            result = retriever.get_additional_context(content_object)

            assert result["ts"] == "1234567891.123456"
            assert "channel" not in result or result.get("channel") is None
            assert "thread_ts" not in result or result.get("thread_ts") is None
            assert "user" not in result or result.get("user") is None
            assert result["ts"] == "1234567891.123456"

    def test_get_additional_context_unknown_content_type(self):
        """Test getting additional context for an unknown content type returns empty dict."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI"),
        ):
            retriever = Retriever()

            content_object = MagicMock()
            content_object.__class__.__name__ = "User"

            result = retriever.get_additional_context(content_object)

            assert result == {}

    def test_extract_content_types_from_query_single_type(self):
        """Test extracting single content type from query."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI"),
        ):
            retriever = Retriever()

            result = retriever.extract_content_types_from_query("Tell me about chapters")
            assert result == ["chapter"]

    def test_extract_content_types_from_query_multiple_types(self):
        """Test extracting multiple content types from query."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI"),
        ):
            retriever = Retriever()

            result = retriever.extract_content_types_from_query("Show me events and projects")
            assert set(result) == {"event", "project"}

    def test_extract_content_types_from_query_plural_forms(self):
        """Test extracting content types from query with plural forms."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI"),
        ):
            retriever = Retriever()

            result = retriever.extract_content_types_from_query("List all committees")
            assert result == ["committee"]

    def test_extract_content_types_from_query_no_matches(self):
        """Test extracting content types when no matches found."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI"),
        ):
            retriever = Retriever()

            result = retriever.extract_content_types_from_query("Random query with no keywords")
            assert result == []

    def test_supported_content_types(self):
        """Test that supported content types are defined correctly."""
        assert set(Retriever.SUPPORTED_ENTITY_TYPES) == {
            "chapter",
            "committee",
            "event",
            "message",
            "project",
        }

    @patch("apps.ai.agent.tools.rag.retriever.Chunk")
    def test_retrieve_with_app_label_content_types(self, mock_chunk):
        """Test retrieve method with app_label.model content types filter."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client

            mock_annotated = MagicMock()
            mock_filtered = MagicMock()
            mock_final = MagicMock()

            mock_chunk.objects.annotate.return_value = mock_annotated
            mock_annotated.filter.return_value = mock_filtered
            mock_filtered.filter.return_value = mock_final
            mock_final.select_related.return_value = mock_final
            mock_final.order_by.return_value = mock_final
            mock_final.__getitem__ = MagicMock(return_value=[])

            retriever = Retriever()
            result = retriever.retrieve("test query", content_types=["owasp.chapter"])

            assert result == []
            mock_chunk.objects.annotate.assert_called_once()
            mock_annotated.filter.assert_called_once()
            mock_filtered.filter.assert_called_once()

    @patch("apps.ai.agent.tools.rag.retriever.Chunk")
    def test_retrieve_successful_with_chunks(self, mock_chunk):
        """Test retrieve method with successful chunk retrieval."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client

            mock_content_object = MagicMock()
            mock_content_object.name = "Test Chapter"
            mock_content_object.__class__.__name__ = "Chapter"
            mock_content_object.suggested_location = "New York"

            mock_entity_type = MagicMock()
            mock_entity_type.model = "chapter"

            mock_context = MagicMock()
            mock_context.entity = mock_content_object
            mock_context.entity_type = mock_entity_type
            mock_context.entity_id = "123"

            mock_chunk_instance = MagicMock()
            mock_chunk_instance.id = 1
            mock_chunk_instance.text = "Test chunk text"
            mock_chunk_instance.similarity = 0.85
            mock_chunk_instance.context = mock_context

            mock_annotated = MagicMock()
            mock_filtered = MagicMock()

            mock_chunk.objects.annotate.return_value = mock_annotated
            mock_annotated.filter.return_value = mock_filtered
            mock_filtered.select_related.return_value = mock_filtered
            mock_filtered.order_by.return_value = mock_filtered
            mock_filtered.__getitem__ = MagicMock(return_value=[mock_chunk_instance])

            retriever = Retriever()
            result = retriever.retrieve("test query")

            assert len(result) == 1
            assert result[0]["text"] == "Test chunk text"
            assert result[0]["source_type"] == "chapter"
            assert result[0]["source_name"] == "Test Chapter"
            assert result[0]["source_id"] == "123"
            assert "additional_context" in result[0]

    @patch("apps.ai.agent.tools.rag.retriever.Chunk")
    def test_retrieve_with_content_types_filter(self, mock_chunk):
        """Test retrieve method with content types filter."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client

            mock_annotated = MagicMock()
            mock_filtered = MagicMock()
            mock_final = MagicMock()

            mock_chunk.objects.annotate.return_value = mock_annotated
            mock_annotated.filter.return_value = mock_filtered
            mock_filtered.filter.return_value = mock_final
            mock_final.select_related.return_value = mock_final
            mock_final.order_by.return_value = mock_final
            mock_final.__getitem__ = MagicMock(return_value=[])

            retriever = Retriever()
            result = retriever.retrieve("test query", content_types=["chapter"])

            assert result == []
            mock_chunk.objects.annotate.assert_called_once()
            mock_annotated.filter.assert_called_once()
            mock_filtered.filter.assert_called_once()

    @patch("apps.ai.agent.tools.rag.retriever.logger")
    @patch("apps.ai.agent.tools.rag.retriever.Chunk")
    def test_retrieve_with_none_content_object(self, mock_chunk, mock_logger):
        """Test retrieve method when content object is None."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client

            mock_chunk_instance = MagicMock()
            mock_chunk_instance.id = 1
            mock_chunk_instance.context = None

            mock_annotated = MagicMock()
            mock_filtered = MagicMock()

            mock_chunk.objects.annotate.return_value = mock_annotated
            mock_annotated.filter.return_value = mock_filtered
            mock_filtered.select_related.return_value = mock_filtered
            mock_filtered.order_by.return_value = mock_filtered
            mock_filtered.__getitem__ = MagicMock(return_value=[mock_chunk_instance])

            retriever = Retriever()
            result = retriever.retrieve("test query")

            assert result == []
            mock_logger.warning.assert_called_once_with(
                "Content object is None for chunk %s. Skipping.", 1
            )

    def test_get_additional_context_message_with_author(self):
        """Test getting additional context for message with named author."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI"),
        ):
            retriever = Retriever()

            conversation = MagicMock()
            conversation.slack_channel_id = "C123456"

            parent_message = MagicMock()
            parent_message.ts = "1234567890.123456"

            author = MagicMock()
            author.name = "John Doe"

            content_object = MagicMock()
            content_object.__class__.__name__ = "Message"
            content_object.conversation = conversation
            content_object.parent_message = parent_message
            content_object.ts = "1234567890.654321"
            content_object.author = author

            result = retriever.get_additional_context(content_object)

            assert result["channel"] == "C123456"
            assert result["thread_ts"] == "1234567890.123456"
            assert result["ts"] == "1234567890.654321"
            assert result["user"] == "John Doe"

    def test_get_additional_context_message_none_fields(self):
        """Test getting additional context for message with None fields."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI"),
        ):
            retriever = Retriever()

            content_object = MagicMock()
            content_object.__class__.__name__ = "Message"
            content_object.conversation = None
            content_object.parent_message = None
            content_object.ts = "1234567890.654321"
            content_object.author = None

            result = retriever.get_additional_context(content_object)

            assert result.get("channel") is None
            assert result.get("thread_ts") is None
            assert result["ts"] == "1234567890.654321"
            assert result.get("user") is None
