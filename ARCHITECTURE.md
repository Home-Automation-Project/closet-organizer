# Closet Organizer - Refactored Architecture

## Overview

This document describes the refactored architecture of the Closet Organizer application. The system has been redesigned to eliminate the need for a backend database and MQTT/IoT infrastructure.

## Architecture Changes

### Previous Architecture
- **Backend**: FastAPI with PostgreSQL database
- **Database**: Used SQLAlchemy ORM with migrations (Alembic)
- **Data Storage**: All data persisted in PostgreSQL
- **Real-time**: MQTT broker for IoT events
- **Schedulers**: APScheduler for reminder scheduling
- **Frontend**: Vue.js calling REST API

### New Architecture
- **Static Data**: JSON files (version-controlled, human-readable)
- **Dynamic Data**: Google Sheets integration via backend proxy
- **Backend**: Simplified FastAPI with no database dependencies
- **Frontend**: Vue.js calling REST API (unchanged interface)
- **Deployment**: Minimal Docker stack (frontend only)

## Data Sources

### 1. Static JSON Files
Located in `/data/json/`:

#### `closets.json`
Defines the complete closet organization structure:
```json
{
  "closets": [
    {
      "id": "closet_1",
      "name": "Linen Closet",
      "location": "Hallway",
      "shelves": [
        {
          "id": "shelf_1",
          "label": "Top Shelf",
          "baskets": [...]
        }
      ]
    }
  ]
}
```

#### `family.json`
Medical information for family members:
```json
{
  "members": [
    {
      "id": "member_1",
      "name": "John Doe",
      "dateOfBirth": "1980-01-15",
      "bloodType": "O+",
      "allergies": "Penicillin",
      "medications": "None",
      "medicalConditions": "Asthma",
      "emergencyContact": "Jane Doe (555-1234)"
    }
  ]
}
```

#### `firstaid.json`
First aid kit definitions (basic and advanced):
```json
{
  "basicKit": {
    "items": [
      {
        "name": "Assorted adhesive bandages",
        "category": "Wound Care",
        "hasExpiration": false,
        "recommendedQty": 30,
        "unit": "pieces"
      }
    ]
  },
  "advancedKit": {
    "bins": [...],
    "items": [...]
  }
}
```

#### `cleaning.json`
Cleaning schedules and checklists by room:
```json
{
  "rooms": [
    {
      "id": "kitchen",
      "label": "Kitchen",
      "categories": [
        {
          "category": "Counters & Sink",
          "items": [...]
        }
      ]
    }
  ]
}
```

### 2. Google Sheets (Dynamic Data)

#### Inventory Sheet
Tracks current inventory quantities and expiration dates:
- Column A: Item Name
- Column B: Quantity
- Column C: Expiration Date (YYYY-MM-DD)
- Column D: Notes
- Column E: Updated At (ISO format)

#### Reminders Sheet
Tracks reminders and their acknowledgment status:
- Column A: Category (CLEANING, FIRST_AID, BEDDING)
- Column B: Reminder Text
- Column C: Due Date (YYYY-MM-DD)
- Column D: Acknowledged At (ISO format, empty if not acknowledged)
- Column E: Created At (ISO format)

## Backend Structure

### Key Files

**`backend/app/data_loader.py`**
- Loads and caches static JSON files
- Provides methods to query closets, family members, first aid items, and cleaning data
- Replaces SQLAlchemy ORM and database queries

**`backend/app/services/gsheets_service.py`**
- Google Sheets API integration
- Methods to read/write inventory and reminders
- Authentication via Google OAuth (future implementation)
- Placeholder methods - ready for Google Sheets API implementation

**`backend/app/routers/*.py`**
- Simplified routers that no longer depend on database sessions
- All routers now use `DataLoader` for static data
- Dynamic data flows through `GoogleSheetsAdapter`
- No more CRUD operations on the database

### API Routes

#### Closets Endpoints
- `GET /api/closets` - List all closets (static JSON)
- `GET /api/closets/{closet_id}` - Get single closet (static JSON)
- `GET /api/shelves` - List shelves by closet (static JSON)
- `GET /api/baskets` - List baskets by shelf (static JSON)

#### Family Endpoints
- `GET /api/family` - List family members (static JSON)
- `GET /api/family/{member_id}` - Get single member (static JSON)

#### First Aid Endpoints
- `GET /api/firstaid/kit/basic` - List basic kit items (static JSON)
- `GET /api/firstaid/kit/advanced/bins` - List advanced kit bins (static JSON)
- `GET /api/firstaid/kit/advanced` - List advanced kit items (static JSON)

