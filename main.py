import logging
import socket
import sys
from pathlib import Path

from PySide6.QtGui import QFontDatabase, QIcon
from PySide6.QtWidgets import QApplication
from zeroconf import ServiceInfo, Zeroconf

from core.app_state import AppState
from core.gui.windows.main_window import MainWindow
from core.services.audio.source_audio_worker import SourceAudioWorker
from core.services.audio.translator_audio_worker import TranslatorAudioWorker
from core.services.broadcast_worker import BroadcastWorker, get_local_ip
from core.services.logger_worker import LogHandler
from core.utils import resource_path


def register_mdns(port: int) -> Zeroconf:
    zc = Zeroconf()
    ip = get_local_ip()
    info = ServiceInfo(
        "_http._tcp.local.",
        "vox-bridge._http._tcp.local.",
        addresses=[socket.inet_aton(ip)],
        port=port,
        properties={},
        server="vox-bridge.local.",
    )
    zc.register_service(info)
    return zc  # guarda la referencia para hacer unregister al cerrar


def main():
    state = AppState()

    broadcast = BroadcastWorker(state)
    translator_audio = TranslatorAudioWorker(state)
    preacher_audio = SourceAudioWorker(state)
    translator_audio.set_chunk_callback(broadcast.push_chunk)

    app = QApplication([])

    # Después de crear QApplication, antes de MainWindow
    log_handler = LogHandler()
    logging.getLogger().addHandler(log_handler)
    logging.getLogger().setLevel(logging.DEBUG)

    app_icon = QIcon(resource_path("assets/images/vox_bridge_logo.png"))

    app.setWindowIcon(app_icon)
    app.setApplicationName("Vox Bridge")
    app.setApplicationDisplayName("Vox Bridge")
    app.setApplicationVersion("v0.1.0")

    QFontDatabase.addApplicationFont(resource_path("assets/fonts/cinzel.ttf"))
    qss = Path(resource_path("assets/styles/theme.qss")).read_text()

    app.setStyleSheet(qss)

    win = MainWindow(state, log_handler, preacher_audio, translator_audio, broadcast)
    win.show()

    zc = register_mdns(state.broadcast_settings.webclient_port)

    zc.unregister_all_services()
    zc.close()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
