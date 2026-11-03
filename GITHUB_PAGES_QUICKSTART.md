# GitHub Pages Deployment Quick Start

This guide walks you through hosting the Closet Organizer frontend on GitHub Pages with the backend API on a separate server.

## What You'll End Up With

```
┌─────────────────────────────────────────────────────────┐
│            Your GitHub Pages Site                        │
│  https://username.github.io/closet-organizer            │
│              (Vue.js Frontend - Static)                  │
│  • Auto-deploys on every git push                        │
│  • Free hosting from GitHub                              │
│  • Global CDN distribution                               │
└──────────────────────┬──────────────────────────────────┘
                       │
                 API Calls to
                       │
┌──────────────────────▼──────────────────────────────────┐
│         Your Backend API Server                          │
│  https://api.yourdomain.com or                           │
│  https://closet-api.railway.app  (hosted elsewhere)      │
│              (Python FastAPI)                            │
│  • Reads/writes Google Sheets                            │
│  • Serves static JSON data                               │
│  • ~$5-10/month or free tier                             │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites

- GitHub account with this repository
- Node.js 18+ installed locally
- Python 3.9+ (for testing backend locally)
- One of: Railway, Render, Heroku, or AWS account (optional, for backend hosting)

## Step 1: Configure Frontend for GitHub Pages

### 1.1 Check Repository Name

GitHub Pages URLs are: `https://username.github.io/repo-name/`

If your repository is **not** named `closet-organizer`, update `vite.config.js`:

```javascript
// frontend/vite.config.js
base: process.env.NODE_ENV === 'production' ? '/your-repo-name/' : '/',
```

### 1.2 Build Locally to Test

```bash
cd frontend
npm install
npm run build
```

Check that `frontend/dist/` folder is created with all assets.

## Step 2: Set Up GitHub Actions Workflow

The repository already includes `.github/workflows/deploy-frontend.yml` that:
- Runs on every push to `main` branch
- Installs Node dependencies
- Builds the frontend
- Deploys to GitHub Pages

**No additional setup needed!** The workflow is ready to go.

### (Optional) Configure Repository Settings

1. Go to repository **Settings** → **Pages**
2. Source should be: **GitHub Actions** (default)
3. Verify your domain is correct

## Step 3: Deploy Backend API

Choose one of these quick options:

### Option A: Railway.app (Recommended - 5 minutes)

1. **Login**: https://railway.app → "Login with GitHub"
2. **Create Project** → "Deploy from GitHub repo"
3. **Select Repository**: `closet-organizer`
4. **Set Environment Variables**:
   ```
   CORS_ORIGINS=https://username.github.io/closet-organizer
   ```
5. **Click Deploy** → Done! (Takes 2-3 minutes)

Your API URL will be something like: `https://closet-organizer-api.railway.app`

### Option B: Render.com (10 minutes, includes free tier)

1. **Login**: https://render.com → "Sign up with GitHub"
2. **New Web Service** → Select `closet-organizer` repository
3. **Configure**:
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Add Environment Variable**: `CORS_ORIGINS=https://username.github.io/closet-organizer`
5. **Click "Create Web Service"** → Done!

Your API URL will be: `https://closet-organizer-api.onrender.com` (or similar)

### Option C: Self-Hosted (SSH to VPS)

See [BACKEND_DEPLOYMENT.md](./BACKEND_DEPLOYMENT.md) → AWS Lightsail section

### Option D: Heroku (Requires CLI)

See [BACKEND_DEPLOYMENT.md](./BACKEND_DEPLOYMENT.md) → Heroku section

## Step 4: Update Frontend with API URL

Now that you have your API URL, update the frontend to use it.

### Method 1: Update Environment Variable (Recommended)

1. Create `frontend/.env.production`:
   ```
   VITE_API_BASE_URL=https://your-api-url.com/api
   ```

2. Commit and push:
   ```bash
   git add frontend/.env.production
   git commit -m "Configure production API URL"
   git push origin main
   ```

3. GitHub Actions automatically rebuilds and deploys

### Method 2: Update API Configuration (Alternative)

Edit `frontend/src/api.js` and change the API URL directly:

