"""
Training script for CNN-BiLSTM potato disease detection model
"""

import os
import sys
import json
import argparse
import numpy as np
import tensorflow as tf
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.cnn_bilstm_model import CNNBiLSTMClassifier
from utils.data_loader import PotatoDataLoader


def plot_training_history(history, save_dir):
    """Plot and save training history"""
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    
    # Accuracy
    axes[0, 0].plot(history.history['accuracy'], label='Train', linewidth=2)
    axes[0, 0].plot(history.history['val_accuracy'], label='Validation', linewidth=2)
    axes[0, 0].set_title('Model Accuracy', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Accuracy')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Loss
    axes[0, 1].plot(history.history['loss'], label='Train', linewidth=2)
    axes[0, 1].plot(history.history['val_loss'], label='Validation', linewidth=2)
    axes[0, 1].set_title('Model Loss', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Loss')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Precision
    axes[0, 2].plot(history.history['precision'], label='Train', linewidth=2)
    axes[0, 2].plot(history.history['val_precision'], label='Validation', linewidth=2)
    axes[0, 2].set_title('Model Precision', fontsize=14, fontweight='bold')
    axes[0, 2].set_xlabel('Epoch')
    axes[0, 2].set_ylabel('Precision')
    axes[0, 2].legend()
    axes[0, 2].grid(True, alpha=0.3)
    
    # Recall
    axes[1, 0].plot(history.history['recall'], label='Train', linewidth=2)
    axes[1, 0].plot(history.history['val_recall'], label='Validation', linewidth=2)
    axes[1, 0].set_title('Model Recall', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Epoch')
    axes[1, 0].set_ylabel('Recall')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # AUC
    axes[1, 1].plot(history.history['auc'], label='Train', linewidth=2)
    axes[1, 1].plot(history.history['val_auc'], label='Validation', linewidth=2)
    axes[1, 1].set_title('Model AUC', fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('Epoch')
    axes[1, 1].set_ylabel('AUC')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    # Combined metrics
    axes[1, 2].axis('off')
    metrics_text = f"""
    Final Training Metrics:
    • Accuracy: {history.history['accuracy'][-1]:.4f}
    • Loss: {history.history['loss'][-1]:.4f}
    • Precision: {history.history['precision'][-1]:.4f}
    • Recall: {history.history['recall'][-1]:.4f}
    • AUC: {history.history['auc'][-1]:.4f}
    
    Final Validation Metrics:
    • Accuracy: {history.history['val_accuracy'][-1]:.4f}
    • Loss: {history.history['val_loss'][-1]:.4f}
    • Precision: {history.history['val_precision'][-1]:.4f}
    • Recall: {history.history['val_recall'][-1]:.4f}
    • AUC: {history.history['val_auc'][-1]:.4f}
    """
    axes[1, 2].text(0.1, 0.5, metrics_text, fontsize=10, verticalalignment='center',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    axes[1, 2].axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'training_history.png'), dpi=300, bbox_inches='tight')
    plt.close()


def evaluate_model(model, test_generator, class_names, save_dir):
    """Evaluate model on test set"""
    print("\n" + "="*60)
    print("MODEL EVALUATION")
    print("="*60)
    
    # Get predictions
    test_steps = len(test_generator)
    predictions = model.predict(test_generator, steps=test_steps, verbose=1)
    predicted_classes = np.argmax(predictions, axis=1)
    
    # Get true labels
    true_classes = test_generator.classes[:len(predictions)]
    
    # Generate classification report
    report = classification_report(
        true_classes, 
        predicted_classes,
        target_names=class_names,
        digits=4
    )
    print("\nClassification Report:")
    print(report)
    
    # Generate confusion matrix
    cm = confusion_matrix(true_classes, predicted_classes)
    
    # Plot confusion matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names,
                yticklabels=class_names)
    plt.title('Confusion Matrix', fontsize=16, fontweight='bold')
    plt.xlabel('Predicted', fontsize=12)
    plt.ylabel('True', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'confusion_matrix.png'), dpi=300)
    plt.close()
    
    # Calculate accuracy
    accuracy = np.mean(predicted_classes == true_classes)
    print(f"\nTest Accuracy: {accuracy:.4f}")
    
    return {
        'accuracy': accuracy,
        'classification_report': report,
        'confusion_matrix': cm.tolist()
    }


def save_metrics(history, evaluation_results, save_dir, timestamp):
    """Save all metrics to JSON"""
    metrics = {
        'training': {
            'final_accuracy': float(history.history['accuracy'][-1]),
            'final_val_accuracy': float(history.history['val_accuracy'][-1]),
            'final_loss': float(history.history['loss'][-1]),
            'final_val_loss': float(history.history['val_loss'][-1]),
            'best_val_accuracy': float(max(history.history['val_accuracy'])),
            'best_val_loss': float(min(history.history['val_loss'])),
            'epochs': len(history.history['accuracy'])
        },
        'testing': {
            'accuracy': evaluation_results['accuracy']
        }
    }
    
    with open(os.path.join(save_dir, f'metrics_{timestamp}.json'), 'w') as f:
        json.dump(metrics, f, indent=4)


def main():
    parser = argparse.ArgumentParser(description='Train CNN-BiLSTM model for potato disease detection')
    parser.add_argument('--data_dir', type=str, default='dataset/train', help='Path to training data')
    parser.add_argument('--test_dir', type=str, default='dataset/test', help='Path to test data')
    parser.add_argument('--epochs', type=int, default=50, help='Number of epochs')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size')
    parser.add_argument('--learning_rate', type=float, default=0.0001, help='Learning rate')
    parser.add_argument('--save_dir', type=str, default='saved_models', help='Directory to save models')
    
    args = parser.parse_args()
    
    # Create save directory
    os.makedirs(args.save_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_path = os.path.join(args.save_dir, f'potato_model_{timestamp}.h5')
    best_model_path = os.path.join(args.save_dir, 'best_model.h5')
    
    print("="*60)
    print("POTATO DISEASE DETECTION - CNN-BiLSTM TRAINING")
    print("="*60)
    print(f"Data directory: {args.data_dir}")
    print(f"Test directory: {args.test_dir}")
    print(f"Epochs: {args.epochs}")
    print(f"Batch size: {args.batch_size}")
    print(f"Learning rate: {args.learning_rate}")
    print("="*60)
    
    # Load data
    print("\n📊 Loading data...")
    data_loader = PotatoDataLoader(
        data_dir=args.data_dir,
        batch_size=args.batch_size
    )
    
    train_gen, val_gen = data_loader.get_data_generators(validation_split=0.2)
    test_gen = data_loader.get_test_generator(args.test_dir)
    
    print(f"\nTraining samples: {train_gen.samples}")
    print(f"Validation samples: {val_gen.samples}")
    print(f"Test samples: {test_gen.samples}")
    print(f"Classes: {data_loader.class_names}")
    
    # Build model
    print("\n🏗️ Building CNN-BiLSTM model...")
    model = CNNBiLSTMClassifier(
        num_classes=data_loader.num_classes
    )
    model.build_model()
    model.compile_model(learning_rate=args.learning_rate)
    model.get_model_summary()
    
    # Train model
    print("\n🚀 Training model...")
    history = model.train(
        train_gen,
        val_gen,
        epochs=args.epochs,
        model_save_path=best_model_path
    )
    
    # Save final model
    print("\n💾 Saving final model...")
    model.save_model(model_path)
    
    # Plot training history
    print("\n📈 Plotting training history...")
    plot_training_history(history, args.save_dir)
    
    # Evaluate on test set
    print("\n🧪 Evaluating on test set...")
    evaluation_results = evaluate_model(
        model.model,
        test_gen,
        data_loader.class_names,
        args.save_dir
    )
    
    # Save metrics
    print("\n💾 Saving metrics...")
    save_metrics(history, evaluation_results, args.save_dir, timestamp)
    
    print("\n" + "="*60)
    print("✅ TRAINING COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"Model saved to: {model_path}")
    print(f"Best model saved to: {best_model_path}")
    print(f"Training history saved to: {args.save_dir}/training_history.png")
    print(f"Confusion matrix saved to: {args.save_dir}/confusion_matrix.png")
    print(f"Metrics saved to: {args.save_dir}/metrics_{timestamp}.json")
    print("="*60)


if __name__ == '__main__':
    main()