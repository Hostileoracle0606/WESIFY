# Wesify

A web application that classifies images to detect if they match Wes Anderson's distinctive aesthetic style using TensorFlow.js.

## Web App

### Development

```bash
# Install dependencies
npm install

# Run development server
npm start

# Build for production
npm run build
```

### Deployment

The app is pre-configured for deployment:

- **Netlify**: Automatically detects `netlify.toml`
- **Vercel**: Automatically detects `vercel.json`
- **Static hosting**: Uses `_redirects` for SPA routing

Domain: `wesify.digital`

## iOS App

See `ios/README.md` for iOS app setup and build instructions.

## Project Structure

```
├── src/          # React web app source code
├── public/       # Static assets and model files (model.json, weights.bin, labels.txt)
├── ios/          # iOS app (Swift + TensorFlow Lite)
├── netlify.toml  # Netlify deployment configuration
├── vercel.json   # Vercel deployment configuration
└── _redirects    # Static hosting SPA redirects
```

## Requirements

- **Web**: Node.js 16+
- **iOS**: Xcode 14+, CocoaPods

Built with React, TensorFlow.js (web) and TensorFlow Lite (iOS).
