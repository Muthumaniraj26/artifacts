from torch.utils.tensorboard import SummaryWriter
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import os

# Paths
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# TensorBoard writers for train and validation
train_writer = SummaryWriter(os.path.join(LOG_DIR, 'train'))
val_writer = SummaryWriter(os.path.join(LOG_DIR, 'validation'))

# Simple Example: Fake Metrics
for epoch in range(10):
    train_loss = torch.rand(1).item()
    val_loss = torch.rand(1).item()
    train_acc = torch.rand(1).item() * 100
    val_acc = torch.rand(1).item() * 100

    # Log scalars
    train_writer.add_scalar('Loss', train_loss, epoch)
    train_writer.add_scalar('Accuracy', train_acc, epoch)
    val_writer.add_scalar('Loss', val_loss, epoch)
    val_writer.add_scalar('Accuracy', val_acc, epoch)

train_writer.close()
val_writer.close()
