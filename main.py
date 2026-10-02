import os
import sys


# ---------- Portable 路徑處理 ----------
def get_app_dir():
    """攞應用程式所在資料夾（exe 或 .py 同層）。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


APP_DIR = get_app_dir()

# 將所有 Qt 緩存、暫存導向 exe 同層
os.environ["XDG_CACHE_HOME"] = os.path.join(APP_DIR, ".cache")
os.environ["XDG_CONFIG_HOME"] = os.path.join(APP_DIR, ".config")
os.environ["XDG_DATA_HOME"] = os.path.join(APP_DIR, ".local", "share")
os.environ["TMP"] = os.path.join(APP_DIR, ".tmp")
os.environ["TEMP"] = os.path.join(APP_DIR, ".tmp")

# 建立必要資料夾
for d in [
    os.path.join(APP_DIR, ".cache"),
    os.path.join(APP_DIR, ".config"),
    os.path.join(APP_DIR, ".local", "share"),
    os.path.join(APP_DIR, ".tmp"),
    os.path.join(APP_DIR, "downloads"),
]:
    os.makedirs(d, exist_ok=True)

# ---------- 輸出編碼 ----------
if sys.platform.startswith("win") and sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

if sys.platform.startswith("win") and sys.stderr is not None:
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("蜂鳥下載器")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()