import os
from openai import OpenAI
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatService:
    """Service for handling AI chat interactions"""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not set. Chat functionality will be limited.")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)

        self.model = "gpt-3.5-turbo"
        self.max_tokens = 1000

    def generate_response(self, user_message: str, context: Optional[List[Dict]] = None) -> str:
        """Generate a chat response, optionally using RAG context"""

        if not self.client:
            return "Error: OpenAI API key not configured. Please set OPENAI_API_KEY in your .env file."

        # Build the system message
        system_message = "You are a helpful AI assistant."

        # If we have RAG context, include it
        if context and len(context) > 0:
            context_text = "\n\n".join([
                f"[Source: {item['source']}]\n{item['text']}"
                for item in context
            ])
            system_message = f"""You are a helpful AI assistant with access to a knowledge base.
Use the following context to answer the user's question. If the context doesn't contain
relevant information, you can still provide a helpful response based on your general knowledge,
but mention that the information isn't from the knowledge base.

Context from knowledge base:
{context_text}
"""

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"Error generating response: {str(e)}"
