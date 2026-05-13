import base64
import binascii
import os
from pathlib import Path
from typing import Protocol

from .config import Settings


class StorageAdapter(Protocol):
    backend: str

    def save_base64(self, relative_path: str, content_base64: str | None) -> str: ...

    def save_text(self, relative_path: str, content: str) -> str: ...

    def exists(self, uri: str) -> bool: ...


class LocalStorageAdapter:
    """Local filesystem storage with URI output used by private deployments."""

    backend = "local"

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _safe_path(self, relative_path: str) -> Path:
        target = (self.root / relative_path).resolve()
        if os.path.commonpath([str(self.root), str(target)]) != str(self.root):
            raise ValueError("path escapes storage root")
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def save_base64(self, relative_path: str, content_base64: str | None) -> str:
        path = self._safe_path(relative_path)
        if content_base64:
            try:
                path.write_bytes(base64.b64decode(content_base64, validate=True))
            except binascii.Error as exc:
                raise ValueError("content_base64 is invalid") from exc
        else:
            path.touch()
        return f"local://{relative_path}"

    def save_text(self, relative_path: str, content: str) -> str:
        path = self._safe_path(relative_path)
        path.write_text(content, encoding="utf-8")
        return f"local://{relative_path}"

    def exists(self, uri: str) -> bool:
        if not uri.startswith("local://"):
            return False
        return self._safe_path(uri.removeprefix("local://")).exists()


class RustFSStorageAdapter:
    """S3-compatible storage adapter for RustFS deployments."""

    backend = "rustfs"

    def __init__(self, endpoint: str, bucket: str, access_key: str, secret_key: str, secure: bool = False, client: object | None = None):
        self.bucket = bucket
        if client is None:
            import boto3
            from botocore.config import Config

            self.client = boto3.client(
                "s3",
                endpoint_url=endpoint,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                use_ssl=secure,
                config=Config(signature_version="s3v4"),
            )
        else:
            self.client = client

    def save_base64(self, relative_path: str, content_base64: str | None) -> str:
        if content_base64:
            try:
                body = base64.b64decode(content_base64, validate=True)
            except binascii.Error as exc:
                raise ValueError("content_base64 is invalid") from exc
        else:
            body = b""
        self.client.put_object(Bucket=self.bucket, Key=relative_path, Body=body)
        return f"rustfs://{self.bucket}/{relative_path}"

    def save_text(self, relative_path: str, content: str) -> str:
        self.client.put_object(Bucket=self.bucket, Key=relative_path, Body=content.encode("utf-8"), ContentType="application/json; charset=utf-8")
        return f"rustfs://{self.bucket}/{relative_path}"

    def exists(self, uri: str) -> bool:
        prefix = f"rustfs://{self.bucket}/"
        if not uri.startswith(prefix):
            return False
        key = uri.removeprefix(prefix)
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
        except Exception:
            return False
        return True


def create_storage_adapter(settings: Settings) -> StorageAdapter:
    if settings.storage_backend == "local":
        return LocalStorageAdapter(settings.local_storage_root)
    missing = [
        name
        for name, value in {
            "LABELZONE_RUSTFS_ENDPOINT": settings.rustfs_endpoint,
            "LABELZONE_RUSTFS_BUCKET": settings.rustfs_bucket,
            "LABELZONE_RUSTFS_ACCESS_KEY": settings.rustfs_access_key,
            "LABELZONE_RUSTFS_SECRET_KEY": settings.rustfs_secret_key,
        }.items()
        if not value
    ]
    if missing:
        raise ValueError(f"RustFS storage requires: {', '.join(missing)}")
    return RustFSStorageAdapter(
        endpoint=settings.rustfs_endpoint or "",
        bucket=settings.rustfs_bucket or "",
        access_key=settings.rustfs_access_key or "",
        secret_key=settings.rustfs_secret_key or "",
        secure=settings.rustfs_secure,
    )
