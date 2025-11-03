# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed - 2025-01-XX

#### Training Early Stopping at 90% Accuracy
- **Reason**: User requested training to terminate when model reaches approximately 90% accuracy to prevent overfitting and save training time
- **Implementation**:
  - Added `AccuracyThresholdCallback` custom callback that monitors validation accuracy
  - Training automatically stops when validation accuracy reaches 90% (0.90)
  - Prevents unnecessary training epochs and reduces risk of overfitting
  - Configurable via `TARGET_ACCURACY` constant (default: 0.90)
- **Files Changed**:
  - `train_model.py`: Added `TARGET_ACCURACY` configuration and `AccuracyThresholdCallback` class
- **Impact**: 
  - Training stops automatically at optimal accuracy point
  - Reduces training time significantly
  - Prevents overfitting by stopping early
  - Saves computational resources

### Fixed - 2025-01-XX

#### Background Image Path Resolution Error
- **Issue**: CSS file contained hard-coded absolute Windows paths (`C:\Users\Waterloo\...`) which caused module resolution errors during webpack build. CSS files processed by webpack cannot resolve absolute paths to files in the `public/` folder.
- **Error Message**: `Module not found: Error: Can't resolve '/image1.png' in 'C:\Users\Waterloo\wes_anderson_classifier\src'`
- **Solution**: 
  - Removed background image URLs from `src/App.css` (lines 7 and 19)
  - Added inline styles in `src/App.js` using `process.env.PUBLIC_URL` to properly reference public folder assets
  - Background images now set via inline styles which correctly resolve at runtime
- **Files Changed**:
  - `src/App.css` - Removed hard-coded paths, kept other background properties
  - `src/App.js` - Added `backgroundImageUrl` variable and inline styles on `.wes-anderson-app` and `.background-container` divs
- **Impact**: Fixes build errors and ensures background images work in both development and production builds

#### Hard-coded Absolute Paths in CSS
- **Issue**: Background images in `src/App.css` used absolute Windows file system paths that wouldn't work on other machines or in production.
- **Solution**: Changed from absolute paths (`'C:\\Users\\Waterloo\\wes_anderson_classifier\\public\\image1.png'`) to relative paths (`'/image1.png'`) initially, then moved to inline styles for proper webpack compatibility.
- **Files Changed**: `src/App.css`
- **Impact**: Code now works across different development environments and operating systems

#### Invalid TypeScript Import in JavaScript File
- **Issue**: `src/MacBookPro141.js` imported `FunctionComponent` from React, which is a TypeScript type and not valid in JavaScript files.
- **Solution**: Removed `FunctionComponent` from the import statement, keeping only valid JavaScript React imports.
- **Files Changed**: `src/MacBookPro141.js` (line 1)
- **Impact**: Eliminates potential runtime errors and maintains code correctness

#### Labels File Formatting
- **Issue**: `public/labels.txt` contained trailing blank lines which could cause parsing issues when loading labels in the application.
- **Solution**: Removed trailing blank lines, keeping only the three class labels with proper formatting.
- **Files Changed**: `public/labels.txt`
- **Impact**: Ensures labels load correctly without empty entries

### Added - 2025-01-XX

#### Advanced Image Scraping with Multiple APIs
- **Reason**: User requested scraper API integration for Pinterest, Instagram, and other large image databases
- **Added Files**:
  - **scrape_training_images.py**: Advanced multi-API image scraper supporting:
    - **SerpApi** (Google Image Search) - Free tier: 100 searches/month
    - **Bing Image Search API** - Free tier: 3,000 queries/month (generous!)
    - **Apify APIs** (Pinterest & Instagram) - Paid with free credits
    - **Pexels API** - Free unlimited (with rate limits)
    - **pinterest-scrapper** Python package - Free fallback option
    - Automatic API fallback and error handling
    - Multiple search keywords per class for diversity
    - Image validation and size checking
  - **API_KEYS_SETUP.md**: Comprehensive guide for obtaining and setting up API keys
  - **run_training_pipeline.py**: Complete automated pipeline script that:
    - Checks prerequisites
    - Runs image scraping from multiple sources
    - Trains the model
    - Guides model export and deployment
  - **scrape_config.json**: Updated configuration file with multiple API key support
