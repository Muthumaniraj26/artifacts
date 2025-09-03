import os
from PIL import Image, ImageDraw, ImageFont
import glob
import math

# --- Configuration ---
dataset_folder = r"separated_images\valid"  # Your dataset folder path
output_folder = r"C:\Users\muthumaniraj\Documents\artifacts\dataset\valid\Thakli"  # Output folder for individual images
font_size = 30
starting_number = 1 # Starting number for comv naming convention
target_total_images = 3000  # Total number of images you want at the end
name="Thakli" 

# Supported image formats
image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.webp']

# Load all images from dataset folder
image_files = []
for ext in image_extensions:
    image_files.extend(glob.glob(os.path.join(dataset_folder, ext)))
    image_files.extend(glob.glob(os.path.join(dataset_folder, ext.upper())))

if not image_files:
    print(f"No images found in {dataset_folder}")
    exit()

print(f"Found {len(image_files)} images in dataset")


# Calculate how many times each image needs to be duplicated
multiply_count = math.ceil(target_total_images / len(image_files))
actual_total = len(image_files) * multiply_count

print(f"Will duplicate each image {multiply_count} times to reach approximately {target_total_images} images")
print(f"Actual total will be {actual_total} images")

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Process each image separately
current_number = starting_number
for i, image_path in enumerate(image_files):
    try:
        # Load the image
        img = Image.open(image_path)
        
        # Duplicate this image to reach target count
        for j in range(multiply_count):
            unified_name = f"{name}{current_number}"
            
            # Save the original image exactly as it is
            output_path = os.path.join(output_folder, f"{unified_name}.png")
            img.save(output_path)
            print(f"Saved: {output_path}")
            
            current_number += 1
        
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

print(f"\nAll {len(image_files)} images have been duplicated {multiply_count} times each")
print(f"Total {actual_total} images saved to '{output_folder}' folder")
print(f"Naming convention: {name}{starting_number} to {name}{starting_number + actual_total - 1}")
