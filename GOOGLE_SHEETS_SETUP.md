# Google Sheets Setup Guide

This guide walks you through setting up Google Sheets integration for the Closet Organizer app.

## Why Google Sheets?

- **Free** — No database costs
- **Easy** — Non-technical users can edit directly
- **Flexible** — Familiar spreadsheet interface
- **No server** — Data syncs automatically
- **Shareable** — Multiple people can access

## Overview

The app stores:
- **Static data** (JSON files) — Closets, family, first aid, cleaning schedules
  - Version-controlled in Git
  - Changes require code commit
- **Dynamic data** (Google Sheets) — Inventory, reminders
  - Editable directly in Google Sheets
  - Updates appear instantly in app
  - No technical knowledge required

## Step 1: Create Google Cloud Project

### 1.1 Go to Google Cloud Console

- Visit https://console.cloud.google.com/
- Sign in with your Google account

### 1.2 Create New Project

- At the top of the page, look for the project dropdown (shows current project name)
- Click it
- Click "NEW PROJECT" button
- Name: `Closet Organizer` (or whatever you like)
- Click "CREATE"
- Wait for project to be created (~1 minute)
- The new project will automatically become active

### 1.3 Enable Sheets API

- In left menu, click "APIs & Services" → "Library"
- Search for "Google Sheets API"
- Click on it
- Click "ENABLE"
- Wait for it to enable (~30 seconds)

## Step 2: Create OAuth Credentials

### 2.1 Create Credentials

- In left menu, click "APIs & Services" → "Credentials"
- Click "CREATE CREDENTIALS" (top)
- Choose "OAuth client ID"
- If prompted, click "CONFIGURE CONSENT SCREEN" first

### 2.2 Configure Consent Screen (First Time Only)

- Choose "External" user type
- Click "CREATE"
- Fill out the form:
  - **App name**: `Closet Organizer`
  - **User support email**: Your email
  - **Developer contact**: Your email
- Click "SAVE AND CONTINUE"
- Skip scopes (click "SAVE AND CONTINUE")
- Review and click "BACK TO DASHBOARD"

### 2.3 Create OAuth Client ID

- Click "CREATE CREDENTIALS" again
- Choose "OAuth client ID"
- Application type: **"Web application"**
- Name: `Closet Organizer`

### 2.4 Add Authorized Redirect URIs

In the "Authorized redirect URIs" section, add:

```
https://YOUR_USERNAME.github.io
https://YOUR_USERNAME.github.io/closet-organizer/
http://localhost:5173
```

Replace `YOUR_USERNAME` with your actual GitHub username.

### 2.5 Create

- Click "CREATE"
- A popup shows your credentials:
  - **Client ID** (long string ending in `.apps.googleusercontent.com`)
  - **Client Secret** (ignore this for now)
- Click "COPY" next to Client ID
- **Save it somewhere safe** — you'll need it in Step 4

### 2.6 Get API Key

- Still in Credentials page
- Click "CREATE CREDENTIALS" again
- Choose "API Key"
- A popup shows your new API key (long string starting with `AIza...`)
- Click "COPY" to copy the key
- **Save it somewhere safe** — you'll need it in Step 4

### 2.7 Restrict API Key (Important!)

**By default, API keys have no restrictions. You MUST restrict this key to Google Sheets only for security.**

After creating the API key, click on it in the Credentials list to edit it:

1. Find your new API key in the Credentials list
2. Click on it to open the edit page
3. Scroll to "API restrictions"
4. Click "Restrict key"
5. Select "Google Sheets API" from the dropdown
6. Click "SAVE"

**Why restrict?** This prevents anyone who finds your API key from using it to access other Google APIs. This is a security best practice.

## Step 3: Create Google Sheets

### 3.1 Create Inventory Sheet

- Go to https://sheets.google.com
- Click "Create" (+ icon, or blank sheet)
- Name it: `Closet Organizer - Inventory`
- Click "CREATE"

### 3.2 Set Up Columns

In the first row, add headers:

| A | B | C | D | E |
|---|---|---|---|---|
| Basket ID | Item Name | Quantity | Expiration Date | Notes |

