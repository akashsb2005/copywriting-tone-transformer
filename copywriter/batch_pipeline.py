"""
Batch pipeline using the OpenAI Batch API.

Use this when results are NOT needed immediately. The Batch API
costs 50% less and runs on a separate, larger rate-limit pool, at
the cost of up to a 24-hour turnaround.
"""
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Union

from .params import get_max_tokens_kwarg, get_temperature
from .realtime import _mock_response
from .schemas import CopyOutput
from .templates import build_master_template


def _build_batch_requests(products: List[Dict], model: str) -> List[dict]:
    requests = []
    for i, product in enumerate(products):
        prompt = build_master_template(
            product["product_name"], product["description"],
            product["platform"], product["tone"],
        )
        temperature = get_temperature(product["platform"], product["tone"])
        token_kwarg = get_max_tokens_kwarg(model)

        requests.append({
            "custom_id": f"product-{i}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You output only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "response_format": {"type": "json_object"},
                **token_kwarg,
            },
        })
    return requests


def batch_pipeline(products: List[Dict], model: str = "gpt-4o",
                    poll_interval: int = 30,
                    mock: bool = False) -> List[Union[CopyOutput, Exception]]:
    if mock:
        results: List[Union[CopyOutput, Exception]] = []
        for product in products:
            try:
                results.append(CopyOutput(**_mock_response(product)))
            except Exception as exc:
                results.append(exc)
        return results

    from openai import OpenAI

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key)
    requests = _build_batch_requests(products, model)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
    ) as f:
        for req in requests:
            f.write(json.dumps(req) + "\n")
        jsonl_path = f.name

    with open(jsonl_path, "rb") as f:
        batch_file = client.files.create(file=f, purpose="batch")
    Path(jsonl_path).unlink(missing_ok=True)

    batch = client.batches.create(
        input_file_id=batch_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )

    while batch.status not in ("completed", "failed", "cancelled", "expired"):
        time.sleep(poll_interval)
        batch = client.batches.retrieve(batch.id)
        print(f"Batch status: {batch.status}")

    if batch.status != "completed":
        raise RuntimeError(f"Batch ended with status: {batch.status}")

    output_file = client.files.content(batch.output_file_id)
    raw_by_id = {
        json.loads(line)["custom_id"]: json.loads(line)
        for line in output_file.text.splitlines()
    }

    results = []
    for i in range(len(products)):
        record = raw_by_id.get(f"product-{i}")
        try:
            content = record["response"]["body"]["choices"][0]["message"]["content"]
            data = json.loads(content)
            results.append(CopyOutput(**data))
        except Exception as exc:
            results.append(exc)

    return results
