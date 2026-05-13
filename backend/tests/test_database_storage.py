from pathlib import Path

from app.database import SQLiteRepository
from app.models import Dataset, Image
from app.storage import RustFSStorageAdapter


class FakeS3Client:
    def __init__(self) -> None:
        self.objects: dict[tuple[str, str], bytes] = {}

    def put_object(self, Bucket: str, Key: str, Body: bytes, **_: object) -> None:
        self.objects[(Bucket, Key)] = Body

    def head_object(self, Bucket: str, Key: str) -> None:
        if (Bucket, Key) not in self.objects:
            raise KeyError(Key)


def test_sqlite_repository_persists_dataset_and_image(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path}/labelzone.sqlite3"
    repository = SQLiteRepository(database_url)
    dataset = Dataset(name="中文数据库")
    repository.save_dataset(dataset)
    image = Image(dataset_id=dataset.id, filename="a.txt", file_uri="local://a.txt", width=1, height=1)
    repository.save_image(image)

    reloaded = SQLiteRepository(database_url)
    assert reloaded.get_dataset(dataset.id).name == "中文数据库"
    assert reloaded.list_images(dataset.id)[0].filename == "a.txt"


def test_rustfs_storage_adapter_writes_s3_compatible_objects() -> None:
    client = FakeS3Client()
    storage = RustFSStorageAdapter("http://rustfs:9000", "labelzone", "admin", "password", client=client)
    uri = storage.save_base64("datasets/1/images/a.txt", "5Lit5paH")
    export_uri = storage.save_text("datasets/1/exports/coco.json", '{"name":"中文"}')

    assert uri == "rustfs://labelzone/datasets/1/images/a.txt"
    assert client.objects[("labelzone", "datasets/1/images/a.txt")] == "中文".encode()
    assert storage.exists(export_uri)
