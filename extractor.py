import json
import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv
from prompts import EXTRACTION_PROMPT
from validator import validate_invoice, Invoice

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def extract_text_from_pdf(file_bytes: bytes, filename: str) -> str:
    """Save uploaded bytes to a temp file and extract text via PyPDFLoader."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        loader = PyPDFLoader(tmp_path)
        pages = loader.load()
        full_text = "\n".join([page.page_content for page in pages])
    finally:
        os.unlink(tmp_path)

    return full_text


def extract_invoice_data(file_bytes: bytes, filename: str) -> Invoice:
    """Full pipeline: PDF text → LLM extraction → Pydantic validation."""

    # Step 1: Extract raw text
    raw_text = extract_text_from_pdf(file_bytes, filename)

    if not raw_text.strip():
        raise ValueError(f"Could not extract text from {filename}. The PDF may be scanned or image-based.")

    # Step 2: LLM extraction
    messages = [
        SystemMessage(content=EXTRACTION_PROMPT),
        HumanMessage(content=f"Invoice text:\n\n{raw_text}")
    ]
    response = llm.invoke(messages)
    raw_json = response.content.strip()

    # Strip markdown code fences if present
    if raw_json.startswith("```"):
        raw_json = raw_json.split("```")[1]
        if raw_json.startswith("json"):
            raw_json = raw_json[4:]

    # Step 3: Parse JSON
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned invalid JSON for {filename}: {e}")

    # Step 4: Validate with Pydantic
    invoice = validate_invoice(data, source_file=filename)
    return invoice