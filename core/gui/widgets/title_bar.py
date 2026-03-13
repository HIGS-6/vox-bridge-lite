from PySide6.QtGui import QColor
from qframelesswindow.titlebar import StandardTitleBar


class VoxTitleBar(StandardTitleBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.titleLabel.hide()

        self.minBtn.setNormalColor(QColor("#4a5568"))
        self.minBtn.setHoverColor(QColor("#ddd8cf"))
        self.minBtn.setHoverBackgroundColor(QColor(255, 255, 255, 13))
        self.minBtn.setPressedColor(QColor("#ddd8cf"))
        self.minBtn.setPressedBackgroundColor(QColor(255, 255, 255, 23))

        self.maxBtn.hide()

        self.closeBtn.setNormalColor(QColor("#4a5568"))
        self.closeBtn.setHoverColor(QColor("#c0554a"))
        self.closeBtn.setHoverBackgroundColor(QColor(192, 85, 74, 46))
        self.closeBtn.setPressedColor(QColor("#c0554a"))
        self.closeBtn.setPressedBackgroundColor(QColor(192, 85, 74, 77))

        self.setStyleSheet(
            "StandardTitleBar { background-color: #0a0d13; border-bottom: 1px solid #1e2130; }"
        )
