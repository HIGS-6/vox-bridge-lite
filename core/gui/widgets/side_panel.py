from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.gui.widgets.utils import colored_icon
from core.utils import resource_path


class WorkerTab(QPushButton):
    def __init__(self, label: str, icon: str, parent=None):
        super().__init__(parent)
        self._icon_name = icon
        self.setText("    " + label)
        self.setProperty("class", "tab")
        self.setIcon(colored_icon(f"assets/icons/{self._icon_name}.svg", "#ddd8cf"))
        self.setIconSize(QSize(18, 18))
        self.setCheckable(True)
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked: bool):
        if checked:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.setIcon(colored_icon(f"assets/icons/{self._icon_name}.svg", "#e8a44a"))
        else:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.setIcon(colored_icon(f"assets/icons/{self._icon_name}.svg", "#ddd8cf"))


class SidePanel(QWidget):
    tab_changed = Signal(str)  # emits worker name
    exit_clicked = Signal()

    def __init__(self, workers: list[str], parent=None):
        super().__init__(parent)
        self._workers = workers
        self._tabs: dict[str, WorkerTab] = {}
        self.setFixedWidth(300)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 24, 16, 16)
        root.setSpacing(0)

        # ── Div 1: Logo + title + version ─────────────────────
        div1 = QWidget()
        div1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        d1 = QVBoxLayout(div1)
        d1.setContentsMargins(0, 0, 0, 0)
        d1.setSpacing(1)

        pixmap = QPixmap(resource_path("assets/images/vox_bridge_logo.png"))
        logo = QLabel("")
        logo.setPixmap(
            pixmap.scaled(
                260,
                260,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("VOX BRIDGE")
        title.setObjectName("AppTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        version = QLabel("v0.1.0 (LITE)")
        version.setProperty("class", "section")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)

        d1.addWidget(logo)
        d1.addWidget(title)
        d1.addWidget(version)
        root.addWidget(div1, alignment=Qt.AlignmentFlag.AlignHCenter)

        root.addSpacing(32)

        # ── Div 2: Worker tabs ─────────────────────────────────
        div2 = QWidget()
        div2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        d2 = QVBoxLayout(div2)
        d2.setContentsMargins(0, 0, 0, 0)
        d2.setSpacing(8)

        for worker in self._workers:
            tab = WorkerTab(worker, worker)
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

        btn_exit = QPushButton("  Exit")
        btn_exit.setProperty("class", "danger")
        btn_exit.setIcon(colored_icon("assets/icons/exit.svg", "#c0554a"))
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