### 3.3 Add Sample Data (Optional)

| A | B | C | D | E |
|---|---|---|---|---|
| basket_1 | Sheets (1000ct) | 10 | 2026-06-01 | Egyptian cotton |
| basket_1 | Pillows | 2 | 2026-12-31 | Down pillows |
| basket_2 | Disinfectant | 5 | 2025-08-15 | Spray bottles |

### 3.4 Get Inventory Sheet ID

- Look at the URL in browser: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`
- Copy the `SHEET_ID` (long string between `/d/` and `/edit`)
- **Save it**

### 3.5 Create Reminders Sheet

- Click "+" (plus icon, bottom left) to add new sheet
- OR create a new sheet at https://sheets.google.com
- Name it: `Closet Organizer - Reminders`

### 3.6 Set Up Reminder Columns

In the first row:

| A | B | C | D | E |
|---|---|---|---|---|
| ID | Category | Text | Due Date | Acknowledged |

### 3.7 Add Sample Reminders (Optional)

| A | B | C | D | E |
|---|---|---|---|---|
| 1 | WASH | Wash sheets | 2026-06-15 | |
| 2 | SEASONAL | Check first aid kit | 2026-12-31 | |
| 3 | CLEAN | Restock cleaning supplies | 2026-06-30 | |

### 3.8 Get Reminders Sheet ID

- Switch to Reminders sheet (click tab at bottom)
- Copy the Sheet ID from URL
- **Save it**

### 3.9 Share Sheets (Important!)

**Both sheets need to be shared with your Google account.**

For each sheet:
1. Click "Share" (top right)
2. Add your email address
3. Click "Editor"
4. Click "Share"

The app will access sheets using your Google account, so it must have Editor permission.

## Step 4: Add Credentials to App

### 4.1 Create `.env` File

In the `frontend/` directory, create `.env`:

```bash
# Copy from Google Cloud Console
VITE_GOOGLE_CLIENT_ID=YOUR_CLIENT_ID.apps.googleusercontent.com
VITE_GOOGLE_API_KEY=YOUR_API_KEY

