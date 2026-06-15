"""
Inference parameter selection: Temperature, Top_P, and token limits.
"""

MODERN_MODELS = {"gpt-4o", "gpt-4o-mini", "o1", "o1-mini", "o3", "o3-mini"}


def get_temperature(platform: str, tone: str) -> float:
    """
    Low temperature (0.2) -> consistent, brand-safe, factual.
    High temperature (0.8) -> varied, surprising, engaging.
    """
    if tone == "Formal" or platform in ("Email", "LinkedIn"):
        return 0.2
    if tone == "Witty" or platform in ("Instagram", "Twitter/X"):
        return 0.8
    return 0.5


def get_max_tokens_kwarg(model: str, max_tokens: int = 400) -> dict:
    """
    Legacy models (gpt-4, gpt-3.5-turbo) use `max_tokens`.
    Modern reasoning models (gpt-4o, o1, ...) use
    `max_completion_tokens` — using the wrong one causes an API error.
    """
    if model in MODERN_MODELS:
        return {"max_completion_tokens": max(max_tokens, 256)}
    return {"max_tokens": max_tokens}
