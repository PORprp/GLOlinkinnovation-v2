"""
Camera-based OCR scanner for Thai lottery tickets.

Captures frames from a webcam, lets the user grab a frame, preprocesses it,
runs OCR to extract fields printed on a GLO ticket (6-digit prize number,
2-digit set number, 80-baht price marker), and collects every scan as a row
in a pandas DataFrame.

Requirements:
    pip install opencv-python pytesseract pandas
    Tesseract OCR engine must be installed separately:
        macOS:   brew install tesseract
        Ubuntu:  sudo apt install tesseract-ocr
        Windows: https://github.com/UB-Mannheim/tesseract/wiki

Usage:
    python OCR.py [--camera 0] [--out results.csv]

Controls (in the preview window):
    c - capture the current frame, run OCR, add a row to the DataFrame
    q - quit and save the collected DataFrame to --out
"""

import argparse
import re
import time
from datetime import datetime

import cv2
import pandas as pd
import pytesseract

TICKET_NUMBER_PATTERN = re.compile(r"\b\d{6}\b")
SET_NUMBER_PATTERN = re.compile(r"\b\d{2}\b")


def preprocess(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11
    )
    return thresh


def run_ocr(image):
    config = "--psm 6 -c tessedit_char_whitelist=0123456789"
    return pytesseract.image_to_string(image, config=config)


def parse_fields(text):
    """Pull structured fields out of the raw OCR text of a GLO ticket."""
    ticket_numbers = TICKET_NUMBER_PATTERN.findall(text)
    # the 2-digit set number is any short number left over once 6-digit
    # prize numbers are stripped out of the text
    remainder = TICKET_NUMBER_PATTERN.sub(" ", text)
    set_numbers = SET_NUMBER_PATTERN.findall(remainder)

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "ticket_number": ticket_numbers[0] if ticket_numbers else None,
        "set_number": set_numbers[0] if set_numbers else None,
        "all_ticket_numbers": ";".join(ticket_numbers),
        "raw_text": text.strip(),
    }


def open_camera(camera_index, retries=5, delay=0.25):
    last_error = None
    for attempt in range(1, retries + 1):
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            cap.release()
            last_error = f"Could not open camera index {camera_index}"
            time.sleep(delay)
            continue

        ok, _ = cap.read()
        if ok:
            return cap

        cap.release()
        last_error = f"Camera index {camera_index} opened but failed to read a frame"
        time.sleep(delay)

    raise RuntimeError(last_error)


def main():
    parser = argparse.ArgumentParser(description="Scan lottery ticket data via camera OCR")
    parser.add_argument("--camera", type=int, default=0, help="camera device index")
    parser.add_argument("--out", default="ocr_results.csv", help="path to save the collected DataFrame")
    args = parser.parse_args()

    try:
        cap = open_camera(args.camera)
    except RuntimeError as exc:
        print(str(exc))
        print("If you are on macOS, grant camera access to Terminal or VS Code in System Settings > Privacy & Security > Camera and try again.")
        raise SystemExit(1) from exc

    print("Press 'c' to capture and scan, 'q' to quit and save.")
    records = []
    last_row = None

    while True:
        frame = None
        for _ in range(5):
            ok, frame = cap.read()
            if ok and frame is not None:
                break
            time.sleep(0.1)

        if frame is None or not ok:
            print("Failed to read from camera after retries.")
            break

        display = frame.copy()
        if last_row:
            text = f"Last: {last_row['ticket_number']} (set {last_row['set_number']})"
            cv2.putText(display, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(display, f"Scanned: {len(records)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("Lottery Ticket Scanner", display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break
        elif key == ord("c"):
            processed = preprocess(frame)
            raw_text = run_ocr(processed)
            row = parse_fields(raw_text)
            records.append(row)
            last_row = row

            if row["ticket_number"]:
                print(f"Detected ticket number: {row['ticket_number']} (set {row['set_number']})")
            else:
                print("No 6-digit ticket number detected. Raw OCR text:")
                print(raw_text.strip() or "(empty)")

    cap.release()
    cv2.destroyAllWindows()

    df = pd.DataFrame(records, columns=["timestamp", "ticket_number", "set_number", "all_ticket_numbers", "raw_text"])
    if not df.empty:
        df.to_csv(args.out, index=False)
        print(f"Saved {len(df)} scan(s) to {args.out}")
    else:
        print("No scans captured, nothing saved.")

    return df


if __name__ == "__main__":
    main()
c