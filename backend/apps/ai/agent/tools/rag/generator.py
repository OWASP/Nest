"""Generator for the RAG system."""

import logging
import os
from typing import Any

import openai

logger = logging.getLogger(__name__)


class Generator:
    """Generates answers to user queries based on retrieved context."""

    MAX_TOKENS = 2000
    SYSTEM_PROMPT = """
You are a helpful and professional AI assistant for the OWASP Foundation.
Your task is to answer user queries based ONLY on the provided context.
Follow these rules strictly:
1. Base your entire answer on the information given in the "CONTEXT" section. Do not use any
external knowledge unless and until it is about OWASP.
2. Do not mention or refer to the word "context", "based on context", "provided information",
"Information given to me" or similar phrases in your responses.
3. you will answer questions only related to OWASP and within the scope of OWASP.
4. Be concise and directly answer the user's query.
5. Provide the necessary link if the context contains a URL.
6. If there is any query based on location, you need to look for latitude and longitude in the
context and provide the nearest OWASP chapter based on that.
7. You can ask for more information if the query is very personalized or user-centric.
8. after trying all of the above, If the context does not contain the information or you think that
it is out of scope for OWASP, you MUST state: "please ask question related to OWASP."
"""
    TEMPERATURE = 0.4

    def __init__(self, chat_model: str = "gpt-4o"):
        """Initialize the Generator.

        Args:
          chat_model (str): The name of the OpenAI chat model to use for generation.

        Raises:
          ValueError: If the OpenAI API key is not set.

        """
        if not (openai_api_key := os.getenv("DJANGO_OPEN_AI_SECRET_KEY")):
            error_msg = "DJANGO_OPEN_AI_SECRET_KEY environment variable not set"
            raise ValueError(error_msg)

        self.chat_model = chat_model
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        logger.info("Generator initialized with chat model: %s", self.chat_model)

    def prepare_context(self, context_chunks: list[dict[str, Any]]) -> str:
        """Format the list of retrieved context chunks into a single string for the LLM.

        Args:
          context_chunks: A list of chunk dictionaries from the retriever.

        Returns:
          A formatted string containing the context.

        """
        if not context_chunks:
            return "No context provided"

        formatted_context = []
        for i, chunk in enumerate(context_chunks):
            source_name = chunk.get("source_name", f"Unknown Source {i + 1}")
            text = chunk.get("text", "")

            context_block = f"Source Name: {source_name}\nContent: {text}"
            formatted_context.append(context_block)

        return "\n\n---\n\n".join(formatted_context)

    def generate_answer(self, query: str, context_chunks: list[dict[str, Any]]) -> str:
        """Generate an answer to the user's query using provided context chunks.

        Args:
          query: The user's query text.
          context_chunks: A list of context chunks retrieved by the retriever.

        Returns:
          The generated answer as a string.

        """
        formatted_context = self.prepare_context(context_chunks)

        user_prompt = f"""
- You are an assistant for question-answering tasks related to OWASP.
- Use the following pieces of retrieved context to answer the question.
- If the question is related to OWASP then you can try to answer based on your knowledge, if you
don't know the answer, just say that you don't know.
- Try to give answer and keep the answer concise, but you really think that the response will be
longer and better you will provide more information.
- Ask for the current location if the query is related to location.
- Ask for the information you need if the query is very personalized or user-centric.
- Do not mention or refer to the word "context", "based on context", "provided information",
"Information given to me" or similar phrases in your responses.
Question: {query}
Context: {formatted_context}
Answer:
"""

        try:
            response = self.openai_client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.TEMPERATURE,
                max_tokens=self.MAX_TOKENS,
            )
            answer = response.choices[0].message.content.strip()
        except openai.OpenAIError:
            logger.exception("OpenAI API error")
            answer = "I'm sorry, I'm currently unable to process your request."

        return answer
