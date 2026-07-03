try:
    import tensorflow as tf
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
except Exception as _err:
    tf = None
    ImageDataGenerator = None
    _TF_IMPORT_ERROR = _err

import numpy as np
import os
try:
    import cv2
except Exception:
    cv2 = None

class PotatoDataLoader:
    """
    Data loader for potato disease detection dataset
    """
    
    def __init__(self, data_dir, img_size=(224, 224), batch_size=32):
        self.data_dir = data_dir
        self.img_size = img_size
        self.batch_size = batch_size
        self.class_names = ['healthy', 'early_blight', 'late_blight']
        self.num_classes = len(self.class_names)
        
    def get_data_generators(self, validation_split=0.2):
        """
        Create data generators with augmentation for training
        """
        # Data augmentation for training
        if ImageDataGenerator is None:
            raise RuntimeError("tensorflow and keras are required to create data generators. Install tensorflow.")

        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=30,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest',
            validation_split=validation_split
        )
        
        # No augmentation for validation
        test_datagen = ImageDataGenerator(
            rescale=1./255,
            validation_split=validation_split
        )
        
        # Training generator
        train_generator = train_datagen.flow_from_directory(
            self.data_dir,
            target_size=self.img_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            subset='training',
            classes=self.class_names,
            shuffle=True
        )
        
        # Validation generator
        validation_generator = test_datagen.flow_from_directory(
            self.data_dir,
            target_size=self.img_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            subset='validation',
            classes=self.class_names,
            shuffle=False
        )
        
        return train_generator, validation_generator
    
    def get_test_generator(self, test_dir):
        """Get test data generator"""
        test_datagen = ImageDataGenerator(rescale=1./255)
        
        test_generator = test_datagen.flow_from_directory(
            test_dir,
            target_size=self.img_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            classes=self.class_names,
            shuffle=False
        )
        
        return test_generator
    
    def load_single_image(self, image_path):
        """Load and preprocess a single image"""
        if cv2 is None:
            raise RuntimeError("OpenCV (cv2) is required to load images. Install opencv-python.")
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, self.img_size)
        img = img.astype(np.float32) / 255.0
        return img
    
    def preprocess_batch(self, images):
        """Preprocess a batch of images"""
        processed = []
        for img in images:
            if cv2 is None:
                raise RuntimeError("OpenCV (cv2) is required to preprocess images. Install opencv-python.")
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            elif img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
            processed.append(cv2.resize(img, self.img_size))
        return np.array(processed) / 255.0
