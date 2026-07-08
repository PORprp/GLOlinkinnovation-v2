# GLO-Link OCR prototype

Streamlit prototype: scan a Thai lottery ticket with your phone camera, OCR
pulls out the 6 structured fields, you review/correct them, and confirming
registers the ticket as a claim record (CSV "database", with duplicate-claim
detection on the unique/barcode number).

## Setup

```bash
cd "Glo link2"
pip install -r requirements.txt
```

Tesseract OCR must also be installed (with the Thai language pack) since
`pytesseract` just calls the `tesseract` CLI:

```bash
brew install tesseract tesseract-lang   # macOS
```

## Run

```bash
streamlit run "OCR Scanning.py"
```

Open the printed **Network URL** from your iPhone's Safari (same Wi-Fi) to
use the phone camera through `st.camera_input`.

## Files

- `OCR Scanning.py` — Streamlit app (camera capture, field review form, records table)
- `ocr_engine.py` — image preprocessing + OCR + regex field extraction
- `storage.py` — CSV-backed dataframe storage, duplicate-claim flagging, optional Google Sheets sync
- `data/tickets.csv` — created on first run, acts as the ticket database

## Notes

- OCR accuracy on phone photos varies with lighting/angle — every field is
  editable in the review form before it's saved, since these records back
  ownership claims.
- Google Sheets sync is optional: create a service-account key, share the
  target sheet with its email, then use the "Sync to Google Sheets" panel
  under the records tab.
