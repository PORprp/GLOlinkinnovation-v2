/* ============================================================
   GLO E-Lottery — Verification API (prototype)
   Node.js (>=22.5) + Express + built-in node:sqlite
   Start:  npm install && npm run seed && npm start
   ============================================================ */
const path = require('node:path');
const express = require('express');
const cors = require('cors');
const { db } = require('./db/db');

const app = express();
app.use(cors());
app.use(express.json({ limit: '12mb' }));                          // base64 images allowed
app.use(express.static(path.join(__dirname, '..', 'frontend')));   // serve the app itself

const CURRENT_DRAW = '1 ก.ค. 2569';

function shape(row) {
  if (!row) return null;
  return {
    barcode: row.barcode, alt_barcode: row.alt_barcode, number: row.number,
    draw_date: row.draw_date, draw_en: row.draw_en,
    series: row.series, set: row.set, price: row.price,
    status: row.status, is_claimed: !!row.is_claimed,
    prize_type: row.prize_type, prize_amount: row.prize_amount
  };
}

// Match a scanned code against the Data Matrix payload, the 1D ITF barcode,
// or the printed 6-digit number (which the Data Matrix also embeds). This makes
// verification robust whichever code the scanner happens to read.
function getTicket(code) {
  if (code == null) return null;
  const c = String(code).trim();
  let row = db.prepare('SELECT * FROM tickets WHERE barcode = ? OR alt_barcode = ?').get(c, c);
  if (row) return row;
  const digits = c.replace(/\D/g, '');
  const six = (c.match(/(?:^|\D)(\d{6})(?:\D|$)/) || [])[1] || (digits.length === 6 ? digits : null);
  if (six) row = db.prepare('SELECT * FROM tickets WHERE number = ? ORDER BY barcode LIMIT 1').get(six);
  return row || null;
}

// GLO prizes are claimable for 2 years after the draw date.
// Returns the last day a prize can be collected, parsed from draw_en ("1 JULY 2026").
const MONTHS = {JAN:0,FEB:1,MAR:2,APR:3,MAY:4,JUN:5,JUL:6,AUG:7,SEP:8,OCT:9,NOV:10,DEC:11};
function claimDeadline(row) {
  const m = (row.draw_en || '').match(/(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})/);
  if (!m) return null;
  const mo = MONTHS[m[2].slice(0,3).toUpperCase()];
  if (mo == null) return null;
  const d = new Date(Number(m[3]), mo, Number(m[1]));
  d.setFullYear(d.getFullYear() + 2);     // 2-year claim window
  return d;
}
function isExpired(row) {
  if (row.status === 'expired') return true;      // manual override
  const dl = claimDeadline(row);
  return dl ? (new Date() > dl) : false;          // past the 2-year window?
}

/* ---------- lookup ---------- */
app.get('/api/tickets/:barcode', (req, res) => {
  const row = getTicket(req.params.barcode);
  if (!row) return res.status(404).json({ error: 'not_found' });
  res.json(shape(row));
});

/* ---------- full rules engine (server-side authority) ---------- */
app.post('/api/verify', (req, res) => {
  // ocr_readable: false = the front photo could not be read (STRICT — do not pass).
  // ai_score: 0..1 authenticity from the image check (< 0.55 = likely screenshot/copy).
  const { barcode, ocr_result, ocr_readable = true, ai_score = 0.9, lat = null, lng = null } = req.body || {};
  const row = getTicket(barcode);
  let result_status = 'ok'; const reasons = [];
  if (!row) { result_status = 'invalid'; reasons.push('barcode_not_found'); }
  else {
    const ocrMatch = ocr_result ? ocr_result === row.number : true;
    const dateOK   = !isExpired(row);               // claimable within 2 years of the draw
    if (row.is_claimed)                 { result_status = 'claimed';    reasons.push('already_claimed'); }
    else if (ocr_readable === false)    { result_status = 'review';     reasons.push('photo_unreadable'); }        // (A) strict OCR
    else if (!ocrMatch)                 { result_status = 'suspicious'; reasons.push('ocr_mismatch'); }
    else if (ai_score < 0.55)           { result_status = 'suspicious'; reasons.push('image_authenticity'); }      // (B) visual check
    else if (!dateOK)                   { result_status = 'expired';    reasons.push('claim_window_closed'); }
    else if (row.status === 'suspicious'){ result_status = 'suspicious'; reasons.push('flagged'); }
  }
  db.prepare(`INSERT INTO scan_actions
    (barcode,action_type,ocr_result,ocr_match,date_match,ai_score,result_status,lat,lng)
    VALUES (?,?,?,?,?,?,?,?,?)`).run(
      barcode || null, 'verify', ocr_result || null,
      row && ocr_result ? (ocr_result === row.number ? 1 : 0) : null,
      row ? (row.status !== 'expired' ? 1 : 0) : null,
      ai_score, result_status, lat, lng);
  res.json({ result_status, reasons, ticket: shape(row) });
});

