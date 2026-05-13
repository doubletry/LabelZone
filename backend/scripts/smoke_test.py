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

export = client.post(f"/api/datasets/{dataset_id}/exports", json={"format": "yolo_detection"})
export.raise_for_status()
assert export.json()["status"] == "succeeded"

print("Backend smoke test passed: 中文内容正常")
