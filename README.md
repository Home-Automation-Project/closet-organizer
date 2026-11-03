# Closet Organizer

A self-hosted home organization web app for tracking what's in your closets — specifically designed around three types of storage: **bedding** (with wash reminders), **cleaning supplies** (with room checklists), and **first aid kits** (basic and advanced). Runs entirely in Docker using static JSON data files and Google Sheets for dynamic data.

> **⚠️ Architectural Refactor**: This project has been refactored to eliminate database and MQTT dependencies. See [ARCHITECTURE.md](./ARCHITECTURE.md) for details.

# Overview
Closet organization with three types of organization:

1. **Bedding** — Track sheets and towels with wash reminders
2. **Cleaning Supplies** — Bins for each room with checklists (daily, weekly, monthly, seasonal)
3. **First Aid** — Basic and advanced medical kits with items, expiration tracking, family medical info

The app features a **web dashboard** (Vue.js) showing each closet shelf and basket representation. Baskets appear:
- **Green** — all items in stock, nothing expired
- **Yellow** — low stock or items expiring within 30 days
- **Red** — expired items or critically low stock

Click a basket to view/edit inventory (quantity, expiration dates). Separate sections for:
- **Setup page** — Configure closets, shelves, baskets
- **First aid reference** — CPR steps, poison control, family allergies/meds
- **Cleaning checklist** — Room-by-room checklist with frequency filters

**All data is stored as JSON files (version-controlled) or Google Sheets (dynamic data).** No database needed.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | Python 3.9+, FastAPI, Uvicorn |
| Data Storage | JSON files (static) + Google Sheets API (dynamic) |
| Frontend | Vue 3.5, Vite 6, Pinia 2.2, Vue Router 4.4, Axios 1.7 |
| Serving | nginx 1.27 (Docker, proxies `/api/` to FastAPI) |
| Containerization | Docker Compose |

**Removed**: PostgreSQL, Alembic, SQLAlchemy, APScheduler, MQTT Broker, paho-mqtt

---

## Project Structure

```
closet-organizer/
├── ARCHITECTURE.md               # Detailed architecture documentation
├── docker-compose.yml            # Frontend + Backend only (no DB or MQTT)
├── data/
│   └── json/                     # Static data files (version-controlled)
│       ├── closets.json          # Closet/shelf/basket structure
│       ├── family.json           # Family member medical info
│       ├── firstaid.json         # First aid kit item definitions
│       └── cleaning.json         # Room cleaning checklists
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py               # FastAPI app (no DB/MQTT startup)
│       ├── data_loader.py        # JSON file loader (replaces ORM)
│       ├── routers/
│       │   ├── closets.py        # /api/closets (from JSON)
│       │   ├── inventory.py      # /api/inventory (from Google Sheets)
│       │   ├── reminders.py      # /api/reminders (from Google Sheets)
│       │   ├── cleaning.py       # /api/cleaning (from JSON)
│       │   ├── firstaid.py       # /api/firstaid (from JSON)
│       │   └── family.py         # /api/family (from JSON)
│       └── services/
│           └── gsheets_service.py # Google Sheets adapter
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    ├── src/
    │   ├── main.js
    │   ├── api.js                # Axios API client (all endpoints)
    │   ├── components/           # Vue components
    │   ├── views/                # Page views
    │   ├── stores/               # Pinia state management
    │   └── router/               # Vue Router
```

---

## Features

✅ **Visual dashboard** — closets → shelves → baskets rendered as colored tiles (green / yellow / red)  
✅ **Basket status engine** — automatically computes status based on inventory health  
✅ **Expiry & quantity tracking** — item-level tracking with status badges  
✅ **Cleaning checklists** — 11+ rooms × 4 frequencies, session-based tracking  
✅ **First aid reference** — CPR steps, poison control, family medical info, itemized kits  
✅ **Google Sheets integration** — Dynamic inventory and reminder data  
✅ **Version control** — All static data in Git with full audit trail  
✅ **No authentication** — Designed for trusted home network use  
✅ **Minimal dependencies** — Simplified deployment, fewer moving parts  

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.9+ (for local development)
- Node.js 18+ (for frontend development)

