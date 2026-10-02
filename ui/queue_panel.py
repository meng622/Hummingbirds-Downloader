import os
import sys

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QListWidget, QListWidgetItem, QPushButton, QLabel,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt, QSize

from core.parse_worker import ParseWorker
from core.task_queue import Task, TaskQueue
from ui.preview_dialog import PreviewDialog
from ui.task_item_widget import TaskItemWidget


class QueuePanel(QWidget):
    """中欄：下載佇列 + 當前任務 + 操作按鈕。"""

    log_message = pyqtSignal(str)
    status_message = pyqtSignal(str)

    def __init__(self, options_panel):
        super().__init__()
        self.options_panel = options_panel
        self.parse_worker: ParseWorker | None = None
        self.task_queue = TaskQueue()
        self.task_widgets: dict[int, TaskItemWidget] = {}
        self._init_ui()
        self._connect_queue()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

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
        layout.addWidget(queue_group, stretch=3)

        info_group = QGroupBox("當前任務")
        info_layout = QHBoxLayout(info_group)
        info_layout.setSpacing(30)

        self.speed_label = QLabel("速度：—")
        self.eta_label = QLabel("剩餘：—")
        self.size_label = QLabel("大小：—")

        info_layout.addWidget(self.speed_label)
        info_layout.addWidget(self.eta_label)
        info_layout.addWidget(self.size_label)
        info_layout.addStretch()

        layout.addWidget(info_group, stretch=0)

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

    def _connect_queue(self):
        self.task_queue.task_added.connect(self._on_task_added)
        self.task_queue.task_updated.connect(self._on_task_updated)
        self.task_queue.task_finished.connect(self._on_task_finished)
        self.task_queue.task_removed.connect(self._on_task_removed)
        self.task_queue.all_finished.connect(self._on_all_finished)
        self.task_queue.log.connect(self.log_message.emit)
        self.task_queue.progress_info.connect(self._on_progress_info)

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
        self.speed_label.setText("速度：—")
        self.eta_label.setText("剩餘：—")
        self.size_label.setText("大小：—")

    def _on_progress_info(self, percent: float, speed: str, eta: str, downloaded: str, total: str):
        self.speed_label.setText(f"速度：{speed}")
        self.eta_label.setText(f"剩餘：{eta}")
        self.size_label.setText(f"大小：{downloaded} / {total}")

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

    def _on_add_to_queue(self):
        url = self.options_panel.get_url()
        if not url:
            self.log_message.emit("[警告] 請先輸入網址")
            return
        options = self.options_panel.get_options()
        self.task_queue.add_task(url, options)
        self.status_message.emit("已加入佇列")

    def _on_download(self):
        url = self.options_panel.get_url()
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
        url = self.options_panel.get_url()
        if not url:
            self.log_message.emit("[警告] 請先輸入網址")
            return

        self.log_message.emit(f"[解析] 開始解析：{url}")
        self.status_message.emit("解析中…")
        self.parse_btn.setEnabled(False)

        if getattr(sys, "frozen", False):
            base = os.path.dirname(sys.executable)
            internal = os.path.join(base, "_internal")
            if os.path.isfile(os.path.join(internal, "yt-dlp.exe")):
                ytdlp_path = os.path.join(internal, "yt-dlp.exe")
            else:
                ytdlp_path = os.path.join(base, "yt-dlp.exe")
        else:
            ytdlp_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "yt-dlp.exe"
            )
        cookie_path = self.options_panel.cookie_manager.get_cookie_path()

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
                options = self.options_panel.get_options()
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

    def _set_running(self, running: bool):
        self.download_btn.setEnabled(not running)
        self.cancel_btn.setEnabled(running)
        self.parse_btn.setEnabled(not running)
        self.add_queue_btn.setEnabled(not running)
        self.options_panel.set_running(running)