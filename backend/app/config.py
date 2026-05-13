from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class OAuth2Provider(BaseModel):
    """Configurable enterprise OAuth2/OIDC provider metadata."""

    name: str
    display_name: str
    authorization_url: HttpUrl
    token_url: HttpUrl
    userinfo_url: HttpUrl
    client_id: str
    redirect_uri: HttpUrl
    scopes: list[str] = Field(default_factory=lambda: ["openid", "profile", "email"])
    username_claim: str = "preferred_username"
    email_claim: str = "email"
    display_name_claim: str = "name"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LABELZONE_", env_nested_delimiter="__")

    app_name: str = "LabelZone"
    default_locale: Literal["en", "zh-CN"] = "zh-CN"
    local_storage_root: Path = Path("./data")
    storage_backend: Literal["local", "rustfs"] = "local"
    rustfs_endpoint: str | None = None
    rustfs_bucket: str | None = None
    public_base_url: str = "http://localhost:8000"
    oauth2_providers: list[OAuth2Provider] = Field(default_factory=list)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.local_storage_root.mkdir(parents=True, exist_ok=True)
    return settings
