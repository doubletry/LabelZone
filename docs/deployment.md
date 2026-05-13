# LabelZone Deployment Guide

中文文档：[`deployment.zh-CN.md`](deployment.zh-CN.md)

This guide explains the smallest practical deployment, database connection, RustFS connection, Docker image builds, and runtime verification.

## 1. Minimal local deployment without Docker

Backend:

```bash
cd backend
python -m pip install -e '.[test]'
LABELZONE_DATABASE_URL=sqlite:////tmp/labelzone/labelzone.sqlite3 \
LABELZONE_LOCAL_STORAGE_ROOT=/tmp/labelzone/files \
LABELZONE_STORAGE_BACKEND=local \
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd frontend
npm ci
npm run dev -- --host 0.0.0.0 --port 5173
```

Verify:

```bash
curl 'http://localhost:8000/api/health?locale=en'
curl 'http://localhost:8000/api/storage/health?locale=en'
```

## 2. Minimal Docker Compose deployment

```bash
docker compose up --build -d
docker compose ps
curl 'http://localhost:8000/api/health?locale=en'
```

Open `http://localhost:8080` for the UI. The backend uses SQLite at `/data/db/labelzone.sqlite3` and local files at `/data/files`, both persisted in the `labelzone-data` Docker volume.

## 3. Build Docker images manually

```bash
docker build -f backend/Dockerfile -t labelzone-backend:local .
docker build -f frontend/Dockerfile -t labelzone-frontend:local .
```

Run manually:

```bash
docker network create labelzone || true
docker volume create labelzone-data

docker run -d --name labelzone-backend --network labelzone \
  -p 8000:8000 \
  -v labelzone-data:/data \
  -e LABELZONE_DATABASE_URL=sqlite:////data/db/labelzone.sqlite3 \
  -e LABELZONE_LOCAL_STORAGE_ROOT=/data/files \
  -e LABELZONE_STORAGE_BACKEND=local \
  labelzone-backend:local

docker run -d --name labelzone-frontend --network labelzone \
  -p 8080:80 \
  labelzone-frontend:local
```

## 4. Database connection

Set a SQLite URL:

```bash
LABELZONE_DATABASE_URL=sqlite:////data/db/labelzone.sqlite3
```

Operational notes:

- Persist the directory that contains the SQLite file.
- Back up the SQLite file before upgrades.
- Stop the backend or use SQLite-safe backup tooling when making filesystem copies.
- The app creates missing tables on startup.

## 5. RustFS connection

Use the RustFS Compose overlay:

```bash
export LABELZONE_RUSTFS_ACCESS_KEY=<access-key>
export LABELZONE_RUSTFS_SECRET_KEY=<secret-key>
export LABELZONE_RUSTFS_BUCKET=labelzone
docker compose -f docker-compose.yml -f docker-compose.rustfs.yml up --build -d
```

Or configure an existing RustFS endpoint:

```bash
LABELZONE_STORAGE_BACKEND=rustfs
LABELZONE_RUSTFS_ENDPOINT=http://rustfs.example.internal:9000
LABELZONE_RUSTFS_BUCKET=labelzone
LABELZONE_RUSTFS_ACCESS_KEY=<access-key>
LABELZONE_RUSTFS_SECRET_KEY=<secret-key>
LABELZONE_RUSTFS_SECURE=false
```

Prepare RustFS before switching production traffic:

1. Create the bucket named by `LABELZONE_RUSTFS_BUCKET`.
2. Create a service account with read/write access to that bucket only.
3. Store credentials in your secret manager, not in source control.
4. Check storage status with `/api/storage/health`.
5. Upload a small test image and create an export to verify `rustfs://...` artifact URIs.

## 6. Offline/private deployment checklist

- Build and save images: `docker save labelzone-backend:local labelzone-frontend:local -o labelzone-images.tar`.
- Mirror Python wheels and npm packages if hosts cannot access the internet.
- Pre-pull or mirror the RustFS image used by `docker-compose.rustfs.yml`.
- Mount persistent volumes for `/data/db`, `/data/files`, and RustFS data.
- Configure OAuth2 provider settings through `LABELZONE_OAUTH2_PROVIDERS` compatible with pydantic-settings nested environment variables.

## 7. Validation commands

```bash
cd backend && pytest && python scripts/smoke_test.py
cd frontend && npm test && npm run build && npm run smoke
curl 'http://localhost:8000/api/health?locale=zh-CN'
curl 'http://localhost:8000/api/storage/health?locale=zh-CN'
```
