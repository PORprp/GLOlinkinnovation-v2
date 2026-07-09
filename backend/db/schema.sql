-- ============================================================
-- GLO E-Lottery — Database schema (SQLite dialect)
-- Portable to PostgreSQL/Supabase with minor type tweaks.
-- ============================================================

-- Registered users of the app
CREATE TABLE IF NOT EXISTS users (
  id            TEXT PRIMARY KEY,          -- phone number or UUID
  name          TEXT NOT NULL,
  bank_name     TEXT,
  bank_account  TEXT,                      -- masked, e.g. xxx-x-x4291-x
  pin_hash      TEXT,                      -- hashed 6-digit PIN (never plain)
  created_at    TEXT DEFAULT (datetime('now'))
);

-- Master ticket table — the source of truth for verification.
-- The barcode is the primary lookup key read by the scanner.
CREATE TABLE IF NOT EXISTS tickets (
  barcode       TEXT PRIMARY KEY,          -- GLO Data Matrix payload, e.g. 69-26-13-039184-4358
  alt_barcode   TEXT,                      -- the 1D ITF barcode on the same ticket
  number        TEXT NOT NULL,             -- printed 6-digit number, e.g. 039184
  draw_date     TEXT NOT NULL,             -- Thai format: 1 ก.ค. 2569
  draw_en       TEXT,                      -- English: 1 JULY 2026
  series        TEXT,                      -- งวดที่
  "set"         TEXT,                      -- ชุดที่
  price         INTEGER DEFAULT 80,
  status        TEXT DEFAULT 'active',     -- active | expired | suspended | invalid | suspicious
  is_claimed    INTEGER DEFAULT 0,         -- 0/1
  prize_type    TEXT,                      -- รางวัลที่ 1 ... or NULL
  prize_amount  INTEGER DEFAULT 0,
  front_img_url TEXT,
  back_img_url  TEXT,
  owner_id      TEXT,                      -- FK users.id once claimed/registered
  created_at    TEXT DEFAULT (datetime('now'))
);

-- Every scan event (verify or collect). Audit trail + fraud signal.
CREATE TABLE IF NOT EXISTS scan_actions (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  barcode       TEXT,
  user_id       TEXT,
  action_type   TEXT,                      -- verify | collect
  ocr_result    TEXT,                      -- number Tesseract/AI read from photo
  ocr_match     INTEGER,                   -- 0/1
  date_match    INTEGER,                   -- 0/1
  ai_score      REAL,                      -- 0.0 - 1.0 authenticity confidence
  result_status TEXT,                      -- ok | suspicious | claimed | invalid | expired
  lat           REAL,
  lng           REAL,
  front_img_url TEXT,
  back_img_url  TEXT,
  scanned_at    TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (barcode) REFERENCES tickets(barcode)
);

-- Prize claim / payout records.
CREATE TABLE IF NOT EXISTS claim_rewards (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  barcode       TEXT,
  user_id       TEXT,
  bank_name     TEXT,
  bank_account  TEXT,
  amount        INTEGER,
  ref_code      TEXT UNIQUE,
  status        TEXT DEFAULT 'success',    -- success | pending | failed | review
  claimed_at    TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (barcode) REFERENCES tickets(barcode)
);

CREATE INDEX IF NOT EXISTS idx_scans_barcode ON scan_actions(barcode);
CREATE INDEX IF NOT EXISTS idx_claims_barcode ON claim_rewards(barcode);
