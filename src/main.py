import argparse
import csv
import json
import os
import re
from datetime import datetime, timezone

# Quick email format check (good enough for spotting obvious bad rows).
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Normalize input so the rest of the pipeline behaves consistently.
def clean_row(row: dict) -> dict:
    def norm(x: str) -> str:
        return (x or "").strip()

    email = norm(row.get("email", "")).lower()
    company = " ".join(norm(row.get("company", "")).split())

    return {
        "first_name": norm(row.get("first_name", "")),
        "last_name": norm(row.get("last_name", "")),
        "email": email,
        "company": company,
        "notes": norm(row.get("notes", "")),
    }


def is_valid(row: dict) -> bool:
    return bool(row["first_name"] and row["last_name"] and EMAIL_RE.match(row["email"]))


def main():
    parser = argparse.ArgumentParser(description="Lead Quality CLI (dry-run)")
    parser.add_argument("--input", required=True, help="Path to CSV file")
    parser.add_argument("--mapping", default="config/mapping.json", help="Path to mapping.json")
    args = parser.parse_args()

    with open(args.input, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    cleaned = [clean_row(r) for r in rows]

    invalid = []
    valid = []
    for i, r in enumerate(cleaned, start=1):
        if is_valid(r):
            valid.append(r)
        else:
            invalid.append({"row": i, "email": r["email"]})

    seen = set()
    deduped = []
    duplicates = []

    # Dedupe by email to avoid importing the same contact twice.
    for i, r in enumerate(valid, start=1):
        if r["email"] in seen:
            duplicates.append({"email": r["email"]})
        else:
            seen.add(r["email"])
            deduped.append(r)

    # Output format is config-driven to mimic real customer-specific mappings.
    with open(args.mapping, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    payload = []
    for r in deduped:
        item = {}
        for target, sources in mapping.items():
            values = [r.get(s, "") for s in sources]
            if target == "full_name":
                item[target] = " ".join([v for v in values if v]).strip()
            else:
                item[target] = values[0] if len(values) == 1 else values
        payload.append(item)

        # Ensure the output folder exists before writing files.
        os.makedirs("out", exist_ok=True)

    os.makedirs("out", exist_ok=True)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_file": args.input,
        "total_rows": len(rows),
        "valid_rows": len(deduped),
        "invalid_rows": len(invalid),
        "duplicates": len(duplicates),
        "invalid_examples": invalid[:5],
        "duplicate_examples": duplicates[:5],
    }

    with open("out/payload.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    with open("out/report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Dry-run: write results to disk (no network calls).
    print(f"Loaded rows: {len(rows)}")
    print(f"Valid: {len(deduped)} | Invalid: {len(invalid)} | Duplicates: {len(duplicates)}")
    print("Wrote out/payload.json and out/report.json")


if __name__ == "__main__":
    main()
