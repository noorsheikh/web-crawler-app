# 🕸️ Web Crawler App

A real-time web crawling and analysis application built with Django Channels, React, and Docker. It allows users to initiate a web crawl, specify allowed/blacklisted domains, and view live crawling stats and records via WebSocket integration.

---

## 🚀 Overview

This project is a full-stack web crawler that allows users to:

- Submit a URL to crawl with a max depth and domain filters.
- Monitor the crawl's progress in real-time through WebSocket-based updates.
- View crawl statistics and individual crawl results via a responsive frontend UI.

The backend is built with Django + Django REST Framework + Channels, while the frontend is built with React, TypeScript, and PrimeReact. The entire application is dockerized for easy local development and testing.

---

## ⚙️ Technologies Used

### Backend

- Python 3
- Django 4.2
- Django REST Framework
- Django Channels + Daphne
- Redis (WebSocket channel layer)
- PostgreSQL
- BeautifulSoup + Requests (for crawling)
- Pytest (testing)
- Pylint (linting)

### Frontend

- React 19
- TypeScript
- Vite
- PrimeReact
- PrimeFlex

### DevOps

- Docker & Docker Compose
- CI/CD Ready Structure (suggested in enhancements)

---

## 🧩 Features

- ✅ Real-time WebSocket integration for crawling status and records
- ✅ Full test coverage using `pytest`
- ✅ Backend code fully documented using Python docstrings
- ✅ Linting with `pylint` to maintain code quality
- ✅ Responsive UI with real-time stats, domain filters, and status tiles
- ✅ Support for depth-based crawling with domain whitelisting/blacklisting

---

## 🐳 Spinning Up with Docker

### 🔧 Prerequisites

Ensure you have the following installed:

- Docker
- Docker Compose

### 📦 Build and Run All Containers

```bash
docker-compose up --build
```

This will:

- Build the backend and frontend images
- Start the Django server (on port 8000)
- Start the React app (on port 5173)
- Start Redis (for channel layer)
- Start PostgreSQL (for persistent data)

## 🖥️ Frontend

The frontend is located in the frontend/ directory and is built with React + TypeScript using Vite for development.

### Run Dev Server (outside Docker)

```bash
cd frontend
npm install
npm run dev
```

### Features

- PrimeReact components and layout
- WebSocket connection to receive real-time crawl updates
- Form for setting URL, max depth, and domain restrictions
- Chips for domain control
- Responsive DataTable for displaying crawl results

##🔧 Backend
The backend is a Django app in the backend/ directory that includes REST endpoints and WebSocket support.

### Run Dev Server (outside Docker)

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
daphne -b 0.0.0.0 -p 8000 crawler.asgi:application
```

### Key Technologies

- Django REST Framework for the API
- Django Channels for WebSocket integration
- Redis for channel layer and caching (see enhancements)
- PostgreSQL as the database

### Testing and Linting

```bash
# Run tests
pytest

# Run linter
pylint backend/
```

## ✨ Enhancements

Here are areas of improvement and ideas for scaling the application:

- **Caching:** Use django-redis to cache crawl results and avoid redundant processing.
- **PostgreSQL Migrations:** Introduce Alembic-style migration tracking for schema evolution. Use Django's built-in \* makemigrations and migrate commands.
- **CI/CD Pipeline:**
  - Set up GitHub Actions or GitLab CI for automated builds
  - Include linting, testing, and deployment steps
  - Run test suite on pull requests and main merges
- **Environment Automation:**
  - Define dev.env and prod.env files for environment config
  - Use Docker Compose overrides for multi-stage environments
- **Rate Limiting & Timeouts:** Add per-domain rate limiting to prevent accidental abuse.
- **Crawl Scheduler:** Add ability to queue crawl tasks for execution on demand or on a schedule.

## 📂 Project Structure

```bash
.
├── backend/              # Django backend
│   ├── crawler/          # Core project (settings, urls, wsgi, asgi)
│   └── manage.py
│   └── .env              # Prod environment variables
│   └── .env.template     # Environment variables template for dev environment
│   └── entrypoint.sh
│   requirements.txt      # Backend Python dependencies
│
├── frontend/             # React frontend
│   ├── src/              # Source files directory for frontend
│   └── package.json
│
├── docker-compose.yml    # Multi-service Docker config
├── README.md             # This file
```

## 🧪 Local Testing Summary

✅ pytest ensures full test coverage for backend
✅ WebSocket is tested manually using websocat and via UI
✅ Frontend tested manually in Vite dev mode
✅ Docker setup tested with all services running in sync
