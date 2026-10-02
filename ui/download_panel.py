import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QCheckBox, QGroupBox, QFileDialog, QProgressBar
)
from PyQt6.QtCore import pyqtSignal

from core.worker import DownloadWorker


class DownloadPanel(QWidget):
    log_message = pyqtSignal(str)
    status_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.worker: DownloadWorker | None = None
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
        self.browse_btn.clicked.connect(self._on_browse)
        grid.addWidget(self.browse_btn, 2, 3)

        layout.addWidget(options_group)

        # 進度區
        progress_group = QGroupBox("下載進度")
        p_layout = QGridLayout(progress_group)
        p_layout.setHorizontalSpacing(15)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        p_layout.addWidget(self.progress_bar, 0, 0, 1, 3)

        self.speed_label = QLabel("速度：—")
        self.eta_label = QLabel("剩餘：—")
        self.size_label = QLabel("大小：—")
        p_layout.addWidget(self.speed_label, 1, 0)
        p_layout.addWidget(self.eta_label, 1, 1)
        p_layout.addWidget(self.size_label, 1, 2)

        layout.addWidget(progress_group)

        # 操作按鈕
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.download_btn = QPushButton("開始下載")
        self.download_btn.setObjectName("downloadBtn")
        self.download_btn.clicked.connect(self._on_download)
        btn_layout.addWidget(self.download_btn)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._on_cancel)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

    # ---------- 事件 ----------

    def _on_browse(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇輸出資料夾")
        if folder:
            self.output_input.setText(folder)

    def _on_download(self):
        if self.worker and self.worker.isRunning():
            self.log_message.emit("[警告] 已有下載進行中")
            return

        url = self.url_input.text().strip()
        if not url:
            self.log_message.emit("[警告] 請先輸入網址")
            return

        options = self.get_options()
        self.log_message.emit(f"[下載] 開始：{url}")
        self.log_message.emit(f"[下載] 選項：{options}")

        self._set_running(True)
        self.progress_bar.setValue(0)
        self.status_message.emit("下載中…")

        self.worker = DownloadWorker(url, options)
        self.worker.log.connect(self.log_message.emit)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished_ok.connect(self._on_finished_ok)
        self.worker.finished_err.connect(self._on_finished_err)
        self.worker.start()

    def _on_cancel(self):
        if self.worker and self.worker.isRunning():
            self.log_message.emit("[取消] 正在終止下載…")
            self.worker.cancel()

    def _on_progress(self, percent: float, speed: str, eta: str, downloaded: str, total: str):
        self.progress_bar.setValue(int(percent))
        self.speed_label.setText(f"速度：{speed}")
        self.eta_label.setText(f"剩餘：{eta}")
        self.size_label.setText(f"大小：{downloaded} / {total}")

    def _on_finished_ok(self, msg: str):
        self.log_message.emit(f"[完成] {msg}")
        self.status_message.emit("完成")
        self.progress_bar.setValue(100)
        self._set_running(False)

    def _on_finished_err(self, msg: str):
        self.log_message.emit(f"[錯誤] {msg}")
        self.status_message.emit("失敗")
        self._set_running(False)

    # ---------- 狀態切換 ----------

    def _set_running(self, running: bool):
        self.download_btn.setEnabled(not running)
        self.cancel_btn.setEnabled(running)
        self.url_input.setEnabled(not running)
        self.platform_combo.setEnabled(not running)
        self.resolution_combo.setEnabled(not running)
        self.subtitle_combo.setEnabled(not running)
        self.danmaku_check.setEnabled(not running)
        self.browse_btn.setEnabled(not running)

    # ---------- 對外 ----------

    def get_options(self) -> dict:
        return {
            "platform": self.platform_combo.currentText(),
            "resolution": self.resolution_combo.currentText(),
            "subtitle": self.subtitle_combo.currentText(),
            "danmaku": self.danmaku_check.isChecked(),
            "output_dir": self.output_input.text().strip() or "./downloads",
        }