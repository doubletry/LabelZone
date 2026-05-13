# LabelZone Architecture

中文文档：[`architecture.zh-CN.md`](architecture.zh-CN.md)

LabelZone is a private annotation platform with bilingual Chinese/English UI, configurable enterprise OAuth2 SSO, SQLite persistence, local storage, RustFS/S3-compatible object storage, dataset export jobs, and training job queue APIs.

## Backend

- FastAPI exposes `/api/health`, OAuth2 provider discovery/login URL generation, storage health, datasets, images, annotations, exports, and training jobs.
- SQLite stores datasets, images, annotations, export jobs, and training jobs. The API layer uses `SQLiteRepository`, so endpoint behavior survives process restarts as long as the SQLite file is persisted.
- Annotation objects support single-label classification, bounding boxes, and polygon-first instance segmentation.
- Training jobs are persisted as queue records. A production GPU worker can poll or subscribe to this API shape later without changing the frontend contract.

## Database model

The SQLite database is configured with `LABELZONE_DATABASE_URL=sqlite:////data/db/labelzone.sqlite3`. Tables are created automatically:

- `datasets(id, data)`
- `images(id, dataset_id, data)`
- `annotations(image_id, id, data)`
- `exports(id, dataset_id, data)`
- `training_jobs(id, dataset_id, data)`

The `data` column stores validated JSON generated from the Pydantic models. This keeps the first private deployment simple while preserving strongly validated API payloads.

## Storage

- `LABELZONE_STORAGE_BACKEND=local` stores files under `LABELZONE_LOCAL_STORAGE_ROOT` and returns `local://...` URIs.
- `LABELZONE_STORAGE_BACKEND=rustfs` uses the RustFS/S3-compatible adapter backed by boto3 and returns `rustfs://bucket/key` URIs.
- The RustFS adapter writes uploads and export artifacts with S3 `put_object` and checks object existence with `head_object`.

## Frontend

The Vue + Element Plus frontend defaults to Chinese and can switch to English. CSS uses CJK-capable fallback fonts so screenshots generated at runtime do not render Chinese text as mojibake or tofu boxes when the host has an appropriate CJK font installed.

## Deployment topology

Minimal deployment uses two containers and one volume:

1. `backend`: FastAPI + SQLite + local file storage
2. `frontend`: static Vue build served by Nginx, with `/api/` proxied to backend
3. `labelzone-data`: persistent volume for the SQLite file and uploaded artifacts

RustFS deployment adds a third service and switches backend storage variables to RustFS.

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
