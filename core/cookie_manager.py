import json
import os
import sys


class CookieManager:
    """記住用戶揀嘅 cookies.txt 路徑。"""

    def __init__(self, config_path: str | None = None):
        if config_path is None:
            if getattr(sys, "frozen", False):
                base = os.path.dirname(sys.executable)
            else:
                base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base, "config.json")
        self.config_path = config_path
        self._config = self._load()

    def _load(self) -> dict:
        if os.path.isfile(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ---------- Cookie ----------

    def get_cookie_path(self) -> str:
        path = self._config.get("cookie_path", "")
        if path and not os.path.isfile(path):
            return ""
        return path

    def set_cookie_path(self, path: str):
        self._config["cookie_path"] = path
        self._save()

    def clear_cookie(self):
        self._config.pop("cookie_path", None)
        self._save()