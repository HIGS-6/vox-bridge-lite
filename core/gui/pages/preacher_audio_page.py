from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from core.app_state import AppState
from core.gui.widgets.utils import (
    build_combo_widget,
    colored_icon,
    fill_input_devices_combo,
    fill_output_devices_combo,
    make_col,
)
from core.models.worker_status import WorkerStatus
from core.services.audio.source_audio_worker import SourceAudioWorker


class PreacherAudioPage(QWidget):
    def __init__(self, app_state: AppState, preacher_audio: SourceAudioWorker):
        super().__init__()
        self._app_state = app_state
        self._preacher_audio = preacher_audio

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
        title = QLabel("Preacher Audio")
        title.setProperty("class", "title")
        root.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft)

        # ---- MAIN CONTENT ----
        main_content = QVBoxLayout()
        main_content.setSpacing(12)

        # Preacher Input Device Field
        preacher_input_device_select = build_combo_widget(
            "Choose an input device",
            self.on_preacher_input_changed,
            fill_input_devices_combo,
        )
        preacher_input_select_col = make_col(
            label="Preacher Input Device",
            hint="Choose an input device",
            widget=preacher_input_device_select,
        )
        main_content.addWidget(preacher_input_select_col)

        # Debajo del combobox de input device
        self._vol_label_row = make_col(
            label="Volume",
            hint="Translator headphone volume",
            widget=self.make_vol_slider(),
        )
        main_content.addWidget(self._vol_label_row)

        # Preacher Output Device Field
        preacher_output_device_select = build_combo_widget(
            "Choose an output device",
            self.on_preacher_output_changed,
            fill_output_devices_combo,
        )
        preacher_output_select_col = make_col(
            label="Preacher Output Device",
            hint="Choose an output device",
            widget=preacher_output_device_select,
        )
        main_content.addWidget(preacher_output_select_col)

        root.addLayout(main_content)
        root.addStretch()

        # ---- BOTTOM CONTROLS (NO SCROLL) ----
        controls = QWidget()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(24, 16, 24, 16)
        controls_layout.setSpacing(12)

        self.start_btn = QPushButton("   Start Preacher Audio")
        self.start_btn.setIcon(colored_icon("assets/icons/start.svg", "#6fa3d8"))
        self.start_btn.setProperty("class", "primary")
        self.start_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.start_btn.clicked.connect(lambda: self._on_start_stop_pressed(True))

        self.stop_btn = QPushButton("    Stop Preacher Audio")
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

    def make_vol_slider(self) -> QSlider:
        self._vol_slider = QSlider(Qt.Orientation.Horizontal)
        self._vol_slider.setRange(0, 100)
        self._vol_slider.setValue(100)
        self._vol_slider.valueChanged.connect(
            lambda v: setattr(self._app_state.audio_settings, "volume", v / 100)
        )
        return self._vol_slider

    def _on_start_stop_pressed(self, off: bool):
        if off:
            self._preacher_audio.start()
        else:
            self._preacher_audio.stop()

        if self._preacher_audio.status == WorkerStatus.STOPPED:
            self.stop_btn.setEnabled(False)
            self.stop_btn.setCursor(Qt.CursorShape.ForbiddenCursor)

            self.start_btn.setEnabled(True)
            self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        if self._preacher_audio.status == WorkerStatus.RUNNING:
            self.stop_btn.setEnabled(True)
            self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)

            self.start_btn.setEnabled(False)
            self.start_btn.setCursor(Qt.CursorShape.ForbiddenCursor)

    # Preacher Combobox Callbacks
    def on_preacher_input_changed(self, device_index: int):
        if type(device_index) is not int:
            raise TypeError("Device index must be an integer")

        print(f"Selected device: {device_index}")
        self._app_state.monitor_settings.input_device_idx = device_index

    def on_preacher_output_changed(self, device_index: int):
        if type(device_index) is not int:
            raise TypeError("Device index must be an integer")

        print(f"Selected device: {device_index}")
        self._app_state.monitor_settings.output_device_idx = device_index
