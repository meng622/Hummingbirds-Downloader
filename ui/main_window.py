from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QStatusBar, QLabel, QApplication
)
from PyQt6.QtCore import Qt

from ui.options_panel import OptionsPanel
from ui.queue_panel import QueuePanel
from ui.log_panel import LogPanel
from ui.custom_splitter import CustomSplitter


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("綜合下載器 v0.1")
        self.resize(1100, 700)
        self._init_ui()
        self._init_statusbar()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)

        h_splitter = CustomSplitter(Qt.Orientation.Horizontal)
        h_splitter.setHandleWidth(9)

        self.options_panel = OptionsPanel()
        self.queue_panel = QueuePanel(self.options_panel)
        self.log_panel = LogPanel()

        h_splitter.addWidget(self.options_panel)
        h_splitter.addWidget(self.queue_panel)
        h_splitter.addWidget(self.log_panel)

        h_splitter.setStretchFactor(0, 1)
        h_splitter.setStretchFactor(1, 2)
        h_splitter.setStretchFactor(2, 1)
        h_splitter.setSizes([260, 520, 320])
        h_splitter.setChildrenCollapsible(False)

        layout.addWidget(h_splitter)

        self.options_panel.log_message.connect(self.log_panel.append_log)
        self.queue_panel.log_message.connect(self.log_panel.append_log)
        self.queue_panel.status_message.connect(self._on_status)

    def _init_statusbar(self):
        status = QStatusBar()
        self.setStatusBar(status)

        self.status_label = QLabel("就緒")
        status.addWidget(self.status_label)

    def _on_status(self, msg: str):
        self.status_label.setText(msg)