# ML Training And Phone Deployment

## Dataset

Build the current training index:

```bash
node scripts/build-training-index.js
```

Outputs:

- `data/training-dataset/index.json`
- `data/training-dataset/labels.csv`

Current intended dataset shape:

- Genuine class: `data/ticket-images/*.jpg` from the 21 real tickets.
- Fake class: `data/manual-dimension-test/*` from the 10 visual fakeness dimensions.

The first fake folder currently uses:

```text
data/manual-dimension-test/01_main_number_spacing/photo/01.png
...
data/manual-dimension-test/01_main_number_spacing/photo/10.png
```

After adding more photos, run the index script again. The `exists` column marks which planned samples are already on disk.

## Image Verification Hook

The app now calls:

```http
POST /api/verify-image
```

The response includes:

- `ai_score`
- `suspicious`
- `source`
- `checklist`

The checklist uses the 10 first-pass dimensions:

1. `main_number_spacing`
2. `main_number_alignment`
3. `main_number_font`
4. `main_number_scale`
5. `logo_position`
6. `logo_scale`
7. `date_alignment`
8. `qr_position`
9. `barcode_position`
10. `patch_boundary`

Without a real model configured, the endpoint returns a structured placeholder checklist plus the current client image heuristic. This gives the CNN or GPT-4o/Claude vision integration a stable API shape to replace later.

## PWA / Phone Use

The frontend now includes:

- `frontend/manifest.webmanifest`
- `frontend/sw.js`
- `frontend/icons/icon.svg`

To use camera capture from a phone, deploy the backend over HTTPS. Camera APIs work on:

- `https://...`
- `http://localhost`

They do not work from ordinary insecure LAN HTTP URLs on phones.

Typical deployment shape:

```bash
cd backend
npm install
npm run seed
npm start
```

Then put an HTTPS reverse proxy or hosting platform in front of port `8080`.
