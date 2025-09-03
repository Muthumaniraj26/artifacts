# training/train_pipeline.py
import os, json, argparse, random, itertools
from pathlib import Path
from typing import List, Tuple
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, UnidentifiedImageError
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import classification_report, confusion_matrix
from collections import Counter
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.optimizers import Adam

# ----------------- Args -----------------
parser = argparse.ArgumentParser()
parser.add_argument('dataset', type=str, help='dataset')
parser.add_argument('--epochs', type=int, default=300)
parser.add_argument('--img_size', type=int, default=224)
parser.add_argument('--batch', type=int, default=32)
parser.add_argument('--seed', type=int, default=42)
args = parser.parse_args()

DATA_DIR = Path(args.dataset)
IMG_SIZE = args.img_size
BATCH = args.batch
EPOCHS = args.epochs
SEED = args.seed
random.seed(SEED); np.random.seed(SEED); tf.random.set_seed(SEED)

# --- GPU Configuration ---
# List available GPUs and set memory growth to prevent TensorFlow from allocating all memory at once.
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        logical_gpus = tf.config.experimental.list_logical_devices('GPU')
        print(f"✅ Found {len(gpus)} Physical GPUs, Configured {len(logical_gpus)} Logical GPUs")
    except RuntimeError as e:
        # Memory growth must be set before GPUs have been initialized
        print(e)
else:
    print("⚠️ No GPU found, training will run on CPU.")


# Mixed precision if available
try:
    tf.keras.mixed_precision.set_global_policy('mixed_float16')
    print("🚀 Mixed precision enabled.")
except Exception:
    pass

os.makedirs('models', exist_ok=True)
os.makedirs('reports', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# ------------- Helpers -------------
def is_image_ok(p: Path) -> bool:
    try:
        with Image.open(p) as im:
            im.verify()
        with Image.open(p) as im2:
            im2.convert('RGB')
        return True
    except (UnidentifiedImageError, OSError, IOError):
        return False

def collect_images(root: Path):
    classes, files, labels = [], [], []
    for d in sorted([x for x in root.iterdir() if x.is_dir()]):
        classes.append(d.name)
        for fp in sorted(d.rglob('*')):
            if fp.is_file() and fp.suffix.lower() in {'.jpg','.jpeg','.png','.bmp','.webp','.tif','.tiff'}:
                if is_image_ok(fp):
                    files.append(str(fp))
                    labels.append(d.name)
                else:
                    print(f"Skipping corrupted: {fp}")
    return classes, np.array(files), np.array(labels)

assert DATA_DIR.exists(), f"Dataset folder not found: {DATA_DIR}"
classes, files, labels = collect_images(DATA_DIR)
assert len(files) > 0, 'No valid images found.'

# Remove empty classes
cnt = {c: (labels==c).sum() for c in classes}
classes = [c for c in classes if cnt[c] > 0]
mask = np.isin(labels, classes)
files, labels = files[mask], labels[mask]
print('Classes:', classes)
print('Total images:', len(files))

# ----------- Stratified 80/10/10 -----------
sss1 = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=SEED)
train_idx, temp_idx = next(sss1.split(files, labels))
X_train, y_train = files[train_idx], labels[train_idx]
X_temp,  y_temp  = files[temp_idx],  labels[temp_idx]

sss2 = StratifiedShuffleSplit(n_splits=1, test_size=0.5, random_state=SEED)
val_idx, test_idx = next(sss2.split(X_temp, y_temp))
X_val, y_val   = X_temp[val_idx], y_temp[val_idx]
X_test, y_test = X_temp[test_idx], y_temp[test_idx]

print(f"Split sizes -> train: {len(X_train)}, val: {len(X_val)}, test: {len(X_test)}")

# ----------- tf.data pipelines -----------
AUTOTUNE = tf.data.AUTOTUNE
cls2idx = {c:i for i,c in enumerate(classes)}
idx2cls = {i:c for c,i in cls2idx.items()}

@tf.function
def load_img(path, label):
    img = tf.io.read_file(path)
    img = tf.io.decode_image(img, channels=3, expand_animations=False)
    img = tf.image.resize(img, [IMG_SIZE, IMG_SIZE], antialias=True)
    img = tf.cast(img, tf.float32)/255.0
    return img, tf.one_hot(label, depth=len(classes))

def make_ds(paths, labels_, augment=False, shuffle=False):
    lbl_idx = np.array([cls2idx[l] for l in labels_], dtype=np.int32)
    ds = tf.data.Dataset.from_tensor_slices((paths, lbl_idx))
    if shuffle:
        ds = ds.shuffle(min(len(paths), 2000), seed=SEED, reshuffle_each_iteration=True)
    ds = ds.map(load_img, num_parallel_calls=AUTOTUNE)
    if augment:
        aug = tf.keras.Sequential([
            layers.RandomFlip('horizontal'),
            layers.RandomRotation(0.08),
            layers.RandomZoom(0.15),
            layers.RandomContrast(0.12),
            layers.RandomTranslation(0.08, 0.08),
        ])
        ds = ds.map(lambda x,y: (aug(x, training=True), y), num_parallel_calls=AUTOTUNE)
    return ds.batch(BATCH).prefetch(AUTOTUNE)

