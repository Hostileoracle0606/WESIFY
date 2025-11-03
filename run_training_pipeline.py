"""
Complete Training Pipeline
1. Scrapes images for training
2. Organizes them into correct folders
3. Trains the model
4. Exports to TensorFlow.js format
"""

import os
import sys
import subprocess
from pathlib import Path

TRAIN_DIR = "training_data"
CLASSES = ["WES_ANDERSON", "NOT_WES_ANDERSON", "OTHER"]
MIN_IMAGES_PER_CLASS = 30  # Minimum required to start training


def check_prerequisites():
    """Check if all required tools and dependencies are installed"""
    print("Checking prerequisites...")
    
    # Check Python packages
    try:
        import tensorflow as tf
        import numpy as np
        import requests
        print("✓ Python packages installed")
    except ImportError as e:
        print(f"✗ Missing package: {e}")
        print("Run: pip install -r requirements_training.txt")
        return False
    
    # Check if training directories exist
    all_dirs_exist = all(os.path.exists(os.path.join(TRAIN_DIR, c)) for c in CLASSES)
    if not all_dirs_exist:
        print(f"Creating training directories...")
        for class_name in CLASSES:
            os.makedirs(os.path.join(TRAIN_DIR, class_name), exist_ok=True)
        print("✓ Training directories created")
    
    return True


def count_images():
    """Count images in each class directory"""
    counts = {}
    for class_name in CLASSES:
        class_dir = os.path.join(TRAIN_DIR, class_name)
        if os.path.exists(class_dir):
            count = len([f for f in os.listdir(class_dir) 
                        if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            counts[class_name] = count
        else:
            counts[class_name] = 0
    return counts


def scrape_images():
    """Run the image scraper"""
    print("\n" + "="*60)
    print("STEP 1: Scraping Training Images")
    print("="*60)
    
    # Check current image counts
    counts = count_images()
    total = sum(counts.values())
    
    print("\nCurrent image counts:")
    for class_name, count in counts.items():
        print(f"  {class_name}: {count} images")
    print(f"  Total: {total} images")
    
    if total >= MIN_IMAGES_PER_CLASS * len(CLASSES):
        response = input(f"\nYou already have {total} images. Continue scraping? (y/n): ")
        if response.lower() != 'y':
            return True
    
    print("\nStarting image scraper...")
    try:
        result = subprocess.run([sys.executable, "scrape_training_images.py"], 
                              check=False)
        if result.returncode != 0:
            print("⚠ Scraper encountered errors but may have downloaded some images")
    except Exception as e:
        print(f"Error running scraper: {e}")
        return False
    
    # Verify we have minimum images
    new_counts = count_images()
    print("\nUpdated image counts:")
    for class_name, count in new_counts.items():
        print(f"  {class_name}: {count} images")
    
    min_count = min(new_counts.values())
    if min_count < MIN_IMAGES_PER_CLASS:
        print(f"\n⚠ Warning: Minimum recommended is {MIN_IMAGES_PER_CLASS} images per class")
        print("Training will still work but accuracy may be limited.")
        response = input("Continue with training anyway? (y/n): ")
        if response.lower() != 'y':
            return False
    
    return True


def train_model():
    """Run the training script"""
    print("\n" + "="*60)
    print("STEP 2: Training Model")
    print("="*60)
    
    # Verify we have training data
    counts = count_images()
    if sum(counts.values()) == 0:
        print("✗ No training images found. Please run scraper first.")
        return False
    
    print("\nStarting model training...")
    print("This may take a while depending on your hardware and dataset size.")
    print("You can monitor progress above.\n")
    
    try:
        result = subprocess.run([sys.executable, "train_model.py"], check=False)
        if result.returncode == 0:
            print("\n✓ Training completed successfully!")
            return True
        else:
            print("\n✗ Training encountered errors. Check output above.")
            return False
    except Exception as e:
        print(f"Error running training: {e}")
        return False


def export_to_js():
    """Guide user through exporting to TensorFlow.js and updating public folder"""
    print("\n" + "="*60)
    print("STEP 3: Export and Deploy Model")
    print("="*60)
    
    # Check if tfjs_model directory exists
    if not os.path.exists("tfjs_model"):
        print("✗ TensorFlow.js model not found.")
        print("  The training script should create 'tfjs_model/' directory")
        print("  If it exists, ensure tensorflowjs is installed:")
        print("    pip install tensorflowjs")
        return False
    
    print("\nTo deploy the new model:")
    print("1. Copy tfjs_model/model.json to public/model.json")
    print("2. Copy all .bin files from tfjs_model/ to public/")
    print("   (If multiple .bin files, merge them into weights.bin)")
    print("3. Update public/labels.txt if class names changed")
    print("4. Restart your React app")
    
    response = input("\nCopy files automatically? (y/n): ")
    if response.lower() == 'y':
        try:
            import shutil
            
            # Copy model.json
            if os.path.exists("tfjs_model/model.json"):
                shutil.copy("tfjs_model/model.json", "public/model.json")
                print("✓ Copied model.json")
            
            # Handle weights files
            weights_files = [f for f in os.listdir("tfjs_model") if f.endswith('.bin')]
            if len(weights_files) == 1:
                shutil.copy(f"tfjs_model/{weights_files[0]}", "public/weights.bin")
                print(f"✓ Copied {weights_files[0]} to weights.bin")
            elif len(weights_files) > 1:
                print(f"⚠ Found {len(weights_files)} weight files. Manual merge may be needed.")
                print("  Files:", weights_files)
            
            print("\n✓ Model files copied to public/ folder")
            print("\n⚠ Note: If you had multiple .bin files, you may need to merge them.")
            print("   The model.json should reference the correct file names.")
            return True
        except Exception as e:
            print(f"Error copying files: {e}")
            return False
    
    return True


def main():
    print("="*60)
    print("Wes Anderson Classifier - Complete Training Pipeline")
    print("="*60)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n✗ Prerequisites not met. Please install dependencies first.")
        return
    
    # Step 1: Scrape images
    if not scrape_images():
        print("\n✗ Image scraping failed or cancelled.")
        return
    
    # Step 2: Train model
    if not train_model():
        print("\n✗ Model training failed.")
        return
    
    # Step 3: Export guidance
    export_to_js()
    
    print("\n" + "="*60)
    print("PIPELINE COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Test the new model by running: npm start")
    print("2. Evaluate accuracy and collect more data if needed")
    print("3. Repeat training with more images to improve accuracy")


if __name__ == "__main__":
    main()


