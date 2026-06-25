import json
from pathlib import Path
from server.config import OUTPUT_DIR

CONFIG_FILE = OUTPUT_DIR / "config.json"


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {
            "provider": "deepseek",
            "model": "deepseek-chat",
            "apiKey": "",
            "baseUrl": "https://api.deepseek.com",
        }
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))


def save_config(data: dict) -> dict:
    CONFIG_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return data
