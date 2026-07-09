# Lottery Ticket Verification System — Project Brief
**Version:** 1.0
**Date:** 7 July 2026
**Role:** Product Owner

---

## 1. Project Goal

Build a 7-day prototype that allows a user to scan a physical lottery ticket barcode, capture the front and back of the ticket, use OCR and AI to compare the ticket with reference data, and check whether the ticket is valid, frozen, registered, or already claimed.

This prototype demonstrates the verification process using pilot/mock data. It does NOT legally certify a real GLO ticket.

---

## 2. Minimum User Flow

Login -> Scan barcode -> Capture front -> Capture back -> Allow location -> Read ticket -> Compare database -> AI visual check -> Check claim status -> Show result

### Result States
- Verified - Not Claimed
- Verified - Already Claimed
- Suspicious - Manual Review
- Invalid Ticket
- Rescan Required

---

## 3. Scope

### In Scope
- Barcode scan and lookup
- Front and back image capture
- OCR extraction and comparison
- Basic AI authenticity check
- Claimed-status check
- Location capture
- Admin manual review screen
- Mock ticket database (35 records)

### Out of Scope
- Blockchain, real bank payout, Paotang integration, full KYC, legal ownership transfer, production cybersecurity, UV/chemical ink checks

---

## 4. Ticket Database Structure

| Field | Example |
|---|---|
| Ticket ID | TKT-00001 |
| Barcode value | 0123456789012 |
| Six-digit number | 123456 |
| Draw date | 16 July 2026 |
| Series / Set | AB-123 |
| Status | Active |
| Frozen | No |
| Registered | No |
| Claimed | No |
| Front image | ticket-00001-front.jpg |
| Back image | ticket-00001-back.jpg |

### Record Distribution (35 total)
| Category | Count |
|---|---|
| Genuine / active | 20 |
| Already claimed | 5 |
| Invalid | 5 |
| Altered number | 5 |
| Duplicate barcode | 5 |

---

## 5. Verification Rules

| Condition | Result |
|---|---|
| Barcode not found | Invalid |
| Barcode found + OCR matches | Continue |
| OCR does not match | Suspicious |
| Draw date mismatch | Invalid |
| Already claimed | Verified - Already Claimed |
| Frozen | Invalid or Manual Review |
| Blurry image | Rescan Required |
| AI detects edit | Manual Review |
| Duplicate scan (another user) | Ownership Conflict |
| All pass | Verified - Not Claimed |

---

## 6. What AI Should Check
- Front and back layout and structure
- Ticket shape and proportions
- Font and digit consistency
- Possible changed numbers
- Screenshot or photocopy detection
- Front/back consistency
- Image quality

NOT: paper composition, UV features, chemical ink, legal ownership, signature identity

---

## 7. Screen Definitions

1. Login - credentials, tap Login
2. Home - Verify Ticket button, recent scans
3. Scan Barcode - camera viewfinder, auto-detect barcode
4. Capture Front - flat surface, all corners visible
5. Capture Back - flip ticket, all corners visible
6. Allow Location - system permission dialog
7. Processing - Reading barcode, Checking DB, Analysing images, Checking claim status
8. Result - status, ticket number, draw date, barcode, OCR, AI score, claim status, location
9. My Tickets - list of past scans
10. Ticket Details - full record, thumbnails, timestamp
11. Admin Manual Review - flagged queue, Approve / Reject / Escalate

---

## 8. Developer Tasks

### Mobile: Login, scan barcode, capture front/back, location, upload to API, show result
### Backend: Auth, ticket DB, barcode lookup, OCR comparison, claim check, rules engine, scan records, admin endpoints
### AI/ML: Quality check, perspective correction, OCR extraction, template comparison, altered-image detection, authenticity score
### Designer: Flow, 11 screens, 5 result states, error copy, admin screen
### Tester: Genuine, fake barcode, altered, claimed, duplicate, screenshot, blurry, wrong front/back

---

## 9. 7-Day Plan

Day 1 - Scope (DONE): user flow, results, goal, screens, in/out scope
Day 2 - Ticket Database: 35 records, images
Day 3 - Fraud Dataset: altered/screenshot/duplicate examples, labels
Day 4 - App Flow Review: scan test, screen wording, feedback
Day 5 - AI Results Review: test table with Expected vs Actual
Day 6 - Fraud + Claim Test: duplicate scans, two accounts, claimed, invalid, no location
Day 7 - Demo: genuine + altered + claimed tickets, demo script, limitations

---

## 10. Daily Check-in Questions

1. What is working now?
2. What is not working?
3. What data do you need from me?
4. What will be ready today?
5. What must be removed to finish within seven days?

---

## 11. Success Criteria

Scan barcode -> capture front and back -> OCR and AI checks -> compare database -> check claimed status -> show result

A working demonstration of the logic is the goal.

---

Document: Product Owner | Lottery Ticket Verification Prototype | 7 days