### Using Docker Compose

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Home-Automation-Project/closet-organizer.git
   cd closet-organizer
   ```

2. **Start the services**:
   ```bash
   docker-compose up -d
   ```

3. **Access the app**:
   - Open http://localhost in your browser
   - Backend API: http://localhost/api/
   - Health check: http://localhost/api/health

### Local Development

#### Backend

```bash
cd backend
pip install fastapi uvicorn
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will automatically load JSON files from `../data/json/`.

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Google Sheets API (optional, for inventory/reminders)
GOOGLE_SHEET_INVENTORY_ID=your_sheet_id_here
GOOGLE_SHEET_REMINDERS_ID=your_sheet_id_here

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Frontend
FRONTEND_HOST=0.0.0.0
FRONTEND_PORT=80
```

### Static Data Files

All static data is in `data/json/`. Edit these files and restart the app for changes to take effect:

- **`closets.json`** — Define your closet structure
- **`family.json`** — Add family members and medical info
- **`firstaid.json`** — First aid kit item definitions (usually not modified)
- **`cleaning.json`** — Add/modify rooms and cleaning checklists

### Google Sheets Integration

To enable dynamic inventory and reminder tracking:

1. Create Google Sheets for inventory and reminders
2. Set up Google Cloud project with Sheets API enabled
3. Add credentials to `.env`
4. Implement the methods in `backend/app/services/gsheets_service.py`

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed setup instructions.

---

## API Endpoints

### Closets (Static JSON)
- `GET /api/closets` — List all closets
- `GET /api/closets/{closet_id}` — Get single closet
- `GET /api/shelves` — List shelves by closet
- `GET /api/baskets` — List baskets by shelf

### Family (Static JSON)
- `GET /api/family` — List family members
- `GET /api/family/{member_id}` — Get member details

### First Aid (Static JSON)
- `GET /api/firstaid/kit/basic` — List basic kit items
- `GET /api/firstaid/kit/advanced/bins` — List advanced kit bins
- `GET /api/firstaid/kit/advanced` — List advanced kit items
- `GET /api/firstaid/cpr` — Get CPR steps

### Cleaning (Static JSON)
- `GET /api/cleaning/rooms` — List rooms
- `GET /api/cleaning/{room_id}` — Get room checklist
- `POST /api/cleaning/{room_id}/complete/{item_key}` — Mark item done
- `DELETE /api/cleaning/{room_id}/complete/{item_key}` — Mark item undone
- `DELETE /api/cleaning/{room_id}/session` — Reset session

### Inventory (Google Sheets)
- `GET /api/inventory/basket/{basket_id}` — Get basket inventory
- `PUT /api/inventory/basket/{basket_id}/item/{item_name}` — Update item
- `DELETE /api/inventory/item/{item_id}` — Delete item

### Reminders (Google Sheets)
- `GET /api/reminders/wash` — Get wash reminders
- `GET /api/reminders/seasonal` — Get seasonal reminders
- `PATCH /api/reminders/{id}/acknowledge` — Acknowledge reminder
- `POST /api/reminders/seasonal` — Create new reminder

---

## Deployment

### Hosting Options

The application supports several deployment architectures:

**Option 1: GitHub Pages + External API (Recommended)**
- Frontend hosted on GitHub Pages (static, free)
- Backend API hosted on Railway, Render, Heroku, or AWS
- See [GITHUB_PAGES_DEPLOYMENT.md](./GITHUB_PAGES_DEPLOYMENT.md) for setup

**Option 2: Docker (Self-Hosted)**
- Deploy entire application using Docker Compose
- Run on any server, VPS, or home network
- See [docker-compose.yml](./docker-compose.yml)

**Option 3: Cloud Platform (AWS, Azure, GCP)**
- Both frontend and backend on cloud platform
- Managed services for scaling

### Getting Started with Deployment

1. **Frontend only** (GitHub Pages):
   - See [GITHUB_PAGES_DEPLOYMENT.md](./GITHUB_PAGES_DEPLOYMENT.md)
   - Automatic deployments on every git push
   - Free hosting on `https://username.github.io/closet-organizer`

2. **Backend API hosting**:
   - See [BACKEND_DEPLOYMENT.md](./BACKEND_DEPLOYMENT.md)
   - Railway.app: Easiest setup (~$5/mo)
   - Render.com: Free tier available
   - AWS Lightsail: Best value (~$3.50/mo)
   - Heroku: Established platform (~$7/mo)

