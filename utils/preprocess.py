"""
Image preprocessing utilities for potato disease detection
"""

import os
import cv2
import numpy as np
from PIL import Image
from typing import Union, List, Tuple


def load_image(image_path: str, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
    """
    Load and preprocess a single image
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, target_size)
        img = img.astype(np.float32) / 255.0
        
        return img
    
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None


def load_image_pil(image_path: str, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
    """
    Load image using PIL
    """
    try:
        img = Image.open(image_path)
        img = img.resize(target_size)
        img = np.array(img) / 255.0
        
        if len(img.shape) == 2:
            img = np.stack([img, img, img], axis=2)
        elif img.shape[2] == 4:
            img = img[:, :, :3]
        
        return img
    
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None


def preprocess_batch(images: List[np.ndarray], target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
    """
    Preprocess a batch of images
    """
    processed = []
    
    for img in images:
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        elif img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        
        img = cv2.resize(img, target_size)
        img = img.astype(np.float32) / 255.0
        
        processed.append(img)
    
    return np.array(processed)


def augment_image(image: np.ndarray) -> np.ndarray:
    """
    Apply data augmentation to a single image
    """
    import random
    
    if random.random() > 0.5:
        image = cv2.flip(image, 1)
    
    angle = random.uniform(-30, 30)
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    image = cv2.warpAffine(image, matrix, (w, h))
    
    brightness = random.uniform(0.8, 1.2)
    image = np.clip(image * brightness, 0, 1)
    
    return image


def get_image_stats(image: np.ndarray) -> dict:
    """
    Get statistics about an image
    """
    return {
        'shape': image.shape,
        'min': float(np.min(image)),
        'max': float(np.max(image)),
        'mean': float(np.mean(image)),
        'std': float(np.std(image)),
        'dtype': str(image.dtype)
    }


if __name__ == "__main__":
    print("✅ Preprocessing utilities loaded successfully!")