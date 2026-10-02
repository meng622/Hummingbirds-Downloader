from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QCheckBox, QGroupBox
)
from PyQt6.QtCore import pyqtSignal


class DownloadPanel(QWidget):
    log_message = pyqtSignal(str)
    status_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 網址列
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("影片網址："))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("貼上 YouTube / Instagram / Facebook / Bilibili / X 嘅影片連結…")
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # 選項區
        options_group = QGroupBox("下載選項")
        grid = QGridLayout(options_group)
        grid.setHorizontalSpacing(15)
        grid.setVerticalSpacing(10)

        grid.addWidget(QLabel("平台："), 0, 0)
        self.platform_combo = QComboBox()
        self.platform_combo.addItems([
            "自動偵測", "YouTube", "Instagram", "Facebook", "Bilibili", "X (Twitter)", "其他"
        ])
        grid.addWidget(self.platform_combo, 0, 1)

        grid.addWidget(QLabel("分辨率："), 0, 2)
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "最佳畫質", "2160p (4K)", "1440p (2K)", "1080p", "720p", "480p", "360p", "僅音訊 (MP3)"
        ])
        grid.addWidget(self.resolution_combo, 0, 3)

        grid.addWidget(QLabel("字幕："), 1, 0)
        self.subtitle_combo = QComboBox()
        self.subtitle_combo.addItems([
            "不下載", "自動", "繁體中文", "簡體中文", "英文", "日文"
        ])
        grid.addWidget(self.subtitle_combo, 1, 1)

        self.danmaku_check = QCheckBox("下載彈幕 (Bilibili)")
        grid.addWidget(self.danmaku_check, 1, 2, 1, 2)

        grid.addWidget(QLabel("輸出資料夾："), 2, 0)
        self.output_input = QLineEdit()
        self.output_input.setPlaceholderText("預設：./downloads")
        grid.addWidget(self.output_input, 2, 1, 1, 2)

        self.browse_btn = QPushButton("瀏覽…")
        grid.addWidget(self.browse_btn, 2, 3)

        layout.addWidget(options_group)

        # 操作按鈕
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.download_btn = QPushButton("開始下載")
        self.download_btn.setObjectName("downloadBtn")
        btn_layout.addWidget(self.download_btn)

        layout.addLayout(btn_layout)

    def get_options(self) -> dict:
        return {
            "platform": self.platform_combo.currentText(),
            "resolution": self.resolution_combo.currentText(),
            "subtitle": self.subtitle_combo.currentText(),
            "danmaku": self.danmaku_check.isChecked(),
            "output_dir": self.output_input.text().strip() or "./downloads",
        }