- **Files Changed**:
  - **requirements_training.txt**: Added `requests`, `pinterest-scrapper`, and `beautifulsoup4`
  - **TRAINING_GUIDE.md**: Updated with API-based scraping instructions
- **Impact**: 
  - Accesses large-scale image databases (Google Images, Bing, Pinterest, Instagram)
  - Free tier options available for immediate use
  - Higher quality and more diverse image datasets
  - Better success rate with multiple API fallbacks
  - Professional-grade image collection for training

#### Changelog Documentation
- **Reason**: User requested a changelog to track all changes and their reasons
- **Added Files**:
  - **CHANGELOG.md**: Comprehensive changelog following Keep a Changelog format documenting all fixes, additions, and changes
- **Files Changed**:
  - **README.md**: Added documentation section linking to changelog and other guides
- **Impact**: Provides clear record of project evolution, making it easier to understand changes, track issues, and maintain project history

#### Model Training Documentation and Tools
- **Reason**: User requested ability to train model on more images to increase accuracy. The existing model was created using Teachable Machine, but no training documentation or scripts existed.
- **Added Files**:
  - **TRAINING_GUIDE.md**: Comprehensive guide explaining two training approaches (Teachable Machine vs. Python script)
  - **train_model.py**: Python training script with:
    - Data augmentation (rotation, flipping, brightness adjustments)
    - MobileNetV2 transfer learning architecture
    - Automatic train/validation split
    - Model checkpointing and early stopping
    - TensorFlow.js export capability
    - Learning rate scheduling
  - **requirements_training.txt**: Python dependencies for training (tensorflow, tensorflowjs, etc.)
  - **DATASET_STRUCTURE.md**: Guide for organizing training images with tips on collecting data
- **Files Changed**:
  - **README.md**: Added "Training Your Model" section with quick start instructions
  - **.gitignore**: Added entries to exclude training data and model files from version control
- **Impact**: 
  - Enables users to retrain the model with more data
  - Provides both beginner-friendly (Teachable Machine) and advanced (Python) options
  - Improves model accuracy potential through better training practices
  - Prevents large model/training files from being committed to git

#### Project Documentation Updates
- **Added**: Updated README.md with project description and training instructions
- **Reason**: Original README was generic Create React App template, didn't describe the actual project
- **Impact**: Better project documentation for users and contributors

### Changed - 2025-01-XX

#### README.md Structure
- **Before**: Generic Create React App template documentation
- **After**: 
  - Added project title and description
  - Added training instructions section
  - Maintained original Create React App documentation
- **Reason**: Project-specific documentation needed alongside framework documentation
- **Files Changed**: `README.md`

#### .gitignore Updates
- **Added Exclusions**:
  - `/training_data` - Training image datasets
  - `*.h5`, `*.hdf5` - Keras model files
  - `/tfjs_model` - TensorFlow.js converted models
  - `__pycache__/`, `*.pyc` - Python cache files
  - `venv/`, `env/` - Python virtual environments
- **Reason**: Training artifacts should not be committed to version control
- **Files Changed**: `.gitignore`
- **Impact**: Keeps repository clean and prevents large binary files from being tracked

## [0.1.0] - 2025-01-23 (Initial Project State)

### Notes
- Initial model created using Teachable Machine (version 2.4.10)
- Model uses MobileNet-based architecture
- Three classification classes: WES_ANDERSON, NOT_WES_ANDERSON, OTHER
- Image input size: 224x224 pixels
- React app structure with TensorFlow.js integration

---

## Change Categories

- **Fixed**: Bug fixes and error corrections
- **Added**: New features, files, or functionality
- **Changed**: Modifications to existing functionality
- **Deprecated**: Features that will be removed in future versions
- **Removed**: Features that have been removed
- **Security**: Security vulnerability fixes

---

## Future Improvements to Track

- [ ] Model accuracy improvements after retraining
- [ ] Additional training data collection progress
- [ ] Performance optimizations
- [ ] UI/UX enhancements
- [ ] Additional classification classes (if needed)

