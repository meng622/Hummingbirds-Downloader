from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt


class PreviewDialog(QDialog):
    """解析預覽對話框。"""

    def __init__(self, items: list[dict], parent=None):
        super().__init__(parent)
        self.items = items
        self.selected_urls: list[str] = []
        self.setWindowTitle("解析結果")
        self.resize(800, 500)
        self._init_ui()
        self._populate()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        self.info_label = QLabel(f"共 {len(self.items)} 條項目")
        layout.addWidget(self.info_label)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["下載", "標題", "時長", "上傳者"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()

        self.select_all_btn = QPushButton("全選")
        self.select_all_btn.clicked.connect(self._on_select_all)
        btn_layout.addWidget(self.select_all_btn)

        self.select_none_btn = QPushButton("全不選")
        self.select_none_btn.clicked.connect(self._on_select_none)
        btn_layout.addWidget(self.select_none_btn)

        btn_layout.addStretch()

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton("開始下載")
        self.ok_btn.setObjectName("downloadBtn")
        self.ok_btn.clicked.connect(self._on_ok)
        btn_layout.addWidget(self.ok_btn)

        layout.addLayout(btn_layout)

    def _populate(self):
        self.table.setRowCount(len(self.items))
        for row, item in enumerate(self.items):
            cb = QCheckBox()
            cb.setChecked(True)
            self.table.setCellWidget(row, 0, cb)

            self.table.setItem(row, 1, QTableWidgetItem(item["title"]))
            self.table.setItem(row, 2, QTableWidgetItem(item["duration"]))
            self.table.setItem(row, 3, QTableWidgetItem(item.get("uploader", "")))

    def _on_select_all(self):
        for row in range(self.table.rowCount()):
            cb = self.table.cellWidget(row, 0)
            if cb:
                cb.setChecked(True)

    def _on_select_none(self):
        for row in range(self.table.rowCount()):
            cb = self.table.cellWidget(row, 0)
            if cb:
                cb.setChecked(False)

    def _on_ok(self):
        self.selected_urls = []
        for row in range(self.table.rowCount()):
            cb = self.table.cellWidget(row, 0)
            if cb and cb.isChecked():
                url = self.items[row]["url"]
                if url:
                    self.selected_urls.append(url)

        if not self.selected_urls:
            QMessageBox.warning(self, "提示", "請至少揀一條片")
            return

        self.accept()