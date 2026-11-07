"""Embedding provider selection without provider calls."""

import pytest

from apps.ai.embeddings.factory import get_embedder


@pytest.fixture
def providers(monkeypatch, mocker, settings):
    monkeypatch.delenv("EMBEDDING_PROVIDER", raising=False)
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    settings.OPEN_AI_SECRET_KEY = "test-openai-key"  # noqa: S105
    settings.GOOGLE_API_KEY = "test-google-key"
    return {
        "openai": mocker.patch("apps.ai.embeddings.openai.OpenAIEmbedder"),
        "google": mocker.patch("apps.ai.embeddings.google.GoogleEmbedder"),
    }


@pytest.mark.parametrize("provider", ["openai", "google"])
def test_explicit_provider_overrides_llm_provider(monkeypatch, providers, provider):
    monkeypatch.setenv("EMBEDDING_PROVIDER", provider.upper())
    monkeypatch.setenv("LLM_PROVIDER", "google" if provider == "openai" else "openai")
    assert get_embedder() is providers[provider].return_value
    providers[provider].assert_called_once_with()


@pytest.mark.parametrize("provider", ["openai", "google"])
def test_embedding_provider_follows_supported_llm(monkeypatch, providers, provider):
    monkeypatch.setenv("LLM_PROVIDER", provider)
    assert get_embedder() is providers[provider].return_value


def test_default_embedding_provider_is_openai(providers):
    assert get_embedder() is providers["openai"].return_value


def test_bedrock_requires_explicit_embedding_provider(monkeypatch, providers):
    monkeypatch.setenv("LLM_PROVIDER", "bedrock")
    with pytest.raises(ValueError, match="EMBEDDING_PROVIDER is required"):
        get_embedder()
    for provider in providers.values():
        provider.assert_not_called()


@pytest.mark.parametrize(
    ("provider", "credential"),
    [("openai", "OPEN_AI_SECRET_KEY"), ("google", "GOOGLE_API_KEY")],
)
@pytest.mark.parametrize("missing", [None, "", "None"])
def test_bedrock_rejects_missing_embedding_credentials(
    monkeypatch, providers, settings, provider, credential, missing
):
    monkeypatch.setenv("LLM_PROVIDER", "bedrock")
    monkeypatch.setenv("EMBEDDING_PROVIDER", provider)
    setattr(settings, credential, missing)
    with pytest.raises(ValueError, match=f"{credential} is required"):
        get_embedder()
    providers[provider].assert_not_called()


@pytest.mark.parametrize("provider", ["openai", "google"])
def test_bedrock_uses_selected_provider_with_credentials(monkeypatch, providers, provider):
    monkeypatch.setenv("LLM_PROVIDER", "bedrock")
    monkeypatch.setenv("EMBEDDING_PROVIDER", provider)
    assert get_embedder() is providers[provider].return_value


@pytest.mark.parametrize("variable", ["LLM_PROVIDER", "EMBEDDING_PROVIDER"])
def test_unsupported_provider_is_not_silently_replaced(monkeypatch, providers, variable):
    monkeypatch.setenv(variable, "typo")
    with pytest.raises(ValueError, match="Unsupported embedding provider: typo"):
        get_embedder()
    for provider in providers.values():
        provider.assert_not_called()
