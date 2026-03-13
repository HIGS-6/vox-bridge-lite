import logging

from PySide6.QtCore import QObject, Signal

LEVEL_ICON = {
    logging.DEBUG: "◌",
    logging.INFO: "●",
    logging.WARNING: "▲",
    logging.ERROR: "✕",
    logging.CRITICAL: "✕",
}

LEVEL_COLOR = {
    logging.DEBUG: "#4a5568",
    logging.INFO: "#6fa3d8",
    logging.WARNING: "#e8a44a",
    logging.ERROR: "#c0554a",
    logging.CRITICAL: "#c0554a",
}


class LogHandler(QObject, logging.Handler):
    new_log = Signal(str)

    def __init__(self):
        QObject.__init__(self)
        logging.Handler.__init__(self)

    def emit(self, record: logging.LogRecord) -> None:  # type: ignore[override]
        try:
            icon = LEVEL_ICON.get(record.levelno, "●")
            color = LEVEL_COLOR.get(record.levelno, "#ddd8cf")
            time = logging.Formatter().formatTime(record, "%H:%M:%S")
            name = record.name.split(".")[-1]
            msg = record.getMessage()
            line = (
                f'<span style="color:{color}; font-family: monospace; font-size: 12px;">[{icon}] </span>'
                f'<span style="color:#4a5568; font-family: monospace; font-size: 12px;">[{time}] [{name}] </span>'
                f'<span style="color:#ddd8cf; font-family: monospace; font-size: 12px;">{msg}</span>'
            )
            self.new_log.emit(line)
        except Exception:
            pass
