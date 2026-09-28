"""
Unit Tests: Phase 3 RAG Pipeline Integration
---------------------------------------------
Tests embedding service interface, retrieval relevance thresholding,
context formatting, structured prompt sections, and Gemini context injection
without making live network requests.
"""

import pytest
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from services.embedding_service import GeminiEmbeddingService
from services.retrieval_service import HealthRetrievalService, format_retrieved_context
from prompts.system_prompt import get_structured_prompt
from services.gemini_service import GeminiService


# ==========================================
# 1. Embedding Service Interface Tests
# ==========================================

def test_embedding_service_satisfies_langchain_interface():
    """Verifies that GeminiEmbeddingService implements LangChain's Embeddings interface."""
    service = GeminiEmbeddingService(api_key="test-key", dimensionality=3072)
    assert isinstance(service, Embeddings)
    assert hasattr(service, "embed_documents")
    assert hasattr(service, "embed_query")


def test_embed_query_empty_returns_zero_vector():
    """Verifies that an empty query returns a zero-vector of expected dimensionality."""
    service = GeminiEmbeddingService(api_key="test-key", dimensionality=3072)
    vector = service.embed_query("")
    assert len(vector) == 3072
    assert all(val == 0.0 for val in vector)


@patch("services.embedding_service.genai.Client")
def test_embed_query_mocked_success(mock_client_cls):
    """Verifies embed_query extracts float vector correctly from GenAI client response."""
    mock_instance = MagicMock()
    mock_client_cls.return_value = mock_instance

    mock_resp = MagicMock()
    mock_item = MagicMock()
    mock_item.values = [0.1, 0.2, 0.3]
    mock_resp.embeddings = [mock_item]
    mock_instance.models.embed_content.return_value = mock_resp

    service = GeminiEmbeddingService(api_key="test-key", dimensionality=3)
    vec = service.embed_query("What causes cramps?")

    assert vec == [0.1, 0.2, 0.3]
    mock_instance.models.embed_content.assert_called_once()


@patch("services.embedding_service.genai.Client")
def test_embed_documents_mocked_success(mock_client_cls):
    """Verifies embed_documents embeds multiple text snippets individually."""
    mock_instance = MagicMock()
    mock_client_cls.return_value = mock_instance

    mock_resp = MagicMock()
    item1 = MagicMock(values=[0.1, 0.2])
    item2 = MagicMock(values=[0.3, 0.4])
    mock_resp.embeddings = [item1, item2]
    mock_instance.models.embed_content.return_value = mock_resp

    service = GeminiEmbeddingService(api_key="test-key", dimensionality=2, batch_size=50)
    vectors = service.embed_documents(["chunk 1", "chunk 2"])

    assert len(vectors) == 2
    assert vectors[0] == [0.1, 0.2]
    assert vectors[1] == [0.3, 0.4]


# ==========================================
# 2. Retrieval & Relevance Threshold Tests
# ==========================================

def test_retrieval_empty_query_rejected():
    """Verifies that empty queries are rejected without querying vector store."""
    service = HealthRetrievalService()
    res = service.retrieve_relevant_documents("")
    assert not res["is_sufficient"]
    assert res["documents"] == []
    assert res["best_distance"] == 999.0


def test_retrieval_threshold_sufficient_match():
    """Verifies that results with cosine distance below threshold are marked sufficient."""
    service = HealthRetrievalService(distance_threshold=0.70)
    mock_store = MagicMock()
    
    mock_doc = Document(
        page_content="Menstrual hygiene practices include regular pad changes.",
        metadata={"source": "who.pdf", "page": 12, "topic": "menstrual_hygiene"}
    )
    # Cosine distance 0.45 <= 0.70 threshold -> sufficient
    mock_store.similarity_search_with_score.return_value = [(mock_doc, 0.45)]
    service._vector_store = mock_store

    res = service.retrieve_relevant_documents("What is menstrual hygiene?")
    assert res["is_sufficient"] is True
    assert res["best_distance"] == 0.45
    assert len(res["documents"]) == 1
    assert "Menstrual hygiene practices" in res["documents"][0].page_content


def test_retrieval_threshold_insufficient_match():
    """Verifies that results with cosine distance above threshold are marked insufficient."""
    service = HealthRetrievalService(distance_threshold=0.70)
    mock_store = MagicMock()
    
    mock_doc = Document(
        page_content="General text not specifically answering the question.",
        metadata={"source": "who.pdf", "page": 1, "topic": "general"}
    )
    # Cosine distance 0.88 > 0.70 threshold -> insufficient
    mock_store.similarity_search_with_score.return_value = [(mock_doc, 0.88)]
    service._vector_store = mock_store

    res = service.retrieve_relevant_documents("Who walked on the Moon?")
    assert res["is_sufficient"] is False
    assert res["best_distance"] == 0.88
    # Documents must be empty when insufficient to avoid grounding on irrelevant data
    assert res["documents"] == []


