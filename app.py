import streamlit as st
import pandas as pd
import json
import os
from extractor import extract_invoice_data
from storage import save_invoice, JSON_FILE, CSV_FILE

st.set_page_config(
    page_title="Invoice Intelligence Pipeline",
    page_icon="🧾",
    layout="wide"
)

st.title("AI Invoice Intelligence Pipeline")
st.caption("Upload invoice PDFs — extract, validate, and export structured data")

# File uploader
uploaded_files = st.file_uploader(
    "Upload invoice PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    st.divider()
    results = []

    for uploaded_file in uploaded_files:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            try:
                invoice = extract_invoice_data(
                    uploaded_file.read(),
                    uploaded_file.name
                )
                save_invoice(invoice)
                results.append({"status": "success", "file": uploaded_file.name, "invoice": invoice})
                st.success(f"Extracted: {uploaded_file.name}")
            except Exception as e:
                results.append({"status": "error", "file": uploaded_file.name, "error": str(e)})
                st.error(f"Failed: {uploaded_file.name} — {e}")

    st.divider()
    st.subheader("Extraction summary")

    # Build summary table
    summary_rows = []
    for r in results:
        if r["status"] == "success":
            inv = r["invoice"]
            summary_rows.append({
                "File": r["file"],
                "Vendor": inv.vendor_name or "—",
                "Invoice No.": inv.invoice_number or "—",
                "Date": inv.invoice_date or "—",
                "Total": f"{inv.currency or ''} {inv.total_amount or '—'}",
                "Customer": inv.customer_name or "—",
                "Status": "Extracted"
            })
        else:
            summary_rows.append({
                "File": r["file"],
                "Vendor": "—",
                "Invoice No.": "—",
                "Date": "—",
                "Total": "—",
                "Customer": "—",
                "Status": "Failed"
            })

    if summary_rows:
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)

    # Detailed view per invoice
    for r in results:
        if r["status"] == "success":
            inv = r["invoice"]
            with st.expander(f"Full details: {r['file']}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Vendor**")
                    st.write(inv.vendor_name or "—")
                    st.markdown("**Invoice number**")
                    st.write(inv.invoice_number or "—")
                    st.markdown("**Invoice date**")
                    st.write(inv.invoice_date or "—")
                    st.markdown("**Due date**")
                    st.write(inv.due_date or "—")
                    st.markdown("**Payment terms**")
                    st.write(inv.payment_terms or "—")

                with col2:
                    st.markdown("**Customer**")
                    st.write(inv.customer_name or "—")
                    st.markdown("**Subtotal**")
                    st.write(f"{inv.currency or ''} {inv.subtotal or '—'}")
                    st.markdown("**Tax**")
                    st.write(f"{inv.tax_amount or '—'}")
                    st.markdown("**Total**")
                    st.write(f"{inv.currency or ''} {inv.total_amount or '—'}")
                    st.markdown("**Currency**")
                    st.write(inv.currency or "—")

                if inv.line_items:
                    st.markdown("**Line items**")
                    line_df = pd.DataFrame([item.model_dump() for item in inv.line_items])
                    st.dataframe(line_df, use_container_width=True)

    st.divider()
    st.subheader("Download outputs")

    col1, col2 = st.columns(2)

    with col1:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, "r") as f:
                st.download_button(
                    label="Download invoices.json",
                    data=f.read(),
                    file_name="invoices.json",
                    mime="application/json"
                )

    with col2:
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, "r") as f:
                st.download_button(
                    label="Download invoices.csv",
                    data=f.read(),
                    file_name="invoices.csv",
                    mime="text/csv"
                )