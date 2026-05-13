import os
import tempfile

os.environ.setdefault("LABELZONE_DATABASE_URL", f"sqlite:///{tempfile.mkdtemp()}/labelzone-smoke.sqlite3")
os.environ.setdefault("LABELZONE_LOCAL_STORAGE_ROOT", tempfile.mkdtemp())

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

health = client.get("/api/health?locale=zh-CN")
health.raise_for_status()
assert "LabelZone" in health.json()["message"]

dataset = client.post("/api/datasets", json={"name": "smoke-中文"})
dataset.raise_for_status()
dataset_id = dataset.json()["id"]

image = client.post(f"/api/datasets/{dataset_id}/images", json={"filename": "smoke.txt", "content_base64": "5Lit5paH", "width": 1, "height": 1})
image.raise_for_status()

listed = client.get(f"/api/datasets/{dataset_id}/images")
listed.raise_for_status()
assert listed.json()[0]["filename"] == "smoke.txt"

export = client.post(f"/api/datasets/{dataset_id}/exports", json={"format": "yolo_detection"})
export.raise_for_status()
assert export.json()["status"] == "succeeded"

print("Backend smoke test passed: 中文内容正常，SQLite 数据库和存储链路正常")