#### Cleaning Endpoints
- `GET /api/cleaning/rooms` - List rooms (static JSON)
- `GET /api/cleaning/{room_id}` - Get room checklist (static JSON)
- `POST /api/cleaning/{room_id}/complete/{item_key}` - Mark item complete (session-based)
- `DELETE /api/cleaning/{room_id}/complete/{item_key}` - Mark item incomplete
- `DELETE /api/cleaning/{room_id}/session` - Reset session

#### Inventory Endpoints (Google Sheets)
- `GET /api/inventory/basket/{basket_id}` - Get inventory from Sheets
- `PUT /api/inventory/basket/{basket_id}/item/{item_name}` - Update inventory in Sheets
- `DELETE /api/inventory/item/{item_id}` - Delete inventory item

#### Reminders Endpoints (Google Sheets)
- `GET /api/reminders/wash` - Get wash reminders
- `GET /api/reminders/seasonal` - Get seasonal reminders
- `PATCH /api/reminders/wash/{reminder_id}/acknowledge` - Acknowledge reminder
- `PATCH /api/reminders/seasonal/{reminder_id}/acknowledge` - Acknowledge reminder
- `POST /api/reminders/seasonal` - Create new reminder

## Frontend Changes

The frontend API module (`frontend/src/api.js`) has been updated with:
1. Documentation of data sources
2. Clarification of which endpoints are static vs dynamic
3. Updated parameter naming (e.g., `itemName` instead of `itemDefId`)

**No Vue.js component changes required** - all API calls remain the same interface.

## Setup & Deployment

### Prerequisites
- Python 3.9+
- Node.js 18+ (for frontend build)
- Google Account with Sheets API enabled (for dynamic data)

### Backend Setup

1. **Install dependencies** (minimal):
```bash
cd backend
pip install fastapi uvicorn
```

2. **Set environment variables** (optional, for Google Sheets):
```bash
export GOOGLE_SHEET_INVENTORY_ID="your_sheet_id"
export GOOGLE_SHEET_REMINDERS_ID="your_sheet_id"
```

3. **Run development server**:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Install dependencies**:
```bash
cd frontend
npm install
```

2. **Development server**:
```bash
npm run dev
```

3. **Production build**:
```bash
npm run build
```

### Docker Deployment

Updated `docker-compose.yml` now includes only:
- Frontend (Nginx)
- Backend API (FastAPI)

No PostgreSQL or Mosquitto services needed.

```bash
docker-compose up
```

## Migration Guide

### From Database to JSON

If you have existing data in the database:

1. **Export closet structure** from database to `data/json/closets.json`
2. **Export family members** to `data/json/family.json`
3. **Keep first aid items** and **cleaning checklists** as-is (already in JSON format)
4. **Move inventory** to Google Sheets (use bulk import feature)
5. **Move reminders** to Google Sheets

### Git Workflow

All JSON files are version-controlled:
```bash
git add data/json/*.json
git commit -m "Update closet structure"
git push
```

Changes to JSON files automatically deploy on pull/restart.

## Implementation Status

### ✅ Completed
- Data loader for static JSON files
- Simplified routers (no database)
- Google Sheets adapter (placeholder)
- Removed all MQTT/IoT code
- Removed Alembic migrations
- Frontend API module updated

### 🔄 In Progress
- Google Sheets API implementation
- Frontend component testing with new data sources
- Docker Compose simplification

### 📋 TODO
- Implement Google Sheets authentication
- Add inventory read/write via Google Sheets API
- Add reminder read/write via Google Sheets API
- Update documentation for users
- Create sample Google Sheets templates

## Advantages of New Architecture

1. **No Database**: Simpler deployment, fewer moving parts
2. **Version Control**: All static data in Git, full audit trail
3. **Collaborative**: Google Sheets allows multiple people to manage data
4. **Offline-friendly**: Static data works offline, Sheets syncs when online
5. **Minimal Dependencies**: No SQLAlchemy, Alembic, APScheduler, or MQTT
6. **Reduced Costs**: No database server needed
7. **Easy Backups**: JSON files are human-readable and easily backed up

## Next Steps

1. Configure Google Sheets API credentials
2. Create sample sheets for inventory and reminders
3. Implement `GoogleSheetsAdapter` methods
4. Test frontend with Google Sheets data
5. Update user documentation
6. Deploy to production
