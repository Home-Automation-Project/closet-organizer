# Closet Organizer

A completely **free** home organization web app hosted on **GitHub Pages**. Track what's in your closets — bedding (with wash reminders), cleaning supplies (with room checklists), and first aid kits (basic and advanced).

**No backend. No database. No servers to manage. Just GitHub + Google Sheets.**

## Quick Overview

- 📦 **Static data** (closets, family, first aid, cleaning) stored as JSON in Git
- 📊 **Dynamic data** (inventory, reminders) stored in Google Sheets
- 🌐 **Hosted free** on GitHub Pages
- 🔐 **Secure** — direct browser auth with Google
- 📱 **Mobile friendly** — Vue.js web app
- ⚡ **Instant updates** — no server cache
- 👥 **Multi-user** — shared Google Sheets access

## Features

✓ Visual dashboard — closets → shelves → baskets  
✓ Inventory tracking with quantity & expiration dates  
✓ Wash reminders & seasonal reminders  
✓ Cleaning checklists by room and frequency  
✓ First aid reference (basic & advanced kits)  
✓ Family medical information  
✓ Version-controlled data in Git  
✓ Real-time Google Sheets sync  

## Cost: **$0/month** 🎉

| Component | Cost |
|-----------|------|
| GitHub Pages hosting | FREE |
| GitHub Actions CI/CD | FREE |
| Google Sheets | FREE |
| Domain (optional) | ~$10/yr |

## Project Structure

```
closet-organizer/
├── README.md                    # This file
├── GOOGLE_SHEETS_SETUP.md       # How to set up Google Sheets
├── data/
│   └── json/                    # Static data files
│       ├── closets.json         # Closet structure
│       ├── family.json          # Family members
│       ├── firstaid.json        # First aid kits
│       └── cleaning.json        # Cleaning schedules
├── .github/
│   └── workflows/
│       └── deploy-frontend.yml  # Auto-deploy to GitHub Pages
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.js
        ├── api.js               # Data loading + Google Sheets client
        ├── services/
        │   └── gsheets.js       # Google Sheets API wrapper
        ├── components/          # Vue components
        ├── views/               # Page views
        ├── stores/              # Pinia state
        └── router/              # Vue Router
```

## Getting Started (5 Steps)

### Step 1: Fork Repository

```bash
git clone https://github.com/Home-Automation-Project/closet-organizer.git
cd closet-organizer
```

### Step 2: Update Base Path (if needed)

If your repository is **NOT** named `closet-organizer`, edit `frontend/vite.config.js`:

```javascript
base: '/your-actual-repo-name/',
```

### Step 3: Set Up Google Sheets

Follow the comprehensive guide: **[GOOGLE_SHEETS_SETUP.md](./GOOGLE_SHEETS_SETUP.md)**

Takes ~15 minutes:
1. Create Google Cloud project
2. Enable Sheets API
3. Generate OAuth credentials
4. Create two Google Sheets (inventory & reminders)
5. Note your credentials and Sheet IDs

### Step 4: Add GitHub Secrets

In your GitHub repository:

1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret" for each:
   - `VITE_GOOGLE_CLIENT_ID` (from Google Cloud)
   - `VITE_GOOGLE_API_KEY` (from Google Cloud)
   - `VITE_INVENTORY_SHEET_ID` (from Google Sheets URL)
   - `VITE_REMINDERS_SHEET_ID` (from Google Sheets URL)

### Step 5: Deploy

```bash
git add .
git commit -m "Add Google Sheets credentials"
git push origin main
```

GitHub Actions automatically deploys! Your site will be live at:

```
https://YOUR_USERNAME.github.io/closet-organizer/
```

(Replace `YOUR_USERNAME` with your GitHub username)

## How It Works

1. **Static data** (JSON files) is bundled at build time
   - Stored in Git for version control
   - Changes require a commit and push
   - Automatically deployed to GitHub Pages
   - Loaded once when app starts

2. **Dynamic data** (inventory & reminders) from Google Sheets
   - Accessed directly by browser
   - User authenticates with Google OAuth
   - Real-time read/write to Sheets
   - No server needed

3. **Deployment** is automatic
   - Push to GitHub → GitHub Actions builds
   - Vite bundles frontend + JSON data
   - Deployed to GitHub Pages in ~2 minutes
   - Works globally via CDN

