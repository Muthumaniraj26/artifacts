import os
import shutil
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from tqdm import tqdm

# ------------------------------
# Main Configuration
# ------------------------------
DATA_DIR = r"dataset"  # Root dataset folder
TRAIN_DIR = os.path.join(DATA_DIR, "train")
VAL_DIR = os.path.join(DATA_DIR, "valid")
TEST_DIR = os.path.join(DATA_DIR, "test")

BATCH_SIZE = 16
EPOCHS = 30
LEARNING_RATE = 0.001
IMG_SIZE = 256
SAVE_MODEL_PATH = 'artifact_with_val.pth'

NUM_WORKERS = 0  # For Windows
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# Validate dataset structure
for path in [TRAIN_DIR, VAL_DIR, TEST_DIR]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Error: Directory '{path}' does not exist. Please split your dataset correctly.")

NUM_CLASSES = len([name for name in os.listdir(TRAIN_DIR) if os.path.isdir(os.path.join(TRAIN_DIR, name))])
if NUM_CLASSES < 2:
    raise ValueError("Error: At least 2 classes are required for classification.")

# ------------------------------
# Remove empty class folders before loading datasets
# ------------------------------
def clean_empty_folders(path):
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp')
    for cls in os.listdir(path):
        cls_path = os.path.join(path, cls)
        if os.path.isdir(cls_path):
            images = [f for f in os.listdir(cls_path) if f.lower().endswith(valid_extensions)]
            if len(images) == 0:
                print(f"⚠️ Removing empty folder: {cls_path}")
                shutil.rmtree(cls_path)

# Clean for validation and test folders
clean_empty_folders(VAL_DIR)
clean_empty_folders(TEST_DIR)

# ------------------------------
# Model Creation
# ------------------------------
def create_model(num_classes):
    model = models.efficientnet_v2_s(weights=models.EfficientNet_V2_S_Weights.IMAGENET1K_V1)

    # Freeze base model
    for param in model.parameters():
        param.requires_grad = False

    # Modify classifier
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Sequential(
        nn.Linear(in_features, 512),
        nn.GELU(),
        nn.BatchNorm1d(512),
        nn.Dropout(0.3),
        nn.Linear(512, num_classes)
    )
    return model

# ------------------------------
# Training & Validation Functions
# ------------------------------
def train_one_epoch(model, loader, optimizer, criterion, device, scaler):
    model.train()
    total_loss, correct, total = 0, 0, 0

    for images, labels in tqdm(loader, desc="Training", leave=False):
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()

        with torch.amp.autocast(device_type=device, enabled=(device == 'cuda')):
            outputs = model(images)
            loss = criterion(outputs, labels)

        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        total_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += labels.size(0)

    return total_loss / total, 100.0 * correct / total

def evaluate(model, loader, criterion, device, phase="Validation"):
    model.eval()
    total_loss, correct, total = 0, 0, 0

    with torch.no_grad():
        for images, labels in tqdm(loader, desc=phase, leave=False):
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)

            total_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            correct += predicted.eq(labels).sum().item()
            total += labels.size(0)

    return total_loss / total, 100.0 * correct / total

# ------------------------------
# Safe ImageFolder Loader
# ------------------------------
def safe_imagefolder(path, transform):
    dataset = datasets.ImageFolder(path, transform=transform)
    if len(dataset) == 0:
        raise ValueError(f"No valid images found in {path}. Check your split or file extensions.")
    return dataset

# ------------------------------
# Main Training Function
# ------------------------------
def main():
    print(f"Using device: {DEVICE}")
    print(f"Found {NUM_CLASSES} classes in '{TRAIN_DIR}'.")

    # Data augmentation
    train_transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    eval_transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # Load datasets
    train_dataset = datasets.ImageFolder(TRAIN_DIR, transform=train_transform)
    val_dataset = safe_imagefolder(VAL_DIR, eval_transform)
    test_dataset = safe_imagefolder(TEST_DIR, eval_transform)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=NUM_WORKERS, pin_memory=True, drop_last=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS, pin_memory=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS, pin_memory=True)

    model = create_model(NUM_CLASSES).to(DEVICE)

    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = optim.AdamW(model.classifier[1].parameters(), lr=LEARNING_RATE)
    scheduler = CosineAnnealingLR(optimizer, T_max=EPOCHS)

    scaler = torch.amp.GradScaler(enabled=(DEVICE == 'cuda'))

    best_acc = 0.0
    for epoch in range(EPOCHS):
        print(f"\n--- Epoch [{epoch+1}/{EPOCHS}] ---")
        train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, criterion, DEVICE, scaler)
        val_loss, val_acc = evaluate(model, val_loader, criterion, DEVICE, phase="Validation")
        scheduler.step()

        print(f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.2f}%")

        # Save best model based on validation accuracy
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), SAVE_MODEL_PATH)
            print(f"✅ Model saved with Val Acc: {best_acc:.2f}%")

    print("\nTraining completed.")
    print(f"Best Validation Accuracy: {best_acc:.2f}%")
    print(f"Best model saved to '{SAVE_MODEL_PATH}'")

    # Final evaluation on test set
    print("\n--- Final Test Evaluation ---")
    model.load_state_dict(torch.load(SAVE_MODEL_PATH))
    test_loss, test_acc = evaluate(model, test_loader, criterion, DEVICE, phase="Testing")
    print(f"Test Loss: {test_loss:.4f} | Test Acc: {test_acc:.2f}%")

if __name__ == "__main__":
    main()
