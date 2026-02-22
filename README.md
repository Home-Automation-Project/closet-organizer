# Closet Organizer

A self-hosted home automation web app for tracking what's in your closets — specifically designed around three types of storage: **bedding** (pressure-mat presence detection), **cleaning supplies** (NFC-tagged bins), and **first aid kits** (basic and advanced). Runs entirely in Docker, integrates with ESP32 hardware over MQTT, and is designed to be used daily on a wall-mounted tablet.

---

## Features

- **Visual dashboard** — closets → shelves → baskets rendered as colored tiles (green / yellow / red) based on inventory health
- **Basket status engine** — automatically computes RED (expired item or critically low stock), YELLOW (expiring within 30 days or below 50% quantity), GREEN (all good)
- **QR code scanning** — every basket gets a unique QR code; scanning opens a mobile-optimized inventory view directly
- **NFC bin support** — cleaning supply bins can trigger MQTT events on tap
- **Bedding wash reminders** — pressure mats on shelves publish MQTT presence events; the app creates a wash reminder when the shelf goes empty and re-publishes the alert if it's overdue
- **Expiry & quantity tracking** — item-level expiration dates and quantity thresholds with status badges
- **Cleaning checklists** — 11 rooms × 4 frequencies (Daily / Weekly / Monthly / Seasonal), session-based completion tracking stored locally per device
- **First aid reference** — CPR steps, poison control info, family medical details (allergies, medications, conditions), and itemized basic + advanced kit contents with bin organization
- **Scheduled alerts** — nightly expiry scan, morning overdue-wash re-publish, weekly seasonal reminder check via APScheduler
- **No authentication required** — designed for trusted home network use

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | Python 3.12, FastAPI 0.115+, Uvicorn |
| ORM / Migrations | SQLAlchemy 2.0 (async), Alembic (async template) |
| Database | PostgreSQL 16 |
| MQTT Broker | Eclipse Mosquitto 2 |
| MQTT Client | paho-mqtt 2.0 |
| Scheduler | APScheduler 3.10 (AsyncIOScheduler + SQLAlchemyJobStore) |
| QR Generation | qrcode\[pil\] |
| Frontend | Vue 3.5, Vite 6, Pinia 2.2, Vue Router 4.4, Axios 1.7 |
| Serving | nginx 1.27 (inside Docker, proxies `/api/` to FastAPI) |
| Containerization | Docker Compose |

---

## Project Structure

```
closet-organizer/
├── .env                          # Local environment overrides (gitignore this)
├── docker-compose.yml
├── mosquitto/
│   └── mosquitto.conf            # Anonymous broker, ports 1883 + 9001 WS
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py                # Async migration runner
│   │   └── versions/             # Auto-generated migration files
│   └── app/
│       ├── main.py               # FastAPI app + lifespan (migrate → seed → MQTT → scheduler)
│       ├── seed.py               # First-aid items + cleaning checklists (idempotent)
│       ├── dependencies.py       # get_db() async session dependency
│       ├── db/
│       │   ├── base.py           # DeclarativeBase + AsyncAttrs
│       │   └── session.py        # create_async_engine, AsyncSessionLocal
│       ├── models/models.py      # All ORM models + enums
│       ├── schemas/schemas.py    # All Pydantic v2 schemas
│       ├── crud/crud.py          # All async CRUD + status computation helpers
│       ├── routers/
│       │   ├── closets.py        # /api/closets, /api/shelves, /api/baskets
│       │   ├── inventory.py      # /api/inventory, QR endpoint, scan-by-token
│       │   ├── reminders.py      # /api/reminders (wash + seasonal)
│       │   ├── cleaning.py       # /api/cleaning (per-room checklists + sessions)
│       │   ├── firstaid.py       # /api/firstaid (CPR, kits)
│       │   └── family.py         # /api/family (family member medical info)
│       └── services/
│           ├── mqtt_service.py   # paho client lifecycle + message routing
│           ├── reminder_service.py # APScheduler jobs
│           └── qr_service.py     # QR PNG/SVG generation
└── frontend/
    ├── Dockerfile                # Multi-stage: Node 22 build → nginx:alpine serve
    ├── nginx.conf                # SPA fallback + /api/ reverse proxy
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.js
        ├── api.js                # Axios API client (all endpoints)
        ├── assets/main.css       # Dark-theme design system + utility classes
        ├── router/index.js       # All routes (createWebHistory for QR compatibility)
        ├── stores/
        │   ├── closets.js        # Closet/shelf/basket CRUD state
        │   ├── inventory.js      # Per-basket inventory state
        │   ├── reminders.js      # Wash + seasonal reminders, auto-poll
        │   └── cleaning.js       # Session token management + checklist state
        ├── components/
        │   ├── AppNav.vue        # Sticky navigation
        │   ├── ReminderBanner.vue # Auto-polling active reminder bar
        │   ├── BasketIcon.vue    # Colored tile with status indicator
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
