"""Embedding abstraction layer for vendor-agnostic embedding generation."""

from apps.ai.embeddings.factory import get_embedder

__all__ = ["get_embedder"]
