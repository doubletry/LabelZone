import json
from urllib.parse import urlencode

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .i18n import MESSAGES, translate
from .models import (
    Annotation,
    AnnotationCreate,
    Dataset,
    DatasetCreate,
    ExportJob,
    ExportRequest,
    Image,
    ImageCreate,
    JobStatus,
    TrainingJob,
    TrainingJobCreate,
)
from .storage import LocalStorageAdapter

settings = get_settings()
storage = LocalStorageAdapter(settings.local_storage_root)
app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATASETS: dict[str, Dataset] = {}
IMAGES: dict[str, Image] = {}
ANNOTATIONS: dict[str, Annotation] = {}
EXPORTS: dict[str, ExportJob] = {}
TRAINING_JOBS: dict[str, TrainingJob] = {}


@app.get("/api/health")
def health(locale: str = Query(default=settings.default_locale)) -> dict[str, str]:
    return {"status": "ok", "message": translate(locale, "health.ok")}


@app.get("/api/i18n/{locale}")
def i18n(locale: str) -> dict[str, str]:
    if locale not in MESSAGES:
        raise HTTPException(status_code=404, detail="locale is not supported")
    return MESSAGES[locale]


@app.get("/api/auth/providers")
def auth_providers() -> dict[str, object]:
    providers = [provider.model_dump(exclude={"token_url", "userinfo_url"}) for provider in settings.oauth2_providers]
    return {"providers": providers, "message": translate(settings.default_locale, "auth.no_provider") if not providers else "ok"}


@app.get("/api/auth/oauth/{provider_name}/login")
def oauth_login(provider_name: str, state: str = "labelzone") -> dict[str, str]:
    provider = next((item for item in settings.oauth2_providers if item.name == provider_name), None)
    if provider is None:
        raise HTTPException(status_code=404, detail="OAuth2 provider is not configured")
    query = urlencode(
        {
            "client_id": provider.client_id,
            "redirect_uri": str(provider.redirect_uri),
            "response_type": "code",
            "scope": " ".join(provider.scopes),
            "state": state,
        }
    )
    return {"authorization_url": f"{provider.authorization_url}?{query}"}


@app.get("/api/auth/oauth/{provider_name}/callback")
def oauth_callback(provider_name: str, code: str | None = None, state: str | None = None) -> dict[str, str | None]:
    if not code:
        raise HTTPException(status_code=400, detail="authorization code is required")
    if not any(item.name == provider_name for item in settings.oauth2_providers):
        raise HTTPException(status_code=404, detail="OAuth2 provider is not configured")
    return {"status": "received", "provider": provider_name, "state": state}


@app.get("/api/storage/health")
def storage_health(locale: str = Query(default=settings.default_locale)) -> dict[str, object]:
    rustfs_configured = bool(settings.rustfs_endpoint and settings.rustfs_bucket)
    backend = "rustfs" if settings.storage_backend == "rustfs" and rustfs_configured else "local"
    message_key = "storage.rustfs" if backend == "rustfs" else "storage.local"
    return {"backend": backend, "available": True, "message": translate(locale, message_key)}


@app.post("/api/datasets", response_model=Dataset)
def create_dataset(payload: DatasetCreate) -> Dataset:
    dataset = Dataset(**payload.model_dump())
    DATASETS[dataset.id] = dataset
    return dataset


@app.get("/api/datasets", response_model=list[Dataset])
def list_datasets() -> list[Dataset]:
    return list(DATASETS.values())


@app.post("/api/datasets/{dataset_id}/images", response_model=Image)
def add_image(dataset_id: str, payload: ImageCreate) -> Image:
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="dataset not found")
    relative_path = f"datasets/{dataset_id}/images/{payload.filename}"
    try:
        uri = storage.save_base64(relative_path, payload.content_base64)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    image = Image(dataset_id=dataset_id, filename=payload.filename, file_uri=uri, width=payload.width, height=payload.height, checksum=payload.checksum)
    IMAGES[image.id] = image
    return image


@app.get("/api/datasets/{dataset_id}/images", response_model=list[Image])
def list_images(dataset_id: str) -> list[Image]:
    return [image for image in IMAGES.values() if image.dataset_id == dataset_id]


@app.put("/api/annotations/{image_id}", response_model=Annotation)
def upsert_annotation(image_id: str, payload: AnnotationCreate) -> Annotation:
    if image_id not in IMAGES or payload.image_id != image_id:
        raise HTTPException(status_code=404, detail="image not found")
    annotation = Annotation(**payload.model_dump())
    ANNOTATIONS[image_id] = annotation
    return annotation


@app.get("/api/annotations/{image_id}", response_model=Annotation)
def get_annotation(image_id: str) -> Annotation:
    annotation = ANNOTATIONS.get(image_id)
    if annotation is None:
        raise HTTPException(status_code=404, detail="annotation not found")
    return annotation


def _build_export(dataset_id: str, export_format: str) -> str:
    images = [image for image in IMAGES.values() if image.dataset_id == dataset_id]
    annotations = [annotation for annotation in ANNOTATIONS.values() if annotation.image_id in {image.id for image in images}]
    content = json.dumps(
        {
            "format": export_format,
            "images": [image.model_dump(mode="json") for image in images],
            "annotations": [annotation.model_dump(mode="json") for annotation in annotations],
        },
        ensure_ascii=False,
        indent=2,
    )
    return storage.save_text(f"datasets/{dataset_id}/exports/{export_format}.json", content)


@app.post("/api/datasets/{dataset_id}/exports", response_model=ExportJob)
def create_export(dataset_id: str, payload: ExportRequest) -> ExportJob:
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="dataset not found")
    job = ExportJob(dataset_id=dataset_id, format=payload.format, status=JobStatus.running)
    job.artifact_uri = _build_export(dataset_id, payload.format)
    job.status = JobStatus.succeeded
    EXPORTS[job.id] = job
    return job


@app.get("/api/exports/{export_id}", response_model=ExportJob)
def get_export(export_id: str) -> ExportJob:
    job = EXPORTS.get(export_id)
    if job is None:
        raise HTTPException(status_code=404, detail="export not found")
    return job


@app.post("/api/training-jobs", response_model=TrainingJob)
def create_training_job(payload: TrainingJobCreate) -> TrainingJob:
    if payload.dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="dataset not found")
    message = translate(payload.locale, "training.created")
    job = TrainingJob(dataset_id=payload.dataset_id, model=payload.model, epochs=payload.epochs, message=message)
    TRAINING_JOBS[job.id] = job
    return job


@app.get("/api/training-jobs/{job_id}", response_model=TrainingJob)
def get_training_job(job_id: str) -> TrainingJob:
    job = TRAINING_JOBS.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="training job not found")
    return job


@app.post("/api/training-jobs/{job_id}/cancel", response_model=TrainingJob)
def cancel_training_job(job_id: str) -> TrainingJob:
    job = get_training_job(job_id)
    job.status = JobStatus.cancelled
    return job
