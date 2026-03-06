import sys

from PySide6.QtWidgets import QApplication

from core.app_state import AppState
from core.gui.windows.main_window import MainWindow
from core.services.audio_worker import PreacherMonitorWorker, TranslatorWorker
from core.services.broadcast_worker import BroadcastWorker


def main():
    state = AppState()

    broadcast = BroadcastWorker(state)
    translator_audio = TranslatorWorker(state)
    preacher_audio = PreacherMonitorWorker(state)

    # Wire audio chunks → broadcast
    translator_audio.set_chunk_callback(broadcast.push_chunk)

    app = QApplication([])

    win = MainWindow(state, preacher_audio, translator_audio, broadcast)
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
