"""
Organize Potato Dataset from PlantVillage into Train/Test Structure
"""

import os
import shutil
import random
from pathlib import Path

def organize_dataset():
    """
    Organize potato dataset from multiple sources into train/test structure
    """
    
    # Source paths (your extracted dataset)
    source_paths = [
        "dataset/archive/PlantVillage/PlantVillage",
        "dataset/archive/PotatoPlants"
    ]
    
    # Target directories
    train_dir = "dataset/train"
    test_dir = "dataset/test"
    
    # Create target directories
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)
    
    # Class mapping (different naming conventions)
    class_mapping = {
        "Potato__Early_blight": "early_blight",
        "Potato__early_blight": "early_blight",
        "Potato___Early_blight": "early_blight",
        "Potato_Early_blight": "early_blight",
        "Potato__healthy": "healthy",
        "Potato___healthy": "healthy",
        "Potato_healthy": "healthy",
        "Potato__Late_blight": "late_blight",
        "Potato__late_blight": "late_blight",
        "Potato___Late_blight": "late_blight",
        "Potato_Late_blight": "late_blight"
    }
    
    print("="*60)
    print("ORGANIZING POTATO DATASET")
    print("="*60)
    
    all_images = {k: [] for k in ['healthy', 'early_blight', 'late_blight']}
    
    # Collect all images from all sources
    for source_path in source_paths:
        if not os.path.exists(source_path):
            print(f"⚠️ Source not found: {source_path}")
            continue
            
        print(f"\n📂 Processing: {source_path}")
        
        for folder_name in os.listdir(source_path):
            folder_path = os.path.join(source_path, folder_name)
            
            if not os.path.isdir(folder_path):
                continue
            
            # Map folder name to class
            class_name = None
            for key, value in class_mapping.items():
                if key in folder_name or key.lower() in folder_name.lower():
                    class_name = value
                    break
            
            if class_name is None:
                print(f"  ⚠️ Unknown class: {folder_name}")
                continue
            
            # Get all images
            images = [f for f in os.listdir(folder_path) 
                     if f.lower().endswith(('.jpg', '.png', '.jpeg', '.JPG', '.PNG'))]
            
            for img in images:
                all_images[class_name].append(os.path.join(folder_path, img))
            
            print(f"  ✅ {class_name}: {len(images)} images found")
    
    # Split and copy images
    print("\n" + "="*60)
    print("SPLITTING AND COPYING IMAGES")
    print("="*60)
    
    for class_name, images in all_images.items():
        if not images:
            print(f"⚠️ No images for {class_name}")
            continue
        
        # Shuffle images
        random.shuffle(images)
        
        # Split (80% train, 20% test)
        split_idx = int(len(images) * 0.8)
        train_images = images[:split_idx]
        test_images = images[split_idx:]
        
        # Create class directories
        os.makedirs(os.path.join(train_dir, class_name), exist_ok=True)
        os.makedirs(os.path.join(test_dir, class_name), exist_ok=True)
        
        # Copy train images
        for img_path in train_images:
            img_name = os.path.basename(img_path)
            dst_path = os.path.join(train_dir, class_name, img_name)
            shutil.copy2(img_path, dst_path)
        
        # Copy test images
        for img_path in test_images:
            img_name = os.path.basename(img_path)
            dst_path = os.path.join(test_dir, class_name, img_name)
            shutil.copy2(img_path, dst_path)
        
        print(f"✅ {class_name}:")
        print(f"   Train: {len(train_images)} images")
        print(f"   Test: {len(test_images)} images")
        print(f"   Total: {len(images)} images")
        print("-"*40)
    
    print("\n" + "="*60)
    print("✅ DATASET ORGANIZED SUCCESSFULLY!")
    print(f"Train directory: {train_dir}")
    print(f"Test directory: {test_dir}")
    print("="*60)

if __name__ == "__main__":
    organize_dataset()