# Copy from Google Sheets URLs
VITE_INVENTORY_SHEET_ID=YOUR_INVENTORY_SHEET_ID
VITE_REMINDERS_SHEET_ID=YOUR_REMINDERS_SHEET_ID
```

### 4.2 Fill In Values

Replace with your actual values:

- **VITE_GOOGLE_CLIENT_ID**: From Step 2.5
- **VITE_GOOGLE_API_KEY**: From Step 2.6
- **VITE_INVENTORY_SHEET_ID**: From Step 3.4
- **VITE_REMINDERS_SHEET_ID**: From Step 3.8

Example:

```
VITE_GOOGLE_CLIENT_ID=123456789-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com
VITE_GOOGLE_API_KEY=AIzaSyDxxx_yyyyy_zzzzz_aaaaaa
VITE_INVENTORY_SHEET_ID=1hR4x8Abc_Defgh-IJK_LmnOPQRstUVWXYZ
VITE_REMINDERS_SHEET_ID=1kL9M_NOpqRSTuvwxyZ_aBCdeFgHIJKLmnOP
```

### 4.3 Verify `.env` is in `.gitignore`

Make sure `.gitignore` includes `.env` so credentials aren't committed:

```bash
cat frontend/.env.example  # Should exist
cat .gitignore | grep env  # Should show ".env"
```

## Step 5: Test & Deploy

### 5.1 Test Locally (Optional)

```bash
cd frontend
npm install
npm run dev
```

- Visit http://localhost:5173
- App should load
- Click "Login" (if inventory/reminders appear)
- Authenticate with Google
- Inventory and reminders should load from Sheets

### 5.2 Deploy to GitHub (Using GitHub Secrets)

For production, use GitHub Secrets instead of `.env` file:

1. **Do NOT commit `.env` to Git** - it's in `.gitignore` for security
2. Go to your GitHub repository
3. Click Settings → Secrets and variables → Actions
4. Click "New repository secret" and add each:
   - `VITE_GOOGLE_CLIENT_ID` 
   - `VITE_GOOGLE_API_KEY`
   - `VITE_INVENTORY_SHEET_ID`
   - `VITE_REMINDERS_SHEET_ID`

The `.github/workflows/deploy-frontend.yml` already reads from these secrets automatically.

5. Commit your changes (but NOT the `.env` file):

```bash
git add .
git commit -m "Ready for Google Sheets deployment"
git push origin main
```

GitHub Actions will automatically build with your secrets and deploy to GitHub Pages.

### 5.3 Local Development (Optional)

For local testing before deploying:

```bash
cd frontend
npm install
npm run dev
```

- Visit http://localhost:5173
- The app will look for credentials in `frontend/.env` (local only)
- Make sure to create `frontend/.env` with your values for local testing
- This `.env` file will NOT be committed to Git (already in `.gitignore`)

## Step 6: First-Time Login

When you deploy to GitHub Pages and visit your site for the first time:

1. The app loads and shows the interface
2. For Inventory and Reminders sections, click "Login with Google"
3. A Google login popup appears
4. Sign in with the Google account that has Editor access to your Sheets
5. Grant the requested permissions
6. You'll be logged in and the app will load your inventory and reminders from Google Sheets

**Note**: Browser remembers your login, so you won't need to sign in every time you visit the app. You can sign out in the app settings if needed.

## Using the App

### Editing Inventory

**From the App:**
1. Click a basket
2. Click "Edit Inventory"
3. Add/remove items
4. Changes saved to Google Sheets

**From Google Sheets:**
1. Open https://sheets.google.com
2. Open "Closet Organizer - Inventory"
3. Add/edit/delete rows
4. Refresh app to see changes

### Editing Reminders

**From the App:**
1. Go to Reminders section
2. Create new reminder
3. Saved to Google Sheets

**From Google Sheets:**
1. Open "Closet Organizer - Reminders" sheet
2. Add new row with reminder details
3. Refresh app to see it

## Troubleshooting

### "Google Sheets not configured"

- Credentials missing from `frontend/.env`
- Check that all 4 variables are set
- Restart dev server: `npm run dev`

### "Not authenticated"

- Click "Login" button in app
- Sign in with Google
- Grant permissions
- Try again

### "Sheet not found"

- Check Sheet IDs are correct (copy from URL)
- Verify sheets exist and have correct names
- Make sure sheets are shared with your account

### Inventory/Reminders not appearing

1. Check Google Sheets exist
2. Verify credentials are correct
3. Open browser console (F12)
4. Look for error messages
5. Check sheet structure matches expected format

### Changes not syncing

**From app to Sheets:**
- Open Google Sheets
- Refresh (F5)
- Changes should appear

**From Sheets to app:**
- Refresh app (F5)
- May take a few seconds to load

### OAuth Error: "invalid_scope"

- Check scopes are correct in Google Cloud Console
- Scopes should be: `https://www.googleapis.com/auth/spreadsheets`

### CORS Error in Browser

- Ensure redirect URIs include your GitHub Pages URL
- Example: `https://username.github.io/closet-organizer/`
- Update in Google Cloud Console
- Redeploy app

## Security Notes

⚠️ **Important:**

- `frontend/.env` contains Google credentials
- **Never commit `.env` to Git**
- Use GitHub Secrets for production instead
- Each user should use their own Google account
- Shares Sheets with people who need access

### Secure Setup

1. Add `.env` to `.gitignore`
2. Use GitHub Secrets for deployments
3. Share Sheets only with trusted people
4. Rotate credentials if they leak

## Advanced: Multiple Users

If multiple family members need to edit:

1. Each person needs their own Google account
2. Share Sheets with all accounts (Editor permission)
3. Each person logs in with their account
4. All see/edit same data

Tip: You can restrict editing with View-only shares if someone should only read data.

## Support

- See [README.md](./README.md) for general info and deployment instructions
- GitHub Issues for bugs: https://github.com/Home-Automation-Project/closet-organizer/issues

---

**Happy organizing! 🏠✨**
