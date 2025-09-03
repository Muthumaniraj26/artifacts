import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, random_split
from tqdm import tqdm
import platform

# ------------------------------
# Main Configuration
# ------------------------------
# --- Set your data path here ---
DATA_DIR = r"C:\Users\muthumaniraj\Documents\artifacts\dataset"

# --- Split and Training Parameters ---
VALIDATION_SPLIT = 0.2  # Use 20% of the data for validation
BATCH_SIZE = 32         # Adjust based on your GPU memory
IMG_SIZE = 380
SAVE_MODEL_PATH = 'artifact_model_finetuned.pth'

# --- Accuracy Improvement: Two-Phase Training Epochs ---
# We'll first train only the new layers (warm-up), then unfreeze and train the whole model (fine-tuning).
WARMUP_EPOCHS = 10
FINETUNE_EPOCHS = 20 # Total epochs will be WARMUP_EPOCHS + FINETUNE_EPOCHS

# --- Accuracy Improvement: Different Learning Rates ---
LR_HEAD = 1e-3      # Learning rate for the new classifier head
LR_FINETUNE = 1e-5  # A very small learning rate for fine-tuning the whole model

# --- Automatically Detect Device ---
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# --- GPU Optimization: Set num_workers based on OS ---
# DataLoader multiprocessing can cause issues on Windows.
NUM_WORKERS = 0 if platform.system() == "Windows" else 4

# --- Automatically Detect Number of Classes ---
try:
    NUM_CLASSES = len([name for name in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, name))])
except FileNotFoundError:
    print(f"Error: The directory '{DATA_DIR}' was not found.")
    print("Please ensure your DATA_DIR is correct.")
    exit()

# ------------------------------
# Model Creation
# ------------------------------
def create_model(num_classes):
    """Creates an EfficientNetV2-L model with a custom classifier head."""
    model = models.efficientnet_v2_l(weights=models.EfficientNet_V2_L_Weights.IMAGENET1K_V1)
    
    # Freeze all the parameters in the base model initially
    for param in model.parameters():
        param.requires_grad = False
        
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Sequential(
        nn.Linear(in_features, 512),
        nn.GELU(),
        nn.BatchNorm1d(512),
        nn.Dropout(0.3),
        nn.Linear(512, num_classes)
    )
    # The new classifier head will have requires_grad=True by default
    return model

# ------------------------------
# Training and Validation
# ------------------------------
def train_one_epoch(model, loader, optimizer, criterion, device, scaler):
    model.train()
    total_loss, correct, total = 0, 0, 0
    use_amp = (device == 'cuda') # Use Automatic Mixed Precision on GPU
    
    for images, labels in tqdm(loader, desc="Training", leave=False):
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        
        with torch.cuda.amp.autocast(enabled=use_amp):
            outputs = model(images)
            loss = criterion(outputs, labels)
            
        # Scaler handles mixed precision scaling
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        
        total_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += labels.size(0)
        
    return total_loss / total, 100.0 * correct / total

def validate(model, loader, criterion, device):
    model.eval()
    total_loss, correct, total = 0, 0, 0
    with torch.no_grad():
        for images, labels in tqdm(loader, desc="Validating", leave=False):
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            total_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            correct += predicted.eq(labels).sum().item()
            total += labels.size(0)
            
    return total_loss / total, 100.0 * correct / total

# ------------------------------
# Main Training Function
# ------------------------------
def main():
    print(f"Using device: {DEVICE}")
    print(f"Using {NUM_WORKERS} workers for DataLoader.")
    print(f"Found {NUM_CLASSES} classes in '{DATA_DIR}'.")

    # --- Data Augmentation and Loading ---
    train_transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    val_transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    full_dataset = datasets.ImageFolder(DATA_DIR)
    total_size = len(full_dataset)
    val_size = int(VALIDATION_SPLIT * total_size)
    train_size = total_size - val_size
    train_subset, val_subset = random_split(full_dataset, [train_size, val_size], generator=torch.Generator().manual_seed(42))
    
    # Apply transforms to the subsets
    train_subset.dataset = datasets.ImageFolder(DATA_DIR, transform=train_transform)
    val_subset.dataset = datasets.ImageFolder(DATA_DIR, transform=val_transform)
    # Re-assign the indices after recreating the datasets
    train_subset.indices = train_subset.indices
    val_subset.indices = val_subset.indices


    train_loader = DataLoader(train_subset, batch_size=BATCH_SIZE, shuffle=True, num_workers=NUM_WORKERS, pin_memory=True, drop_last=True)
    val_loader = DataLoader(val_subset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS, pin_memory=True)
    
    model = create_model(NUM_CLASSES).to(DEVICE)
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    scaler = torch.cuda.amp.GradScaler(enabled=(DEVICE == 'cuda'))
    best_acc = 0.0

    # --- PHASE 1: WARM-UP (Train only the classifier head) ---
    print("\n--- PHASE 1: WARM-UP ---")
    print("Training only the new classifier head...")
    # The optimizer only targets the parameters of the new classifier
    optimizer = optim.AdamW(model.classifier[1].parameters(), lr=LR_HEAD)
    scheduler = CosineAnnealingLR(optimizer, T_max=WARMUP_EPOCHS)

    for epoch in range(WARMUP_EPOCHS):
        print(f"\n--- Warm-up Epoch [{epoch+1}/{WARMUP_EPOCHS}] ---")
        train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, criterion, DEVICE, scaler)
        val_loss, val_acc = validate(model, val_loader, criterion, DEVICE)
        scheduler.step()
        print(f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.2f}%")
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), SAVE_MODEL_PATH)
            print(f"✅ Model saved with Val Acc: {best_acc:.2f}%")

    # --- PHASE 2: FINE-TUNING (Train the whole model) ---
    print("\n--- PHASE 2: FINE-TUNING ---")
    print("Unfreezing all layers and training with a low learning rate...")
    # Unfreeze all layers
    for param in model.parameters():
        param.requires_grad = True
    
    # Optimizer now targets all model parameters with a very low learning rate
    optimizer = optim.AdamW(model.parameters(), lr=LR_FINETUNE)
    scheduler = CosineAnnealingLR(optimizer, T_max=FINETUNE_EPOCHS)

    for epoch in range(FINETUNE_EPOCHS):
        print(f"\n--- Fine-tuning Epoch [{epoch+1}/{FINETUNE_EPOCHS}] ---")
        train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, criterion, DEVICE, scaler)
        val_loss, val_acc = validate(model, val_loader, criterion, DEVICE)
        scheduler.step()
        print(f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.2f}%")
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), SAVE_MODEL_PATH)
            print(f"✅ Model saved with Val Acc: {best_acc:.2f}%")

    print(f"\nTraining completed. Best Validation Accuracy: {best_acc:.2f}%")
    print(f"Best model saved to '{SAVE_MODEL_PATH}'")

if __name__ == "__main__":
    main()