def test_retrieval_empty_results_from_store():
    """Verifies behavior when vector store returns zero matches."""
    service = HealthRetrievalService()
    mock_store = MagicMock()
    mock_store.similarity_search_with_score.return_value = []
    service._vector_store = mock_store

    res = service.retrieve_relevant_documents("Rare unknown condition")
    assert res["is_sufficient"] is False
    assert res["documents"] == []
    assert res["best_distance"] == 999.0


# ==========================================
# 3. Context Formatting Tests
# ==========================================

def test_format_retrieved_context_sufficient():
    """Verifies that sufficient retrieved documents are formatted cleanly with source tags."""
    doc = Document(
        page_content="Prostaglandins trigger uterine muscle contractions.",
        metadata={"source": "guidance.pdf", "page": 24, "topic": "menstrual_health"}
    )
    retrieval_result = {
        "is_sufficient": True,
        "best_distance": 0.52,
        "documents": [doc],
    }

    formatted = format_retrieved_context(retrieval_result)
    assert "--- EXCERPT 1" in formatted
    assert "guidance.pdf" in formatted
    assert "Page: 24" in formatted
    assert "Topic: menstrual_health" in formatted
    assert "Prostaglandins trigger uterine muscle contractions." in formatted


def test_format_retrieved_context_insufficient():
    """Verifies that insufficient context produces an explicit warning notice."""
    retrieval_result = {
        "is_sufficient": False,
        "best_distance": 0.89,
        "documents": [],
    }

    formatted = format_retrieved_context(retrieval_result)
    assert "INSUFFICIENT_KNOWLEDGE_BASE_CONTEXT" in formatted
    assert "Do NOT invent medical facts" in formatted
    assert "consulting a qualified healthcare provider" in formatted


# ==========================================
# 4. Structured Prompt & Section Tests
# ==========================================

def test_structured_prompt_contains_all_required_rag_sections():
    """Verifies that the prompt contains all 5 required structural sections."""
    query = "What causes menstrual cramps?"
    context = "Excerpt: Prostaglandins cause contractions."
    prompt = get_structured_prompt(user_query=query, context=context)

    assert "[ROLE]" in prompt
    assert "[TASK]" in prompt
    assert "[CONTEXT]" in prompt
    assert "[SAFETY RULES]" in prompt
    assert "[RESPONSE FORMAT]" in prompt
    assert query in prompt
    assert "Prostaglandins cause contractions." in prompt


def test_structured_prompt_with_empty_context_notifies_deficiency():
    """Verifies structured prompt handles empty context gracefully."""
    query = "What is PCOS?"
    prompt = get_structured_prompt(user_query=query, context="")

    assert "[CONTEXT]" in prompt
    assert "No verified local documents available" in prompt
    assert query in prompt


# ==========================================
# 5. Gemini Service RAG Integration Tests
# ==========================================

@patch("services.gemini_service.genai.Client")
def test_gemini_service_injects_rag_context_into_generation(mock_client_cls):
    """Verifies that passing context to generate_response builds structured prompt with [CONTEXT]."""
    mock_instance = MagicMock()
    mock_client_cls.return_value = mock_instance

    mock_resp = MagicMock()
    mock_resp.text = "Cramps are caused by prostaglandins as stated in WHO guidance."
    mock_instance.models.generate_content.return_value = mock_resp

    service = GeminiService(api_key="valid-test-key")
    context_text = "WHO Excerpt: Uterine prostaglandins trigger cramps."
    
    result = service.generate_response(
        user_message="What causes cramps?",
        context=context_text,
    )

    assert "prostaglandins" in result
    mock_instance.models.generate_content.assert_called_once()
    call_args = mock_instance.models.generate_content.call_args
    contents = call_args.kwargs.get("contents")
    
    # Check that user turn contains the structured prompt with [CONTEXT]
    user_turn = contents[-1]
    user_text = user_turn.parts[0].text
    assert "[CONTEXT]" in user_text
    assert "WHO Excerpt: Uterine prostaglandins trigger cramps." in user_text
    assert "[ROLE]" in user_text
    assert "[SAFETY RULES]" in user_text


@patch("services.gemini_service.genai.Client")
def test_gemini_service_without_context_preserves_plain_user_message(mock_client_cls):
    """Verifies backward-compatibility when no context is provided."""
    mock_instance = MagicMock()
    mock_client_cls.return_value = mock_instance

    mock_resp = MagicMock()
    mock_resp.text = "Educational answer."
    mock_instance.models.generate_content.return_value = mock_resp

    service = GeminiService(api_key="valid-test-key")
    result = service.generate_response("Simple question without RAG")

    assert result == "Educational answer."
    call_args = mock_instance.models.generate_content.call_args
    contents = call_args.kwargs.get("contents")
    user_turn = contents[-1]
    assert user_turn.parts[0].text == "Simple question without RAG"
