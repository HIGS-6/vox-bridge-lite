from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QStackedWidget, QWidget

from core.app_state import AppState
from core.gui.pages.broadcast_page import BroadcastPage
from core.gui.pages.logs_page import LogsPage
from core.gui.pages.preacher_audio_page import PreacherAudioPage
from core.gui.pages.translator_audio_page import TranslatorAudioPage
from core.gui.widgets.side_panel import SidePanel
from core.services.audio_worker import PreacherMonitorWorker, TranslatorWorker
from core.services.broadcast_worker import BroadcastWorker

LITE_WORKERS = ["Preacher Audio", "Translator Audio", "Broadcast"]


class MainWindow(QWidget):
    _show_signal = Signal()  # bridge: gui_ready comes from worker thread

    def __init__(
        self,
        app_state: AppState,
        preacher_audio: PreacherMonitorWorker,
        translator_audio: TranslatorWorker,
        broadcast_worker: BroadcastWorker,
    ):
        super().__init__()
        self._app_state = app_state
        # Workers:
        self.preacher_audio = preacher_audio
        self.translator_audio = translator_audio
        self.broadcast_worker = broadcast_worker

        self.setWindowTitle("Vox Bridge - (Lite)")
        self.resize(900, 600)
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._side = SidePanel(workers=LITE_WORKERS)
        self._side.tab_changed.connect(self._on_tab_changed)
        self._side.exit_clicked.connect(self.close)
        root.addWidget(self._side)

        self._stack = QStackedWidget()
        for worker in LITE_WORKERS:
            self._stack.addWidget(self._make_page(worker))
        root.addWidget(self._stack)

        self._side.select(LITE_WORKERS[0])

    def _make_page(self, worker: str) -> QWidget:
        match worker:
            case "Preacher Audio":
                return PreacherAudioPage(self._app_state, self.preacher_audio)
            case "Translator Audio":
                return TranslatorAudioPage(self._app_state, self.translator_audio)
            case "Broadcast":
                return BroadcastPage(self._app_state, self.broadcast_worker)
            case "Logs":
                return LogsPage(self._app_state)
            case _:
                from PySide6.QtCore import Qt
                from PySide6.QtWidgets import QLabel

                p = QWidget()
                lbl = QLabel(worker)
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                QHBoxLayout(p).addWidget(lbl)
                return p

    def _on_tab_changed(self, worker: str):
        self._stack.setCurrentIndex(LITE_WORKERS.index(worker))
