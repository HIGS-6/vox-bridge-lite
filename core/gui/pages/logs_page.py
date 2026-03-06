from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.app_state import AppState
from core.gui.widgets.utils import (
    block,
    make_double,
    make_row,
    make_section,
    make_spinbox,
)


class LogsPage(QWidget):
    def __init__(self, app_state: AppState):
        super().__init__()
        self._app_state = app_state

        self._build()

    def _build(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        root = QVBoxLayout(container)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(12)
        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        title = QLabel("Logs")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        root.addWidget(title)
        root.addSpacing(8)

        # Main Content
        _layout = QHBoxLayout()
        lbl = QLabel("Hello, World!")
        _layout.addWidget(lbl)

        outer.addLayout(_layout)
