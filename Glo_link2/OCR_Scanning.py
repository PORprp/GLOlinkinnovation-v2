"""
GLO-Link ticket scanner prototype (Streamlit).

Run with:
    streamlit run "OCR Scanning.py"

Flow mirrors the mobile mockup: user takes a photo of the ticket -> the app
OCRs it and prefills the 6 structured fields -> user reviews/corrects the
fields -> confirms to register the ticket into the "database" (CSV today,
optionally mirrored to Google Sheets).
"""

import streamlit as st

from ocr_engine import FIELDS, image_from_bytes, scan_ticket
import storage

st.set_page_config(page_title="GLO-Link · สแกนเก็บสลาก", page_icon="\U0001F39F️")

FIELD_LABELS = {
    "ticket_number": "6-digit ticket number",
    "draw_date_th": "Draw date (Thai)",
    "draw_date_en": "Draw date (English)",
    "period": "Period (งวดที่)",
    "batch": "Batch (ชุดที่)",
    "unique_number": "Unique / barcode number",
}

if "tickets" not in st.session_state:
    st.session_state.tickets = storage.load_tickets()
if "pending" not in st.session_state:
    st.session_state.pending = None
if "scan_message" not in st.session_state:
    st.session_state.scan_message = ""
if "scan_status" not in st.session_state:
    st.session_state.scan_status = ""

st.title("\U0001F39F️ สแกนเก็บสลาก — GLO-Link ticket scanner")
st.caption("Take a photo of your lottery ticket to register it and claim ownership.")


def ticket_duplicate_status(record, tickets):
    unique_number = (record.get("unique_number") or "").strip()
    if not unique_number:
        return "invalid"

    if (tickets["unique_number"] == unique_number).any():
        return "duplicate"
    return "new"

tab_scan, tab_records = st.tabs(["Scan ticket", "My registered tickets"])

with tab_scan:
    photo = st.camera_input("วาง QR Code / บาร์โค้ดของสลากให้อยู่ในกรอบ (place the ticket inside the frame)")

    if photo is not None:
        image_bgr = image_from_bytes(photo.getvalue())
        with st.spinner("Reading ticket..."):
            try:
                record, processed = scan_ticket(image_bgr)
            except RuntimeError as exc:
                # Likely a missing Tesseract binary — present a clear message
                msg = str(exc)
                st.error(
                    "OCR failure: Tesseract is not installed or not found.\n"
                    "Install it and restart the app: `brew install tesseract tesseract-lang` (macOS)"
                )
                st.session_state.scan_message = (
                    "OCR service unavailable: ติดตั้ง Tesseract แล้วเริ่มแอปใหม่"
                )
                st.session_state.scan_status = "error"
                record = None
                processed = None
        status = None
        if record is not None:
            status = ticket_duplicate_status(record, st.session_state.tickets)
        # If status is None, an earlier error occurred (e.g. OCR failure)
        if status == "duplicate":
            st.session_state.scan_message = (
                "ไม่สามารถบันทึกสลากอีกครั้งได้ เนื่องจากสลากใบนี้ถูกบันทึกข้อมูลแล้ว"
            )
            st.session_state.scan_status = "duplicate"
            st.session_state.pending = None
        elif status == "new":
            st.session_state.scan_message = "บันทึกสลาก สำเร็จ"
            st.session_state.scan_status = "new"
            st.session_state.pending = record
        elif status == "invalid":
            st.session_state.scan_message = "ข้อมูลสลากไม่สมบูรณ์ กรุณาตรวจสอบและถ่ายใหม่"
            st.session_state.scan_status = "invalid"
            st.session_state.pending = None
        else:
            # status is None: keep any existing scan_message (e.g. OCR error)
            pass

        if processed is not None:
            with st.expander("Preprocessed image (what OCR actually saw)"):
                st.image(processed, channels="GRAY", use_container_width=True)

    if st.session_state.scan_message:
        if st.session_state.scan_status == "duplicate":
            st.warning(st.session_state.scan_message)
        elif st.session_state.scan_status == "new":
            st.success(st.session_state.scan_message)
        else:
            st.error(st.session_state.scan_message)

    if st.session_state.pending:
        st.subheader("Review extracted fields")
        st.caption("OCR is a best guess — correct any field before confirming.")

        with st.form("review_form"):
            values = {}
            for field in FIELDS:
                values[field] = st.text_input(
                    FIELD_LABELS[field], value=st.session_state.pending.get(field) or ""
                )
            confirmed = st.form_submit_button("✅ สแกนสำเร็จ (Confirm & register)")

        if confirmed:
            if not values["unique_number"] or not values["ticket_number"]:
                st.error("Ticket number and unique/barcode number are required to register a claim.")
            else:
                record = {**st.session_state.pending, **values}
                st.session_state.tickets, claim_status = storage.add_ticket(
                    st.session_state.tickets, record
                )
                st.session_state.pending = None
                if claim_status == "duplicate":
                    st.warning(
                        "ไม่สามารถบันทึกสลากอีกครั้งได้ เนื่องจากสลากใบนี้ถูกบันทึกข้อมูลแล้ว"
                    )
                else:
                    st.success("บันทึกสลาก สำเร็จ")
                st.session_state.scan_message = ""
                st.session_state.scan_status = ""

with tab_records:
    st.subheader("Registered tickets")
    df = st.session_state.tickets
    if df.empty:
        st.info("No tickets registered yet — scan one from the Scan ticket tab.")
    else:
        display_cols = FIELDS + ["scanned_at", "claim_status"]
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
        n_dupes = (df["claim_status"] == "duplicate").sum()
        if n_dupes:
            st.warning(f"{n_dupes} duplicate claim(s) need manual review.")
        st.download_button(
            "Download as CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="tickets.csv",
            mime="text/csv",
        )

        with st.expander("Sync to Google Sheets (optional)"):
            sheet_name = st.text_input("Google Sheet name")
            creds_path = st.text_input(
                "Service account credentials JSON path", value="credentials.json"
            )
            if st.button("Sync now"):
                try:
                    storage.sync_to_google_sheets(df, sheet_name, creds_path)
                    st.success(f"Synced {len(df)} rows to '{sheet_name}'.")
                except Exception as exc:
                    st.error(f"Sync failed: {exc}")
