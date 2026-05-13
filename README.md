# LabelZone

中文文档：[`README.zh-CN.md`](README.zh-CN.md)

LabelZone is a private bilingual image annotation platform for enterprise environments. It includes a FastAPI backend, a Vue + Element Plus frontend, SQLite persistence, local storage, and a RustFS/S3-compatible object storage adapter.

## Features

- Enterprise OAuth2/OIDC SSO configuration hooks
- Chinese and English UI
- SQLite database persistence through `LABELZONE_DATABASE_URL`
- Local storage by default with RustFS-compatible object storage support
- Dataset, image, annotation, export, and training job APIs
- Single-label classification validation
- Bounding box and polygon annotation support
- COCO/YOLO-style export job endpoint
- GPU training queue API surface for integration with a separate training service

## Quick start

### Backend

```bash
cd backend
python -m pip install -e '.[test]'
LABELZONE_DATABASE_URL=sqlite:////tmp/labelzone.sqlite3 \
LABELZONE_LOCAL_STORAGE_ROOT=/tmp/labelzone-files \
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

### Minimal Docker deployment

```bash
docker compose up --build -d
curl http://localhost:8000/api/health?locale=en
open http://localhost:8080
```

This starts:

- backend on `http://localhost:8000`
- frontend on `http://localhost:8080`
- a Docker volume `labelzone-data` containing `/data/db/labelzone.sqlite3` and local uploaded files

### Docker deployment with RustFS

```bash
export LABELZONE_RUSTFS_ACCESS_KEY=<access-key>
export LABELZONE_RUSTFS_SECRET_KEY=<secret-key>
export LABELZONE_RUSTFS_BUCKET=labelzone
docker compose -f docker-compose.yml -f docker-compose.rustfs.yml up --build -d
```

Before production use, create dedicated RustFS credentials, set them through environment variables or a secret manager, and review the bucket policy and network exposure.

## Database configuration

The backend currently supports SQLite database URLs:

```bash
LABELZONE_DATABASE_URL=sqlite:////data/db/labelzone.sqlite3
```

The application creates tables automatically for datasets, images, annotations, exports, and training jobs. Persist `/data/db` as a volume in Docker or back up the SQLite file regularly.

## RustFS configuration

Set these variables to use RustFS/S3-compatible object storage:

```bash
LABELZONE_STORAGE_BACKEND=rustfs
LABELZONE_RUSTFS_ENDPOINT=http://rustfs:9000
LABELZONE_RUSTFS_BUCKET=labelzone
LABELZONE_RUSTFS_ACCESS_KEY=labelzone
LABELZONE_RUSTFS_SECRET_KEY=<secret-key>
LABELZONE_RUSTFS_SECURE=false
```

The adapter writes uploaded images and export artifacts using S3 `put_object` and stores returned URIs as `rustfs://bucket/key`.

## Tests and smoke checks

```bash
cd backend && pytest && python scripts/smoke_test.py
cd frontend && npm test && npm run build && npm run smoke
```

## More documentation

- [`docs/architecture.md`](docs/architecture.md) / [`docs/architecture.zh-CN.md`](docs/architecture.zh-CN.md)
- [`docs/deployment.md`](docs/deployment.md) / [`docs/deployment.zh-CN.md`](docs/deployment.zh-CN.md)
