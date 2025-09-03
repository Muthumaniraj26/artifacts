import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, random_split
from tqdm import tqdm

# ------------------------------
# Main Configuration
# ------------------------------
DATA_DIR = r"C:\Users\muthumaniraj\Documents\artifacts\dataset"

VALIDATION_SPLIT = 0.2
# --- CHANGE 1: Reduced batch size to lower memory usage ---
BATCH_SIZE = 16
EPOCHS = 30
LEARNING_RATE = 0.001
# --- CHANGE 2: Reduced image size to significantly lower memory usage ---
IMG_SIZE = 256
SAVE_MODEL_PATH = 'artifact_model.pth'

# Set to 0 for Windows to avoid multiprocessing bottlenecks
NUM_WORKERS = 0

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

try:
    NUM_CLASSES = len([name for name in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, name))])
except FileNotFoundError:
    print(f"Error: The directory '{DATA_DIR}' was not found.")
    exit()

# ------------------------------
# Model Creation
# ------------------------------
def create_model(num_classes):
    """Creates a pre-trained EfficientNetV2-S model with a custom classifier head."""
    # --- CHANGE 3: Switched to a smaller, less memory-intensive model ---
    model = models.efficientnet_v2_s(weights=models.EfficientNet_V2_S_Weights.IMAGENET1K_V1)

    # Freeze all parameters in the model initially
    for param in model.parameters():
        param.requires_grad = False
        
    # Replace the classifier and ensure its parameters are trainable
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Sequential(
        nn.Linear(in_features, 512),
        nn.GELU(),
        nn.BatchNorm1d(512),
        nn.Dropout(0.3),
        nn.Linear(512, num_classes)
    )
    # This loop is redundant if you just created the sequential block, 
    # as new layers have requires_grad=True by default, but it's good for clarity.
    for param in model.classifier[1].parameters():
        param.requires_grad = True
        
    return model

# ------------------------------
# Training and Validation Functions
# ------------------------------
def train_one_epoch(model, loader, optimizer, criterion, device, scaler):
    model.train()
    total_loss, correct, total = 0, 0, 0
    
    for images, labels in tqdm(loader, desc="Training", leave=False):
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        
        with torch.amp.autocast(device_type=device, enabled=(device=='cuda')):
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
    print(f"Found {NUM_CLASSES} classes in '{DATA_DIR}'.")
    print(f"Splitting data: {1-VALIDATION_SPLIT:.0%} train, {VALIDATION_SPLIT:.0%} validation.")

    train_transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    val_transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    full_dataset = datasets.ImageFolder(DATA_DIR, transform=val_transform)
    total_size = len(full_dataset)
    val_size = int(VALIDATION_SPLIT * total_size)
    train_size = total_size - val_size
    train_subset, val_subset = random_split(full_dataset, [train_size, val_size],
                                            generator=torch.Generator().manual_seed(42))
    
    # A small correction from your script: only the train_subset needs the train_transform.
    # The val_subset should keep the val_transform it was initialized with.
    train_subset.dataset.transform = train_transform
    # The line below is not necessary as val_subset already uses the full_dataset 
    # with val_transform. Re-assigning it is harmless but redundant.
    # val_subset.dataset.transform = val_transform

    train_loader = DataLoader(train_subset, batch_size=BATCH_SIZE, shuffle=True, num_workers=NUM_WORKERS, pin_memory=True, drop_last=True)
    val_loader = DataLoader(val_subset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS, pin_memory=True)
    
    model = create_model(NUM_CLASSES).to(DEVICE)
        
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = optim.AdamW(model.classifier[1].parameters(), lr=LEARNING_RATE)
    scheduler = CosineAnnealingLR(optimizer, T_max=EPOCHS)
    
    scaler = torch.amp.GradScaler(enabled=(DEVICE == 'cuda'))

    best_acc = 0.0
    for epoch in range(EPOCHS):
        print(f"\n--- Epoch [{epoch+1}/{EPOCHS}] ---")
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