"""
Quick script to check scraping progress
"""

import os

TRAIN_DIR = "training_data"
CLASSES = ["WES_ANDERSON", "NOT_WES_ANDERSON", "OTHER"]

print("="*60)
print("Scraping Progress Check")
print("="*60)

total = 0
for class_name in CLASSES:
    class_dir = os.path.join(TRAIN_DIR, class_name)
    if os.path.exists(class_dir):
        count = len([f for f in os.listdir(class_dir) 
                    if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        total += count
        status = "[OK]" if count >= 30 else "[NEEDS MORE]"
        print(f"{status} {class_name}: {count} images")
    else:
        print(f"[NO DIR] {class_name}: 0 images")

print(f"\nTotal: {total} images")
target = 90  # Minimum 30 per class
if total >= target:
    print("\n[READY] Enough images to start training!")
    print("Next step: python train_model.py")
else:
    print(f"\n[WAIT] Need at least {target} images total (30 per class)")
    print("Scraper is still running...")


