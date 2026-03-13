from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QStackedWidget, QVBoxLayout, QWidget
from qframelesswindow import FramelessWindow

from core.app_state import AppState
from core.gui.pages.broadcast_page import BroadcastPage
from core.gui.pages.logs_page import LogsPage
from core.gui.pages.preacher_audio_page import PreacherAudioPage
from core.gui.pages.translator_audio_page import TranslatorAudioPage
from core.gui.widgets.side_panel import SidePanel
from core.gui.widgets.title_bar import VoxTitleBar
from core.services.audio.source_audio_worker import SourceAudioWorker
from core.services.audio.translator_audio_worker import TranslatorAudioWorker
from core.services.broadcast_worker import BroadcastWorker
from core.services.logger_worker import LogHandler

LITE_WORKERS = ["Preacher Audio", "Translator Audio", "Broadcast", "Logs"]


class MainWindow(FramelessWindow):
    _show_signal = Signal()

    def __init__(
        self,
        app_state: AppState,
        log_handler: LogHandler,
        preacher_audio: SourceAudioWorker,
        translator_audio: TranslatorAudioWorker,
        broadcast_worker: BroadcastWorker,
    ):
        super().__init__()
        self._log_handler = log_handler
        self._app_state = app_state

        self._title_bar = VoxTitleBar(self)
        self.setTitleBar(self._title_bar)

        # Workers:
        self.preacher_audio = preacher_audio
        self.translator_audio = translator_audio
        self.broadcast_worker = broadcast_worker

        self.setWindowTitle("Vox Bridge - (Lite)")
        self.resize(1000, 700)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addWidget(self._title_bar)

        # Contenido horizontal debajo
        content = QWidget()
        root = QHBoxLayout(content)
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

        outer.addWidget(content)
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
                return LogsPage(self._app_state, self._log_handler)
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
