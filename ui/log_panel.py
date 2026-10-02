from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPlainTextEdit, QPushButton
)
from PyQt6.QtGui import QFont


class LogPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 標題列
        header = QHBoxLayout()
        header.addWidget(QLabel("執行日誌"))
        header.addStretch()

        self.clear_btn = QPushButton("清除")
        self.clear_btn.clicked.connect(self.clear_log)
        header.addWidget(self.clear_btn)

        layout.addLayout(header)

        # 日誌本體
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Consolas", 9))
        self.log_view.setPlaceholderText("日誌會顯示喺呢度…")
        layout.addWidget(self.log_view)

    def append_log(self, text: str):
        self.log_view.appendPlainText(text)

    def clear_log(self):
        self.log_view.clear()