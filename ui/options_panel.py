import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QCheckBox, QGroupBox,
    QFileDialog, QMessageBox, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal

from core.cookie_manager import CookieManager


class OptionsPanel(QWidget):
    """左欄：下載選項。"""

    log_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.cookie_manager = CookieManager()
        self._init_ui()
        self._load_cookie_state()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(8, 8, 8, 8)

        # 網址
        layout.addWidget(QLabel("影片網址："))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("貼上影片或播放列表連結…")
        layout.addWidget(self.url_input)

        # 選項群組
        options_group = QGroupBox("下載選項")
        grid = QGridLayout(options_group)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        grid.addWidget(QLabel("平台："), 0, 0)
        self.platform_combo = QComboBox()
        self.platform_combo.addItems([
            "自動偵測", "YouTube", "Instagram", "Facebook", "Bilibili", "X (Twitter)", "其他"
        ])
        grid.addWidget(self.platform_combo, 0, 1)

        grid.addWidget(QLabel("分辨率："), 1, 0)
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "最佳畫質", "2160p (4K)", "1440p (2K)", "1080p", "720p", "480p", "360p", "僅音訊 (MP3)"
        ])
        grid.addWidget(self.resolution_combo, 1, 1)

        grid.addWidget(QLabel("字幕："), 2, 0)
        self.subtitle_combo = QComboBox()
        self.subtitle_combo.addItems([
            "不下載", "自動", "繁體中文", "簡體中文", "英文", "日文"
        ])
        grid.addWidget(self.subtitle_combo, 2, 1)

        self.danmaku_check = QCheckBox("下載彈幕 (Bilibili)")
        grid.addWidget(self.danmaku_check, 3, 0, 1, 2)

        self.mux_danmaku_check = QCheckBox("合成彈幕/字幕")
        self.mux_danmaku_check.setChecked(True)
        grid.addWidget(self.mux_danmaku_check, 4, 0, 1, 2)

        layout.addWidget(options_group)

        # 輸出資料夾
        output_group = QGroupBox("輸出資料夾")
        out_layout = QGridLayout(output_group)
        self.output_input = QLineEdit()
        self.output_input.setPlaceholderText("預設：./downloads")
        out_layout.addWidget(self.output_input, 0, 0, 1, 2)

        self.browse_btn = QPushButton("瀏覽…")
        self.browse_btn.clicked.connect(self._on_browse)
        out_layout.addWidget(self.browse_btn, 1, 0)

        self.open_folder_btn = QPushButton("打開資料夾")
        self.open_folder_btn.clicked.connect(self._on_open_folder)
        out_layout.addWidget(self.open_folder_btn, 1, 1)

        layout.addWidget(output_group)

        # Cookies
        cookie_group = QGroupBox("Cookies")
        cookie_layout = QVBoxLayout(cookie_group)
        self.cookie_label = QLabel("未匯入")
        self.cookie_label.setStyleSheet("color: #888;")
        cookie_layout.addWidget(self.cookie_label)

        cookie_btn_layout = QHBoxLayout()
        self.cookie_import_btn = QPushButton("匯入…")
        self.cookie_import_btn.clicked.connect(self._on_import_cookie)
        cookie_btn_layout.addWidget(self.cookie_import_btn)

        self.cookie_clear_btn = QPushButton("清除")
        self.cookie_clear_btn.clicked.connect(self._on_clear_cookie)
        self.cookie_clear_btn.setEnabled(False)
        cookie_btn_layout.addWidget(self.cookie_clear_btn)

        cookie_layout.addLayout(cookie_btn_layout)
        layout.addWidget(cookie_group)

        layout.addStretch()

    # ---------- Cookie ----------

    def _load_cookie_state(self):
        path = self.cookie_manager.get_cookie_path()
        if path:
            self.cookie_label.setText(f"已載入：{os.path.basename(path)}")
            self.cookie_label.setStyleSheet("color: #2e7d32;")
            self.cookie_clear_btn.setEnabled(True)
        else:
            self.cookie_label.setText("未匯入")
            self.cookie_label.setStyleSheet("color: #888;")
            self.cookie_clear_btn.setEnabled(False)

    def _on_import_cookie(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "選擇 cookies.txt", "", "Cookies 檔案 (*.txt);;所有檔案 (*)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                first_lines = f.read(500)
        except Exception as e:
            QMessageBox.warning(self, "讀取失敗", f"無法讀取檔案：{e}")
            return
        if "Netscape" not in first_lines and "\t" not in first_lines:
            reply = QMessageBox.question(
                self, "格式警告",
                "呢個檔案睇落唔似標準 Netscape cookies.txt 格式。\n要繼續匯入嗎？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        self.cookie_manager.set_cookie_path(path)
        self._load_cookie_state()
        self.log_message.emit(f"[Cookie] 已匯入：{path}")

    def _on_clear_cookie(self):
        self.cookie_manager.clear_cookie()
        self._load_cookie_state()
        self.log_message.emit("[Cookie] 已清除")

    # ---------- 事件 ----------

    def _on_browse(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇輸出資料夾")
        if folder:
            self.output_input.setText(folder)

    def _on_open_folder(self):
        import subprocess
        import sys

        folder = self.output_input.text().strip() or "./downloads"
        folder = os.path.abspath(folder)

        if not os.path.isdir(folder):
            try:
                os.makedirs(folder, exist_ok=True)
            except Exception as e:
                QMessageBox.warning(self, "錯誤", f"無法建立資料夾：{e}")
                return

        try:
            if sys.platform.startswith("win"):
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])
        except Exception as e:
            QMessageBox.warning(self, "錯誤", f"無法打開資料夾：{e}")

    # ---------- 對外 ----------

    def get_options(self) -> dict:
        return {
            "platform": self.platform_combo.currentText(),
            "resolution": self.resolution_combo.currentText(),
            "subtitle": self.subtitle_combo.currentText(),
            "danmaku": self.danmaku_check.isChecked(),
            "mux_danmaku": self.mux_danmaku_check.isChecked(),
            "output_dir": self.output_input.text().strip() or "./downloads",
            "cookie_path": self.cookie_manager.get_cookie_path(),
        }

    def get_url(self) -> str:
        return self.url_input.text().strip()

    def set_url(self, url: str):
        self.url_input.setText(url)

    def set_running(self, running: bool):
        self.url_input.setEnabled(not running)
        self.platform_combo.setEnabled(not running)
        self.resolution_combo.setEnabled(not running)
        self.subtitle_combo.setEnabled(not running)
        self.danmaku_check.setEnabled(not running)
        self.mux_danmaku_check.setEnabled(not running)
        self.browse_btn.setEnabled(not running)
        self.cookie_import_btn.setEnabled(not running)
        self.cookie_clear_btn.setEnabled(not running and bool(self.cookie_manager.get_cookie_path()))