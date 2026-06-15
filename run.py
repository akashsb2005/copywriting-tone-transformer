#!/usr/bin/env python3
"""
Project 2: Automated Copywriting & Tone Transformer
Command-line entry point.
"""
import argparse
import asyncio
import sys

from copywriter.batch_pipeline import batch_pipeline
from copywriter.csv_loader import load_products_from_csv
from copywriter.realtime import realtime_pipeline
from copywriter.templates import VALID_PLATFORMS, VALID_TONES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Automated Copywriting & Tone Transformer",
        prefix_chars="-+",
    )
    parser.add_argument("--product", help="Product name")
    parser.add_argument("--description", default="", help="Raw product description")
    parser.add_argument("--platform", choices=VALID_PLATFORMS, help="Target platform")
    parser.add_argument("--tone", choices=VALID_TONES, default="Professional")
    parser.add_argument("--model", default="gpt-4o", help="Model name (default: gpt-4o)")
    parser.add_argument("--concurrency", type=int, default=5,
                         help="Max concurrent requests in real-time mode")
    parser.add_argument("--csv", default="", help="Path to a CSV file of products")
    parser.add_argument("+b", "--batch", action="store_true",
                         help="Use the OpenAI Batch API (cheaper, up to 24h)")
    parser.add_argument("--mock", action="store_true",
                         help="Run the full pipeline without calling the real API")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.csv:
        products = load_products_from_csv(args.csv)
    elif args.product and args.platform:
        products = [{
            "product_name": args.product,
            "description": args.description,
            "platform": args.platform,
            "tone": args.tone,
        }]
    else:
        print("Provide either --csv <file>  OR  both --product and --platform.")
        sys.exit(1)

    if args.batch:
        print(f"Running BATCH pipeline for {len(products)} product(s)...")
        results = batch_pipeline(products, model=args.model, mock=args.mock)
    else:
        print(f"Running REAL-TIME pipeline for {len(products)} product(s)...")
        results = asyncio.run(
            realtime_pipeline(products, model=args.model,
                               max_concurrency=args.concurrency, mock=args.mock)
        )

    for i, result in enumerate(results):
        print("\n" + "=" * 60)
        if isinstance(result, Exception):
            print(f"Product {i + 1} ({products[i]['product_name']}): "
                  f"FAILED -> {result}")
            continue

        print(f"Product {i + 1}: {products[i]['product_name']} | "
              f"{result.platform} | {result.tone_used}")
        print("-" * 60)
        print(f"Headline: {result.headline}")
        print(f"Body:\n{result.body}")
        if result.hashtags:
            print(f"Hashtags: {' '.join(result.hashtags)}")
        print(f"CTA: {result.cta}")
        print(f"Character count: {result.character_count}")


if __name__ == "__main__":
    main()