3. **Full Docker deployment**:
   - See [docker-compose.yml](./docker-compose.yml)
   - Run locally or on any server with Docker installed

---

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for a comprehensive guide to:
- Data source architecture (JSON + Google Sheets)
- Backend structure and data flow
- Frontend changes and integration
- Setup and deployment instructions
- Migration guide from previous database-based architecture

---

## Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** — Complete architecture overview and reference
- **[GITHUB_PAGES_DEPLOYMENT.md](./GITHUB_PAGES_DEPLOYMENT.md)** — Deploy frontend to GitHub Pages
- **[BACKEND_DEPLOYMENT.md](./BACKEND_DEPLOYMENT.md)** — Deploy backend API to various providers
- **[REFACTOR_SUMMARY.md](./REFACTOR_SUMMARY.md)** — Summary of architectural changes

---

## License

[LICENSE](./LICENSE)ator
        │   ├── InventoryTable.vue # Editable inventory table with status badges
        │   └── AppModal.vue      # Reusable modal (Teleport)
        └── views/
            ├── DashboardView.vue
            ├── SetupView.vue
            ├── BasketDetailView.vue
            ├── ScanView.vue      # Mobile QR/NFC scan target
            ├── NotFoundView.vue
            ├── cleaning/
            │   ├── RoomListView.vue
            │   └── ChecklistView.vue
            └── firstaid/
                ├── FirstAidHub.vue
                ├── CprView.vue
                ├── PoisonView.vue
                ├── FamilyMedView.vue
                ├── BasicKitView.vue
                └── AdvancedKitView.vue
```

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine + Compose plugin)
- A local network accessible from your ESP32 devices

---

## Getting Started

### 1. Clone and configure

```bash
git clone <repo-url>
cd closet-organizer
```

Copy the default environment file and edit as needed:

```bash
cp .env .env.local   # or just edit .env directly
```

`.env` defaults:

```dotenv
POSTGRES_USER=closet
POSTGRES_PASSWORD=closetpass
POSTGRES_DB=closetdb
APP_HOST=http://localhost        # Base URL used to generate QR code scan links
```

Set `APP_HOST` to your host's LAN IP (e.g. `http://192.168.1.50`) so QR codes resolve correctly on mobile devices.

### 2. Start all services

```bash
docker compose up --build
```

On first boot the backend will:
1. Run `alembic upgrade head` to create all database tables
2. Seed first-aid item definitions (43 basic + 64 advanced) and cleaning checklist items (120+ across 11 rooms)
3. Connect to the Mosquitto broker
4. Start the APScheduler reminder jobs

### 3. Open the app

| URL | Description |
|---|---|
| `http://localhost` | Main app (Dashboard) |
| `http://localhost:8000/docs` | FastAPI interactive API docs |
| `http://localhost:1883` | MQTT broker (TCP) |
| `http://localhost:9001` | MQTT broker (WebSocket) |

---

## UI Pages

| Route | Page |
|---|---|
| `/` | Dashboard — all closets with shelf/basket status grid |
| `/setup` | Setup — create/edit closets, shelves, baskets; download QR codes |
| `/basket/:id` | Basket detail — inventory list with expiry/quantity editing |
| `/scan/:token` | Scan target — mobile-optimized read-only view, opened by QR code |
| `/cleaning` | Room list — grid of 11 rooms linking to their checklists |
| `/cleaning/:room` | Checklist — items grouped by frequency, tap to complete |
| `/firstaid` | First Aid hub — links to all first aid sections |
| `/firstaid/cpr` | CPR steps |
| `/firstaid/poison` | Poison control numbers and guidance |
| `/firstaid/family` | Family medical info (allergies, medications, conditions) |
| `/firstaid/kit/basic` | Basic kit items by category |
| `/firstaid/kit/advanced` | Advanced kit with bin selector tabs |

---

## MQTT Integration

The broker accepts anonymous connections. Configure your ESP32 to publish to the broker at port `1883`.

### Topics the backend **subscribes to**

