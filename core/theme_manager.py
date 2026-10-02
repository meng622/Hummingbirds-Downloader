import os
import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette
from PyQt6.QtCore import QSettings


THEME_SYSTEM = "system"
THEME_LIGHT = "light"
THEME_DARK = "dark"


class ThemeManager:
    """管理應用程式主題（跟隨系統 / 淺色 / 深色）。"""

    def __init__(self, app: QApplication):
        self.app = app
        self.settings = QSettings("VideoDownloader", "Theme")
        self.assets_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets"
        )
        self._current_mode = self.settings.value("mode", THEME_SYSTEM)

    def current_mode(self) -> str:
        return self._current_mode

    def apply(self, mode: str | None = None):
        if mode is not None:
            self._current_mode = mode
            self.settings.setValue("mode", mode)

        if self._current_mode == THEME_SYSTEM:
            actual = self._detect_system_theme()
        else:
            actual = self._current_mode

        qss_path = os.path.join(self.assets_dir, f"{actual}.qss")
        if not os.path.isfile(qss_path):
            self.app.setStyleSheet("")
            return

        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                qss = f.read()

            # 將 {ASSETS} 替換成實際 assets 資料夾嘅絕對路徑
            assets_path = self.assets_dir.replace("\\", "/")
            qss = qss.replace("{ASSETS}", assets_path)

            self.app.setStyleSheet(qss)
        except Exception:
            self.app.setStyleSheet("")

    @staticmethod
    def _detect_system_theme() -> str:
        try:
            from PyQt6.QtCore import Qt
            hints = QApplication.styleHints()
            scheme = hints.colorScheme()
            if scheme == Qt.ColorScheme.Dark:
                return THEME_DARK
            elif scheme == Qt.ColorScheme.Light:
                return THEME_LIGHT
        except Exception:
            pass

        try:
            palette = QApplication.palette()
            bg = palette.color(QPalette.ColorRole.Window)
            if bg.lightness() < 128:
                return THEME_DARK
        except Exception:
            pass

        if sys.platform.startswith("win"):
            try:
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                )
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                return THEME_LIGHT if value == 1 else THEME_DARK
            except Exception:
                pass

        return THEME_LIGHT