/* ---------- (B) image authenticity — production hook ----------
   POST { front_b64, back_b64 } → { ai_score, is_screenshot, is_photocopy, suspicious }
   If ANTHROPIC_API_KEY (or OPENAI) is set, wire a vision model here and return its JSON
   (prompt in ROADMAP Phase 4). Until then it echoes the client heuristic so the pipeline
   is fully connected end-to-end. */
app.post('/api/verify-image', async (req, res) => {
  const { front_b64, client_score = null } = req.body || {};
  if (!front_b64) return res.status(400).json({ error: 'front_b64 required' });

  if (process.env.ANTHROPIC_API_KEY) {
    // TODO Phase 4: call Claude vision with the front/back images and return its JSON.
    // Left unimplemented on purpose so no key is required to run the prototype.
  }
  // fallback: trust the client-side heuristic score (0..100 → 0..1)
  const score = client_score != null ? Number(client_score) / 100 : 0.9;
  res.json({
    ai_score: score,
    is_screenshot: score < 0.55,
    is_photocopy: false,
    suspicious: score < 0.55,
    source: process.env.ANTHROPIC_API_KEY ? 'model-configured' : 'client-heuristic'
  });
});

/* ---------- record a scan/save ---------- */
app.post('/api/scans', (req, res) => {
  const { barcode, user_id = null, action_type = 'verify', ocr_result = null,
          result_status = 'ok', lat = null, lng = null } = req.body || {};
  const info = db.prepare(`INSERT INTO scan_actions
    (barcode,user_id,action_type,ocr_result,result_status,lat,lng)
    VALUES (?,?,?,?,?,?,?)`).run(barcode, user_id, action_type, ocr_result, result_status, lat, lng);
  res.json({ ok: true, id: info.lastInsertRowid });
});

/* ---------- claim a prize ---------- */
app.post('/api/claims', (req, res) => {
  const { barcode, user_id = '0812345678', bank = 'กรุงไทย',
          bank_account = 'xxx-x-x4291-x', amount = 0, ref } = req.body || {};
  const row = getTicket(barcode);
  if (!row) return res.status(404).json({ error: 'not_found' });
  if (row.is_claimed) return res.status(409).json({ error: 'already_claimed' });
  const ref_code = ref || ('PTG-GLO-' + Date.now());
  db.prepare('UPDATE tickets SET is_claimed = 1, owner_id = ? WHERE barcode = ?').run(user_id, barcode);
  db.prepare(`INSERT INTO claim_rewards (barcode,user_id,bank_name,bank_account,amount,ref_code)
    VALUES (?,?,?,?,?,?)`).run(barcode, user_id, bank, bank_account, amount, ref_code);
  res.json({ ok: true, ref_code, amount, status: 'success' });
});

/* ---------- history / admin ---------- */
app.get('/api/scans', (req, res) =>
  res.json(db.prepare('SELECT * FROM scan_actions ORDER BY scanned_at DESC LIMIT 50').all()));
app.get('/api/admin/review', (req, res) =>
  res.json(db.prepare(`SELECT * FROM scan_actions WHERE result_status IN ('suspicious','review') ORDER BY scanned_at DESC`).all()));
app.get('/api/health', (req, res) => res.json({ ok: true, draw: CURRENT_DRAW }));

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => console.log(`🎟️  GLO API + app running → http://localhost:${PORT}`));
