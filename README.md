# LabelZone

LabelZone is a private bilingual image annotation platform for enterprise environments.

## Features

- Enterprise OAuth2/OIDC SSO configuration hooks
- Chinese and English UI
- Local storage by default with RustFS-compatible deployment hooks
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
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

### Docker Compose

```bash
docker compose up --build
```

## Tests and smoke checks

```bash
cd backend && pytest && python scripts/smoke_test.py
cd frontend && npm test && npm run build && npm run smoke
```

## Private deployment notes

For offline deployment, pre-package Docker images, the Python wheelhouse, and the frontend npm cache. Configure `LABELZONE_LOCAL_STORAGE_ROOT` for server-local storage. If object storage is required, configure RustFS-compatible values with `LABELZONE_STORAGE_BACKEND=rustfs`, `LABELZONE_RUSTFS_ENDPOINT`, and `LABELZONE_RUSTFS_BUCKET`.