## Local Development

```bash
cd frontend
npm install
npm run dev
```

Visit: http://localhost:5173

**Note**: Inventory & reminders need Google Sheets config to work. Static data (closets, cleaning, first aid) works without setup.

## Modifying Static Data

Edit JSON files in `data/json/`:

- **`closets.json`** — Define your closet structure (shelves & baskets)
- **`family.json`** — Add family members and medical info
- **`firstaid.json`** — First aid kit definitions (usually unchanged)
- **`cleaning.json`** — Room checklists and tasks

Then:
```bash
git add data/json/
git commit -m "Update closet data"
git push origin main
```

GitHub Actions redeploys automatically (~2 min). Hard refresh browser to see changes.

## Using Google Sheets

### Editing Inventory

**From the app:**
1. Click a basket
2. Click "Edit Inventory"
3. Add/edit items
4. Changes saved to Google Sheets

**From Google Sheets directly:**
1. Open your Inventory sheet
2. Add/edit/delete rows
3. Refresh the app to see changes

### Editing Reminders

**From the app:**
1. Go to Reminders section
2. Create new reminder
3. Saved to Google Sheets

**From Google Sheets directly:**
1. Open your Reminders sheet
2. Add new row with reminder details
3. Refresh app to see it

## Sheet Structure

### Inventory Sheet

| Basket ID | Item Name | Quantity | Expiration Date | Notes |
|-----------|-----------|----------|-----------------|-------|
| basket_1  | Sheets    | 10       | 2026-06-01      | 1000ct |
| basket_1  | Pillows   | 2        | 2026-12-31      | Down |

### Reminders Sheet

| ID | Category | Text | Due Date | Acknowledged |
|----|----------|------|----------|--------------|
| 1  | WASH     | Wash sheets | 2026-06-15 | |
| 2  | SEASONAL | Check first aid | 2026-12-31 | |

## Troubleshooting

### "Google Sheets not configured"

You'll see this if credentials are incomplete.

Solution: Follow [GOOGLE_SHEETS_SETUP.md](./GOOGLE_SHEETS_SETUP.md) and add credentials to GitHub Secrets.

### Inventory/Reminders don't appear

1. Check Google Sheets exist and are shared with your account
2. Verify Sheet IDs are correct
3. Check browser console (F12) for errors
4. Make sure sheets have correct structure (headers in row 1)

### Changes not appearing

**Static data (JSON):**
- Requires commit & push
- Wait ~2 minutes for GitHub Actions
- Hard refresh browser (Ctrl+Shift+R)

**Dynamic data (Google Sheets):**
- Edit directly in Google Sheets
- Refresh app (F5)
- Changes appear immediately

### Site shows 404

Make sure `frontend/vite.config.js` has correct base path:

```javascript
base: '/your-actual-repo-name/',
```

Then commit, push, and wait 2 minutes.

## Architecture

### What You Get

✓ **GitHub Pages** — Free static hosting  
✓ **GitHub Actions** — Free CI/CD  
✓ **Google Sheets** — Free dynamic data storage  
✓ **No backend server** — Nothing to manage  
✓ **No database** — Costs zero to run  
✓ **HTTPS** — Automatic from GitHub  
✓ **CDN** — Global fast delivery  
✓ **Version control** — All data in Git  

### Security

- OAuth 2.0 with Google (industry standard)
- Credentials stored in GitHub Secrets (encrypted)
- Browser makes direct HTTPS calls to Google
- No passwords stored anywhere
- User controls data sharing via Google Sheets

## Multi-User Setup

If multiple family members need access:

1. Each person creates/uses a Google account
2. Share both Google Sheets with all accounts (Editor permission)
3. Each person logs in with their Google account
4. All see and edit the same Sheets

**Tip:** You can grant View-only access if someone should only read data.

## Support & Documentation

- **[GOOGLE_SHEETS_SETUP.md](./GOOGLE_SHEETS_SETUP.md)** — Complete Google Sheets setup guide
- **GitHub Issues** — Report bugs or suggest features
- **Discussions** — Ask questions or share ideas

## License

[LICENSE](./LICENSE)

---

**Happy organizing! Built completely free with GitHub Pages + Google Sheets. 🏠✨**
