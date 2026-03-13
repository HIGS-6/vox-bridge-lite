import io

import qrcode
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.app_state import AppState
from core.gui.widgets.utils import colored_icon
from core.models.worker_status import WorkerStatus
from core.services.broadcast_worker import BroadcastWorker, get_local_ip


class BroadcastPage(QWidget):
    def __init__(self, app_state: AppState, broadcast_worker: BroadcastWorker):
        super().__init__()
        self._app_state = app_state
        self._broadcast_worker = broadcast_worker
        self._build()
        self._on_start_stop_pressed(False)

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
        root.setSpacing(24)
        scroll.setWidget(container)
        # ---- TITLE ----
        title = QLabel("Broadcast")
        title.setProperty("class", "title")
        root.addWidget(title)
        # ---- MAIN CONTENT ----
        main_content = QHBoxLayout()
        main_content.setSpacing(24)
        main_content.addLayout(self._build_clients_col(), stretch=1)
        main_content.addLayout(self._build_qr_col(), stretch=1)
        root.addLayout(main_content)
        root.addStretch()

        # ---- BOTTOM CONTROLS (NO SCROLL) ----
        controls = QWidget()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(24, 16, 24, 16)
        controls_layout.setSpacing(12)

        self.start_btn = QPushButton("    Start Translator Audio")
        self.start_btn.setIcon(colored_icon("assets/icons/start.svg", "#6fa3d8"))
        self.start_btn.setProperty("class", "primary")
        self.start_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.start_btn.clicked.connect(lambda: self._on_start_stop_pressed(True))

        self.stop_btn = QPushButton("    Stop Translator Audio")
        self.stop_btn.setIcon(colored_icon("assets/icons/stop.svg", "#d06860"))
        self.stop_btn.setProperty("class", "danger")
        self.stop_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.stop_btn.clicked.connect(lambda: self._on_start_stop_pressed(False))

        controls_layout.addWidget(self.start_btn, 1)
        controls_layout.addWidget(self.stop_btn, 1)
        controls_layout.addStretch()

        # ---- ADD TO PAGE ----
        outer.addWidget(scroll)
        outer.addWidget(controls)

    def _build_clients_col(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(8)

        lbl = QLabel("Connected Clients")
        lbl.setProperty("class", "section")
        col.addWidget(lbl)

        self._client_list = QListWidget()
        self._client_list.setMinimumHeight(200)
        self._client_list.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._refresh_clients()
        col.addWidget(self._client_list)

        return col

    def _build_qr_col(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(8)
        col.setAlignment(Qt.AlignmentFlag.AlignTop)

        lbl = QLabel("Web Client")
        lbl.setProperty("class", "section")
        col.addWidget(lbl)

        port = self._app_state.broadcast_settings.webclient_port
        ip = get_local_ip()
        url = f"http://{ip}:{port}"

        # QR
        qr_label = QLabel()
        qr_label.setPixmap(self._generate_qr(url))
        qr_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        col.addWidget(qr_label)

        # URL text below QR
        url_lbl = QLabel(url)
        url_lbl.setProperty("class", "value")
        url_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        col.addWidget(url_lbl)

        return col

    def _generate_qr(self, url: str) -> QPixmap:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=6,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#ddd8cf", back_color="#0f1117")

        buf = io.BytesIO()
        img.save(buf)
        buf.seek(0)

        qimage = QImage.fromData(buf.read())
        return QPixmap.fromImage(qimage)

    def _refresh_clients(self):
        self._client_list.clear()
        for client in self._app_state.broadcast_settings.connected_clients:
            self._client_list.addItem(str(client))

    def _on_start_stop_pressed(self, off: bool):
        if off:
            self._broadcast_worker.start()
        else:
            self._broadcast_worker.stop()

        if self._broadcast_worker.status == WorkerStatus.STOPPED:
            self.stop_btn.setEnabled(False)
            self.stop_btn.setCursor(Qt.CursorShape.ForbiddenCursor)

            self.start_btn.setEnabled(True)
            self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        if self._broadcast_worker.status == WorkerStatus.RUNNING:
            self.stop_btn.setEnabled(True)
            self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)

            self.start_btn.setEnabled(False)
            self.start_btn.setCursor(Qt.CursorShape.ForbiddenCursor)
