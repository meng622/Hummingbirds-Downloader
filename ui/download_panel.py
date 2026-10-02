import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QCheckBox, QGroupBox, QFileDialog, QProgressBar,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal

from core.worker import DownloadWorker
from core.cookie_manager import CookieManager
from core.parse_worker import ParseWorker
from ui.preview_dialog import PreviewDialog


class DownloadPanel(QWidget):
    log_message = pyqtSignal(str)
    status_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.worker: DownloadWorker | None = None
        self.parse_worker: ParseWorker | None = None
        self.cookie_manager = CookieManager()
        self._init_ui()
        self._load_cookie_state()

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
        self.danmaku_check.toggled.connect(self._on_danmaku_toggled)
        grid.addWidget(self.danmaku_check, 1, 2)

        self.mux_danmaku_check = QCheckBox("合成彈幕")
        self.mux_danmaku_check.setChecked(True)
        self.mux_danmaku_check.setEnabled(False)
        grid.addWidget(self.mux_danmaku_check, 1, 3)

        grid.addWidget(QLabel("輸出資料夾："), 2, 0)
        self.output_input = QLineEdit()
        self.output_input.setPlaceholderText("預設：./downloads")
        grid.addWidget(self.output_input, 2, 1, 1, 2)

        self.browse_btn = QPushButton("瀏覽…")
        self.browse_btn.clicked.connect(self._on_browse)
        grid.addWidget(self.browse_btn, 2, 3)

        # ---- Cookie 區 ----
        grid.addWidget(QLabel("Cookies："), 3, 0)
        self.cookie_label = QLabel("未匯入")
        self.cookie_label.setStyleSheet("color: #888;")
        grid.addWidget(self.cookie_label, 3, 1, 1, 2)

        cookie_btn_layout = QHBoxLayout()
        self.cookie_import_btn = QPushButton("匯入…")
        self.cookie_import_btn.clicked.connect(self._on_import_cookie)
        cookie_btn_layout.addWidget(self.cookie_import_btn)

        self.cookie_clear_btn = QPushButton("清除")
        self.cookie_clear_btn.clicked.connect(self._on_clear_cookie)
        self.cookie_clear_btn.setEnabled(False)
        cookie_btn_layout.addWidget(self.cookie_clear_btn)

        grid.addLayout(cookie_btn_layout, 3, 3)

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

        self.parse_btn = QPushButton("解析")
        self.parse_btn.clicked.connect(self._on_parse)
        btn_layout.addWidget(self.parse_btn)

        self.download_btn = QPushButton("開始下載")
        self.download_btn.setObjectName("downloadBtn")
        self.download_btn.clicked.connect(self._on_download)
        btn_layout.addWidget(self.download_btn)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._on_cancel)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

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
                "呢個檔案睇落唔似標準 Netscape cookies.txt 格式。\n"
                "yt-dlp 可能會讀唔到。要繼續匯入嗎？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self.cookie_manager.set_cookie_path(path)
        self._load_cookie_state()
        self.log_message.emit(f"[Cookie] 已匯入：{path}")
        self.status_message.emit("Cookie 已載入")

    def _on_clear_cookie(self):
        self.cookie_manager.clear_cookie()
        self._load_cookie_state()
        self.log_message.emit("[Cookie] 已清除")
        self.status_message.emit("Cookie 已清除")

    # ---------- 事件 ----------

    def _on_browse(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇輸出資料夾")
        if folder:
            self.output_input.setText(folder)

    def _on_danmaku_toggled(self, checked: bool):
        self.mux_danmaku_check.setEnabled(checked)
        if not checked:
            self.mux_danmaku_check.setChecked(False)

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

    def _on_parse(self):
        url = self.url_input.text().strip()
        if not url:
            self.log_message.emit("[警告] 請先輸入網址")
            return

        self.log_message.emit(f"[解析] 開始解析：{url}")
        self.status_message.emit("解析中…")
        self.parse_btn.setEnabled(False)

        ytdlp_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "yt-dlp.exe"
        )
        cookie_path = self.cookie_manager.get_cookie_path()

        self.parse_worker = ParseWorker(url, ytdlp_path, cookie_path)
        self.parse_worker.log.connect(self.log_message.emit)
        self.parse_worker.finished_ok.connect(self._on_parse_ok)
        self.parse_worker.finished_err.connect(self._on_parse_err)
        self.parse_worker.start()

    def _on_parse_ok(self, items: list):
        self.status_message.emit("解析完成")
        self.parse_btn.setEnabled(True)

        dlg = PreviewDialog(items, self)
        if dlg.exec() == PreviewDialog.DialogCode.Accepted:
            if dlg.selected_urls:
                self.url_input.setText(dlg.selected_urls[0])
                self.log_message.emit(
                    f"[解析] 已選 {len(dlg.selected_urls)} 條，"
                    f"而家填入第一條，撳「開始下載」"
                )
                if len(dlg.selected_urls) > 1:
                    self.log_message.emit(
                        "[提示] 多條下載功能（C）尚未實作，"
                        "目前只會下載第一條"
                    )

    def _on_parse_err(self, msg: str):
        self.status_message.emit("解析失敗")
        self.log_message.emit(f"[錯誤] {msg}")
        self.parse_btn.setEnabled(True)

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
        self.parse_btn.setEnabled(not running)
        self.cancel_btn.setEnabled(running)
        self.url_input.setEnabled(not running)
        self.platform_combo.setEnabled(not running)
        self.resolution_combo.setEnabled(not running)
        self.subtitle_combo.setEnabled(not running)
        self.danmaku_check.setEnabled(not running)
        self.browse_btn.setEnabled(not running)
        self.cookie_import_btn.setEnabled(not running)
        self.cookie_clear_btn.setEnabled(not running and bool(self.cookie_manager.get_cookie_path()))

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