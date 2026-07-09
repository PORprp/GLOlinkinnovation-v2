# Roadmap — From Prototype to Production

You chose **"full working app with backend."** This is the phased plan to get there. Each phase is independently shippable and testable. Phases 1–2 are already built in this repo; 3 onward is the forward plan.

## Phase 1 — Pixel-perfect frontend ✅ (done)
- All 8 screens rebuilt to match the official GLO design (logo, seal, colors, proportions, icon positions).
- Real barcode scanning via the browser `BarcodeDetector` API.
- Real front/back photo capture from the camera.
- Real OCR of the printed number via Tesseract.js.
- Client-side rules engine with graceful offline fallback.

## Phase 2 — Real backend + database ✅ (done)
- Express REST API with a SQL database (`node:sqlite`).
- Tables: `users`, `tickets`, `scan_actions`, `claim_rewards`.
- Endpoints for lookup, verify, scan logging, claim, and an admin review queue.
- Server-side rules engine as the source of truth; every scan is audited.
- Duplicate-claim protection (409).

## Phase 3 — Real accounts & authentication
**Goal:** each ticket is owned by a real, logged-in user.
- Phone/OTP or ThaID login; issue a session/JWT.
- Hash the 6-digit PIN (bcrypt/argon2) — never store plaintext.
- Bind a bank account to the user record (masked display only).
- Tie `scan_actions` and `claim_rewards` to `user_id`.
- **Deliverable:** login screen + protected endpoints.
- **Est:** 3–5 days.

## Phase 4 — Image authenticity check  🟡 (partially built)
**Goal:** the front/back photos are analysed, not just OCR'd.
- ✅ **Strict OCR** — an unreadable front photo now returns `review` instead of silently
  passing (frontend `runOCR`, backend `/api/verify` `ocr_readable`).
- ✅ **Client-side heuristic** — real pixel analysis (`analyzeImage` in `app.js`) produces an
  authenticity score from white-background ratio, saturation/high-frequency (screen moiré),
  lighting uniformity and blur; a low score flags `suspicious (image_authenticity)`.
- ✅ **`POST /api/verify-image`** endpoint is wired end-to-end (returns the heuristic today).
- ⬜ **Production model** — swap the heuristic for a Claude/GPT-4o vision call returning
  `{ is_ticket, is_screenshot, is_photocopy, number_value, suspicious, confidence }`; set
  `ANTHROPIC_API_KEY` and implement the TODO in `/api/verify-image`.
- ⬜ **Image storage** — upload captured photos to object storage (S3 / Supabase); keep URLs
  on `scan_actions` as claim evidence.
- **Est. remaining:** 3–5 days.

## Phase 5 — Admin / manual-review panel
**Goal:** humans adjudicate flagged tickets.
- Web panel listing the `suspicious`/`review` queue with images, OCR, and AI score.
- Approve / reject / escalate actions that update ticket status.
- Basic role-based access for reviewers.
- **Deliverable:** `/admin` panel wired to `/api/admin/*`.
- **Est:** 3–4 days.

## Phase 6 — Production data & hosting
**Goal:** real scale, not a demo file.
- Migrate `node:sqlite` → PostgreSQL/Supabase (schema is already portable).
- Seed with real GLO ticket + draw data via secured import.
- Deploy backend (Render/Fly/Cloud Run) behind HTTPS; host the frontend as a PWA.
- Rate limiting, input validation, structured logging, backups.
- **Est:** 1–2 weeks.

## Phase 7 — Real payout & compliance ⚠️ (requires external agreements)
**Goal:** actually move prize money. Out of scope for engineering alone.
- Formal GLO data/API agreement for authoritative ticket verification.
- Bank / PromptPay payout integration; KYC/AML; tax withholding.
- Security audit, pen-test, and legal sign-off.
- **Note:** this phase depends on institutional partnerships and cannot be completed by code changes alone. Until then, the claim flow records a payout intent rather than transferring funds.

---

### Suggested next step
Start **Phase 3 (auth)** — it's the smallest change that turns the demo into a real multi-user app, and everything else (ownership, claims, admin) builds on having real accounts.
