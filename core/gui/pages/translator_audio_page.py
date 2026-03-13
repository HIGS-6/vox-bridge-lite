from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.app_state import AppState
from core.gui.widgets.utils import (
    build_combo_widget,
    colored_icon,
    fill_input_devices_combo,
    make_col,
)
from core.models.worker_status import WorkerStatus
from core.services.audio.translator_audio_worker import TranslatorAudioWorker


class TranslatorAudioPage(QWidget):
    def __init__(self, app_state: AppState, translator_audio: TranslatorAudioWorker):
        super().__init__()
        self._app_state = app_state
        self._transltor_audio = translator_audio
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
        root.setSpacing(16)

        scroll.setWidget(container)

        # ---- TITLE ----
        title = QLabel("Translator Audio")
        title.setProperty("class", "title")
        root.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft)

        # ---- MAIN CONTENT ----
        main_content = QVBoxLayout()
        main_content.setSpacing(12)

        translator_input_device_select = build_combo_widget(
            "Choose an input device",
            self.on_translator_input_changed,
            fill_input_devices_combo,
        )
        translator_input_device_select_col = make_col(
            label="Translator Input Device",
            hint="Choose an input device",
            widget=translator_input_device_select,
        )
        main_content.addWidget(translator_input_device_select_col)

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

    def _on_start_stop_pressed(self, off: bool):
        if off:
            self._transltor_audio.start()
        else:
            self._transltor_audio.stop()

        if self._transltor_audio.status == WorkerStatus.STOPPED:
            self.stop_btn.setEnabled(False)
            self.stop_btn.setCursor(Qt.CursorShape.ForbiddenCursor)

            self.start_btn.setEnabled(True)
            self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        if self._transltor_audio.status == WorkerStatus.RUNNING:
            self.stop_btn.setEnabled(True)
            self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)

            self.start_btn.setEnabled(False)
            self.start_btn.setCursor(Qt.CursorShape.ForbiddenCursor)

    # Translator Combobox Callback
    def on_translator_input_changed(self, device_index: int):
        if type(device_index) is not int:
            raise TypeError("Device index must be an integer")

        print(f"Selected device: {device_index}")
        self._app_state.audio_settings.device_idx = device_index

        # Restart the broadcast worker
        # self._broadcast_worker.restart()
