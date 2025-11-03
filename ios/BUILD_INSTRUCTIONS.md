# Build iOS App - Step by Step Guide

## Prerequisites

- **macOS** (required - Xcode only runs on Mac)
- **Xcode 14.0 or later** (download from Mac App Store)
- **CocoaPods** - Install with: `sudo gem install cocoapods`

## Step 1: Create Xcode Project

1. **Open Xcode** (on your Mac)

2. **Create New Project**:
   - File → New → Project
   - Choose **"App"** template (iOS → App)
   - Click **Next**

3. **Configure Project**:
   - **Product Name**: `WesifyApp`
   - **Team**: Select your Apple Developer account (or "None" for simulator only)
   - **Organization Identifier**: `com.wesify` (or your own)
   - **Interface**: **SwiftUI**
   - **Language**: **Swift**
   - **Minimum Deployment**: iOS 15.0
   - **Storage**: Do NOT check "Use Core Data"
   - Click **Next**

4. **Save Location**:
   - Navigate to: `wes_anderson_classifier/ios/WesifyApp/`
   - **Important**: Save it INSIDE the existing `WesifyApp` folder
   - Click **Create**

## Step 2: Replace Xcode Files

After creating the project, replace the default files:

1. **Replace App.swift**:
   - Delete the default `App.swift` in Xcode
   - Right-click `WesifyApp` folder → Add Files to "WesifyApp"
   - Select `ios/WesifyApp/WesifyApp/App.swift`
   - Make sure "Copy items if needed" is UNCHECKED
   - Click **Add**

2. **Add other Swift files**:
   - Add `ContentView.swift`
   - Add `ModelManager.swift`
   - Add `Info.plist` (if needed)

3. **Add Model File**:
   - Right-click `WesifyApp` folder → Add Files to "WesifyApp"
   - Select `ios/WesifyApp/model.tflite`
   - Make sure "Copy items if needed" is CHECKED
   - Make sure "Add to targets: WesifyApp" is CHECKED
   - Click **Add**

## Step 3: Install CocoaPods Dependencies

1. **Open Terminal** (on Mac)

2. **Navigate to project**:
   ```bash
   cd /path/to/wes_anderson_classifier/ios/WesifyApp
   ```

3. **Install CocoaPods** (if not installed):
   ```bash
   sudo gem install cocoapods
   ```

4. **Install dependencies**:
   ```bash
   pod install
   ```

5. **Close Xcode** if it's open

## Step 4: Open Workspace

1. **Open the workspace** (NOT the .xcodeproj):
   ```bash
   open WesifyApp.xcworkspace
   ```
   
   Or double-click `WesifyApp.xcworkspace` in Finder

2. **Important**: Always use `.xcworkspace`, never `.xcodeproj`

## Step 5: Configure Signing

1. In Xcode, select the **WesifyApp** project in the navigator
2. Select the **WesifyApp** target
3. Go to **"Signing & Capabilities"** tab
4. **Team**: Select your Apple Developer account
   - If you don't have one, you can use "None" for simulator-only builds
   - For device testing, you need a free Apple Developer account
5. **Bundle Identifier**: Change if needed (e.g., `com.wesify.app`)

## Step 6: Add Model to Bundle

1. In Xcode, ensure `model.tflite` is in the project navigator
2. Select `model.tflite` in the navigator
3. In the File Inspector (right panel), check:
   - ✅ **Target Membership**: WesifyApp should be checked
   - ✅ **Copy Bundle Resources**: Should be checked

## Step 7: Update ModelManager (Apply 95% Threshold)

The iOS app needs the same 95% confidence threshold. Update `ModelManager.swift`:

In the `classifyImage` method, filter results to only show >= 95% confidence:

```swift
// Only return WES_ANDERSON if confidence >= 95%
if predictedClass == "WES_ANDERSON" && confidence >= 95.0 {
    return (predictedClass, confidence)
} else {
    return nil // Don't show images below 95%
}
```

## Step 8: Build and Run

1. **Select Target**:
   - Choose a simulator (e.g., "iPhone 15 Pro") or connect a physical device
   - For physical device: Connect via USB, trust the computer if prompted

2. **Build**:
   - Press **⌘B** (Cmd+B) or Product → Build

3. **Run**:
   - Press **⌘R** (Cmd+R) or click the Play button
   - The app will build and launch on the simulator/device

## Step 9: Test the App

1. Tap "Select Photos" or camera button
2. Select images from photo library or take photos
3. The app should only display images with >= 95% confidence for WES_ANDERSON

## Troubleshooting

### CocoaPods Issues
```bash
pod repo update
pod install --repo-update
```

### Build Errors
- **Clean Build**: Product → Clean Build Folder (⇧⌘K)
- **Delete Derived Data**: Xcode → Settings → Locations → Derived Data → Delete

### Model Not Found
- Ensure `model.tflite` is in the project
- Check Target Membership includes "WesifyApp"
- Verify the file is in "Copy Bundle Resources" build phase

### Swift Compiler Errors
- Make sure you're using Xcode 14+ (Swift 5.7+)
- Check that all Swift files are added to the target

## Alternative: Quick Setup Script

If you're comfortable with command line, you can also:

1. Create Xcode project via command line
2. Use XcodeGen (third-party tool) to generate project from YAML

But the manual method above is the most reliable.