```javascript
const getApiBaseUrl = () => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }
  if (import.meta.env.DEV) {
    return '/api'  // Dev server proxy
  }
  return 'https://your-api-url.com/api'  // Production
}
```

## Step 5: Test Everything

### 5.1 Test Frontend Deployment

1. Visit: `https://username.github.io/closet-organizer`
2. You should see the Closet Organizer dashboard
3. Check browser console for any errors (F12 → Console tab)

### 5.2 Test API Connection

In browser console, run:

```javascript
fetch('https://your-api-url.com/api/health')
  .then(r => r.json())
  .then(d => console.log('API healthy:', d))
  .catch(e => console.error('API error:', e))
```

Should print: `API healthy: { status: "ok" }`

### 5.3 Test Full Features

1. **Dashboard**: Should load closets, shelves, baskets
2. **Family**: Should show family members from JSON
3. **First Aid**: Should show kits and items
4. **Cleaning**: Should show room checklists
5. **Inventory**: Should attempt to load from Google Sheets (may show placeholder data if sheets not configured)

## Step 6: Set Up Google Sheets (Optional)

For inventory and reminders to work:

1. Create Google Sheets for inventory and reminders
2. Generate OAuth credentials from Google Cloud Console
3. Set environment variables in backend:
   ```
   GOOGLE_SHEETS_CREDENTIALS_JSON=<your_credentials>
   INVENTORY_SHEET_ID=<sheet_id>
   REMINDERS_SHEET_ID=<sheet_id>
   ```
4. Redeploy backend

See [ARCHITECTURE.md](./ARCHITECTURE.md) → Google Sheets Setup for details.

## Troubleshooting

### Frontend deploys but shows 404

- Check that base path in `vite.config.js` matches repository name
- Try clearing browser cache (Ctrl+Shift+Delete)
- Check GitHub Actions workflow succeeded: Settings → Actions

### API calls fail with CORS error

Error: `"Access to XMLHttpRequest blocked by CORS policy"`

Solution: Backend's `CORS_ORIGINS` must include your GitHub Pages URL:
```
CORS_ORIGINS=https://username.github.io/closet-organizer
```

Then redeploy backend.

### API returns 404

- Verify backend is running: `curl https://your-api-url.com/api/health`
- Check API URL is correct in frontend
- Verify base path doesn't have extra slashes: `/api` not `/api/`

### GitHub Actions workflow not triggering

- Check workflow file exists: `.github/workflows/deploy-frontend.yml`
- Go to Actions tab, check if last workflow passed
- Try force-push: `git commit --allow-empty -m "Trigger deploy" && git push`

## Environment Variables Reference

### Frontend (.env.production)
```
VITE_API_BASE_URL=https://your-api-url.com/api
VITE_ENV=production
```

### Backend (.env)
```
CORS_ORIGINS=https://username.github.io/closet-organizer
GOOGLE_SHEETS_CREDENTIALS_JSON=<credentials_json>
INVENTORY_SHEET_ID=<sheet_id>
REMINDERS_SHEET_ID=<sheet_id>
```

## Next Steps

1. ✓ Frontend deployed on GitHub Pages
2. ✓ Backend API deployed on external server
3. ⏳ Set up Google Sheets for inventory/reminders (optional)
4. ⏳ Share URL with family members
5. ⏳ Customize JSON data for your home

## Support

- See [GITHUB_PAGES_DEPLOYMENT.md](./GITHUB_PAGES_DEPLOYMENT.md) for detailed info
- See [BACKEND_DEPLOYMENT.md](./BACKEND_DEPLOYMENT.md) for all backend options
- See [ARCHITECTURE.md](./ARCHITECTURE.md) for complete reference

## Cost Breakdown

| Component | Cost |
|-----------|------|
| GitHub Pages (frontend) | **FREE** |
| Railway Backend | ~$5-20/month |
| Render Backend | ~$7-15/month |
| AWS Lightsail | ~$3.50-10/month |
| Domain name (optional) | ~$10/year |
| **TOTAL** | **~$5-20/month** |

Much cheaper than the original database + MQTT setup!

---

**Happy organizing! 🏠✨**
