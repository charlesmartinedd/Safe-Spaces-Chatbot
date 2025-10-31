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

    def _build_system_message(self, context: Optional[List[Dict]], user_profile: Optional[Dict] = None) -> str:
        grade_context = ""
        role_context = ""

        if user_profile:
            grade_context = f"Grade Level: {user_profile.get('grade_levels', 'K-12')}"
            role_context = f"Professional Role: {user_profile.get('role', 'Education professional')}"

        base_message = f"""You are an RRC (Recognize, Respond, Connect) Support Coach - an expert in the RRC course content specializing in:
- Supporting California K-12 educational professionals with trauma-informed practices
- Providing evidence-based strategies from the RRC course and research literature
- Delivering actionable guidance grounded in California education guidelines and regulations

{grade_context}
{role_context}

RESPONSE FORMAT REQUIREMENTS:
1. Keep responses between 300-400 words maximum
2. Use HTML formatting ONLY - NEVER use markdown (**, ##, etc.)
3. Use <strong>text</strong> for emphasis and important terms
4. Use <ul> and <li> tags for bullet lists - each bullet on a separate line
5. Break text into short paragraphs using <p> tags (2-3 sentences max)
6. Be warm, supportive, and direct in tone

CONTENT STRUCTURE (MANDATORY):
Every response must include:
- Brief introduction addressing the question/scenario
- 1-2 specific, actionable strategies based on RRC course content
- Reference to relevant California guidelines or regulations when applicable
- Do NOT include source citations in the main response (sources will be appended separately)

GROUNDING RULES:
- Base all advice on the RRC course content (primary source of truth)
- Support with research literature and references when available
- Minimize hallucinations - stay within knowledge base boundaries
- If information is not in the knowledge base, acknowledge limitations
- Never make up statistics or research findings

HTML FORMATTING EXAMPLE:
<p><strong>Understanding the Situation:</strong> When a student shows signs of trauma...</p>
<p>Here are evidence-based strategies you can use:</p>
<ul>
<li>Strategy 1: Create a predictable classroom routine...</li>
<li>Strategy 2: Use trauma-sensitive language...</li>
</ul>"""

        if context:
            context_text = "\n\n".join(
                [f"[Source: {item['source']}]\n{item['text']}" for item in context]
            )
            base_message += f"\n\nKnowledge Base Context:\n{context_text}"

        return base_message

    def generate_response(
        self,
        user_message: str,
        context: Optional[List[Dict]] = None,
        provider: Optional[str] = None,
        user_profile: Optional[Dict] = None,
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
        system_message = self._build_system_message(context, user_profile)

        try:
            response = config["client"].chat.completions.create(
                model=config["model"],
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=600,  # ~400 words for 300-400 word responses
                temperature=0.1,  # Low temperature for accuracy and minimal hallucination
            )
            content = response.choices[0].message.content

            # Format as HTML
            content = self._format_as_html(content)

            return content, provider_name
        except Exception as exc:  # noqa: BLE001
            logger.error("Error generating response with %s: %s", provider_name, exc)
            return (f"Error generating response: {exc}", provider_name)

    def _format_as_html(self, text: str) -> str:
        """Convert AI response to proper HTML formatting."""
        import re

        # If already contains HTML tags, return as-is
        if '<p>' in text or '<ul>' in text:
            return text.strip()

        # Convert markdown bold to HTML strong
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)

        # Remove markdown headers (##, ###, etc.) and make them strong
        text = re.sub(r'^#+\s+(.+)$', r'<strong>\1</strong>', text, flags=re.MULTILINE)

        # Convert bullet points to HTML list
        lines = text.split('\n')
        formatted_lines = []
        in_list = False

        for line in lines:
            stripped = line.strip()

            # Check if line is a bullet point
            if re.match(r'^[-*+•]\s+', stripped):
                if not in_list:
                    formatted_lines.append('<ul>')
                    in_list = True
                # Extract content after bullet marker
                content = re.sub(r'^[-*+•]\s+', '', stripped)
                formatted_lines.append(f'<li>{content}</li>')
            # Check if line is a numbered list
            elif re.match(r'^\d+\.\s+', stripped):
                if not in_list:
                    formatted_lines.append('<ul>')
                    in_list = True
                content = re.sub(r'^\d+\.\s+', '', stripped)
                formatted_lines.append(f'<li>{content}</li>')
            else:
                if in_list:
                    formatted_lines.append('</ul>')
                    in_list = False
                if stripped:
                    # Wrap non-empty lines in <p> tags if not already HTML
                    if not stripped.startswith('<'):
                        formatted_lines.append(f'<p>{stripped}</p>')
                    else:
                        formatted_lines.append(stripped)

        if in_list:
            formatted_lines.append('</ul>')

        return '\n'.join(formatted_lines).strip()
