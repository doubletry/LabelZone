import base64
import binascii
from pathlib import Path


class LocalStorageAdapter:
    """Local filesystem storage with URI output used by private deployments."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _safe_path(self, relative_path: str) -> Path:
        target = (self.root / relative_path).resolve()
        if not str(target).startswith(str(self.root)):
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
