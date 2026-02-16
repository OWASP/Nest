"""Google implementation of embedder."""

from __future__ import annotations

# Try deprecated google.generativeai first (has configure/embed_content methods)
# The new google.genai has a different API (Client-based) that we also support
genai = None
genai_client_module = None
use_deprecated_api = False

try:
    import google.generativeai as genai_deprecated

    # Check if it has the methods we need
    if hasattr(genai_deprecated, "configure") and hasattr(genai_deprecated, "embed_content"):
        genai = genai_deprecated
        use_deprecated_api = True
except ImportError:
    pass

# If deprecated API not available, try new google.genai (Client-based API)
if not use_deprecated_api:
    try:
        from google import genai as genai_new

        # Check if it has Client class
        if hasattr(genai_new, "Client"):
            genai_client_module = genai_new
    except ImportError:
        pass

import requests  # noqa: E402
from django.conf import settings  # noqa: E402

from apps.ai.embeddings.base import Embedder  # noqa: E402

# Mapping of Google embedding model names to their output dimensions
# This ensures get_dimensions() returns correct values for downstream vector storage
MODEL_DIMENSIONS: dict[str, int] = {
    "gemini-embedding-001": 768,  # Recommended, current model
    "text-embedding-004": 768,  # Deprecated but same dimensions
    "embedding-001": 768,  # Alternative model
}

# Default model and dimensions (used as fallback)
DEFAULT_MODEL = "gemini-embedding-001"
DEFAULT_DIMENSIONS = 768

# Error message for unrecognized API structure
_EMBEDDING_EXTRACTION_ERROR = (
    "Could not extract embedding from new API response. Unexpected result structure."
)


def _raise_embedding_extraction_error() -> None:
    """Raise ValueError for unrecognized API structure.

    Helper function to satisfy TRY301 linting rule.
    """
    raise ValueError(_EMBEDDING_EXTRACTION_ERROR)


