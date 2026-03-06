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
    build_combo_widget,
    fill_input_devices_combo,
    fill_output_devices_combo,
    make_double,
    make_row,
    make_section,
    make_spinbox,
)
from core.services.audio_worker import PreacherMonitorWorker


class PreacherAudioPage(QWidget):
    def __init__(self, app_state: AppState, preacher_audio: PreacherMonitorWorker):
        super().__init__()
        self._app_state = app_state
        self._preacher_audio = preacher_audio

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

        title = QLabel("Preacher Audio")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        root.addWidget(title)
        root.addSpacing(8)

        # Main Content
        _layout = QHBoxLayout()
        # Preacher Input Device Field
        preacher_input_device_select = build_combo_widget(
            "Preacher Input Device",
            "Choose an input device",
            self.on_preacher_input_changed,
            fill_input_devices_combo,
        )
        _layout.addLayout(preacher_input_device_select)

        # Preacher Output Device Field
        preacher_output_device_select = build_combo_widget(
            "Preacher Output Device",
            "Choose an output device",
            self.on_preacher_output_changed,
            fill_output_devices_combo,
        )
        _layout.addLayout(preacher_output_device_select)

        # Action button:
        start_preacher_audio_btn = QPushButton("Start Preacher Audio")
        start_preacher_audio_btn.clicked.connect(lambda: self._preacher_audio.start())
        root.addWidget(start_preacher_audio_btn)

        stop_preacher_audio_btn = QPushButton("Stop Preacher Audio")
        stop_preacher_audio_btn.clicked.connect(lambda: self._preacher_audio.stop())
        root.addWidget(stop_preacher_audio_btn)

        outer.addLayout(_layout)

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