train_ds = make_ds(X_train, y_train, augment=True,  shuffle=True)
val_ds   = make_ds(X_val,   y_val,   augment=False, shuffle=False)
test_ds  = make_ds(X_test,  y_test,  augment=False, shuffle=False)

# ----------- Class Weights -----------
counts = Counter(y_train)
mx = max(counts.values())
class_weights = {cls2idx[c]: mx/counts[c] for c in counts}
print('Class weights:', class_weights)

# ----------- Model -----------
# Ensure channels_last so pretrained weights expect 3 input channels
tf.keras.backend.set_image_data_format('channels_last')

# Build EfficientNet - try with pretrained weights first, fallback to random if mismatch
try:
    inputs = layers.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    base = EfficientNetB0(include_top=False, weights='imagenet', input_tensor=inputs)
    print("Loaded EfficientNetB0 with ImageNet weights")
except ValueError as e:
    print(f"ImageNet weights mismatch: {e}")
    print("Falling back to random initialization...")
    inputs = layers.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    base = EfficientNetB0(include_top=False, weights=None, input_tensor=inputs)

base.trainable = False
x = base.output
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.4)(x)
x = layers.Dense(512, activation='relu')(x)
x = layers.Dropout(0.4)(x)
outputs = layers.Dense(len(classes), activation='softmax', dtype='float32')(x)
model = models.Model(inputs, outputs)

model.compile(optimizer=Adam(1e-4), loss='categorical_crossentropy', metrics=['accuracy'])

# Increased patience for early stopping to allow more training with higher epochs
ckpt1 = tf.keras.callbacks.ModelCheckpoint('models/best_phase1.h5', monitor='val_accuracy', save_best_only=True, mode='max')
early = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=25, restore_best_weights=True)
rlr   = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', patience=8, factor=0.5, min_lr=1e-6)
tb    = tf.keras.callbacks.TensorBoard(log_dir='logs')

# Phase 1: warmup - increased from 12 to 50 epochs
hist1 = model.fit(train_ds, validation_data=val_ds, epochs=min(50, EPOCHS), callbacks=[ckpt1, early, rlr, tb], class_weight=class_weights)

# Phase 2: fine-tune last ~40 layers
base.trainable = True
for l in base.layers[:-40]:
    l.trainable = False
model.compile(optimizer=Adam(1e-5), loss='categorical_crossentropy', metrics=['accuracy'])
ckpt2 = tf.keras.callbacks.ModelCheckpoint('models/best_finetuned.h5', monitor='val_accuracy', save_best_only=True, mode='max')
remain = max(EPOCHS - len(hist1.history['loss']), 1)
hist2 = model.fit(train_ds, validation_data=val_ds, epochs=remain, callbacks=[ckpt2, early, rlr, tb], class_weight=class_weights)

best_path = 'models/best_finetuned.h5' if os.path.exists('models/best_finetuned.h5') else 'models/best_phase1.h5'
best = tf.keras.models.load_model(best_path)

# ----------- Evaluation & Reports -----------
probs = best.predict(test_ds, verbose=0)
y_pred = np.argmax(probs, axis=1)
y_true = np.concatenate([np.argmax(y.numpy(), axis=1) for _, y in test_ds])

report = classification_report(y_true, y_pred, target_names=classes, digits=4)
print('\n=== TEST REPORT ===\n')
print(report)
with open('reports/classification_report.txt', 'w', encoding='utf-8') as f:
    f.write(report)

cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(12,10))
plt.imshow(cm, interpolation='nearest')
plt.title('Confusion Matrix (Test)')
plt.colorbar()
plt.xticks(range(len(classes)), classes, rotation=90)
plt.yticks(range(len(classes)), classes)
th = cm.max()/2
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        v = cm[i,j]
        if v>0:
            plt.text(j,i,str(v),ha='center',va='center',color='white' if v>th else 'black',fontsize=8)
plt.tight_layout(); plt.ylabel('True'); plt.xlabel('Predicted')
plt.savefig('reports/confusion_matrix.png', dpi=180, bbox_inches='tight')
plt.close()

# Save labels map
with open('models/class_labels.json','w',encoding='utf-8') as f:
    json.dump({i:c for i,c in enumerate(classes)}, f, indent=2)

# Export TFLite
try:
    conv = tf.lite.TFLiteConverter.from_keras_model(best)
    conv.optimizations = [tf.lite.Optimize.DEFAULT]
    tfl = conv.convert()
    open('models/artifact_classifier.tflite','wb').write(tfl)
    print('Saved models/artifact_classifier.tflite')
except Exception as e:
    print('TFLite export skipped:', e)

print('\nDone. Best model:', best_path)
print('Reports in ./reports, models in ./models')
