import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QCheckBox, QGroupBox, QFileDialog, QMessageBox,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import pyqtSignal, Qt, QSize

from core.cookie_manager import CookieManager
from core.parse_worker import ParseWorker
from core.task_queue import Task, TaskQueue
from ui.preview_dialog import PreviewDialog
from ui.task_item_widget import TaskItemWidget


class DownloadPanel(QWidget):
    log_message = pyqtSignal(str)
    status_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.cookie_manager = CookieManager()
        self.parse_worker: ParseWorker | None = None
        self.task_queue = TaskQueue()
        self.task_widgets: dict[int, TaskItemWidget] = {}
        self._init_ui()
        self._connect_queue()
        self._load_cookie_state()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("影片網址："))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("貼上 YouTube / Instagram / Facebook / Bilibili / X 嘅影片或播放列表連結…")
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

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

        # 任務列表
        queue_group = QGroupBox("下載佇列")
        queue_layout = QVBoxLayout(queue_group)

        self.task_list = QListWidget()
        self.task_list.setAlternatingRowColors(True)
        self.task_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        queue_layout.addWidget(self.task_list)

        queue_btn_layout = QHBoxLayout()
        queue_btn_layout.addStretch()

        self.start_all_btn = QPushButton("全部下載")
        self.start_all_btn.clicked.connect(self._on_start_all)
        queue_btn_layout.addWidget(self.start_all_btn)

        self.clear_done_btn = QPushButton("清除已完成")
        self.clear_done_btn.clicked.connect(self._on_clear_done)
        queue_btn_layout.addWidget(self.clear_done_btn)

        self.clear_all_btn = QPushButton("清除所有任務")
        self.clear_all_btn.clicked.connect(self._on_clear_all)
        queue_btn_layout.addWidget(self.clear_all_btn)

        self.cancel_all_btn = QPushButton("全部取消")
        self.cancel_all_btn.clicked.connect(self._on_cancel_all)
        queue_btn_layout.addWidget(self.cancel_all_btn)

        queue_layout.addLayout(queue_btn_layout)
        layout.addWidget(queue_group)

        # 操作按鈕
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.parse_btn = QPushButton("解析")
        self.parse_btn.clicked.connect(self._on_parse)
        btn_layout.addWidget(self.parse_btn)

        self.add_queue_btn = QPushButton("加入佇列")
        self.add_queue_btn.clicked.connect(self._on_add_to_queue)
        btn_layout.addWidget(self.add_queue_btn)

        self.download_btn = QPushButton("開始下載")
        self.download_btn.setObjectName("downloadBtn")
        self.download_btn.clicked.connect(self._on_download)
        btn_layout.addWidget(self.download_btn)

        self.cancel_btn = QPushButton("取消當前")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._on_cancel)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

    # ---------- 佇列連接 ----------

    def _connect_queue(self):
        self.task_queue.task_added.connect(self._on_task_added)
        self.task_queue.task_updated.connect(self._on_task_updated)
        self.task_queue.task_finished.connect(self._on_task_finished)
        self.task_queue.task_removed.connect(self._on_task_removed)
        self.task_queue.all_finished.connect(self._on_all_finished)
        self.task_queue.log.connect(self.log_message.emit)

    def _on_task_added(self, idx: int, task: Task):
        widget = TaskItemWidget(task.url)
        widget.pause_clicked.connect(lambda i=idx: self._on_pause_task(i))
        widget.resume_clicked.connect(lambda i=idx: self._on_resume_task(i))
        widget.delete_clicked.connect(lambda i=idx: self._on_delete_task(i))
        item = QListWidgetItem()
        item.setSizeHint(QSize(0, 56))
        self.task_list.addItem(item)
        self.task_list.setItemWidget(item, widget)
        self.task_widgets[idx] = widget
        self._refresh_task_widget(idx, task)

    def _on_task_updated(self, idx: int, task: Task):
        self._refresh_task_widget(idx, task)

    def _refresh_task_widget(self, idx: int, task: Task):
        widget = self.task_widgets.get(idx)
        if widget is None:
            return
        state_map = {
            Task.STATE_WAITING: "waiting",
            Task.STATE_RUNNING: "running",
            Task.STATE_PAUSED: "paused",
            Task.STATE_DONE: "done",
            Task.STATE_FAILED: "failed",
            Task.STATE_CANCELLED: "cancelled",
        }
        state = state_map.get(task.state, "waiting")
        if task.state == Task.STATE_RUNNING:
            text = f"[{task.progress:.1f}%] {task.url}"
        elif task.state == Task.STATE_DONE:
            text = task.url
        elif task.state == Task.STATE_PAUSED:
            text = f"[已暫停] {task.url}"
        else:
            text = task.url
        widget.set_state(state, text)

    def _on_task_finished(self, idx: int, task: Task, success: bool):
        self._refresh_task_widget(idx, task)

    def _on_task_removed(self, idx: int):
        self._rebuild_task_list()

    def _rebuild_task_list(self):
        self.task_list.clear()
        self.task_widgets.clear()
        for idx, task in enumerate(self.task_queue.tasks):
            widget = TaskItemWidget(task.url)
            widget.pause_clicked.connect(lambda i=idx: self._on_pause_task(i))
            widget.resume_clicked.connect(lambda i=idx: self._on_resume_task(i))
            widget.delete_clicked.connect(lambda i=idx: self._on_delete_task(i))
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 56))
            self.task_list.addItem(item)
            self.task_list.setItemWidget(item, widget)
            self.task_widgets[idx] = widget
            self._refresh_task_widget(idx, task)

    def _on_all_finished(self):
        self._set_running(False)
        self.status_message.emit("全部完成")

    # ---------- 任務操作 ----------

    def _on_pause_task(self, idx: int):
        self.task_queue.pause_task(idx)

    def _on_resume_task(self, idx: int):
        self.task_queue.resume_task(idx)

    def _on_delete_task(self, idx: int):
        reply = QMessageBox.question(
            self, "確認刪除",
            f"確定要刪除任務 #{idx + 1} 嗎？\n（如果正在下載，會立即取消）",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.task_queue.remove_task(idx)
        self.log_message.emit(f"[佇列] 刪除任務 #{idx + 1}")

    def _on_start_all(self):
        if not self.task_queue.tasks:
            self.log_message.emit("[警告] 佇列係空嘅")
            return
        self._set_running(True)
        self.task_queue.start_all()

    def _on_clear_all(self):
        if not self.task_queue.tasks:
            return
        reply = QMessageBox.question(
            self, "確認清除",
            f"確定要清除全部 {len(self.task_queue.tasks)} 條任務嗎？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.task_queue.clear_all()
        self.task_list.clear()
        self.task_widgets.clear()
        self._set_running(False)
        self.log_message.emit("[佇列] 已清除所有任務")

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

    def _on_danmaku_toggled(self, checked: bool):
        self.mux_danmaku_check.setEnabled(checked)
        if not checked:
            self.mux_danmaku_check.setChecked(False)

    def _on_add_to_queue(self):
        url = self.url_input.text().strip()
        if not url:
            self.log_message.emit("[警告] 請先輸入網址")
            return
        options = self.get_options()
        self.task_queue.add_task(url, options)
        self.status_message.emit("已加入佇列")

    def _on_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.log_message.emit("[警告] 請先輸入網址")
            return
        self._on_add_to_queue()
        if not self.task_queue.is_running:
            self._set_running(True)
            self.task_queue.start()

    def _on_cancel(self):
        self.task_queue.cancel_current()

    def _on_cancel_all(self):
        self.task_queue.cancel_all()
        self._set_running(False)
        self.status_message.emit("已全部取消")

    def _on_clear_done(self):
        self.task_queue.clear_finished()
        self._rebuild_task_list()

    # ---------- 解析 ----------

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
                options = self.get_options()
                for url in dlg.selected_urls:
                    self.task_queue.add_task(url, options)
                self.log_message.emit(
                    f"[解析] 已加入 {len(dlg.selected_urls)} 條任務到佇列"
                )
                if not self.task_queue.is_running:
                    self._set_running(True)
                    self.task_queue.start()

    def _on_parse_err(self, msg: str):
        self.status_message.emit("解析失敗")
        self.log_message.emit(f"[錯誤] {msg}")
        self.parse_btn.setEnabled(True)

    # ---------- 狀態切換 ----------

    def _set_running(self, running: bool):
        self.download_btn.setEnabled(not running)
        self.cancel_btn.setEnabled(running)
        self.url_input.setEnabled(not running)
        self.platform_combo.setEnabled(not running)
        self.resolution_combo.setEnabled(not running)
        self.subtitle_combo.setEnabled(not running)
        self.danmaku_check.setEnabled(not running)
        self.mux_danmaku_check.setEnabled(not running and self.danmaku_check.isChecked())
        self.browse_btn.setEnabled(not running)
        self.cookie_import_btn.setEnabled(not running)
        self.cookie_clear_btn.setEnabled(not running and bool(self.cookie_manager.get_cookie_path()))
        self.parse_btn.setEnabled(not running)
        self.add_queue_btn.setEnabled(not running)

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