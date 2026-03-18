import json
import os
import pandas as pd
from datetime import datetime
from validator import Invoice

OUTPUTS_DIR = "outputs"
JSON_FILE = os.path.join(OUTPUTS_DIR, "invoices.json")
CSV_FILE = os.path.join(OUTPUTS_DIR, "invoices.csv")


def ensure_outputs_dir():
    os.makedirs(OUTPUTS_DIR, exist_ok=True)


def invoice_to_dict(invoice: Invoice) -> dict:
    """Flatten invoice to a dict, serialising line items as a string."""
    data = invoice.model_dump()
    if data.get("line_items"):
        data["line_items"] = json.dumps(data["line_items"])
    return data


def save_to_json(invoice: Invoice):
    """Append invoice to invoices.json."""
    ensure_outputs_dir()

    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r") as f:
            records = json.load(f)
    else:
        records = []

    records.append(invoice.model_dump())

    with open(JSON_FILE, "w") as f:
        json.dump(records, f, indent=2)


def save_to_csv(invoice: Invoice):
    """Append invoice row to invoices.csv."""
    ensure_outputs_dir()

    row = invoice_to_dict(invoice)
    row["extracted_at"] = datetime.now().isoformat()

    df_new = pd.DataFrame([row])

    if os.path.exists(CSV_FILE):
        df_existing = pd.read_csv(CSV_FILE)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_csv(CSV_FILE, index=False)


def save_invoice(invoice: Invoice):
    """Save invoice to both JSON and CSV."""
    save_to_json(invoice)
    save_to_csv(invoice)