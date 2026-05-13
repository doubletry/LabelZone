from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class ImageStatus(StrEnum):
    unlabeled = "unlabeled"
    labeling = "labeling"
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"


class JobStatus(StrEnum):
    queued = "queued"
    preparing_dataset = "preparing_dataset"
    waiting_for_gpu = "waiting_for_gpu"
    running = "running"
    uploading_artifacts = "uploading_artifacts"
    succeeded = "succeeded"
    failed = "failed"
    cancelled = "cancelled"


class DatasetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = ""


class Dataset(DatasetCreate):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ImageCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_base64: str | None = None
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    checksum: str | None = None


class Image(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    dataset_id: str
    filename: str
    file_uri: str
    width: int
    height: int
    checksum: str | None = None
    status: ImageStatus = ImageStatus.unlabeled


class BBox(BaseModel):
    x: float = Field(ge=0)
    y: float = Field(ge=0)
    width: float = Field(gt=0)
    height: float = Field(gt=0)


class AnnotationObject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    label_id: str = Field(min_length=1)
    type: Literal["classification", "bbox", "polygon"]
    bbox: BBox | None = None
    polygon: list[tuple[float, float]] | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    attributes: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_shape(self) -> "AnnotationObject":
        if self.type == "bbox" and self.bbox is None:
            raise ValueError("bbox objects require bbox coordinates")
        if self.type == "polygon" and (not self.polygon or len(self.polygon) < 3):
            raise ValueError("polygon objects require at least three points")
        if self.type == "classification" and (self.bbox or self.polygon):
            raise ValueError("classification objects must not include geometry")
        return self


class AnnotationCreate(BaseModel):
    image_id: str
    project_id: str = "default"
    task_type: Literal["classification", "detection", "instance_segmentation"]
    source: Literal["manual", "pre_annotation", "imported"] = "manual"
    objects: list[AnnotationObject] = Field(default_factory=list)

    @field_validator("objects")
    @classmethod
    def validate_single_classification(cls, objects: list[AnnotationObject]) -> list[AnnotationObject]:
        classifications = [obj for obj in objects if obj.type == "classification"]
        if len(classifications) > 1:
            raise ValueError("single-label classification allows only one classification object per image")
        return objects


class Annotation(AnnotationCreate):
    id: str = Field(default_factory=lambda: str(uuid4()))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExportRequest(BaseModel):
    format: Literal["coco", "yolo_detection", "yolo_segmentation", "yolo_classification"]


class ExportJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    dataset_id: str
    format: str
    status: JobStatus = JobStatus.queued
    artifact_uri: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TrainingJobCreate(BaseModel):
    dataset_id: str
    model: str = "yolo11n"
    epochs: int = Field(default=10, ge=1, le=1000)
    locale: Literal["en", "zh-CN"] = "zh-CN"


class TrainingJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    dataset_id: str
    model: str
    epochs: int
    status: JobStatus = JobStatus.queued
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metrics: dict[str, float] = Field(default_factory=dict)
