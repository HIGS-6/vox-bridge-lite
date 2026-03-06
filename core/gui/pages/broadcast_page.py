from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
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
from core.services.broadcast_worker import BroadcastWorker


class BroadcastPage(QWidget):
    def __init__(self, app_state: AppState, broadcast_worker: BroadcastWorker):
        super().__init__()
        self._app_state = app_state
        self._broadcast_worker = broadcast_worker

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

        title = QLabel("Broadcast")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        root.addWidget(title)
        root.addSpacing(8)

        # Main Content
        _layout = QHBoxLayout()
        # Broadcast Worker
        start_broadcast_btn = QPushButton("Start Broadcast")
        start_broadcast_btn.clicked.connect(lambda: self._broadcast_worker.start())
        root.addWidget(start_broadcast_btn)

        stop_broadcast_btn = QPushButton("Stop Broadcast")
        stop_broadcast_btn.clicked.connect(lambda: self._broadcast_worker.stop())
        root.addWidget(stop_broadcast_btn)

        outer.addLayout(_layout)
