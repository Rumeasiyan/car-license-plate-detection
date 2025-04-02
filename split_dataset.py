import os
import shutil
import random
from pathlib import Path

# Set random seed for reproducibility
random.seed(42)

# Define paths
ARCHIVE_IMAGES = "archive/images"
ARCHIVE_LABELS = "yolo_labels"
TRAIN_IMAGES = "datasets/images/train"
VAL_IMAGES = "datasets/images/val"
TRAIN_LABELS = "datasets/labels/train"
VAL_LABELS = "datasets/labels/val"

# Create directories if they don't exist
os.makedirs(TRAIN_IMAGES, exist_ok=True)
os.makedirs(VAL_IMAGES, exist_ok=True)
os.makedirs(TRAIN_LABELS, exist_ok=True)
os.makedirs(VAL_LABELS, exist_ok=True)

# Get all image files
image_files = [f for f in os.listdir(ARCHIVE_IMAGES) if f.endswith(('.jpg', '.jpeg', '.png'))]
random.shuffle(image_files)

# Split ratio (80% train, 20% validation)
split_idx = int(len(image_files) * 0.8)
train_files = image_files[:split_idx]
val_files = image_files[split_idx:]

# Copy training files
for img_file in train_files:
    # Copy image
    shutil.copy2(
        os.path.join(ARCHIVE_IMAGES, img_file),
        os.path.join(TRAIN_IMAGES, img_file)
    )
    
    # Copy corresponding label file
    label_file = Path(img_file).stem + '.txt'
    if os.path.exists(os.path.join(ARCHIVE_LABELS, label_file)):
        shutil.copy2(
            os.path.join(ARCHIVE_LABELS, label_file),
            os.path.join(TRAIN_LABELS, label_file)
        )

# Copy validation files
for img_file in val_files:
    # Copy image
    shutil.copy2(
        os.path.join(ARCHIVE_IMAGES, img_file),
        os.path.join(VAL_IMAGES, img_file)
    )
    
    # Copy corresponding label file
    label_file = Path(img_file).stem + '.txt'
    if os.path.exists(os.path.join(ARCHIVE_LABELS, label_file)):
        shutil.copy2(
            os.path.join(ARCHIVE_LABELS, label_file),
            os.path.join(VAL_LABELS, label_file)
        )

print(f"Dataset split complete:")
print(f"Training images: {len(train_files)}")
print(f"Validation images: {len(val_files)}") 