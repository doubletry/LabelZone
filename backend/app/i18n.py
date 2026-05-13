MESSAGES: dict[str, dict[str, str]] = {
    "en": {
        "app.title": "LabelZone",
        "health.ok": "LabelZone is running",
        "storage.local": "Local storage is available",
        "storage.rustfs": "RustFS-compatible storage is configured",
        "auth.no_provider": "No OAuth2 provider is configured",
        "training.created": "Training job queued",
    },
    "zh-CN": {
        "app.title": "LabelZone 标注平台",
        "health.ok": "LabelZone 正在运行",
        "storage.local": "本地存储可用",
        "storage.rustfs": "RustFS 兼容存储已配置",
        "auth.no_provider": "尚未配置 OAuth2 身份提供方",
        "training.created": "训练任务已入队",
    },
}


def translate(locale: str, key: str) -> str:
    catalog = MESSAGES.get(locale, MESSAGES["en"])
    return catalog.get(key, MESSAGES["en"].get(key, key))
