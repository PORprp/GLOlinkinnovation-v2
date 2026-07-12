#!/usr/bin/env python3
"""Train a small CNN to distinguish genuine vs fake ticket photos.

Usage:
  python ml/train.py --epochs 10 --batch-size 16 --model-dir models/lotto_cnn

The script reads `data/training-dataset/labels.csv` and trains a transfer-learning
MobileNetV2 classifier. It saves the final Keras SavedModel to `--model-dir`.
"""
import argparse
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf


def make_dataset(filepaths, labels, img_size=(224, 224), batch_size=32, shuffle=True, augment=None):
    path_ds = tf.data.Dataset.from_tensor_slices(filepaths)
    label_ds = tf.data.Dataset.from_tensor_slices(labels.astype('float32'))
    ds = tf.data.Dataset.zip((path_ds, label_ds))

    def _load(path, label):
        image = tf.io.read_file(path)
        image = tf.image.decode_image(image, channels=3, expand_animations=False)
        image.set_shape([None, None, 3])
        image = tf.image.resize(image, img_size)
        image = tf.cast(image, tf.float32)
        image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
        return image, label

    ds = ds.map(_load, num_parallel_calls=tf.data.AUTOTUNE)
    if shuffle:
        ds = ds.shuffle(1024)
    if augment is not None:
        ds = ds.map(lambda x, y: (augment(x, training=True), y), num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)
    return ds


def build_model(img_size=(224, 224, 3)):
    base = tf.keras.applications.MobileNetV2(include_top=False, weights='imagenet', input_shape=img_size, pooling='avg')
    base.trainable = False
    inputs = tf.keras.Input(shape=img_size)
    x = base(inputs, training=False)
    x = tf.keras.layers.Dropout(0.3)(x)
    outputs = tf.keras.layers.Dense(1, activation='sigmoid')(x)
    model = tf.keras.Model(inputs, outputs)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-4), loss='binary_crossentropy', metrics=['accuracy', tf.keras.metrics.AUC(name='auc')])
    return model


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument('--labels', default='data/training-dataset/labels.csv')
    p.add_argument('--root', default='.')
    p.add_argument('--epochs', type=int, default=5)
    p.add_argument('--batch-size', type=int, default=16)
    p.add_argument('--model-dir', default='models/lotto_cnn')
    p.add_argument('--fine-tune-epochs', type=int, default=0, help='Additional epochs to unfreeze base model and fine-tune')
    p.add_argument('--img-size', type=int, default=224)
    args = p.parse_args(argv)

    labels_csv = Path(args.labels)
    if not labels_csv.exists():
        print(f"Labels file not found: {labels_csv}")
        sys.exit(2)

    df = pd.read_csv(labels_csv)
    # interpret exists column if present
    if 'exists' in df.columns:
        df = df[df['exists'].astype(str).str.lower().isin(['true', '1', 't', 'yes'])]

    root = Path(args.root).resolve()
    paths = [str((root / rp).resolve()) for rp in df['relative_path'].tolist()]
    labels = df['class_label'].apply(lambda s: 1 if str(s).lower() == 'fake' else 0).to_numpy()

    # filter out missing files
    filtered = [(p, l) for p, l in zip(paths, labels) if Path(p).exists()]
    if not filtered:
        print('No image files found on disk. Run `node scripts/build-training-index.js` and add images.')
        sys.exit(2)
    paths, labels = zip(*filtered)
    paths = list(paths)
    labels = np.array(labels)

    # train/val split
    indices = np.arange(len(paths))
    np.random.seed(42)
    np.random.shuffle(indices)
    split = int(len(indices) * 0.8)
    train_idx, val_idx = indices[:split], indices[split:]

    train_paths = [paths[i] for i in train_idx]
    train_labels = labels[train_idx]
    val_paths = [paths[i] for i in val_idx]
    val_labels = labels[val_idx]

    # augmentation
    augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip('horizontal'),
        tf.keras.layers.RandomRotation(0.03),
        tf.keras.layers.RandomTranslation(0.02, 0.02),
        tf.keras.layers.RandomZoom(0.05),
        tf.keras.layers.RandomContrast(0.08),
    ])

    train_ds = make_dataset(train_paths, train_labels, img_size=(args.img_size, args.img_size), batch_size=args.batch_size, augment=augmentation)
    val_ds = make_dataset(val_paths, val_labels, img_size=(args.img_size, args.img_size), batch_size=args.batch_size, shuffle=False)

    Path(args.model_dir).mkdir(parents=True, exist_ok=True)
    checkpoint_path = os.path.join(args.model_dir, 'best.keras')

    model = build_model(img_size=(args.img_size, args.img_size, 3))
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(checkpoint_path, save_best_only=True, save_weights_only=False),
        tf.keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True)
    ]

    # class weights to handle imbalance
    from collections import Counter
    counter = Counter(train_labels.tolist())
    total = sum(counter.values())
    class_weight = {cls: total / (len(counter) * count) for cls, count in counter.items()}

    model.fit(train_ds, validation_data=val_ds, epochs=args.epochs, callbacks=callbacks, class_weight=class_weight)

    # optional fine-tuning
    if args.fine_tune_epochs > 0:
        base = model.layers[1] if len(model.layers) > 1 else None
        # more robust: find the MobileNetV2 layer by name
        for layer in model.layers:
            if isinstance(layer, tf.keras.Model) and 'mobilenetv2' in layer.name.lower():
                base = layer
                break
        if base is not None:
            base.trainable = True
            model.compile(optimizer=tf.keras.optimizers.Adam(1e-5), loss='binary_crossentropy', metrics=['accuracy', tf.keras.metrics.AUC(name='auc')])
            model.fit(train_ds, validation_data=val_ds, epochs=args.fine_tune_epochs, callbacks=callbacks, class_weight=class_weight)

    model.save(args.model_dir, include_optimizer=False)
    print('Model saved to', args.model_dir)


if __name__ == '__main__':
    main(sys.argv[1:])
