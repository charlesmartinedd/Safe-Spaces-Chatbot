import os
import logging
from typing import Dict, List, Optional, Tuple

from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatService:
    """Service for handling AI chat interactions with pluggable providers."""

    def __init__(self):
        self.providers: Dict[str, Dict] = {}

        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.providers["openai"] = {
                "client": OpenAI(api_key=openai_key),
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "1000")),
            }
        else:
            logger.info("OPENAI_API_KEY not set.")

        xai_key = os.getenv("XAI_API_KEY")
        if xai_key:
            base_url = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")
            self.providers["xai"] = {
                "client": OpenAI(api_key=xai_key, base_url=base_url),
                "model": os.getenv("XAI_MODEL", "grok-beta"),
                "max_tokens": int(os.getenv("XAI_MAX_TOKENS", "1000")),
            }
        else:
            logger.info("XAI_API_KEY not set.")

        default_provider = os.getenv("LLM_PROVIDER", "openai").lower()
        if default_provider in self.providers:
            self.default_provider = default_provider
        else:
            self.default_provider = next(iter(self.providers), None)

        if not self.default_provider:
            logger.warning("No LLM providers configured. Chat functionality will be limited.")

    def available_providers(self) -> List[str]:
        """Return a sorted list of configured providers."""
        return sorted(self.providers.keys())

    def _build_system_message(self, context: Optional[List[Dict]]) -> str:
        base_message = "You are a helpful AI assistant."
        if context:
            context_text = "\n\n".join(
                [f"[Source: {item['source']}]\n{item['text']}" for item in context]
            )
            base_message = (
                "You are a helpful AI assistant with access to a curated Safe Spaces knowledge base.\n"
                "Use the provided context when it is relevant. If it is not, answer based on general knowledge "
                "and mention that the knowledge base did not cover the request.\n\n"
                f"Context from knowledge base:\n{context_text}\n"
            )
        return base_message

    def generate_response(
        self,
        user_message: str,
        context: Optional[List[Dict]] = None,
        provider: Optional[str] = None,
    ) -> Tuple[str, str]:
        """Generate a chat response and return the provider used."""

        if not self.providers:
            return (
                "Error: no language model providers are configured. Please supply API keys in the .env file.",
                "unavailable",
            )

        provider_name = (provider or self.default_provider or "").lower()
        if provider_name not in self.providers:
            available = ", ".join(sorted(self.providers.keys()))
            return (
                f"Error: provider '{provider_name or 'unknown'}' is not available. Available providers: {available}.",
                provider_name or "unknown",
            )

        config = self.providers[provider_name]
        system_message = self._build_system_message(context)

        try:
            response = config["client"].chat.completions.create(
                model=config["model"],
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=config["max_tokens"],
                temperature=0.7,
            )
            content = response.choices[0].message.content
            return content, provider_name
        except Exception as exc:  # noqa: BLE001
            logger.error("Error generating response with %s: %s", provider_name, exc)
            return (f"Error generating response: {exc}", provider_name)
