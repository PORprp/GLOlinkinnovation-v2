# Manual Lotto Fakeness Dimension Test

Put your own photos into the 10 dimension folders below. Use 10 images per folder:

```text
01.jpg
02.jpg
03.jpg
04.jpg
05.jpg
06.jpg
07.jpg
08.jpg
09.jpg
10.jpg
```

Each folder should contain photos where the main visible fake signal is that one dimension only. This keeps the test clean and makes it easier to see what the model actually learns.

## The 10 Dimensions To Check First

1. `main_number_spacing` - wrong gap between lotto digits.
2. `main_number_alignment` - digit baseline, height, rotation, or centering is wrong.
3. `main_number_font` - one or more digits use a different font shape.
4. `main_number_scale` - one or more digits are too large, small, wide, tall, or stretched.
5. `logo_position` - logo or agency header is shifted from the normal location.
6. `logo_scale` - logo/header mark is too large, too small, or stretched.
7. `date_alignment` - Thai/English date lines, baseline, or spacing are misaligned.
8. `qr_position` - QR code is shifted or too close to other layout elements.
9. `barcode_position` - barcode or barcode number is shifted/misaligned.
10. `patch_boundary` - visible edit patch, tone change, halo, or texture discontinuity.

## Folder Rules

- Use real input photos directly, not generated mockups.
- Keep one fake dimension per photo when possible.
- Use the same naming convention in every folder: `01.jpg` to `10.jpg`.
- If a photo has multiple fake signals, put the strongest one in `dimension` and describe the others in `notes`.
- Do not add watermarks over the area the model should learn from.

## Labels

Edit `labels.csv` after placing the photos if a filename, severity, or note changes.

Recommended severity values:

- `subtle`
- `medium`
- `obvious`

