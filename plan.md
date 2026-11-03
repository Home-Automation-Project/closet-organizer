# GitHub Pages Full Static Architecture

## New Architecture

```
┌─────────────────────────────────────────────────┐
│       GitHub Pages (Everything Static)           │
│  https://username.github.io/closet-organizer    │
│                                                  │
│  • Frontend (Vue.js app)                        │
│  • JSON data files (embedded in build)          │
│  • No backend API needed                        │
│  • Free hosting with auto-deploy                │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │ Browser-Based Google Sheets Integration  │  │
│  │ • Inventory read/write                   │  │
│  │ • Reminders read/write                   │  │
│  │ • Direct API calls from frontend         │  │
│  └──────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────┘
                     │
        Browser Makes Direct API Calls
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
    ┌─────────────┐      ┌─────────────┐
    │Google Sheets│      │Google Drive  │
    │             │      │  (Optional)  │
    │ Inventory   │      │              │
    │ Reminders   │      │              │
    └─────────────┘      └─────────────┘
```

## Advantages

- ✓ Zero backend infrastructure
- ✓ Completely free (GitHub Pages + Google Sheets)
- ✓ Single-click deployment
- ✓ No server maintenance
- ✓ Automatic HTTPS
- ✓ Global CDN
- ✓ Simple, clean architecture
- ✓ All data in version control (JSON) or Google Sheets
- ✓ Anyone can edit Google Sheets directly

## Changes Needed

1. **Remove backend entirely** - not needed
2. **Browser-based Google Sheets API** - frontend calls Sheets directly
3. **Simplify Vite config** - no need for API proxy or base path concerns (can be simple)
4. **Update API module** - direct Google Sheets client instead of backend calls
5. **Update README** - explain Google Sheets setup for browser access
6. **No Docker/backend deployment** - just frontend

## Implementation

### Frontend Architecture

```
index.html
├── Vite (build system)
├── Vue 3 (app framework)
├── Pinia (state management)
├── Google Sheets API Client (gapi.js)
│   └── Direct browser auth
│       └── Read/write Sheets
└── Static JSON data
    ├── closets.json
    ├── family.json
    ├── firstaid.json
    └── cleaning.json
```

### Google Sheets Setup

User creates:
1. Google Cloud project
2. Enable Sheets API
3. Create OAuth 2.0 credentials (public/web)
4. Create two Google Sheets:
   - Inventory data
   - Reminders data
5. Share read/write access

### Frontend Integration

```javascript
// frontend/src/services/gsheets.js
import { google } from 'googleapis'

class GoogleSheetsClient {
  async authenticate() {
    // OAuth 2.0 flow in browser
  }
  
  async getInventory() {
    // Read from inventory sheet
  }
  
  async updateInventory() {
    // Write to inventory sheet
  }
}
```
