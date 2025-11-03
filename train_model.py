"""
Training script for Wes Anderson Image Classifier
This script trains a model to classify images as WES_ANDERSON, NOT_WES_ANDERSON, or OTHER
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import os
import time
from pathlib import Path

# Configuration
IMAGE_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 0.001
TRAIN_DIR = "training_data"  # Directory with subdirectories for each class
TARGET_ACCURACY = 0.90  # Stop training when validation accuracy reaches 90%

# Class labels (must match your folder structure)
CLASSES = ["WES_ANDERSON", "NOT_WES_ANDERSON", "OTHER"]
NUM_CLASSES = len(CLASSES)

def create_data_generators(train_dir, validation_split=0.2):
    """
    Create data generators with augmentation for training and validation
    """
    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        validation_split=validation_split,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        brightness_range=[0.8, 1.2],
        fill_mode='nearest'
    )
    
    # Only rescaling for validation (no augmentation)
    validation_datagen = ImageDataGenerator(
        rescale=1./255,
        validation_split=validation_split
    )
    
    # Training generator
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(IMAGE_SIZE, IMAGE_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training',
        shuffle=True
    )
    
    # Validation generator
    validation_generator = validation_datagen.flow_from_directory(
        train_dir,
        target_size=(IMAGE_SIZE, IMAGE_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation',
        shuffle=False
    )
    
    return train_generator, validation_generator

class AccuracyThresholdCallback(keras.callbacks.Callback):
    """
    Custom callback to stop training when validation accuracy reaches target threshold
    """
    def __init__(self, target_accuracy=0.90, start_time=None):
        super().__init__()
        self.target_accuracy = target_accuracy
        self.start_time = start_time if start_time else time.time()
        self.epoch_times = []
        
    def on_epoch_begin(self, epoch, logs=None):
        self.epoch_start = time.time()
        
    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        val_accuracy = logs.get('val_accuracy', 0)
        epoch_time = time.time() - self.epoch_start
        self.epoch_times.append(epoch_time)
        total_time = time.time() - self.start_time
        
        avg_epoch_time = np.mean(self.epoch_times) if self.epoch_times else epoch_time
        
        # Estimate remaining epochs based on accuracy improvement rate
        if hasattr(self, 'prev_val_acc') and self.prev_val_acc > 0:
            acc_improvement_rate = max(0.001, (val_accuracy - self.prev_val_acc))
            accuracy_gap = self.target_accuracy - val_accuracy
            epochs_remaining_estimate = max(1, int(accuracy_gap / acc_improvement_rate))
        else:
            epochs_remaining_estimate = 15  # Default estimate
        
        self.prev_val_acc = val_accuracy
        estimated_remaining = avg_epoch_time * epochs_remaining_estimate
        
        print(f"\n[Epoch {epoch + 1}] Validation Accuracy: {val_accuracy:.2%} | "
              f"Epoch Time: {epoch_time:.1f}s | "
              f"Total Time: {total_time/60:.1f}min | "
              f"Est. Remaining: ~{estimated_remaining/60:.1f}min")
        
        if val_accuracy >= self.target_accuracy:
            print(f"\n[SUCCESS] Target accuracy of {self.target_accuracy:.0%} reached!")
            print(f"Validation accuracy: {val_accuracy:.2%} (epoch {epoch + 1})")
            print(f"Total training time: {total_time/60:.1f} minutes")
            print("Stopping training early to prevent overfitting.")
            self.model.stop_training = True

def create_model(fine_tune=False):
    """
    Create a MobileNetV2-based model (similar to Teachable Machine)
    If fine_tune=True, unfreezes last layers for fine-tuning
    """
    # Load pre-trained MobileNetV2 as base
    base_model = keras.applications.MobileNetV2(
        input_shape=(IMAGE_SIZE, IMAGE_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )
    
    if fine_tune:
        # Unfreeze the top layers for fine-tuning
        base_model.trainable = True
        # Freeze bottom layers, keep top layers trainable
        for layer in base_model.layers[:-30]:  # Freeze all but last 30 layers
            layer.trainable = False
        print("[INFO] Fine-tuning enabled: Last 30 layers are trainable")
    else:
        # Freeze base model layers initially
        base_model.trainable = False
        print("[INFO] Transfer learning: Base model frozen")
    
    # Add custom classification head
    model = keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(NUM_CLASSES, activation='softmax')
    ])
    
    # Use lower learning rate for fine-tuning
    lr = LEARNING_RATE / 10 if fine_tune else LEARNING_RATE
    
    # Compile model
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=lr),
        loss='categorical_crossentropy',
        metrics=['accuracy', 'top_k_categorical_accuracy']
    )
    
    return model

def train_model():
    """
    Main training function
    """
    print("=" * 50)
    print("Wes Anderson Classifier Training")
    print("=" * 50)
    
    # Check if training data directory exists
    if not os.path.exists(TRAIN_DIR):
        print(f"ERROR: Training data directory '{TRAIN_DIR}' not found!")
        print(f"\nPlease create the following structure:")
        print(f"{TRAIN_DIR}/")
        for class_name in CLASSES:
            print(f"  {class_name}/")
            print(f"    (put training images here)")
        return
    
    # Verify class directories exist
    missing_dirs = []
    for class_name in CLASSES:
        class_dir = os.path.join(TRAIN_DIR, class_name)
        if not os.path.exists(class_dir):
            missing_dirs.append(class_name)
    
    if missing_dirs:
        print(f"ERROR: Missing class directories: {missing_dirs}")
        return
    
    # Count images per class
    print("\nTraining Data Summary:")
    total_images = 0
    for class_name in CLASSES:
        class_dir = os.path.join(TRAIN_DIR, class_name)
        image_count = len([f for f in os.listdir(class_dir) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        total_images += image_count
        print(f"  {class_name}: {image_count} images")
    print(f"  Total: {total_images} images")
    
    if total_images < 30:
        print("\nWARNING: Very few training images. Consider collecting more data for better accuracy.")
    
    # Create data generators
    print("\nCreating data generators...")
    train_gen, val_gen = create_data_generators(TRAIN_DIR)
    
    print(f"\nTraining samples: {train_gen.samples}")
    print(f"Validation samples: {val_gen.samples}")
    
    # Start time tracking
    training_start_time = time.time()
    
    # PHASE 1: Initial training with frozen base model
    print("\n" + "=" * 50)
    print("PHASE 1: Initial Training (Frozen Base)")
    print("=" * 50)
    
    print("\nCreating model...")
    model = create_model(fine_tune=False)
    model.summary()
    
    # Callbacks for Phase 1
    phase1_start_time = time.time()
    phase1_callbacks = [
        AccuracyThresholdCallback(target_accuracy=TARGET_ACCURACY, start_time=training_start_time),
        keras.callbacks.ModelCheckpoint(
            'best_model.h5',
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=15,  # More patience for initial training
            restore_best_weights=True,
            verbose=1,
            min_delta=0.001
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=0.00001,
            verbose=1
        )
    ]
    
    print(f"\nTraining will stop when validation accuracy reaches {TARGET_ACCURACY:.0%}")
    print("\n[Phase 1] Starting initial training with frozen base model...")
    print("Estimated time per epoch: 15-30 seconds (CPU) or 2-5 seconds (GPU)")
    print("Estimated total time to 90%: 10-30 minutes (varies by hardware)\n")
    
    history1 = model.fit(
        train_gen,
        epochs=EPOCHS,
        validation_data=val_gen,
        callbacks=phase1_callbacks,
        verbose=1
    )
    
    # Check if we reached target accuracy
    best_val_acc = max(history1.history.get('val_accuracy', [0]))
    
    if best_val_acc >= TARGET_ACCURACY:
        print(f"\n[SUCCESS] Target accuracy reached in Phase 1!")
        final_history = history1.history
    else:
        print(f"\n[Phase 1 Complete] Best validation accuracy: {best_val_acc:.2%}")
        print(f"Proceeding to Phase 2: Fine-tuning for higher accuracy...")
        
        # PHASE 2: Fine-tuning with unfrozen layers
        print("\n" + "=" * 50)
        print("PHASE 2: Fine-Tuning (Unfrozen Layers)")
        print("=" * 50)
        
        print("\nCreating fine-tuning model...")
        model_finetune = create_model(fine_tune=True)
        
        # Copy weights from Phase 1
        model_finetune.set_weights(model.get_weights())
        
        phase2_callbacks = [
            AccuracyThresholdCallback(target_accuracy=TARGET_ACCURACY, start_time=training_start_time),
            keras.callbacks.ModelCheckpoint(
                'best_model.h5',
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            ),
            keras.callbacks.EarlyStopping(
                monitor='val_accuracy',
                patience=10,
                restore_best_weights=True,
                verbose=1,
                min_delta=0.001
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=3,
                min_lr=0.00001,
                verbose=1
            )
        ]
        
        print("[Phase 2] Fine-tuning with lower learning rate...")
        print("Estimated time per epoch: 30-60 seconds (CPU) or 3-8 seconds (GPU)")
        print("Estimated remaining time: 5-20 minutes\n")
        
        history2 = model_finetune.fit(
            train_gen,
            epochs=EPOCHS,
            validation_data=val_gen,
            callbacks=phase2_callbacks,
            verbose=1,
            initial_epoch=len(history1.history.get('accuracy', []))
        )
        
        model = model_finetune
        # Combine histories
        final_history = {
            'accuracy': history1.history.get('accuracy', []) + history2.history.get('accuracy', []),
            'val_accuracy': history1.history.get('val_accuracy', []) + history2.history.get('val_accuracy', []),
            'loss': history1.history.get('loss', []) + history2.history.get('loss', []),
            'val_loss': history1.history.get('val_loss', []) + history2.history.get('val_loss', [])
        }
        
        final_val_acc = max(history2.history.get('val_accuracy', [0]))
        if final_val_acc >= TARGET_ACCURACY:
            print(f"\n[SUCCESS] Target accuracy reached in Phase 2!")
        else:
            print(f"\n[Note] Final accuracy: {final_val_acc:.2%} (target: {TARGET_ACCURACY:.0%})")
            print("Consider: adding more training data, adjusting hyperparameters, or training for more epochs")
    
    total_training_time = time.time() - training_start_time
    print(f"\nTotal training time: {total_training_time/60:.1f} minutes ({total_training_time:.1f} seconds)")
    
    print("\n" + "=" * 50)
    print("Training completed!")
    print("=" * 50)
    
    # Evaluate model
    print("\nEvaluating on validation set...")
    val_loss, val_accuracy, val_top_k = model.evaluate(val_gen, verbose=1)
    print(f"\nValidation Accuracy: {val_accuracy:.2%}")
    print(f"Validation Top-K Accuracy: {val_top_k:.2%}")
    
    # Save final model
    print("\nSaving final model...")
    model.save('final_model.h5')
    
    # Convert to TensorFlow.js format
    print("\nConverting to TensorFlow.js format...")
    try:
        import tensorflowjs as tfjs
        tfjs.converters.save_keras_model(model, 'tfjs_model')
        print("TensorFlow.js model saved to 'tfjs_model/' directory")
        print("\nNext steps:")
        print("1. Copy 'tfjs_model/model.json' to 'public/model.json'")
        print("2. Copy 'tfjs_model/*.bin' files to 'public/weights.bin' (may need to merge)")
        print("3. Update 'public/labels.txt' with your class names")
    except ImportError:
        print("WARNING: tensorflowjs not installed. Install it with: pip install tensorflowjs")
        print("Then run: tensorflowjs_converter --input_format keras final_model.h5 tfjs_model")
    
    return model, final_history

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
    
    train_model()

