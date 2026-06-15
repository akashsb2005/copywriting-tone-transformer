<<<<<<< HEAD
# Automated Copywriting & Tone Transformer

A Python pipeline that generates platform-specific, tone-matched marketing
copy from raw product facts, using dynamic prompt templates, tuned
inference parameters, and Pydantic-validated output.

## Setup
```bash
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
```

## Usage
```bash
# Mock mode (no API key needed)
python run.py --csv data/sample_products.csv --mock

# Real-time pipeline
python run.py --product "NovaBrew Pro" --platform Instagram --tone Witty \
  --description "AI coffee maker, 30-second brew"

# Batch API (50% cheaper, up to 24h)
python run.py --csv data/sample_products.csv +b
```
=======
# copywriting-tone-transformer
Automated Copywriting &amp; Tone Transformer — Generative AI Project 2
>>>>>>> origin/main
