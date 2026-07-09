# Lottery Ticket Verification System — Project Brief
**Version:** 1.0  
**Date:** 7 July 2026  
**Role producing this document:** Product Owner  
**Audience:** Mobile developer, backend developer, AI/ML developer, UI/UX designer, tester

---

## 1. Project Goal

Build a **7-day prototype** that allows a user to scan a physical lottery ticket barcode, capture the front and back of the ticket, use OCR and AI to compare the ticket with reference data, and check whether the ticket is **valid, frozen, registered, or already claimed**.

> This prototype demonstrates the verification process using pilot/mock data. It does **not** legally certify a real GLO ticket.

---

## 2. Minimum User Flow

```
Login
→ Scan barcode
→ Capture ticket front
→ Capture ticket back
→ Allow location
→ System reads ticket information
→ System compares ticket with database
→ AI checks visual authenticity
→ System checks claimed status
→ Show result
```

### Result States

| Result | Description |
|---|---|
| ✅ Verified – Not Claimed | Ticket is genuine and has not been redeemed |
| ⚠️ Verified – Already Claimed | Ticket is genuine but prize has been collected |
| 🔶 Suspicious – Manual Review | Something doesn't match; human review needed |
| ❌ Invalid Ticket | Barcode or data not found or does not match records |
| 🔁 Rescan Required | Image quality too low to process |

---

## 3. What Is In Scope (Pilot Only)

| In Scope | Out of Scope |
|---|---|
| Barcode scan and lookup | Blockchain integration |
| Front and back image capture | Real bank payout |
| OCR extraction and comparison | Real Paotang integration |
| Basic AI authenticity check | Full KYC |
| Claimed-status check | Legal ownership transfer |
| Location capture | Production cybersecurity |
| Admin manual review screen | UV / chemical ink verification |
| Mock ticket database (35 records) | Large-scale cloud infrastructure |
| 7 result states | Perfect counterfeit detection |

---

## 4. Ticket Database Structure

The database spreadsheet should use these fields:

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
| Front image filename | ticket-00001-front.jpg |
| Back image filename | ticket-00001-back.jpg |

### Record Distribution (35 total)

| Category | Count |
|---|---|
| Genuine / active | 20 |
| Already claimed | 5 |
| Invalid (no record / wrong date) | 5 |
| Altered number | 5 |
| Duplicate barcode | 5 |

---

## 5. Image Dataset

### Genuine Examples to Prepare
- Clear front image
- Clear back image
- Different lighting conditions
- Slightly folded ticket
- Different phone cameras
- Different backgrounds

### Fraud Examples to Prepare
- Number digitally changed
- Barcode copied from another ticket
- Screenshot of a ticket
- Photocopy
- Front and back from different tickets
- Old draw date changed
- Blurred or cropped image

Target: **40–100 labelled images** (sufficient for a demonstration; not production-grade).

### Folder Structure

```
dataset/
    genuine/
    altered-number/
    fake-barcode/
    screenshot/
    photocopy/
    wrong-front-back/
    already-claimed/
    poor-quality/
```

### Image Label Format

```
ticket_001_front.jpg    → genuine
ticket_002_front.jpg    → altered-number
ticket_003_front.jpg    → screenshot
```

---

## 6. Verification Rules

| Condition | Result |
|---|---|
| Barcode not found in database | Invalid |
| Barcode found and OCR matches | Continue to next check |
| OCR number does not match barcode | Suspicious |
| Draw date does not match | Invalid |
| Ticket already claimed | Verified – Already Claimed |
| Ticket frozen | Invalid or Manual Review |
| Image blurry / low quality | Rescan Required |
| AI detects image was edited | Manual Review |
| Same ticket scanned by another user | Ownership Conflict → Manual Review |
| All checks pass | Verified – Not Claimed |

---

## 7. What AI Should Check

### Check These
- Front-page layout and structure
- Back-page layout and structure
- Ticket shape and proportions
- Font and digit consistency
- Possible changed numbers
- Screenshot or photocopy detection
- Front and back consistency with each other
- Overall image quality

### Do Not Ask AI to Check
- Real paper composition
- UV security features
- Chemical ink properties
- Legal ticket ownership
- Signature identity

---

## 8. Screen Definitions

### Screen 1 — Login
**User sees:** App logo, email/phone field, password field, login button  
**Actions:** Enter credentials → tap Login

---

### Screen 2 — Home
**User sees:** Welcome message, large "Verify Ticket" button, recent scans list  
**Actions:** Tap Verify Ticket → go to Scan Barcode

---

### Screen 3 — Scan Barcode
**User sees:** Camera viewfinder with barcode guide overlay, instruction text  
**Instruction text:** "Point your camera at the barcode on the ticket."  
**Actions:** Scan barcode (auto-detect) | Enter manually | Cancel

---

### Screen 4 — Capture Front
**User sees:** Camera viewfinder with ticket-shape guide, instruction text  
**Instruction text:** "Place the lottery ticket on a flat surface. Make sure all four corners are visible."  
**Actions:** Capture | Retake | Continue

---

### Screen 5 — Capture Back
**User sees:** Camera viewfinder with ticket-shape guide  
**Instruction text:** "Flip the ticket over. Make sure all four corners are visible."  
**Actions:** Capture | Retake | Continue

---

