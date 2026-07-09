---
name: glo-ticket-verification
description: >
  Build or extend a lottery/document ticket verification app that scans a barcode,
  captures front/back photos, runs OCR + a rules engine against a database, and drives a
  scan → verify → prize → claim flow. Use when the user references GLO, สลากกินแบ่ง,
  lottery ticket scanning/verification, barcode + OCR authenticity checking, or wants to
  reproduce this scan-verify-claim workflow for another ticket/coupon/document type.
---

# GLO Ticket Verification — Workflow Skill

This skill reproduces the "scan → verify → prize → claim" ticket-verification app and its
backend. Follow these steps.

## 1. Gather the design spec
- If the user supplies app screenshots, save them into `design-reference/` and read every
  one before coding. Match logo, colors, fonts (Noto Sans Thai), proportions, icon
  positions exactly. Do not approximate the layout.
- Confirm the current draw date, prize table, and any Thai-language copy.

## 2. Frontend (`frontend/index.html` + `app.js`)
Build a single-page app, no build step, with these screens:
`home · my-tickets · scan · capture-front · capture-back · processing · verify · prize · claim · success`.
- **Scanning is real:** use the browser `BarcodeDetector` API on a `getUserMedia` video stream.
- **OCR is real:** Tesseract.js (digit whitelist) reads the printed 6-digit number from the
  captured front photo.
- **No manual barcode entry** — camera only.
- Draw the GLO logo, royal seal, and hero art as inline SVG (see `app.js` `GLO_LOGO`).
- All API calls go through `apiLookup`/`apiPost` with an embedded seed fallback so the file
  also runs standalone.

## 3. Verification rules engine
Combine, in this order: (1) barcode exists in DB → else `invalid`;
(2) OCR number == registered number → else `suspicious`; (3) draw date not expired → else
`expired`; (4) already claimed → `claimed`; else `ok`. Run the same rules on the server as
the source of truth and log every scan.

## 4. Backend (`backend/`)
- Node.js ≥ 22.5 + Express + built-in `node:sqlite` (no native build).
- Tables: `users`, `tickets`, `scan_actions`, `claim_rewards` (see `db/schema.sql`).
- Endpoints: `GET /api/tickets/:barcode`, `POST /api/verify`, `POST /api/scans`,
  `POST /api/claims` (guard duplicate claims → 409), `GET /api/admin/review`, `GET /api/health`.
- Serve the frontend as static files so the camera works over `http://localhost`.
- Seed 5 tickets covering: genuine winner, genuine no-prize, already-claimed, expired,
  number-mismatch/suspicious.

## 5. Camera gotcha
`file://` blocks `getUserMedia`. Always serve over `http://localhost` (the backend does
this) or provide a small static server. Document this for the user.

## 6. Deliverables & organization
Produce an organized repo: `frontend/ backend/ design-reference/ docs/ skill/`,
plus `README.md`, `ROADMAP.md`, `.gitignore` (ignore `node_modules/` and `*.db`). Verify the
backend actually runs (`npm run seed && npm start`) and curl the endpoints before declaring done.

## 7. Roadmap to production
Remind the user of the phases beyond the prototype: real auth (hashed PIN), image storage +
AI vision authenticity check, admin review panel, PostgreSQL/Supabase migration, and — only
with GLO/bank agreements — real payout. Never implement real fund transfer without those
agreements; record a payout intent instead.
