"""
Pydantic schemas for validating AI-generated marketing copy.
"""
from typing import List
from pydantic import BaseModel, field_validator

PLATFORM_RULES = {
    "LinkedIn": {"max_hashtags": 3, "max_chars": None},
    "Instagram": {"min_hashtags": 5, "max_hashtags": 10, "max_chars": None},
    "Email": {"max_hashtags": 0, "max_chars": None, "max_headline_chars": 50},
    "Twitter/X": {"max_hashtags": 2, "max_chars": 280},
}


class CopyOutput(BaseModel):
    """The required shape of every generated piece of copy.

    NOTE: field order matters. In Pydantic v2, a field validator's
    `info.data` only contains fields validated earlier (declared
    earlier). `platform` and `tone_used` go first so later
    validators can read them.
    """

    platform: str
    tone_used: str
    headline: str
    body: str
    hashtags: List[str] = []
    cta: str
    character_count: int

    @field_validator("character_count")
    @classmethod
    def check_character_limit(cls, v: int, info):
        platform = info.data.get("platform", "")
        max_chars = PLATFORM_RULES.get(platform, {}).get("max_chars")
        if max_chars and v > max_chars:
            raise ValueError(
                f"{platform} copy is {v} characters, which exceeds the "
                f"{max_chars}-character limit."
            )
        return v

    @field_validator("hashtags")
    @classmethod
    def check_hashtag_count(cls, v: List[str], info):
        platform = info.data.get("platform", "")
        rules = PLATFORM_RULES.get(platform, {})
        max_h, min_h = rules.get("max_hashtags"), rules.get("min_hashtags")

        if max_h is not None and len(v) > max_h:
            raise ValueError(
                f"{platform} copy has {len(v)} hashtags, max allowed is {max_h}."
            )
        if min_h is not None and len(v) < min_h:
            raise ValueError(
                f"{platform} copy has {len(v)} hashtags, minimum required is {min_h}."
            )
        return v

    @field_validator("headline")
    @classmethod
    def check_headline_length(cls, v: str, info):
        platform = info.data.get("platform", "")
        max_len = PLATFORM_RULES.get(platform, {}).get("max_headline_chars")
        if max_len and len(v) > max_len:
            raise ValueError(
                f"{platform} headline is {len(v)} characters, max allowed "
                f"is {max_len}."
            )
        return v
