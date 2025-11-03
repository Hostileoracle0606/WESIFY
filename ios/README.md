# Wesify iOS App

iOS version of the Wes Anderson image classifier built with SwiftUI and TensorFlow Lite.

## Prerequisites

- macOS with Xcode 14.0 or later
- iOS 15.0+ device or simulator
- CocoaPods (`sudo gem install cocoapods`)

## Setup Instructions

### Step 1: Install Dependencies

```bash
cd ios/WesifyApp
pod install
```

### Step 2: Open in Xcode

```bash
open WesifyApp.xcworkspace
```

**Important**: Open the `.xcworkspace` file, not the `.xcodeproj` file.

### Step 3: Configure Signing

1. Select the `WesifyApp` target
2. Go to "Signing & Capabilities"
3. Select your development team
4. Xcode will automatically manage provisioning profiles

### Step 4: Build and Run

1. Select your target device or simulator
2. Press ⌘R or click the Run button
3. The app will build and launch

## Project Structure

```
WesifyApp/
├── WesifyApp/
│   ├── App.swift           # Main app entry point
│   ├── ContentView.swift   # Main UI view
│   ├── ModelManager.swift  # TensorFlow Lite model handler
│   └── Info.plist          # App configuration
├── model.tflite            # TensorFlow Lite model file
├── Podfile                 # CocoaPods dependencies
└── WesifyApp.xcworkspace   # Xcode workspace (use this to open)
```

## Features

- 📸 Select multiple images from photo library
- 📷 Take photos with camera
- 🤖 Real-time image classification using TensorFlow Lite
- 🎨 Wes Anderson-inspired UI design
- ✨ Shows only images classified as Wes Anderson style

## Model

The TensorFlow Lite model (`model.tflite`) is already included. It classifies images into:
- `WES_ANDERSON` - Images matching Wes Anderson aesthetic
- `NOT_WES_ANDERSON` - Regular images
- `OTHER` - Other aesthetic styles

## Troubleshooting

### CocoaPods Issues

If `pod install` fails:
```bash
pod repo update
pod install --repo-update
```

### Model Not Loading

- Ensure `model.tflite` is in the `WesifyApp` directory
- Check that the file is included in the Xcode project bundle
- Verify Info.plist has proper permissions for file access

### Build Errors

- Clean build folder: Product → Clean Build Folder (⇧⌘K)
- Delete derived data: Xcode → Preferences → Locations → Derived Data
