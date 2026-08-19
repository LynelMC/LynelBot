import json
import os
from threading import Lock

DATA_FILE = os.path.join(os.path.dirname(__file__), "config.json")
_lock = Lock()


def _load() -> dict:
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _save(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_guild_config(guild_id: int) -> dict:
    with _lock:
        data = _load()
        return data.get(str(guild_id), {})


def set_guild_value(guild_id: int, key: str, value) -> None:
    with _lock:
        data = _load()
        gid = str(guild_id)
        if gid not in data:
            data[gid] = {}
        data[gid][key] = value
        _save(data)


def get_value(guild_id: int, key: str, default=None):
    conf = get_guild_config(guild_id)
    return conf.get(key, default)
