"""
The Master Instruction Template — the "gatekeeper" of the pipeline.
"""

VALID_PLATFORMS = ["LinkedIn", "Instagram", "Email", "Twitter/X"]
VALID_TONES = ["Professional", "Witty", "Formal", "Casual", "Urgent"]

BRAND_RULES = """\
BRAND VOICE RULES (never break these):
- Never use the words "revolutionary", "game-changer", "disruptive", or "synergy"
- Write in second person ("you", "your"), not first person
- Do not make unverifiable superlative claims (e.g. "the best in the world")
- Always end with exactly one clear call to action (CTA)\
"""

PLATFORM_INSTRUCTIONS = {
    "LinkedIn": (
        "FORMAT: Paragraph form (no bullet lists). Maximum 300 words. "
        "Include at most 3 relevant hashtags. The tone should feel like "
        "thought leadership."
    ),
    "Instagram": (
        "FORMAT: The first line must hook the reader before the 'more' "
        "fold. Use short sentences and line breaks. Maximum 150 words "
        "before hashtags. Include between 5 and 10 relevant hashtags."
    ),
    "Email": (
        "FORMAT: Provide a subject line (max 50 characters) as the "
        "headline, a body (200-400 words), and a single clear CTA. "
        "Do not include hashtags."
    ),
    "Twitter/X": (
        "FORMAT: STRICT HARD LIMIT of 280 characters for headline + body "
        "combined. Include 1-2 relevant hashtags. Every word must earn "
        "its place."
    ),
}

OUTPUT_FORMAT_INSTRUCTIONS = """\
Return your response as a single valid JSON object with EXACTLY these
fields and no others:
{
  "headline": "<a short hook / title / subject line>",
  "body": "<the main copy text>",
  "hashtags": ["<list of hashtag strings, each including the # symbol>"],
  "cta": "<the single call-to-action text>",
  "platform": "<the platform name exactly as given below>",
  "tone_used": "<the tone exactly as given below>",
  "character_count": <integer: total characters in headline + body combined>
}
Return ONLY the JSON object. No markdown formatting, no code fences,
no explanation before or after.\
"""


def build_master_template(product_name: str, description: str,
                           platform: str, tone: str) -> str:
    """Compile the final prompt sent to the model."""
    if platform not in VALID_PLATFORMS:
        raise ValueError(f"Unknown platform '{platform}'. Choose from {VALID_PLATFORMS}")
    if tone not in VALID_TONES:
        raise ValueError(f"Unknown tone '{tone}'. Choose from {VALID_TONES}")

    platform_rules = PLATFORM_INSTRUCTIONS[platform]

    return f"""You are a senior marketing copywriter.

{BRAND_RULES}

TASK
Product name: {product_name}
Product description (raw facts from the client): {description}
Target platform: {platform}
Required tone: {tone}

PLATFORM RULES
{platform_rules}

OUTPUT FORMAT
{OUTPUT_FORMAT_INSTRUCTIONS}
"""
