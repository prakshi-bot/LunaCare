"""
LunaCare: Health Knowledge Retrieval Service Layer
-------------------------------------------------
Demonstrates Week 4 Syllabus Concepts:
- Vector Semantic Search: Instead of matching literal keywords, Chroma calculates
  the geometric angular distance (cosine distance) between the user query vector
  and all indexed chunk vectors in 3072-dimensional space.
- Relevance Thresholding: Nearest-neighbor search always returns *something*,
  even if the query is totally unrelated (e.g. 'What is the capital of France?').
  We apply a distance threshold so that unrelated or out-of-scope queries are
  flagged as having 'insufficient context' rather than injecting irrelevant text.
- What makes this system RAG (Retrieval-Augmented Generation):
  1. Retrieve: Fetch only the most relevant paragraphs from verified documents.
  2. Augment: Inject those paragraphs into the LLM prompt under [CONTEXT].
  3. Generate: Instruct Gemini to answer strictly grounded in the retrieved facts.
"""

import logging
from typing import List, Dict, Any, Optional

# SQLite3 compatibility shim for Streamlit Community Cloud (Linux container requires SQLite >= 3.35.0)
try:
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

from langchain_core.documents import Document
from langchain_chroma import Chroma

from config import (
    VECTOR_STORE_DIR,
    CHROMA_COLLECTION_NAME,
    RETRIEVAL_K,
    SIMILARITY_DISTANCE_THRESHOLD,
)
from services.embedding_service import get_embedding_service

logger = logging.getLogger("lunacare.retrieval_service")


class HealthRetrievalService:
    """
    Manages vector database connections, similarity search, and context assembly.
    Separates database mechanics from Streamlit UI and LLM generation layers.
    """

    def __init__(
        self,
        collection_name: str = CHROMA_COLLECTION_NAME,
        persist_dir = VECTOR_STORE_DIR,
        distance_threshold: float = SIMILARITY_DISTANCE_THRESHOLD,
    ):
        self.collection_name = collection_name
        self.persist_dir = str(persist_dir)
        self.distance_threshold = distance_threshold
        self._vector_store: Optional[Chroma] = None

    def _get_vector_store(self) -> Chroma:
        """Initializes and returns the LangChain Chroma vector store wrapper."""
        if not self._vector_store:
            embedding_service = get_embedding_service()
            self._vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=embedding_service,
                persist_directory=self.persist_dir,
            )
        return self._vector_store

    def retrieve_relevant_documents(
        self,
        query: str,
        k: int = RETRIEVAL_K,
        threshold: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Performs semantic similarity search for a user query.
        
        Args:
            query: User search inquiry (e.g., 'What causes menstrual cramps?')
            k: Top number of document chunks to retrieve (defaults to 4).
            threshold: Cosine distance threshold (lower = closer match).
            
        Returns:
            Dict containing:
            - 'query': original query string
            - 'is_sufficient': bool indicating if best match satisfies threshold
            - 'best_distance': float distance of top match (or 999.0 if empty)
            - 'documents': list of retrieved LangChain Document objects
            - 'distances': list of distance floats corresponding to documents
        """
        clean_query = query.strip() if query else ""
        if not clean_query:
            return {
                "query": "",
                "is_sufficient": False,
                "best_distance": 999.0,
                "documents": [],
                "distances": [],
            }

        effective_threshold = threshold if threshold is not None else self.distance_threshold
        store = self._get_vector_store()

        try:
            # Chroma similarity_search_with_score returns List[Tuple[Document, distance]]
            # In Chroma, distance is cosine distance: 0.0 means identical, >= 1.0 means unrelated
            results = store.similarity_search_with_score(clean_query, k=k)

            if not results:
                return {
                    "query": clean_query,
                    "is_sufficient": False,
                    "best_distance": 999.0,
                    "documents": [],
                    "distances": [],
                }

            docs: List[Document] = [doc for doc, _ in results]
            distances: List[float] = [float(dist) for _, dist in results]
            best_distance = distances[0] if distances else 999.0

            # Evaluate relevance against threshold
            # If the closest match is farther than the threshold, the query is not covered
            is_sufficient = best_distance <= effective_threshold

            logger.info(
                "Query: '%s' | Best Distance: %.4f (Threshold: %.4f) | Sufficient: %s",
                clean_query[:50],
                best_distance,
                effective_threshold,
                is_sufficient,
            )

            return {
                "query": clean_query,
                "is_sufficient": is_sufficient,
                "best_distance": best_distance,
                "documents": docs if is_sufficient else [],
                "distances": distances if is_sufficient else [],
                "raw_results_count": len(results),
            }

        except Exception as err:
            logger.error("Retrieval search failed for query '%s': %s", clean_query[:50], str(err))
            return {
                "query": clean_query,
                "is_sufficient": False,
                "best_distance": 999.0,
                "documents": [],
                "distances": [],
                "error": str(err),
            }

    def format_retrieved_context(self, retrieval_result: Dict[str, Any]) -> str:
        """
        Formats retrieved document chunks into clean structured text for the LLM prompt.
        
        If the query was judged insufficient by the distance threshold or if no
        documents were retrieved, returns an explicit notice instructing the LLM
        to state that the knowledge base lacks information on this topic.
        """
        if not retrieval_result.get("is_sufficient", False):
            return (
                "INSUFFICIENT_KNOWLEDGE_BASE_CONTEXT:\n"
                "LunaCare's local verified health knowledge base does not contain sufficiently "
                "relevant documents for this specific inquiry. "
                "Do NOT invent medical facts or speculate. Clearly acknowledge to the user that "
                "LunaCare's current curated knowledge base does not have enough verified information "
                "on this specific question, and advise consulting a qualified healthcare provider."
            )

        documents = retrieval_result.get("documents", [])
        if not documents:
            return "No relevant context found."

        context_blocks = []
        for idx, doc in enumerate(documents, start=1):
            source = doc.metadata.get("source", "Verified WHO Document")
            page = doc.metadata.get("page", "N/A")
            topic = doc.metadata.get("topic", "Health")
            content = doc.page_content.strip()

            block = (
                f"--- EXCERPT {idx} [Topic: {topic} | Source: {source} | Page: {page}] ---\n"
                f"{content}\n"
            )
            context_blocks.append(block)

        return "\n".join(context_blocks)


# Module-level convenience singleton
_default_retrieval_service = HealthRetrievalService()


def retrieve_relevant_documents(query: str, k: int = RETRIEVAL_K) -> Dict[str, Any]:
    """Convenience function to retrieve documents using the default retrieval service."""
    return _default_retrieval_service.retrieve_relevant_documents(query, k=k)


def format_retrieved_context(retrieval_result: Dict[str, Any]) -> str:
    """Convenience function to format retrieved context for LLM prompts."""
    return _default_retrieval_service.format_retrieved_context(retrieval_result)
