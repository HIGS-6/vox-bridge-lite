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
    make_double,
    make_row,
    make_section,
    make_spinbox,
)
from core.services.audio_worker import TranslatorWorker


class TranslatorAudioPage(QWidget):
    def __init__(self, app_state: AppState, translator_audio: TranslatorWorker):
        super().__init__()
        self._app_state = app_state
        self._transltor_audio = translator_audio

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

        title = QLabel("Translator Audio")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        root.addWidget(title)
        root.addSpacing(8)

        # Main Content
        _layout = QVBoxLayout()

        # Action buttons
        start_translator_audio_btn = QPushButton("Start Translator Audio")
        start_translator_audio_btn.clicked.connect(
            lambda: self._transltor_audio.start()
        )
        _layout.addWidget(start_translator_audio_btn)

        stop_translator_audio_btn = QPushButton("Stop Translator Audio")
        stop_translator_audio_btn.clicked.connect(lambda: self._transltor_audio.start())
        _layout.addWidget(stop_translator_audio_btn)

        # Input Device Field
        translator_input_device_select = build_combo_widget(
            "Translator Input Device",
            "Choose an input device",
            self.on_translator_input_changed,
            fill_input_devices_combo,
        )
        _layout.addLayout(translator_input_device_select)

        outer.addLayout(_layout)

    # Translator Combobox Callback
    def on_translator_input_changed(self, device_index: int):
        if type(device_index) is not int:
            raise TypeError("Device index must be an integer")

        print(f"Selected device: {device_index}")
        self._app_state.audio_settings.device_idx = device_index

        # Restart the broadcast worker
        # self._broadcast_worker.restart()
