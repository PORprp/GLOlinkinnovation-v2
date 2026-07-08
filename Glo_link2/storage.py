"""
Persistence layer for scanned GLO ticket records.

Default backend is a CSV file acting as the "database" (matches the 6-column
+ metadata dataframe shape from the concept doc). If a Google service-account
key is present at GOOGLE_SHEETS_CREDENTIALS_PATH and gspread is installed,
records can optionally be mirrored to a Google Sheet instead/in addition --
this is opt-in since it requires the user's own Google Cloud credentials.
"""

import os

import pandas as pd

from ocr_engine import FIELDS

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CSV_PATH = os.path.join(DATA_DIR, "tickets.csv")

COLUMNS = FIELDS + ["raw_text", "scanned_at", "claim_status"]


def _ensure_store():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        pd.DataFrame(columns=COLUMNS).to_csv(CSV_PATH, index=False)


def load_tickets() -> pd.DataFrame:
    _ensure_store()
    return pd.read_csv(CSV_PATH, dtype=str).fillna("")


def save_tickets(df: pd.DataFrame):
    _ensure_store()
    df.to_csv(CSV_PATH, index=False)


def add_ticket(df: pd.DataFrame, record: dict) -> tuple[pd.DataFrame, str]:
    """Append a scanned record, flagging duplicate unique_number claims.

    Returns (updated_dataframe, claim_status) where claim_status is one of
    "new" (first time this ticket has been registered) or "duplicate"
    (this unique_number was already claimed -- mirrors the GLO-Link
    "Verified - Already Claimed" case).
    """
    unique_number = record.get("unique_number")
    is_duplicate = bool(unique_number) and (df["unique_number"] == unique_number).any()
    claim_status = "duplicate" if is_duplicate else "new"

    row = {col: record.get(col, "") for col in COLUMNS}
    row["claim_status"] = claim_status

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    save_tickets(df)
    return df, claim_status


def sync_to_google_sheets(df: pd.DataFrame, sheet_name: str, credentials_path: str):
    """Optional mirror of the ticket dataframe to a Google Sheet.

    Requires `pip install gspread google-auth` and a service-account JSON key
    with edit access to the target spreadsheet shared with the service
    account's email address.
    """
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    sheet.clear()
    sheet.update([df.columns.tolist()] + df.astype(str).values.tolist())
