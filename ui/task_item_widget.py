from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal


class TaskItemWidget(QWidget):
    """下載佇列嘅單一任務 widget。"""

    pause_clicked = pyqtSignal()
    resume_clicked = pyqtSignal()
    delete_clicked = pyqtSignal()

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(6)

        self.icon_label = QLabel("⏳")
        self.icon_label.setFixedWidth(24)
        layout.addWidget(self.icon_label)

        self.title_label = QLabel(self.url)
        self.title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.title_label.setWordWrap(False)
        layout.addWidget(self.title_label)

        self.pause_btn = QPushButton("暫停")
        self.pause_btn.setFixedSize(60, 26)
        self.pause_btn.setToolTip("暫停 / 繼續")
        self.pause_btn.clicked.connect(self._on_pause_clicked)
        layout.addWidget(self.pause_btn)

        self.delete_btn = QPushButton("刪除")
        self.delete_btn.setFixedSize(60, 26)
        self.delete_btn.setToolTip("刪除此任務")
        self.delete_btn.clicked.connect(self.delete_clicked.emit)
        layout.addWidget(self.delete_btn)

        self._state = "waiting"

    def set_state(self, state: str, text: str):
        self._state = state
        icon_map = {
            "waiting": "⏳",
            "running": "⬇️",
            "paused": "⏸",
            "done": "✅",
            "failed": "❌",
            "cancelled": "🚫",
        }
        self.icon_label.setText(icon_map.get(state, "•"))
        self.title_label.setText(text)

        if state == "running":
            self.pause_btn.setEnabled(True)
            self.pause_btn.setText("暫停")
            self.pause_btn.setToolTip("暫停")
            self.delete_btn.setEnabled(False)
        elif state == "paused":
            self.pause_btn.setEnabled(True)
            self.pause_btn.setText("繼續")
            self.pause_btn.setToolTip("繼續")
            self.delete_btn.setEnabled(True)
        elif state == "waiting":
            self.pause_btn.setEnabled(False)
            self.delete_btn.setEnabled(True)
        else:
            self.pause_btn.setEnabled(False)
            self.delete_btn.setEnabled(True)

    def get_state(self) -> str:
        return self._state

    def _on_pause_clicked(self):
        if self._state == "running":
            self.pause_clicked.emit()
        elif self._state == "paused":
            self.resume_clicked.emit()