class GoogleEmbedder(Embedder):
    """Google implementation of embedder using Google Generative AI SDK."""

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        """Initialize Google embedder.

        Args:
            model: The Google embedding model to use.
                  Default: gemini-embedding-001 (recommended, 768 dimensions)
                  Supported models: gemini-embedding-001, text-embedding-004 (deprecated),
                  embedding-001

        Note:
            If an unsupported model is provided, a warning is issued and the default
            model (gemini-embedding-001) is used to ensure correct vector dimensions
            for downstream storage.

        """
        self.api_key = settings.GOOGLE_API_KEY
        # Initialize base_url for REST API fallback (used in all code paths)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

        # Validate and set model
        if model not in MODEL_DIMENSIONS:
            import warnings

            warnings.warn(
                (
                    f"Model '{model}' is not in the known dimensions mapping. "
                    f"Using default model '{DEFAULT_MODEL}' with {DEFAULT_DIMENSIONS} dimensions. "
                    f"Supported models: {', '.join(MODEL_DIMENSIONS.keys())}"
                ),
                UserWarning,
                stacklevel=2,
            )
            self.model = DEFAULT_MODEL
            self._dimensions = DEFAULT_DIMENSIONS
        else:
            self.model = model
            self._dimensions = MODEL_DIMENSIONS[model]

        # Determine which API to use based on what's available
        # Priority: deprecated API (google.generativeai) > new API (google.genai.Client) > REST
        if genai and use_deprecated_api:
            # Use deprecated google.generativeai API
            # Warn only when actually using the deprecated API
            import warnings

            warnings.warn(
                (
                    "google.generativeai is deprecated. "
                    "Please install google-genai package: pip install google-genai"
                ),
                DeprecationWarning,
                stacklevel=2,
            )
            try:
                genai.configure(api_key=self.api_key)
                self.use_deprecated_sdk = True
                self.use_new_sdk = False
                self.client = None
            except (AttributeError, TypeError, ValueError):
                self.use_deprecated_sdk = False
                self.use_new_sdk = False
                self.client = None
        elif genai_client_module:
            # Use new google.genai Client API
            try:
                self.client = genai_client_module.Client(api_key=self.api_key)
                self.use_deprecated_sdk = False
                self.use_new_sdk = True
            except (AttributeError, TypeError, ValueError):
                self.use_deprecated_sdk = False
                self.use_new_sdk = False
                self.client = None
        else:
            # Fallback to REST API (base_url already initialized above)
            self.use_deprecated_sdk = False
            self.use_new_sdk = False
            self.client = None
            import warnings

            warnings.warn(
                (
                    "Google GenAI SDK not available. "
                    "Install it with: pip install google-generativeai or pip install google-genai"
                ),
                UserWarning,
                stacklevel=2,
            )

    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a query string.

        Args:
            text: The query text to embed.

        Returns:
            List of floats representing the embedding vector.

        """
        if self.use_deprecated_sdk and genai:
            # Use deprecated google.generativeai API
            result = genai.embed_content(
                model=self.model,
                content=text,
            )
            # SDK returns an object with embeddings attribute
            # For single embedding: result.embeddings[0].values
            return result.embeddings[0].values

        if self.use_new_sdk and self.client:
            # Use new google.genai Client API
            # The new API uses client.models.embed_content() or similar
            # Note: Exact API may vary, this is a placeholder implementation
            try:
                # Try the new API pattern (may need adjustment based on actual API)
                result = self.client.models.embed_content(
                    model=self.model,
                    content=text,
                )
                # Extract embedding values from result
                # The exact structure depends on the new API - may need adjustment
                if hasattr(result, "embeddings") and result.embeddings:
                    return result.embeddings[0].values
                if hasattr(result, "embedding") and hasattr(result.embedding, "values"):
                    return result.embedding.values
                # Fallback: try to access as dict-like
                embedding = result.get("embedding", {}).get("values", [])
                if embedding:
                    return embedding
                # If we can't extract embedding, raise an error instead of returning empty
                _raise_embedding_extraction_error()
            except (AttributeError, TypeError, ValueError) as e:
                # If new API structure is different, fall back to REST
                import warnings

                warnings.warn(
                    f"New google.genai API structure unexpected: {e}. Falling back to REST API.",
                    UserWarning,
                    stacklevel=2,
                )

        # Fallback to REST API
        # Use header instead of query parameter to avoid API key in logs
        endpoint = f"{self.base_url}/models/{self.model}:embedContent"
        response = requests.post(
            endpoint,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key,
            },
            json={
                "content": {"parts": [{"text": text}]},
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["embedding"]["values"]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple documents.

        Args:
            texts: List of document texts to embed.

        Returns:
            List of embedding vectors, one per document.

        """
        if self.use_deprecated_sdk and genai:
            # Use deprecated google.generativeai API
            # Process sequentially (SDK doesn't have native batch API for embeddings)
            results = []
            for text in texts:
                result = genai.embed_content(
                    model=self.model,
                    content=text,
                )
                # SDK returns an object with embeddings attribute
                results.append(result.embeddings[0].values)
            return results

        if self.use_new_sdk and self.client:
            # Use new google.genai Client API
            # Process sequentially (may support batch in future)
            results = []
            for text in texts:
                embedding_values = None
                try:
                    result = self.client.models.embed_content(
                        model=self.model,
                        content=text,
                    )
                    # Extract embedding values from result
                    if hasattr(result, "embeddings") and result.embeddings:
                        embedding_values = result.embeddings[0].values
                    elif hasattr(result, "embedding") and hasattr(result.embedding, "values"):
                        embedding_values = result.embedding.values
                    else:
                        # Fallback: try to access as dict-like
                        embedding = result.get("embedding", {}).get("values", [])
                        if embedding:
                            embedding_values = embedding
                        else:
                            # If extraction fails, raise error to trigger REST fallback
                            _raise_embedding_extraction_error()
                except (AttributeError, TypeError, ValueError):
                    # If SDK call fails, embedding_values remains None
                    # This will trigger REST fallback below
                    pass

                if embedding_values:
                    results.append(embedding_values)
                else:
                    # Fall back to REST API for this item
                    # Use header instead of query parameter to avoid API key in logs
                    endpoint = f"{self.base_url}/models/{self.model}:embedContent"
                    response = requests.post(
                        endpoint,
                        headers={
                            "Content-Type": "application/json",
                            "x-goog-api-key": self.api_key,
                        },
                        json={
                            "content": {"parts": [{"text": text}]},
                        },
                        timeout=30,
                    )
                    response.raise_for_status()
                    data = response.json()
                    results.append(data["embedding"]["values"])
            return results

        # Fallback to REST API
        # Use header instead of query parameter to avoid API key in logs
        endpoint = f"{self.base_url}/models/{self.model}:batchEmbedContents"
        response = requests.post(
            endpoint,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key,
            },
            json={
                "requests": [
                    {
                        "model": self.model,
                        "content": {"parts": [{"text": text}]},
                    }
                    for text in texts
                ],
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return [item["embedding"]["values"] for item in data["embeddings"]]

    def get_dimensions(self) -> int:
        """Get the dimension of embeddings produced by this embedder.

        Returns:
            Integer representing the embedding dimension.

        """
        return self._dimensions
