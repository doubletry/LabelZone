import sqlite3
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from .models import Annotation, Dataset, ExportJob, Image, TrainingJob

ModelT = TypeVar("ModelT", bound=BaseModel)


class SQLiteRepository:
    """Small SQLite repository used by the API until external services are added."""

    def __init__(self, database_url: str):
        if not database_url.startswith("sqlite:///"):
            raise ValueError("only sqlite:/// database URLs are currently supported")
        self.database_path = database_url.removeprefix("sqlite:///")
        if self.database_path != ":memory:":
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=30)
        connection.row_factory = sqlite3.Row
        return connection

    def init_schema(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS datasets (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS images (
                    id TEXT PRIMARY KEY,
                    dataset_id TEXT NOT NULL,
                    data TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_images_dataset_id ON images(dataset_id);
                CREATE TABLE IF NOT EXISTS annotations (
                    image_id TEXT PRIMARY KEY,
                    id TEXT NOT NULL,
                    data TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS exports (
                    id TEXT PRIMARY KEY,
                    dataset_id TEXT NOT NULL,
                    data TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS training_jobs (
                    id TEXT PRIMARY KEY,
                    dataset_id TEXT NOT NULL,
                    data TEXT NOT NULL
                );
                """
            )

    def _save(self, table: str, model: BaseModel, **columns: str) -> None:
        save_queries = {
            "datasets": "INSERT INTO datasets (id, data) VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET data=excluded.data",
            "images": "INSERT INTO images (id, dataset_id, data) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET dataset_id=excluded.dataset_id, data=excluded.data",
            "exports": "INSERT INTO exports (id, dataset_id, data) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET dataset_id=excluded.dataset_id, data=excluded.data",
            "training_jobs": "INSERT INTO training_jobs (id, dataset_id, data) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET dataset_id=excluded.dataset_id, data=excluded.data",
        }
        query = save_queries[table]
        values = (getattr(model, "id"), model.model_dump_json()) if table == "datasets" else (getattr(model, "id"), columns["dataset_id"], model.model_dump_json())
        with self._connect() as connection:
            connection.execute(query, values)

    def _get(self, table: str, id_column: str, item_id: str, model_type: type[ModelT]) -> ModelT | None:
        get_queries = {
            ("datasets", "id"): "SELECT data FROM datasets WHERE id = ?",
            ("images", "id"): "SELECT data FROM images WHERE id = ?",
            ("annotations", "image_id"): "SELECT data FROM annotations WHERE image_id = ?",
            ("exports", "id"): "SELECT data FROM exports WHERE id = ?",
            ("training_jobs", "id"): "SELECT data FROM training_jobs WHERE id = ?",
        }
        with self._connect() as connection:
            row = connection.execute(get_queries[(table, id_column)], (item_id,)).fetchone()
        return model_type.model_validate_json(row["data"]) if row else None

    def _list(self, table: str, model_type: type[ModelT], where: tuple[str, str] | None = None) -> list[ModelT]:
        list_queries = {
            ("datasets", None): "SELECT data FROM datasets",
            ("images", "dataset_id"): "SELECT data FROM images WHERE dataset_id = ?",
        }
        key = (table, where[0] if where else None)
        params = (where[1],) if where else ()
        with self._connect() as connection:
            rows = connection.execute(list_queries[key], params).fetchall()
        return [model_type.model_validate_json(row["data"]) for row in rows]

    def save_dataset(self, dataset: Dataset) -> None:
        self._save("datasets", dataset)

    def get_dataset(self, dataset_id: str) -> Dataset | None:
        return self._get("datasets", "id", dataset_id, Dataset)

    def list_datasets(self) -> list[Dataset]:
        return self._list("datasets", Dataset)

    def save_image(self, image: Image) -> None:
        self._save("images", image, dataset_id=image.dataset_id)

    def get_image(self, image_id: str) -> Image | None:
        return self._get("images", "id", image_id, Image)

    def list_images(self, dataset_id: str) -> list[Image]:
        return self._list("images", Image, ("dataset_id", dataset_id))

    def save_annotation(self, annotation: Annotation) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO annotations (image_id, id, data) VALUES (?, ?, ?)
                ON CONFLICT(image_id) DO UPDATE SET id=excluded.id, data=excluded.data
                """,
                (annotation.image_id, annotation.id, annotation.model_dump_json()),
            )

    def get_annotation(self, image_id: str) -> Annotation | None:
        return self._get("annotations", "image_id", image_id, Annotation)

    def list_annotations_for_images(self, image_ids: set[str]) -> list[Annotation]:
        if not image_ids:
            return []
        with self._connect() as connection:
            connection.execute("CREATE TEMP TABLE selected_image_ids (image_id TEXT PRIMARY KEY)")
            connection.executemany("INSERT INTO selected_image_ids (image_id) VALUES (?)", [(image_id,) for image_id in image_ids])
            rows = connection.execute(
                """
                SELECT annotations.data
                FROM annotations
                JOIN selected_image_ids ON selected_image_ids.image_id = annotations.image_id
                """
            ).fetchall()
            connection.execute("DROP TABLE selected_image_ids")
        return [Annotation.model_validate_json(row["data"]) for row in rows]

    def save_export(self, job: ExportJob) -> None:
        self._save("exports", job, dataset_id=job.dataset_id)

    def get_export(self, export_id: str) -> ExportJob | None:
        return self._get("exports", "id", export_id, ExportJob)

    def save_training_job(self, job: TrainingJob) -> None:
        self._save("training_jobs", job, dataset_id=job.dataset_id)

    def get_training_job(self, job_id: str) -> TrainingJob | None:
        return self._get("training_jobs", "id", job_id, TrainingJob)