| Topic | Payload | Action |
|---|---|---|
| `closet/shelf/<shelf_id>/presence` | `{"state": "occupied"}` or `{"state": "empty"}` | Records a shelf event; creates a wash reminder when state becomes `empty` |
| `closet/basket/<basket_id>/nfc_tap` | `{"token": "<qr_token>"}` | Looks up the basket and can trigger further processing |

### Topics the backend **publishes**

| Topic | Payload | Trigger |
|---|---|---|
| `closet/alerts/wash_reminder` | `{"shelf_id", "message", "due_at"}` | Shelf goes empty; also re-published nightly if overdue |
| `closet/alerts/expiring_item` | `{"basket_id", "item_definition_id", "expiration_date"}` | Nightly expiry scan |
| `closet/alerts/seasonal_reminder` | `{"reminder_id", "basket_id", "note", "due_date"}` | Weekly seasonal check |

### ESP32 example (Arduino/PlatformIO)

```cpp
// Publish presence on mat state change
String topic = "closet/shelf/" + String(SHELF_ID) + "/presence";
String payload = matOccupied ? "{\"state\":\"occupied\"}" : "{\"state\":\"empty\"}";
mqttClient.publish(topic.c_str(), payload.c_str());
```

---

## API Overview

Full interactive docs are available at `http://localhost:8000/docs` once the stack is running.

| Prefix | Resource |
|---|---|
| `GET /api/health` | Health check |
| `GET/POST/PUT/DELETE /api/closets` | Closet management |
| `GET/POST/PUT/DELETE /api/shelves` | Shelf management |
| `GET/POST/PUT/DELETE /api/baskets` | Basket management |
| `GET/PUT/DELETE /api/inventory/basket/:id` | Inventory items with computed status |
| `GET /api/inventory/basket/:id/qr.png` | QR code image for a basket |
| `GET /api/inventory/scan/:token` | Look up basket by QR token |
| `GET/POST/DELETE /api/reminders/wash` | Wash reminders |
| `GET/POST/DELETE /api/reminders/seasonal` | Seasonal reminders |
| `GET /api/cleaning/rooms` | List of supported rooms |
| `GET /api/cleaning/:room` | Fetch checklist + session state |
| `POST/DELETE /api/cleaning/:room/complete/:item_key` | Toggle item completion |
| `POST /api/cleaning/:room/reset` | Reset session |
| `GET /api/firstaid/cpr` | CPR step list |
| `GET /api/firstaid/kit/basic` | Basic first aid kit items |
| `GET /api/firstaid/kit/advanced` | Advanced kit bins + items |
| `GET/POST/PUT/DELETE /api/family` | Family member medical info |

---

## Basket Types & Status Logic

| Type | Description |
|---|---|
| `BEDDING` | Shelf with pressure mat; tracks wash reminders |
| `CLEANING` | NFC-tagged bins for cleaning supplies |
| `FIRST_AID_BASIC` | Standard first aid items |
| `FIRST_AID_ADVANCED` | Advanced kit with 12 sub-bins |

**Status computation (per basket):**

- 🔴 **RED** — any item is expired, or quantity is at or below 0
- 🟡 **YELLOW** — any item expires within 30 days, or quantity is below 50% of the expected amount
- 🟢 **GREEN** — all items within acceptable thresholds

---

## Supported Cleaning Rooms

`library` · `kitchen` · `dining_room` · `gym` · `bedroom` · `bathroom` · `playroom` · `hallways` · `laundry_room` · `garage` · `family_room`

Each room has checklist items across four frequencies: **Daily**, **Weekly**, **Monthly**, and **Seasonal**.

---

## Scheduled Jobs

| Job | Schedule | Action |
|---|---|---|
| Expiry scan | Daily at 02:00 | Publishes MQTT alert for items expiring within 30 days |
| Overdue wash re-notify | Daily at 06:00 | Re-publishes unacknowledged wash reminders that are past due |
| Seasonal reminder check | Mondays at 07:00 | Publishes alerts for seasonal reminders due within 7 days |

---

## Development (without Docker)

**Backend:**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
# Set environment variables (or create a .env in /backend)
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev                   # Proxies /api/ to localhost:8000
```

---

## Resetting the Database

```bash
docker compose down -v        # Removes named volumes (wipes DB)
docker compose up --build     # Fresh start with seeded data
```
