# AI Invoice Intelligence Pipeline

An AI-powered document intelligence system that extracts structured data from invoice PDFs, validates the output, and exports clean records to both JSON and CSV — built with LangChain, GPT-4o-mini, and Pydantic.

---

## What it does

- Accepts single or batch invoice PDF uploads via Streamlit
- Extracts raw text from PDFs using PyPDFLoader
- Uses GPT-4o-mini to extract all key invoice fields
- Validates and enforces data types with a Pydantic schema
- Displays a structured summary table in the UI
- Saves all extracted records to both JSON and CSV
- Provides one-click download for both output formats

---

## Extracted fields

| Field | Description |
|---|---|
| `vendor_name` | Company or person issuing the invoice |
| `vendor_address` | Vendor address |
| `invoice_number` | Invoice or reference number |
| `invoice_date` | Date of the invoice |
| `due_date` | Payment due date |
| `customer_name` | Bill-to company or person |
| `customer_address` | Customer address |
| `line_items` | List of items with description, quantity, unit price, total |
| `subtotal` | Amount before tax |
| `tax_rate` | Tax percentage |
| `tax_amount` | Tax amount |
| `total_amount` | Final invoice total |
| `currency` | Currency code (USD, EUR, NGN, etc.) |
| `payment_terms` | e.g. Net 30 |
| `notes` | Additional notes or comments |

---

## System architecture

| Layer | Component | Description |
|---|---|---|
| User interface | Streamlit (`app.py`) | File upload, summary table, download buttons |
| PDF parsing | `PyPDFLoader` | Extracts raw text from uploaded PDFs |
| Extraction | `ChatOpenAI` (gpt-4o-mini) | Extracts structured fields from invoice text |
| Validation | Pydantic (`validator.py`) | Type checks and enforces schema on extracted data |
| Storage | `storage.py` | Saves records to `invoices.json` and `invoices.csv` |
| Prompts | `prompts.py` | System prompt for the extraction agent |

---

## Tech stack

- Python
- LangChain-OpenAI (`ChatOpenAI`)
- LangChain-Community (`PyPDFLoader`)
- Pydantic (schema validation)
- Pandas (CSV handling)
- Streamlit
- python-dotenv

---

## Project structure

```
invoice-intelligence-pipeline/
│
├── app.py              # Streamlit UI
├── extractor.py        # PDF parsing + LLM extraction
├── validator.py        # Pydantic invoice schema
├── storage.py          # Saves to JSON and CSV
├── prompts.py          # Extraction system prompt
├── outputs/            # Auto-created — stores invoices.json and invoices.csv
├── requirements.txt
└── README.md
```

---

## How to run

**1. Clone the repo**
```bash
git clone https://github.com/edubio228/invoice-intelligence-pipeline.git
cd invoice-intelligence-pipeline
```

**2. Create and activate a virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux
```

**3. Add your OpenAI API key**

Create a `.env` file in the root:
```
OPENAI_API_KEY=your_key_here
```

**4. Install dependencies**
```bash
pip install -r requirements.txt
```

**5. Launch the app**
```bash
streamlit run app.py
```

Opens at `http://localhost:8501`. Upload any invoice PDF to begin.

---

## Sample output

Input: `invoice_acme_oct2025.pdf`

Extracted summary table:

| File | Vendor | Invoice No. | Date | Total | Status |
|---|---|---|---|---|---|
| invoice_acme_oct2025.pdf | Acme Corp | INV-00482 | 2025-10-01 | USD 4,250.00 | Extracted |

`invoices.json` record:
```json
{
  "vendor_name": "Acme Corp",
  "invoice_number": "INV-00482",
  "invoice_date": "2025-10-01",
  "due_date": "2025-10-31",
  "customer_name": "TechCorp Lagos",
  "total_amount": 4250.00,
  "currency": "USD",
  "payment_terms": "Net 30",
  "line_items": [
    {
      "description": "Software licence - annual",
      "quantity": 1,
      "unit_price": 4250.00,
      "total": 4250.00
    }
  ]
}
```

---

## Design decisions

**Pydantic validation** — raw LLM output is unpredictable. Running it through a Pydantic model enforces types, catches missing fields, and ensures every record saved to disk has a consistent structure.

**Temp file approach for PDFs** — Streamlit uploads return bytes objects, not file paths. Writing to a temp file and cleaning up after lets PyPDFLoader work without leaving files on disk.

**Separate JSON and CSV outputs** — JSON preserves the full nested structure including line items. CSV flattens the record for easy import into Excel, Google Sheets, or any database. Both are generated from every run.

**Batch processing** — the pipeline handles multiple PDFs in a single session, appending each extracted record to the same output files so you build up a dataset over time.