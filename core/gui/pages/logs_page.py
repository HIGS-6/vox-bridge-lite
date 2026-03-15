from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.app_state import AppState
from core.gui.widgets.utils import colored_icon
from core.services.logger_worker import LogHandler


class LogsPage(QWidget):
    def __init__(self, app_state: AppState, log_handler: LogHandler):
        super().__init__()
        self._log_handler = log_handler
        self._app_state = app_state
        self._build()

    def _build(self):
        # ---- ROOT PAGE LAYOUT ----
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        # ---- SCROLL AREA ----
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        container = QWidget()
        root = QVBoxLayout(container)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(16)
        scroll.setWidget(container)
        # ---- TITLE ROW ----
        title_row = QHBoxLayout()
        title = QLabel("Logs")
        title.setProperty("class", "title")
        title_row.addWidget(title)
        title_row.addStretch()
        btn_clear = QPushButton("  Clear")
        btn_clear.setIcon(colored_icon("assets/icons/circle_x.svg"))
        btn_clear.clicked.connect(self._clear)
        title_row.addWidget(btn_clear)
        root.addLayout(title_row)
        # ---- MAIN CONTENT ----
        main_content = QVBoxLayout()
        main_content.setSpacing(12)
        self._log_view = QTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setFont(QFont("Courier New", 12))
        self._log_view.setStyleSheet(
            "background-color: #080b10; border: 1px solid #1e2130;"
        )
        # self._log_view.setMinimumHeight(400)
        main_content.addWidget(self._log_view)
        root.addLayout(main_content)
        # root.addStretch()
        # ---- WIRE HANDLER ----
        self._log_handler.new_log.connect(self._append)
        self._log_view.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        # ---- ADD TO PAGE ----
        outer.addWidget(scroll)

    def _append(self, line: str):
        self._log_view.append(line)
        self._log_view.verticalScrollBar().setValue(
            self._log_view.verticalScrollBar().maximum()
        )

    def _clear(self):
        self._log_view.clear()
