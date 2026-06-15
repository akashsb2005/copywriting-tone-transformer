"""
Real-time async pipeline.

Uses asyncio + httpx for concurrency, an asyncio.Semaphore to cap the
number of requests in flight at once, and Tenacity for automatic
retry with exponential backoff on transient failures.
"""
import asyncio
import json
import os
from typing import Dict, List, Union

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .params import get_max_tokens_kwarg, get_temperature
from .schemas import CopyOutput
from .templates import build_master_template

OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def _build_payload(product: Dict, model: str) -> dict:
    prompt = build_master_template(
        product["product_name"], product["description"],
        product["platform"], product["tone"],
    )
    temperature = get_temperature(product["platform"], product["tone"])
    token_kwarg = get_max_tokens_kwarg(model)

    return {
        "model": model,
        "messages": [
            {"role": "system", "content": "You output only valid JSON."},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        **token_kwarg,
    }


@retry(
    retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TransportError)),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=20),
)
async def _call_openai(client: httpx.AsyncClient, payload: dict, api_key: str) -> dict:
    response = await client.post(
        OPENAI_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json=payload,
        timeout=60.0,
    )
    response.raise_for_status()
    return response.json()


def _mock_response(product: Dict) -> dict:
    body = (
        f"{product['product_name']} brings a {product['tone'].lower()} "
        f"upgrade to your routine. {product['description'][:120]}"
    )
    hashtags = {
        "LinkedIn": ["#Innovation", "#Productivity"],
        "Instagram": ["#NewLaunch", "#MustHave", "#TechLife", "#Upgrade", "#DailyEssentials"],
        "Email": [],
        "Twitter/X": ["#NewLaunch"],
    }[product["platform"]]

    return {
        "headline": f"Meet {product['product_name']}",
        "body": body,
        "hashtags": hashtags,
        "cta": "Learn more today",
        "platform": product["platform"],
        "tone_used": product["tone"],
        "character_count": len(body) + len(f"Meet {product['product_name']}"),
    }


async def _generate_one(client, sem, product, model, api_key,
                         mock: bool = False) -> Union[CopyOutput, Exception]:
    try:
        if mock:
            await asyncio.sleep(0.3)
            data = _mock_response(product)
        else:
            payload = _build_payload(product, model)
            async with sem:
                raw = await _call_openai(client, payload, api_key)
            content = raw["choices"][0]["message"]["content"]
            data = json.loads(content)

        return CopyOutput(**data)
    except Exception as exc:
        return exc


async def realtime_pipeline(products: List[Dict], model: str = "gpt-4o",
                             max_concurrency: int = 5,
                             mock: bool = False) -> List[Union[CopyOutput, Exception]]:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not mock and not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Set it as an environment variable "
            "(or Colab secret), or pass mock=True to test without one."
        )

    sem = asyncio.Semaphore(max_concurrency)

    async with httpx.AsyncClient() as client:
        tasks = [
            _generate_one(client, sem, product, model, api_key, mock=mock)
            for product in products
        ]
        return await asyncio.gather(*tasks)
