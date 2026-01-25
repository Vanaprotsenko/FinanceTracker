# Finance Tracker

A personal finance tracking application featuring a FastAPI backend, a Telegram bot for easy data entry, and a web-based dashboard.

## 🚀 Features

- **Transaction Tracking**: Log and manage your expenses and income.
- **Telegram Bot**: Quick and easy transaction logging via Telegram.
- **Web Dashboard**: Visualize your financial data (served via FastAPI).
- **Automated Migrations**: Database versioning with Alembic.
- **Dockerized**: Easy deployment with Docker Compose.

## 📁 Project Structure

```text
.
├── alembic/              # Database migration scripts
├── frontend/             # Frontend static files (HTML, CSS, JS)
├── src/                  # Backend source code
│   ├── bot/              # Telegram bot implementation
│   ├── db/               # Database connection and session management
│   ├── models/           # SQLAlchemy database models
│   ├── repositories/     # Data access layer
│   ├── router/           # FastAPI application routes
│   ├── schemas/          # Pydantic data validation schemas
│   ├── services/         # Business logic layer
│   └── main.py           # FastAPI application entry point
├── Dockerfile            # API container specification
├── docker-compose.yml    # Multi-container setup (API, Bot, Postgres)
├── Makefile              # Shortcut commands for migrations
└── requirements.txt      # Python dependencies
```

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Vanilla JS, HTML, CSS
- **Database**: PostgreSQL
- **Bot**: Telegram Bot API
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Deployment**: Docker, Docker Compose

## 🚦 Getting Started

### Local Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd FinanceTracker
   ```

2. **Configure Environment**:
   Create a `.env` file based on the project requirements (include `TELEGRAM_BOT_TOKEN`, `DATABASE_URL`, etc.).

3. **Run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

4. **Apply Migrations**:
   ```bash
   make migrate
   ```

The API and Frontend will be available at `http://localhost:8000`.

### 🌐 Tunneling (SSL)
For creating a tunnel with an SSL certificate (useful for Telegram Webhooks):
```bash
cloudflared tunnel --url http://localhost:8000
```

## 📜 Makefile Commands

- `make migrate`: Run database migrations.
- `make makemigration msg="your message"`: Create a new migration file.