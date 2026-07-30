import json
import os
import threading

class Storage:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Storage, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.base_path = "/home/ubuntu/data"
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
        self.cache = {}
        self._initialized = True

    def _get_file_path(self, module):
        return os.path.join(self.base_path, f"{module}.json")

    def _load_data(self, module):
        path = self._get_file_path(module)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_data(self, module, data):
        path = self._get_file_path(module)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_data(self, module):
        if module not in self.cache:
            self.cache[module] = self._load_data(module)
        return self.cache[module]

    def set_data(self, module, guild_id, key, value):
        data = self.get_data(module)
        guild_id_str = str(guild_id)
        if guild_id_str not in data:
            data[guild_id_str] = {}
        data[guild_id_str][key] = value
        self._save_data(module, data)

    def get_setting(self, module, guild_id, key, default=None):
        data = self.get_data(module)
        guild_data = data.get(str(guild_id), {})
        return guild_data.get(key, default)

    def get_guild_data(self, module, guild_id):
        data = self.get_data(module)
        return data.get(str(guild_id), {})

storage = Storage()
