# GLO-Link Project Concept

## 1. Project Overview
GLO-Link is a mobile-first “Scan-to-Verify” platform designed to connect physical lottery tickets with secure digital ownership and instant claim processing. The solution helps customers protect their tickets before the draw, verify legitimacy after the draw, and receive payouts quickly through the existing Pao Tang ecosystem.

## 2. Problem Statement
Physical lottery tickets are still widely used, but the current claim process creates several major issues:
- High manual workload for staff at GLO counters
- Customer anxiety about losing, damaging, or misplacing tickets
- Fraud risks from duplicate claims and disputed ownership
- Accessibility barriers for winners who cannot travel to claim in person

## 3. Core Value Proposition
GLO-Link turns a paper-based lottery experience into a trusted digital journey by enabling:
- Verified ticket ownership before the draw
- Faster and safer prize verification after the draw
- Instant payout options to bank accounts or digital wallets
- Reduced operational burden for GLO staff and agents

## 4. Target Users
- Physical lottery buyers who want assurance that their ticket is safely registered
- Winners who need a simple and convenient claim process
- GLO operational teams who want to reduce manual verification workload
- Partners in the digital payments and loyalty ecosystem

## 5. Key Features
### 5.1 Scan and Register Ticket
Users can scan their physical ticket barcode and upload ticket information through the app before the draw.

### 5.2 Ownership Verification
The platform links the ticket to a KYC-verified user account, creating a stronger record of ownership and reducing fraudulent claims.

### 5.3 AI-Based Authenticity Check
The system evaluates ticket characteristics such as:
- barcode consistency
- printed text and number integrity
- signature and visual document validation
- potential image tampering or screenshot reuse

### 5.4 Claim Alert and Notification
Users receive automated alerts on draw day and can proceed to claim directly through the app.

### 5.5 Instant Payout Integration
Winners can receive payouts through supported payment methods such as Krungthai bank transfers or G-Wallet.

## 6. Proposed Workflow
1. User logs in and grants camera access.
2. User scans the lottery ticket barcode.
3. The app performs OCR on the front of the ticket.
4. The app captures back-page and signature details.
5. The verification engine checks the ticket against trusted data.
6. The app returns one of four results:
   - Verified – Not Claimed
   - Verified – Already Claimed
   - Suspicious – Manual Review
   - Invalid

## 7. Technical Direction
The platform architecture combines mobile access, OCR, AI/ML verification, and secure backend services.

### Core Components
- Mobile application for users
- OCR engine for front and back ticket scanning
- AI/ML verification service for authenticity and fraud checks
- Risk engine for anomaly detection and location-based analysis
- Secure backend integration with official lottery systems and payment gateways

### Security Considerations
- Secure HTTPS/TLS communication
- KYC-based identity linkage
- Fraud detection for abnormal access patterns
- Protection of sensitive customer and transaction data

## 8. Business Impact
GLO-Link is expected to deliver strong operational and strategic value:
- Reduce walk-in claims and save staff time
- Improve customer confidence and convenience
- Lower fraud and claim disputes
- Build a new digital customer data layer for future products and services

## 9. Strategic Value
Beyond claims processing, the platform creates a foundation for long-term growth:
- Better understanding of offline purchase behavior
- More precise customer targeting and service design
- Expansion into future digital financial and loyalty offerings
- Stronger inclusive access for users in remote or underserved areas

## 10. Roadmap
### Phase 1: Fix the Claim Process
- Scan-to-verify ticket flow
- Draw-day notifications
- Instant bank transfer payout support

### Phase 2: Build a Unified Data Layer
- Link physical ticket purchases to verified digital customer profiles
- Improve analytics and fraud monitoring

### Phase 3: Expand into New Digital Products
- Personalized offers and loyalty services
- New ecosystem features based on customer behavior and verified identity

## 11. Executive Summary
GLO-Link reimagines physical lottery participation by combining the trust of paper tickets with the convenience of digital ownership verification and instant payout. It solves a real operational bottleneck while creating a scalable foundation for future digital growth.
