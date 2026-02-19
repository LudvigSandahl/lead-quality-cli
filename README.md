**lead-quality-cli**

A small command-line tool I built to make messy CSV contact lists easier to work with before an import/sync.
It cleans and validates rows, removes duplicates, and writes two output files you can review.

This is **dry-run only** for now — it generates output files, but doesn’t send anything to an API.

**Run**
```bash
python src/main.py --input data/sample_leads.csv
