try:
    import tensorflow as tf
    from tensorflow.keras import layers, models, applications
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
except Exception as _err:
    tf = None
    layers = models = applications = None
    Adam = EarlyStopping = ReduceLROnPlateau = ModelCheckpoint = None
    _TF_IMPORT_ERROR = _err

import numpy as np

class CNNBiLSTMClassifier:
    """
    Hybrid CNN-BiLSTM model for potato disease classification
    Combines CNN for spatial feature extraction with BiLSTM for sequential learning
    """
    
    def __init__(self, input_shape=(224, 224, 3), num_classes=3):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.model = None
        self.history = None
        
    def build_model(self):
        """Build the complete CNN-BiLSTM architecture"""
        if tf is None:
            raise RuntimeError("TensorFlow is not installed or failed to import. Install TensorFlow to build the model.")
        
        # ============================================
        # 1. CNN Base - MobileNetV2 (Efficient)
        # ============================================
        base_model = applications.MobileNetV2(
            input_shape=self.input_shape,
            include_top=False,
            weights='imagenet'
        )
        base_model.trainable = False  # Freeze base layers initially
        
        # ============================================
        # 2. Spatial Attention Mechanism
        # ============================================
        cnn_output = base_model.output
        
        # Channel attention
        attention = layers.GlobalAveragePooling2D()(cnn_output)
        attention = layers.Dense(256, activation='relu')(attention)
        attention = layers.Dense(cnn_output.shape[-1], activation='sigmoid')(attention)
        attention = layers.Reshape((1, 1, cnn_output.shape[-1]))(attention)
        attended_features = layers.multiply([cnn_output, attention])
        
        # ============================================
        # 3. Reshape for BiLSTM
        # ============================================
        # Global pooling to reduce dimensions
        pooled = layers.GlobalAveragePooling2D()(attended_features)
        # Reshape to (batch_size, timesteps=1, features)
        reshape = layers.Reshape((1, pooled.shape[-1]))(pooled)
        
        # ============================================
        # 4. Bidirectional LSTM Layers
        # ============================================
        # First BiLSTM layer - returns sequences
        lstm1 = layers.Bidirectional(
            layers.LSTM(256, return_sequences=True, dropout=0.3, recurrent_dropout=0.2)
        )(reshape)
        
        # Second BiLSTM layer - returns sequences
        lstm2 = layers.Bidirectional(
            layers.LSTM(128, return_sequences=True, dropout=0.3, recurrent_dropout=0.2)
        )(lstm1)
        
        # Third BiLSTM layer - final
        lstm3 = layers.Bidirectional(
            layers.LSTM(64, return_sequences=False, dropout=0.3, recurrent_dropout=0.2)
        )(lstm2)
        
        # ============================================
        # 5. Dense Layers with Dropout
        # ============================================
        dense1 = layers.Dense(256, activation='relu')(lstm3)
        batch_norm1 = layers.BatchNormalization()(dense1)
        dropout1 = layers.Dropout(0.5)(batch_norm1)
        
        dense2 = layers.Dense(128, activation='relu')(dropout1)
        batch_norm2 = layers.BatchNormalization()(dense2)
        dropout2 = layers.Dropout(0.4)(batch_norm2)
        
        dense3 = layers.Dense(64, activation='relu')(dropout2)
        dropout3 = layers.Dropout(0.3)(dense3)
        
        # ============================================
        # 6. Output Layer
        # ============================================
        output = layers.Dense(self.num_classes, activation='softmax')(dropout3)
        
        # Create model
        self.model = models.Model(inputs=base_model.input, outputs=output)
        
        return self.model
    
    def compile_model(self, learning_rate=0.0001):
        """Compile the model with Adam optimizer and metrics"""
        if tf is None:
            raise RuntimeError("TensorFlow is not installed or failed to import. Install TensorFlow to compile the model.")
        self.model.compile(
            optimizer=Adam(learning_rate=learning_rate),
            loss='categorical_crossentropy',
            metrics=[
                'accuracy',
                tf.keras.metrics.Precision(name='precision'),
                tf.keras.metrics.Recall(name='recall'),
                tf.keras.metrics.AUC(name='auc')
            ]
        )
        return self.model
    
    def get_callbacks(self, model_save_path='saved_models/best_model.h5'):
        """Get training callbacks"""
        if tf is None:
            raise RuntimeError("TensorFlow is not installed or failed to import. Install TensorFlow to get training callbacks.")
        return [
            EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.2,
                patience=5,
                min_lr=1e-7,
                verbose=1
            ),
            ModelCheckpoint(
                model_save_path,
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            )
        ]
    
    def train(self, train_generator, val_generator, epochs=50, model_save_path='saved_models/best_model.h5'):
        """Train the model"""
        if tf is None:
            raise RuntimeError("TensorFlow is not installed or failed to import. Install TensorFlow to train the model.")
        callbacks = self.get_callbacks(model_save_path)
        
        self.history = self.model.fit(
            train_generator,
            validation_data=val_generator,
            epochs=epochs,
            callbacks=callbacks,
            verbose=1
        )
        
        return self.history
    
    def predict(self, image):
        """Predict disease class for a single image"""
        if tf is None:
            raise RuntimeError("TensorFlow is not installed or failed to import. Install TensorFlow to run predictions.")
        if len(image.shape) == 3:
            image = tf.expand_dims(image, axis=0)
        
        predictions = self.model.predict(image, verbose=0)
        predicted_class = np.argmax(predictions[0])
        confidence = np.max(predictions[0])
        
        return predicted_class, confidence
    
    def predict_batch(self, images):
        """Predict for a batch of images"""
        if tf is None:
            raise RuntimeError("TensorFlow is not installed or failed to import. Install TensorFlow to run batch predictions.")
        predictions = self.model.predict(images, verbose=0)
        predicted_classes = np.argmax(predictions, axis=1)
        confidences = np.max(predictions, axis=1)
        
        return predicted_classes, confidences
    
    def save_model(self, filepath):
        """Save the trained model"""
        if tf is None:
            raise RuntimeError("TensorFlow is not installed or failed to import. Install TensorFlow to save the model.")
        self.model.save(filepath)
    
    def load_model(self, filepath):
        """Load a trained model"""
        if tf is None:
            raise RuntimeError("TensorFlow is not installed or failed to import. Install TensorFlow to load a saved model.")
        self.model = tf.keras.models.load_model(filepath)
        return self.model
    
    def get_model_summary(self):
        """Get model summary"""
        return self.model.summary()