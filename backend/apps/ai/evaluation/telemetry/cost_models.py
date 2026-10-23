"""Model token pricing and cost computation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelPrice:
    """Pricing rates per 1,000,000 tokens in USD."""

    input_per_million: float
    output_per_million: float


# Current pricing tiers (USD per 1M tokens)
MODEL_PRICING: dict[str, ModelPrice] = {
    "gpt-4o": ModelPrice(input_per_million=2.50, output_per_million=10.00),
    "gpt-4o-mini": ModelPrice(input_per_million=0.15, output_per_million=0.60),
    "gpt-4.1-mini": ModelPrice(input_per_million=0.15, output_per_million=0.60),
    "gemini-2.5-flash": ModelPrice(input_per_million=0.15, output_per_million=0.60),
    "gemini-1.5-flash": ModelPrice(input_per_million=0.075, output_per_million=0.30),
}

DEFAULT_MODEL = "gpt-4o-mini"


def calculate_token_cost(
    prompt_tokens: int,
    completion_tokens: int,
    model: str = DEFAULT_MODEL,
) -> float:
    """Calculate the estimated monetary cost in USD for a given token usage.

    Args:
        prompt_tokens: Number of input/prompt tokens.
        completion_tokens: Number of output/completion tokens.
        model: Model name string.

    Returns:
        Estimated cost in USD rounded to 6 decimal places.

    """
    pricing = MODEL_PRICING.get(model, MODEL_PRICING[DEFAULT_MODEL])
    input_cost = (prompt_tokens / 1_000_000) * pricing.input_per_million
    output_cost = (completion_tokens / 1_000_000) * pricing.output_per_million
    return round(input_cost + output_cost, 6)
