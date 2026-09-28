"""
LunaCare: Gemini API Service Layer
----------------------------------
Integrates with the official Google GenAI SDK to generate controlled,
empathetic, and educational female health responses using Gemini 2.5 Flash.

Demonstrates Week 3 Syllabus Concepts:
- Official Google GenAI SDK client lifecycle
- Secure API key authentication via environment variables
- Generation parameter tuning (temperature, max_output_tokens)
- Graceful exception recovery preventing UI crashes
"""

import logging
import os
import time
from typing import List, Dict, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import MODEL_NAME, TEMPERATURE, MAX_OUTPUT_TOKENS, MEMORY_WINDOW
from prompts.system_prompt import LUNACARE_SYSTEM_INSTRUCTION, get_structured_prompt

# Ensure environment variables are loaded
load_dotenv()

# Internal logger (logs errors without exposing them to the UI)
logger = logging.getLogger("lunacare.gemini_service")


class GeminiService:
    """
    Encapsulates interactions with the Google Gemini API.
    Separates authentication, prompt compilation, and network execution from the UI.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = model_name or MODEL_NAME
        self.temperature = TEMPERATURE
        self.max_output_tokens = MAX_OUTPUT_TOKENS
        self._client: Optional[genai.Client] = None

    def is_configured(self) -> bool:
        """Returns True if a valid non-placeholder API key is available."""
        return bool(self.api_key and self.api_key != "your_gemini_api_key_here")

    def _get_client(self) -> genai.Client:
        """Initializes and returns the official Google GenAI client instance."""
        if not self._client:
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def _format_conversation_contents(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        context: Optional[str] = None,
        tool_result: Optional[str] = None,
    ) -> List[types.Content]:
        """
        Converts conversational history into the sequence of Content objects
        expected by the Google GenAI SDK. Maps UI role 'assistant' to Gemini 'model'.
        If context or tool_result is provided, formats user turn using LunaCare's structured prompt.
        """
        contents: List[types.Content] = []

        if conversation_history:
            # Enforce sliding memory window: at most MEMORY_WINDOW recent user/model turns
            effective_history = (
                conversation_history[-MEMORY_WINDOW:]
                if len(conversation_history) > MEMORY_WINDOW
                else conversation_history
            )
            for turn in effective_history:
                role = turn.get("role", "user")
                text = turn.get("content", "").strip()
                if not text:
                    continue

                gemini_role = "user" if role == "user" else "model"
                contents.append(
                    types.Content(
                        role=gemini_role,
                        parts=[types.Part.from_text(text=text)],
                    )
                )

        # Format current user query: if context or tool_result is provided, wrap in structured prompt
        if context is not None or tool_result is not None:
            user_turn_text = get_structured_prompt(
                user_message, context=context or "", tool_result=tool_result
            )
        else:
            user_turn_text = user_message

        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_turn_text)],
            )
        )
        return contents

    def generate_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        context: Optional[str] = None,
        tool_result: Optional[str] = None,
    ) -> str:
        """
        Executes a generation request to the Gemini API with optional RAG context and tool results.
        
        Returns:
            str: Natural-language response from LunaCare, or a friendly error notice.
        """
        # 1. Input Validation
        if not user_message or not user_message.strip():
            return "Please enter a question so I can assist you."

        clean_query = user_message.strip()

        # 2. Authentication Check
        if not self.is_configured():
            logger.warning("Gemini API key is not configured in environment.")
            return (
                "LunaCare's AI connection is not yet configured. "
                "Please add your `GEMINI_API_KEY` in the `.env` file to enable live responses."
            )

        # 3. Call Gemini API with minimal retry on transient spikes (no aggressive retries on 429)
        max_retries = 2
        for attempt in range(1, max_retries + 1):
            try:
                client = self._get_client()

                # Generation configuration with system instructions & parameters
                config = types.GenerateContentConfig(
                    system_instruction=LUNACARE_SYSTEM_INSTRUCTION,
                    temperature=self.temperature,
                    max_output_tokens=self.max_output_tokens,
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                )

                # Format multi-turn conversation contents (with optional RAG context and tool result)
                contents = self._format_conversation_contents(
                    clean_query, conversation_history, context=context, tool_result=tool_result
                )

                # Generate content using configured model
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=config,
                )

                # 4. Extract and validate text response
                if response and response.text:
                    return response.text.strip()
                else:
                    return (
                        "I was unable to generate a complete answer. "
                        "Please feel free to rephrase your question, and I will be happy to help."
                    )

            except Exception as err:
                err_str = str(err).lower()
                logger.warning(
                    "Gemini API attempt %d/%d failed: %s", attempt, max_retries, str(err)
                )

                # If quota exhausted (429), immediately return fallback without wasteful sleep loops
                if "429" in err_str or "resource_exhausted" in err_str:
                    logger.warning("Gemini API daily quota reached. Returning graceful connection fallback.")
                    return (
                        "I'm having trouble connecting right now. "
                        "Please try again in a moment, or rephrase your question."
                    )

                # Retry on transient server unavailability (503) once
                if attempt < max_retries and any(
                    code in err_str for code in ["503", "unavailable", "high demand"]
                ):
                    time.sleep(2 * attempt)
                    continue

                # Internal logging (stack trace kept on server, never exposed to user)
                logger.error("Gemini API generation error: %s", str(err), exc_info=True)

                # Friendly user-facing fallback
                return (
                    "I'm having trouble connecting right now. "
                    "Please try again in a moment, or rephrase your question."
                )


# Module-level convenience singleton
_default_service = GeminiService()


def generate_response(
    user_message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    context: Optional[str] = None,
    tool_result: Optional[str] = None,
) -> str:
    """
    Convenience function to generate a LunaCare response using the default service.
    """
    # Refresh API key from environment dynamically if it was loaded recently
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if api_key != _default_service.api_key:
        _default_service.api_key = api_key
        _default_service._client = None

    return _default_service.generate_response(
        user_message, conversation_history, context=context, tool_result=tool_result
    )