### Screen 6 — Allow Location
**User sees:** System location permission dialog  
**Instruction text:** "We need your location to complete verification."  
**Actions:** Allow | Deny (shows warning that verification may be limited)

---

### Screen 7 — Processing
**User sees:** Loading animation, status steps ticking through  
**Steps shown:** Reading barcode → Checking database → Analysing images → Checking claim status  
**Actions:** None (auto-advances to result)

---

### Screen 8 — Result
**User sees:** Result status (large, colour-coded), ticket details, action buttons  
**Content shown:**
```
Verification result      [colour-coded status]
Ticket number:           123456
Draw date:               16 July 2026
Barcode:                 Matched
OCR:                     Matched
Visual authenticity:     91%
Claim status:            Not claimed
Location captured:       Yes
```
**Actions:** Save to My Tickets | Scan Another | Contact Support (if suspicious/invalid)

---

### Screen 9 — My Tickets
**User sees:** List of past scans with date, ticket number, and result status  
**Actions:** Tap any entry → go to Ticket Details

---

### Screen 10 — Ticket Details
**User sees:** Full verification record for a single scan  
**Content:** All result fields + front/back image thumbnails + timestamp + location  
**Actions:** Share | Report Issue

---

### Screen 11 — Admin Manual Review
**User sees:** Queue of flagged tickets, each with images, OCR data, and AI score  
**Actions:** Approve (mark genuine) | Reject (mark invalid) | Escalate

---

## 9. Developer Task List

### Mobile Developer
- Login screen
- Barcode scanning (camera)
- Front image capture
- Back image capture
- Location permission request
- Upload images and barcode to backend API
- Display result from API

### Backend Developer
- User authentication API
- Ticket database (using spreadsheet as seed data)
- Barcode lookup endpoint
- OCR text comparison logic
- Claim-status check
- Verification rules engine (see Section 6)
- Save scan records and results
- Admin review endpoints

### AI / ML Developer
- Image quality check (blur, cropping)
- Ticket crop and perspective correction
- OCR text extraction from image
- Template comparison (layout, font, proportions)
- Basic altered-image detection
- Authenticity confidence score (0–100%)

### UI / UX Designer
- User flow diagram
- Mobile screen designs (all 11 screens above)
- Result state designs (all 5 states)
- Error message copy
- Admin review screen

### Tester
Test cases to cover:
- Genuine ticket → expect Verified – Not Claimed
- Fake barcode → expect Invalid
- Altered number → expect Suspicious
- Already claimed ticket → expect Verified – Already Claimed
- Duplicate ticket (two accounts) → expect Ownership Conflict
- Screenshot of a ticket → expect Suspicious
- Blurry image → expect Rescan Required
- Wrong front and back → expect Suspicious

---

## 10. 7-Day Task Plan

### Day 1 — Define Scope *(today)*
- [x] Confirm user flow
- [x] Confirm result statuses
- [x] Confirm project goal
- [x] Create screen list
- [x] Decide in/out of scope

**Deliverable:** This document

---

### Day 2 — Prepare Ticket Database
- Create ticket spreadsheet (35 records)
- Add all field values
- Mark claimed, frozen, and invalid tickets
- Collect or create front and back images

**Deliverable:** `ticket-database.xlsx` + image folder

---

### Day 3 — Prepare Fraud Dataset
- Create altered-number examples
- Create screenshot examples
- Create duplicate/mismatched examples
- Label every image with category

**Deliverable:** Labelled `dataset/` folder

---

### Day 4 — Review Application Flow
- Test barcode scanning end-to-end
- Verify correct ticket appears after scan
- Test front and back capture
- Review screen wording and instructions
- Report any confusing or broken steps

**Deliverable:** Feedback list for developer

---

### Day 5 — Review AI Results

Use this table format:

| Test Case | Expected | Actual | Pass? |
|---|---|---|---|
| Genuine ticket | Verified | | |
| Changed number | Suspicious | | |
| Screenshot | Suspicious | | |
| Poor quality | Rescan | | |

**Deliverable:** Completed test table

---

### Day 6 — Test Fraud and Claimed Status
- Scan same ticket twice (same account)
- Scan same ticket from two different accounts
- Scan an already-claimed ticket
- Scan an invalid barcode
- Scan with location disabled

**Deliverable:** Test result report

---

### Day 7 — Prepare Demo

**Demo tickets to select:**
- 1 genuine ticket
- 1 altered ticket
- 1 already-claimed ticket

**Demo sequence:**
```
1. Scan genuine ticket       → Show Verified – Not Claimed
2. Scan altered ticket       → Show Suspicious – Manual Review
3. Scan claimed ticket       → Show Verified – Already Claimed
```

**Deliverable:** Demo script + screenshots + known limitations list

---

## 11. Daily Check-in Questions (Ask the Developer Every Day)

1. What is working now?
2. What is not working?
3. What data do you need from me?
4. What will be ready today?
5. What must be removed to finish within seven days?

---

## 12. Success Criteria for the Prototype

The prototype is considered successful if a live demo can show this single flow from end to end:

> **Scan barcode → capture front and back → OCR and AI checks → compare database → check claimed status → show result**

Accuracy and scale are not required. A working demonstration of the logic is the goal.

---

*Document prepared by: Product Owner*  
*Project: Lottery Ticket Verification Prototype*  
*Duration: 7 days*
