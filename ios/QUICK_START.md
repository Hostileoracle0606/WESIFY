# Quick Start: Build iOS App

## Prerequisites (Mac Only)

1. **macOS** - Xcode only runs on Mac
2. **Xcode 14+** - Download from Mac App Store (free)
3. **CocoaPods** - Install: `sudo gem install cocoapods`

## Steps

### 1. Create Xcode Project

1. Open **Xcode**
2. **File → New → Project**
3. Choose **"App"** (iOS tab)
4. Configure:
   - **Product Name**: `WesifyApp`
   - **Interface**: **SwiftUI**
   - **Language**: **Swift**
   - **Minimum Deployment**: iOS 15.0
5. Click **Next**
6. **Save inside**: `ios/WesifyApp/` folder
7. Click **Create**

### 2. Replace Default Files

1. **Delete** the default `ContentView.swift` Xcode created
2. **Add existing files**:
   - Right-click `WesifyApp` folder → **Add Files to "WesifyApp"**
   - Select these files (one at a time):
     - `ios/WesifyApp/WesifyApp/App.swift`
     - `ios/WesifyApp/WesifyApp/ContentView.swift`
     - `ios/WesifyApp/WesifyApp/ModelManager.swift`
     - `ios/WesifyApp/WesifyApp/Info.plist`
   - **Important**: Uncheck "Copy items if needed" (they're already in the right place)
   - Check "Add to targets: WesifyApp"
   - Click **Add**

### 3. Add Model File

1. Right-click `WesifyApp` folder → **Add Files to "WesifyApp"**
2. Select `ios/WesifyApp/model.tflite`
3. **Check**: "Copy items if needed"
4. **Check**: "Add to targets: WesifyApp"
5. Click **Add**

### 4. Install Dependencies

1. **Open Terminal** (on Mac)
2. Navigate to project:
   ```bash
   cd /path/to/wes_anderson_classifier/ios/WesifyApp
   ```
3. Install CocoaPods (if not installed):
   ```bash
   sudo gem install cocoapods
   ```
4. Install dependencies:
   ```bash
   pod install
   ```

### 5. Open Workspace

1. **Close Xcode** if open
2. Open the **workspace** (NOT .xcodeproj):
   ```bash
   open WesifyApp.xcworkspace
   ```
   
   Or double-click `WesifyApp.xcworkspace` in Finder

### 6. Configure Signing

1. In Xcode, select **WesifyApp** project (blue icon)
2. Select **WesifyApp** target
3. Go to **"Signing & Capabilities"** tab
4. **Team**: Select your Apple ID (or "None" for simulator only)
5. Xcode will auto-generate bundle identifier

### 7. Build & Run

1. **Select device**: Choose iPhone simulator (e.g., "iPhone 15 Pro")
2. **Build**: Press **⌘B** (Cmd+B)
3. **Run**: Press **⌘R** (Cmd+R) or click ▶️ Play button

## Result

The app will:
- ✅ Load the TensorFlow Lite model
- ✅ Allow photo selection from library
- ✅ Allow camera capture
- ✅ Only display images with >= 95% confidence for WES_ANDERSON

## Troubleshooting

**"pod install" fails?**
```bash
pod repo update
pod install --repo-update
```

**Model not found?**
- Check `model.tflite` is in project navigator
- Verify Target Membership includes "WesifyApp"
- Check "Copy Bundle Resources" build phase

**Build errors?**
- Clean: Product → Clean Build Folder (⇧⌘K)
- Delete Derived Data: Xcode → Settings → Locations → Delete Derived Data

**Need help?** See `ios/BUILD_INSTRUCTIONS.md` for detailed guide.

