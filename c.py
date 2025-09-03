import os
from shutil import copy2

dataset_dir = r"C:\Users\muthumaniraj\Documents\artifacts\dataset\test"
destination_dir = r"C:\Users\muthumaniraj\Documents\artifacts\dataset\train"

for img in os.listdir(dataset_dir):
    src_path = os.path.join(dataset_dir, img)
    if os.path.isfile(src_path):  # ✅ Only copy files
        copy2(src_path, destination_dir)
