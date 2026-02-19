# #**Lead Quality CLI**

A small command-line tool I built to make messy CSV lists of contacts easier to work with. It takes a CSV, cleans it up, flags common issues, removes duplicates, and outputs a payload + report that’s ready for import/sync.

The idea is simple: before importing a contact list into another system, I want a quick way to clean it, catch issues, and remove duplicates. Dry-run only for now, it generates payload.json and report.json, but doesn’t send anything to an API.

### **What it does**
- Reads a CSV export of leads/contacts
- Normalizes fields (trim spaces, lowercase emails, tidy company names)
- Validates required fields and basic email format
- Removes duplicates by email (keeps the first occurrence)
- Produces:
  - `out/payload.json` (mapped, sync-ready data)
  - `out/report.json` (quality summary + issues)

### **Quick start**
```bash
python src/main.py --input data/sample_leads.csv
