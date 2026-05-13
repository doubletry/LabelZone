import os
import tempfile

os.environ.setdefault("LABELZONE_DATABASE_URL", f"sqlite:///{tempfile.mkdtemp()}/labelzone-test.sqlite3")
os.environ.setdefault("LABELZONE_LOCAL_STORAGE_ROOT", tempfile.mkdtemp())

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_is_bilingual() -> None:
    zh = client.get("/api/health?locale=zh-CN")
    en = client.get("/api/health?locale=en")
    assert zh.status_code == 200
    assert "正在运行" in zh.json()["message"]
    assert en.json()["message"] == "LabelZone is running"


def test_dataset_image_annotation_export_and_training_flow() -> None:
    dataset = client.post("/api/datasets", json={"name": "烟火检测", "description": "中文数据集"}).json()
    image = client.post(
        f"/api/datasets/{dataset['id']}/images",
        json={"filename": "image-001.txt", "content_base64": "5Lit5paH", "width": 640, "height": 480},
    ).json()
    annotation = client.put(
        f"/api/annotations/{image['id']}",
        json={
            "image_id": image["id"],
            "task_type": "instance_segmentation",
            "objects": [{"label_id": "fire", "type": "polygon", "polygon": [[1, 1], [10, 1], [10, 10]]}],
        },
    )
    assert annotation.status_code == 200
    assert client.get(f"/api/datasets/{dataset['id']}/images").json()[0]["filename"] == "image-001.txt"
    export = client.post(f"/api/datasets/{dataset['id']}/exports", json={"format": "coco"}).json()
    assert export["status"] == "succeeded"
    assert export["artifact_uri"].startswith("local://")
    training = client.post("/api/training-jobs", json={"dataset_id": dataset["id"], "locale": "zh-CN"}).json()
    assert training["status"] == "queued"
    assert "已入队" in training["message"]


def test_single_label_classification_rejects_multiple_labels() -> None:
    dataset = client.post("/api/datasets", json={"name": "classification"}).json()
    image = client.post(f"/api/datasets/{dataset['id']}/images", json={"filename": "a.jpg", "width": 10, "height": 10}).json()
    response = client.put(
        f"/api/annotations/{image['id']}",
        json={
            "image_id": image["id"],
            "task_type": "classification",
            "objects": [
                {"label_id": "cat", "type": "classification"},
                {"label_id": "dog", "type": "classification"},
            ],
        },
    )
    assert response.status_code == 422


def test_storage_health_defaults_to_local() -> None:
    response = client.get("/api/storage/health?locale=zh-CN")
    assert response.status_code == 200
    assert response.json()["backend"] == "local"
