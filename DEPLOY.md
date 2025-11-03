# Deploy Wesify to wesify.digital

## Quick Deploy Options

### Option 1: Netlify (Recommended - Easiest)

1. **Go to [netlify.com](https://www.netlify.com)** and sign in with GitHub

2. **Click "Add new site" → "Import an existing project"**

3. **Select your GitHub repository**: `Hostileoracle0606/WESIFY`

4. **Build settings** (auto-detected from `netlify.toml`):
   - Build command: `npm run build`
   - Publish directory: `build`
   - Node version: `18`

5. **Click "Deploy site"** - Netlify will build and deploy automatically

6. **Add custom domain**:
   - Go to Site settings → Domain management
   - Click "Add custom domain"
   - Enter: `wesify.digital`
   - Follow DNS setup instructions:
     - Add a CNAME record: `wesify.digital` → `your-site.netlify.app`
     - Or add A record pointing to Netlify's IP (instructions shown)

7. **Enable HTTPS** (automatic with Netlify)

### Option 2: Vercel

1. **Go to [vercel.com](https://vercel.com)** and sign in with GitHub

2. **Click "Add New Project"**

3. **Import repository**: `Hostileoracle0606/WESIFY`

4. **Configure** (auto-detected from `vercel.json`):
   - Framework: Create React App
   - Build Command: `npm run build`
   - Output Directory: `build`

5. **Deploy** - Vercel will build and deploy automatically

6. **Add domain**:
   - Go to Project Settings → Domains
   - Add `wesify.digital`
   - Configure DNS as instructed

## Automatic Deployment

Both Netlify and Vercel will automatically deploy on every push to `main` branch.

## Manual Deployment (Alternative)

If you have your own server:

1. Build the app: `npm run build`
2. Upload `build/` folder contents to your web server
3. Configure DNS: Point `wesify.digital` to your server IP
4. Set up HTTPS with Let's Encrypt

## Verify Deployment

After deployment, check:
- ✅ Site loads at https://wesify.digital
- ✅ Image upload works
- ✅ Model files load (model.json, weights.bin)
- ✅ Classification works correctly
- ✅ Mobile responsive

