"""
Evaluation script for Wes Anderson Classifier
Evaluates the trained model and provides detailed accuracy metrics
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import os
from pathlib import Path

# Configuration (must match training script)
IMAGE_SIZE = 224
BATCH_SIZE = 32
TRAIN_DIR = "training_data"
MODEL_PATH = "best_model.h5"

# Class labels (must match training script)
CLASSES = ["WES_ANDERSON", "NOT_WES_ANDERSON", "OTHER"]
NUM_CLASSES = len(CLASSES)

def load_model(model_path):
    """Load the trained model"""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    print(f"Loading model from {model_path}...")
    model = keras.models.load_model(model_path)
    print("[OK] Model loaded successfully")
    return model

def create_validation_generator(train_dir, validation_split=0.2):
    """Create validation data generator"""
    validation_datagen = ImageDataGenerator(
        rescale=1./255,
        validation_split=validation_split
    )
    
    validation_generator = validation_datagen.flow_from_directory(
        train_dir,
        target_size=(IMAGE_SIZE, IMAGE_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation',
        shuffle=False  # Important: don't shuffle for consistent evaluation
    )
    
    return validation_generator

def create_test_generator(train_dir):
    """Create a generator for all data (can be used if we want to evaluate on entire dataset)"""
    test_datagen = ImageDataGenerator(rescale=1./255)
    
    test_generator = test_datagen.flow_from_directory(
        train_dir,
        target_size=(IMAGE_SIZE, IMAGE_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )
    
    return test_generator

def evaluate_model(model, generator, dataset_name="Validation"):
    """Evaluate model and return predictions and true labels"""
    print(f"\n{'='*60}")
    print(f"Evaluating on {dataset_name} Set")
    print(f"{'='*60}")
    
    print(f"Total samples: {generator.samples}")
    print(f"Number of batches: {len(generator)}")
    
    # Reset generator to ensure we start from the beginning
    generator.reset()
    
    # Get predictions
    print("\nGenerating predictions...")
    predictions = model.predict(generator, verbose=1)
    predicted_classes = np.argmax(predictions, axis=1)
    
    # Get true labels
    true_classes = generator.classes
    
    return true_classes, predicted_classes, predictions

def print_detailed_metrics(true_classes, predicted_classes, predictions, class_names):
    """Print detailed classification metrics"""
    print("\n" + "="*60)
    print("DETAILED METRICS")
    print("="*60)
    
    # Overall accuracy
    accuracy = np.mean(true_classes == predicted_classes)
    print(f"\n{'Overall Accuracy:':<30} {accuracy:.2%}")
    print(f"{'Overall Error Rate:':<30} {(1 - accuracy):.2%}")
    
    # Per-class metrics
    print("\n" + "-"*60)
    print("Per-Class Metrics:")
    print("-"*60)
    
    from sklearn.metrics import precision_recall_fscore_support
    
    precision, recall, f1, support = precision_recall_fscore_support(
        true_classes, predicted_classes, labels=range(len(class_names)), zero_division=0
    )
    
    print(f"\n{'Class':<20} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support':<12}")
    print("-"*60)
    for i, class_name in enumerate(class_names):
        print(f"{class_name:<20} {precision[i]:>11.2%} {recall[i]:>11.2%} {f1[i]:>11.2%} {support[i]:>11}")
    
    # Per-class accuracy
    print("\n" + "-"*60)
    print("Per-Class Accuracy:")
    print("-"*60)
    for i, class_name in enumerate(class_names):
        class_mask = true_classes == i
        if np.sum(class_mask) > 0:
            class_accuracy = np.mean(predicted_classes[class_mask] == i)
            print(f"{class_name:<20} {class_accuracy:>11.2%} ({np.sum(predicted_classes[class_mask] == i)}/{np.sum(class_mask)} correct)")
        else:
            print(f"{class_name:<20} {'N/A (no samples)':>30}")
    
    # Classification report
    print("\n" + "="*60)
    print("Classification Report:")
    print("="*60)
    print(classification_report(
        true_classes, 
        predicted_classes, 
        target_names=class_names,
        digits=4
    ))
    
    # Confusion matrix
    print("\n" + "="*60)
    print("Confusion Matrix:")
    print("="*60)
    cm = confusion_matrix(true_classes, predicted_classes)
    
    # Print confusion matrix with labels
    print("\nPredicted ->")
    print(f"{'':<20}", end="")
    for class_name in class_names:
        print(f"{class_name[:15]:<15}", end="")
    print()
    
    for i, class_name in enumerate(class_names):
        print(f"{class_name[:15]:<20}", end="")
        for j in range(len(class_names)):
            print(f"{cm[i, j]:<15}", end="")
        print(f" (Actual: {class_name})")
    
    # Percentages in confusion matrix
    print("\nConfusion Matrix (Percentages):")
    print(f"{'':<20}", end="")
    for class_name in class_names:
        print(f"{class_name[:15]:<15}", end="")
    print()
    
    cm_percent = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100
    for i, class_name in enumerate(class_names):
        print(f"{class_name[:15]:<20}", end="")
        for j in range(len(class_names)):
            print(f"{cm_percent[i, j]:>6.1f}%{'':<8}", end="")
        print()
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'support': support,
        'confusion_matrix': cm
    }

def main():
    """Main evaluation function"""
    print("="*60)
    print("Wes Anderson Classifier - Model Evaluation")
    print("="*60)
    
    # Check if training data directory exists
    if not os.path.exists(TRAIN_DIR):
        print(f"\nERROR: Training data directory '{TRAIN_DIR}' not found!")
        return
    
    # Verify class directories exist
    missing_dirs = []
    for class_name in CLASSES:
        class_dir = os.path.join(TRAIN_DIR, class_name)
        if not os.path.exists(class_dir):
            missing_dirs.append(class_name)
    
    if missing_dirs:
        print(f"\nERROR: Missing class directories: {missing_dirs}")
        return
    
    # Count images per class
    print("\nDataset Summary:")
    total_images = 0
    for class_name in CLASSES:
        class_dir = os.path.join(TRAIN_DIR, class_name)
        image_count = len([f for f in os.listdir(class_dir) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        total_images += image_count
        print(f"  {class_name}: {image_count} images")
    print(f"  Total: {total_images} images")
    
    # Load model
    try:
        model = load_model(MODEL_PATH)
    except Exception as e:
        print(f"\nERROR: Failed to load model: {e}")
        return
    
    # Create validation generator (using same split as training)
    print("\nCreating validation generator...")
    validation_generator = create_validation_generator(TRAIN_DIR, validation_split=0.2)
    
    print(f"Class indices: {validation_generator.class_indices}")
    
    # Evaluate on validation set
    true_classes, predicted_classes, predictions = evaluate_model(
        model, validation_generator, dataset_name="Validation"
    )
    
    # Print detailed metrics
    metrics = print_detailed_metrics(
        true_classes, predicted_classes, predictions, CLASSES
    )
    
    # Summary
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    print(f"Overall Accuracy: {metrics['accuracy']:.2%}")
    print(f"Number of samples evaluated: {len(true_classes)}")
    print(f"Correct predictions: {np.sum(true_classes == predicted_classes)}")
    print(f"Incorrect predictions: {np.sum(true_classes != predicted_classes)}")
    
    print("\n" + "="*60)
    print("Evaluation Complete!")
    print("="*60)

if __name__ == "__main__":
    # Set GPU memory growth (optional, for GPU users)
    try:
        gpus = tf.config.experimental.list_physical_devices('GPU')
        if gpus:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print(f"Using GPU: {gpus[0]}")
    except:
        print("Using CPU")
    
    main()

