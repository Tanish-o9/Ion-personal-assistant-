# JARVIS AT SCALE — PRODUCTION DEPLOYMENT GUIDE

## 1. System Requirements & Architecture

JARVIS AT SCALE is designed for deployment on standard Linux virtual machines (Ubuntu 22.04 LTS recommended) or containerized environments.

### Required Infrastructure:
* **API Server**: Python 3.13 / Uvicorn ASGI (`0.0.0.0:8000`)
* **Database**: PostgreSQL 16
* **Cache**: Redis 7
* **Frontend**: React + Vite static bundle served via Nginx or API static file handler

---

## 2. Quickstart with Docker Compose

```bash
# 1. Clone repository
git clone https://github.com/your-org/jarvis.git
cd jarvis

# 2. Copy environment template and configure secrets
cp .env.example .env
nano .env

# 3. Launch PostgreSQL, Redis, and API containers
docker-compose up -d --build

# 4. Check deployment health
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

---

## 3. Production Nginx Reverse Proxy Configuration

```nginx
server {
    listen 80;
    server_name jarvis.yourdomain.com;

    client_max_body_size 10M;

    # Serve React Frontend Static Files
    location / {
        root /app/static;
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Proxy WebSocket connections
    location /ws/ {
        proxy_pass http://127.0.0.1:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
```

---

## 4. Database Backup & Restore

### PostgreSQL Backup:
```bash
docker exec -t jarvis-postgres pg_dump -U jarvis_user jarvis_db > backup_$(date +%F).sql
```

### PostgreSQL Restore:
```bash
cat backup_2026-09-03.sql | docker exec -i jarvis-postgres psql -U jarvis_user -d jarvis_db
```
