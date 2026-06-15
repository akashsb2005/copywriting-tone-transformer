"""CSV ingestion layer: read product variables from a spreadsheet."""
import csv
from pathlib import Path
from typing import Dict, List

REQUIRED_COLUMNS = {"product_name", "description", "platform", "tone"}


def load_products_from_csv(filepath: str) -> List[Dict]:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {filepath}")

    products: List[Dict] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing required columns: {missing}")

        for row in reader:
            products.append({
                "product_name": row["product_name"].strip(),
                "description": row["description"].strip(),
                "platform": row["platform"].strip(),
                "tone": row["tone"].strip(),
            })
    return products
