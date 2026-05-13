# LabelZone Architecture

LabelZone is a private annotation platform with bilingual Chinese/English UI, configurable enterprise OAuth2 SSO, local-first storage, optional RustFS-compatible storage configuration, dataset export jobs, and training job queue APIs.

## Backend

- FastAPI exposes `/api/health`, OAuth2 provider discovery/login URL generation, storage health, datasets, images, annotations, exports, and training jobs.
- The first implementation uses an in-process job model for smoke-tested development. Production deployments can replace this with Redis/Celery/RQ while preserving the API shape.
- Annotation objects support single-label classification, bounding boxes, and polygon-first instance segmentation.

## Storage

Local storage is the default and stores files under `LABELZONE_LOCAL_STORAGE_ROOT`. RustFS can be selected through `LABELZONE_STORAGE_BACKEND=rustfs` with `LABELZONE_RUSTFS_ENDPOINT` and `LABELZONE_RUSTFS_BUCKET`; the API reports whether that configuration is active.

## Frontend

The Vue + Element Plus frontend defaults to Chinese and can switch to English. CSS uses CJK-capable fallback fonts so screenshots generated at runtime do not render Chinese text as mojibake or tofu boxes when the host has an appropriate CJK font installed.

## Validation

Run backend tests and smoke test:

```bash
cd backend
python -m pip install -e '.[test]'
pytest
python scripts/smoke_test.py
```

Run frontend unit, build, and smoke checks:

```bash
cd frontend
npm ci
npm test
npm run build
npm run smoke
```
