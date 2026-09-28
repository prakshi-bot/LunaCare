"""
LunaCare: Gemini Embedding Service Layer
---------------------------------------
Demonstrates Week 4 Syllabus Concepts:
- Text-to-Vector Embeddings: Converting human medical and wellness language
  into high-dimensional numerical coordinates.
- Semantic Vector Space: In this 3072-dimensional space, phrases with similar
  meaning (e.g., 'painful periods' and 'dysmenorrhea') are geometrically close,
  enabling conceptual search beyond basic keyword matching.

How Embeddings Work (Beginner Guide):
1. Input Text: "What causes menstrual cramps?"
2. Neural Embedding Model: Evaluates semantic concepts, context, and syntax.
3. Numerical Vector: Output array of 3,072 floating-point numbers:
   [0.0142, -0.0521, 0.0891, ..., -0.0034]
4. Vector Comparison: Stored in Chroma DB where cosine similarity measures
   the angular distance between the query vector and document chunk vectors.
"""

import logging
import os
import time
from typing import List, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from langchain_core.embeddings import Embeddings

from config import EMBEDDING_MODEL, EMBEDDING_DIMENSIONALITY

load_dotenv()
logger = logging.getLogger("lunacare.embedding_service")


class GeminiEmbeddingService(Embeddings):
    """
    Service wrapper for Google's official gemini-embedding-2 model.
    Implements the standard LangChain Embeddings interface (embed_documents & embed_query)
    to integrate seamlessly with Chroma vector storage.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        dimensionality: Optional[int] = None,
        batch_size: int = 50,
    ):
        """
        Initializes the embedding service.
        
        Args:
            api_key: Google Gemini API key (defaults to GEMINI_API_KEY from environment).
            model_name: Embedding model identifier (defaults to gemini-embedding-2).
            dimensionality: Target vector size (defaults to 3072).
            batch_size: Maximum chunks to embed per API request to prevent payload overflows.
        """
        self.api_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = model_name or EMBEDDING_MODEL
        self.dimensionality = dimensionality or EMBEDDING_DIMENSIONALITY
        self.batch_size = batch_size
        self._client: Optional[genai.Client] = None

    def _get_client(self) -> genai.Client:
        """Instantiates and returns the official Google GenAI client instance."""
        if not self._client:
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Converts a list of document chunks into a list of 3072-dimensional embedding vectors.
        
        CRITICAL ARCHITECTURAL REQUIREMENT:
        Each document chunk receives its own independent embedding vector.
        We pass a list of distinct types.Content objects so the API returns one
        vector per text snippet, avoiding accidental batch-level aggregation.
        """
        if not texts:
            return []

        client = self._get_client()
        embed_config = types.EmbedContentConfig(output_dimensionality=self.dimensionality)
        all_embeddings: List[List[float]] = []

        # Process in batches of up to 50 items to keep requests low and stay well under quotas
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            
            # Wrap each text chunk in its own distinct Content object (1 vector per chunk)
            contents = [
                types.Content(parts=[types.Part.from_text(text=snippet)])
                for snippet in batch
            ]

            max_retries = 4
            success = False

            for attempt in range(1, max_retries + 1):
                try:
                    response = client.models.embed_content(
                        model=self.model_name,
                        contents=contents,
                        config=embed_config,
                    )

                    if not response or not response.embeddings:
                        raise ValueError(f"No embeddings returned for batch starting at index {i}")

                    for item in response.embeddings:
                        all_embeddings.append(list(item.values))

                    success = True
                    # Short polite pause between batches to preserve RPM quota
                    time.sleep(1.2)
                    break

                except Exception as err:
                    err_str = str(err).lower()
                    if "429" in err_str or "resource_exhausted" in err_str:
                        wait_sec = 16 * attempt
                        logger.warning(
                            "Rate limit (429) hit during batch %d-%d. Pausing for %d seconds before retry %d/%d...",
                            i, i + len(batch), wait_sec, attempt, max_retries
                        )
                        print(f"      ⏳ Quota pause: waiting {wait_sec}s for rate limit to reset (attempt {attempt}/{max_retries})...")
                        time.sleep(wait_sec)
                    else:
                        logger.error("Error generating document embeddings for batch %d-%d: %s", i, i + len(batch), str(err))
                        if attempt == max_retries:
                            raise err
                        time.sleep(3)

            if not success:
                raise RuntimeError(f"Failed to embed batch {i}-{i+len(batch)} after {max_retries} attempts.")

        return all_embeddings

    def embed_query(self, text: str) -> List[float]:
        """
        Embeds a single user question into a 3072-dimensional vector in the same
        semantic space as the document chunks.
        
        Args:
            text: User search query (e.g. "What causes menstrual cramps?")
            
        Returns:
            List[float]: 3072-dimensional coordinate vector.
        """
        clean_text = text.strip() if text else ""
        if not clean_text:
            return [0.0] * self.dimensionality

        client = self._get_client()
        embed_config = types.EmbedContentConfig(output_dimensionality=self.dimensionality)
        content = types.Content(parts=[types.Part.from_text(text=clean_text)])

        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                response = client.models.embed_content(
                    model=self.model_name,
                    contents=content,
                    config=embed_config,
                )

                if response and response.embeddings:
                    return list(response.embeddings[0].values)
                raise ValueError("No query embedding returned from Gemini API.")

            except Exception as err:
                err_str = str(err).lower()
                logger.warning(
                    "Error generating query embedding for '%s' (attempt %d/%d): %s",
                    clean_text[:40], attempt, max_retries, str(err)
                )
                if attempt == max_retries:
                    logger.error("Failed to generate query embedding after %d attempts for '%s'", max_retries, clean_text[:40])
                    raise err
                wait_sec = 2 * attempt
                if "429" in err_str or "resource_exhausted" in err_str:
                    wait_sec = 10 * attempt
                time.sleep(wait_sec)


# Convenience module-level singleton
_default_embedding_service = GeminiEmbeddingService()


def get_embedding_service() -> GeminiEmbeddingService:
    """Returns the default configured GeminiEmbeddingService instance."""
    # Dynamically update API key if modified in environment
    current_key = os.getenv("GEMINI_API_KEY", "").strip()
    if current_key != _default_embedding_service.api_key:
        _default_embedding_service.api_key = current_key
        _default_embedding_service._client = None
    return _default_embedding_service
