# ML training helper

This folder contains a small example training script to train a genuine-vs-fake
classifier for lottery ticket photos.

Quick start

1. Create a Python environment and install packages:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r ml/requirements.txt
```

2. Ensure `data/training-dataset/labels.csv` and the referenced images exist.
   Generate the index with:

```bash
node scripts/build-training-index.js
```

3. Run training:

```bash
python ml/train.py --epochs 10 --batch-size 8 --model-dir models/lotto_cnn
```

Fine-tune after initial training (unfreeze base and continue training):

```bash
python ml/train.py --epochs 5 --fine-tune-epochs 5 --batch-size 8 --model-dir models/lotto_cnn
```

Notes

- This is a minimal, instructional pipeline. For production you should add
  data augmentation, class balancing, mixed-precision, and a proper eval.
- The script saves a Keras SavedModel to `--model-dir`.
