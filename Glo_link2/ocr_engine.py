"""
Field-extraction engine for Thai Government Lottery Office (GLO) tickets.

Pipeline: preprocess a photo -> run Tesseract OCR (Thai+English) -> pull out
the 6 structured fields called out in the ticket layout:

    ticket_number   6-digit prize number (large yellow boxes)
    draw_date_th    Thai-calendar draw date, e.g. "1 กรกฎาคม 2569"
    draw_date_en    Gregorian draw date, e.g. "1 July 2026"
    period          งวดที่ (draw period, 2 digits)
    batch           ชุดที่ (batch/set number, 2 digits)
    unique_number   long barcode/serial number under "ชุดที่"

OCR on a phone photo is noisy, so every field returned here is a best-effort
guess meant to prefill a form the user reviews before it is saved as a claim
record -- not to be trusted blindly.
"""

import re
from datetime import datetime

import cv2
import numpy as np
import pytesseract
import shutil
import os
import sys

# Ensure pytesseract knows where the tesseract binary is. In some
# environments (e.g. GUI-launched apps or VS Code), /opt/homebrew/bin
# may not be on PATH; attempt to find common installation locations and
# set pytesseract.pytesseract.tesseract_cmd so OCR works reliably.
if shutil.which("tesseract") is None:
    common_paths = [
        "/opt/homebrew/bin/tesseract",
        "/usr/local/bin/tesseract",
        "/usr/bin/tesseract",
        os.path.join(sys.prefix, "bin", "tesseract"),
    ]
    for p in common_paths:
        if os.path.exists(p):
            pytesseract.pytesseract.tesseract_cmd = p
            break

THAI_MONTHS = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม",
]
EN_MONTHS = (
    r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?"
)

TICKET_NUMBER_RE = re.compile(r"(?<!\d)\d{6}(?!\d)")
DRAW_DATE_TH_RE = re.compile(
    r"\d{1,2}\s*(?:%s)\s*\d{4}" % "|".join(THAI_MONTHS)
)
DRAW_DATE_EN_RE = re.compile(
    r"\d{1,2}\s+(?:%s)\.?\s+\d{4}" % EN_MONTHS, re.IGNORECASE
)
PERIOD_RE = re.compile(r"งวดที่\D{0,10}(\d{1,3})")
BATCH_RE = re.compile(r"ชุดที่\D{0,10}(\d{1,3})")
# barcode / serial: long digit run, optionally split by a hyphen, e.g.
# "262601984407801-5359"
UNIQUE_NUMBER_RE = re.compile(r"(?<!\d)\d{10,}(?:-\d{2,6})?(?!\d)")

FIELDS = ["ticket_number", "draw_date_th", "draw_date_en", "period", "batch", "unique_number"]


def preprocess(image_bgr, max_dim=1800):
    """Resize, denoise and binarize a photo so Tesseract has an easier time."""
    h, w = image_bgr.shape[:2]
    scale = max_dim / max(h, w)
    if scale < 1:
        image_bgr = cv2.resize(image_bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, 15
    )
    return thresh


def run_ocr(image, lang="tha+eng"):
    """Run Tesseract with a sparse-text page mode (fields are scattered on the ticket)."""
    config = "--psm 11"
    try:
        return pytesseract.image_to_string(image, lang=lang, config=config)
    except pytesseract.pytesseract.TesseractNotFoundError as exc:
        # Raise a clearer runtime error so callers (UI) can present
        # actionable instructions instead of crashing with a stacktrace.
        raise RuntimeError(
            "Tesseract Not Found: tesseract is not installed or it's not in your PATH."
            " Install Tesseract (e.g. on macOS: `brew install tesseract tesseract-lang`)."
        ) from exc


def _first_match(pattern, text):
    m = pattern.search(text)
    return m.group(0) if m else None


def _first_group(pattern, text):
    m = pattern.search(text)
    return m.group(1) if m else None


def parse_fields(raw_text):
    """Pull the 6 structured GLO ticket fields out of raw OCR text."""
    text = raw_text.replace("\n", " ")

    unique_number = _first_match(UNIQUE_NUMBER_RE, text)
    # the ticket number is a standalone 6-digit run that is NOT part of the
    # (usually much longer) barcode/serial number
    remainder = UNIQUE_NUMBER_RE.sub(" ", text)
    ticket_number = _first_match(TICKET_NUMBER_RE, remainder)

    return {
        "ticket_number": ticket_number,
        "draw_date_th": _first_match(DRAW_DATE_TH_RE, text),
        "draw_date_en": _first_match(DRAW_DATE_EN_RE, text),
        "period": _first_group(PERIOD_RE, text),
        "batch": _first_group(BATCH_RE, text),
        "unique_number": unique_number,
        "raw_text": raw_text.strip(),
        "scanned_at": datetime.now().isoformat(timespec="seconds"),
    }


def scan_ticket(image_bgr):
    """Convenience wrapper: preprocess + OCR + parse a BGR image (e.g. from cv2/PIL)."""
    processed = preprocess(image_bgr)
    raw_text = run_ocr(processed)
    return parse_fields(raw_text), processed


def image_from_bytes(data: bytes) -> np.ndarray:
    arr = np.frombuffer(data, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)
