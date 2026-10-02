from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QLabel
)
from PyQt6.QtCore import Qt

from ui.download_panel import DownloadPanel
from ui.log_panel import LogPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("綜合下載器 v0.1")
        self.resize(900, 650)
        self._init_ui()
        self._init_statusbar()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)

        splitter = QSplitter(Qt.Orientation.Vertical)

        self.download_panel = DownloadPanel()
        self.log_panel = LogPanel()

        splitter.addWidget(self.download_panel)
        splitter.addWidget(self.log_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)

        self.download_panel.log_message.connect(self.log_panel.append_log)

    def _init_statusbar(self):
        status = QStatusBar()
        self.setStatusBar(status)
        self.status_label = QLabel("就緒")
        status.addWidget(self.status_label)

        self.download_panel.status_message.connect(self.status_label.setText)