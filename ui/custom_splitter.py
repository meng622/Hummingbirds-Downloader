from PyQt6.QtWidgets import QSplitter, QSplitterHandle
from PyQt6.QtGui import QPainter, QColor, QBrush
from PyQt6.QtCore import Qt, QRectF, QPointF


class CustomSplitterHandle(QSplitterHandle):
    """自訂 Splitter Handle：一條圓角粗線 + 中間三點，hover 變藍。"""

    COLOR_LINE = QColor("#3a3a3a")
    COLOR_DOTS = QColor("#7a7a82")
    COLOR_HOVER = QColor("#0e639c")
    COLOR_HOVER_DOT = QColor("#ffffff")

    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        self.setMouseTracking(True)

    def enterEvent(self, event):
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        hovered = self.underMouse()

        painter.fillRect(rect, Qt.GlobalColor.transparent)

        if hovered:
            line_color = self.COLOR_HOVER
            dot_color = self.COLOR_HOVER_DOT
        else:
            line_color = self.COLOR_LINE
            dot_color = self.COLOR_DOTS

        # 畫圓角粗線（垂直）
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(line_color))

        line_width = 7
        x = (rect.width() - line_width) / 2
        y = rect.height() * 0.05
        h = rect.height() * 0.9
        painter.drawRoundedRect(QRectF(x, y, line_width, h), line_width / 2, line_width / 2)

        # 畫中間三點
        cx = (rect.width() - 4) / 2 + 2
        cy = (rect.height() - 4) / 2 + 2
        painter.setBrush(QBrush(dot_color))
        for offset in [-7, 0, 7]:
            painter.drawEllipse(QPointF(cx, cy + offset), 2.0, 2.0)


class CustomSplitter(QSplitter):
    """自訂 Splitter，用 CustomSplitterHandle。"""

    def createHandle(self):
        return CustomSplitterHandle(self.orientation(), self)