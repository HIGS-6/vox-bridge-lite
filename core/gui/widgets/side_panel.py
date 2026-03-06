from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class WorkerTab(QPushButton):
    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self.setText(label)
        self.setCheckable(True)
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class SidePanel(QWidget):
    tab_changed = Signal(str)  # emits worker name
    exit_clicked = Signal()

    def __init__(self, workers: list[str], parent=None):
        super().__init__(parent)
        self._workers = workers
        self._tabs: dict[str, WorkerTab] = {}
        self.setFixedWidth(220)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 24, 16, 24)
        root.setSpacing(0)

        # ── Div 1: Logo + title + version ─────────────────────
        div1 = QWidget()
        div1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        d1 = QVBoxLayout(div1)
        d1.setContentsMargins(0, 0, 0, 0)
        d1.setSpacing(2)

        # Logo placeholder — swap for QLabel with QPixmap when ready
        logo = QLabel("▣")
        logo.setFont(QFont("Segoe UI", 28))
        logo.setAlignment(Qt.AlignmentFlag.AlignLeft)

        title = QLabel("Vox Bridge")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)

        version = QLabel("v0.0.1")
        version.setFont(QFont("Segoe UI", 8))
        version.setStyleSheet("color: #888;")
        version.setAlignment(Qt.AlignmentFlag.AlignLeft)

        d1.addWidget(logo)
        d1.addWidget(title)
        d1.addWidget(version)
        root.addWidget(div1)

        root.addSpacing(32)

        # ── Div 2: Worker tabs ─────────────────────────────────
        div2 = QWidget()
        div2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        d2 = QVBoxLayout(div2)
        d2.setContentsMargins(0, 0, 0, 0)
        d2.setSpacing(4)

        for worker in self._workers:
            tab = WorkerTab(worker)
            tab.clicked.connect(lambda _, w=worker: self._on_tab_clicked(w))
            self._tabs[worker] = tab
            d2.addWidget(tab)

        d2.addStretch()
        root.addWidget(div2)

        # ── Div 3: Exit button ─────────────────────────────────
        div3 = QWidget()
        div3.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        d3 = QVBoxLayout(div3)
        d3.setContentsMargins(0, 0, 0, 0)

        btn_exit = QPushButton("Exit")
        btn_exit.setFixedHeight(40)
        btn_exit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_exit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_exit.clicked.connect(self.exit_clicked.emit)

        d3.addWidget(btn_exit)
        root.addWidget(div3)

    def _on_tab_clicked(self, worker: str):
        for name, tab in self._tabs.items():
            tab.setChecked(name == worker)
        self.tab_changed.emit(worker)

    def select(self, worker: str):
        """Programmatically select a tab."""
        self._on_tab_clicked(worker)
