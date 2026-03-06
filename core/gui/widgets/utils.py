from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.services.audio_worker import get_available_devices, list_input_devices


def make_section(title: str) -> QLabel:
    lbl = QLabel(title.upper())
    lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
    lbl.setStyleSheet("color: #888; letter-spacing: 1px;")
    return lbl


def make_row(label: str, hint: str, widget: QWidget) -> QFrame:
    row = QFrame()
    row.setFrameShape(QFrame.Shape.StyledPanel)
    layout = QHBoxLayout(row)
    layout.setContentsMargins(16, 12, 16, 12)
    layout.setSpacing(16)

    col = QVBoxLayout()
    col.setSpacing(2)
    lbl = QLabel(label)
    lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
    hint_lbl = QLabel(hint)
    hint_lbl.setFont(QFont("Segoe UI", 9))
    hint_lbl.setStyleSheet("color: #888;")
    col.addWidget(lbl)
    col.addWidget(hint_lbl)

    layout.addLayout(col)
    layout.addStretch()
    layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignVCenter)
    return row


def make_spinbox(lo: int, hi: int, on_change) -> QSpinBox:
    w = QSpinBox()
    w.setRange(lo, hi)
    w.setFixedWidth(120)
    w.valueChanged.connect(on_change)
    return w


def make_double(
    lo: float, hi: float, step: float, decimals: int, on_change
) -> QDoubleSpinBox:
    w = QDoubleSpinBox()
    w.setRange(lo, hi)
    w.setSingleStep(step)
    w.setDecimals(decimals)
    w.setFixedWidth(120)
    w.valueChanged.connect(on_change)
    return w


def make_combo(options: list[str], on_change) -> QComboBox:
    w = QComboBox()
    w.setFixedWidth(180)
    w.addItems(options)
    w.currentTextChanged.connect(on_change)
    return w


def make_toggle(on_change) -> QCheckBox:
    w = QCheckBox()
    w.toggled.connect(on_change)
    return w


def block(widgets: list, fn):
    """Block signals on all widgets, run fn(), then unblock."""
    for w in widgets:
        w.blockSignals(True)
    fn()
    for w in widgets:
        w.blockSignals(False)


def build_combo_widget(title, placeholder, on_select, on_refresh):
    row = QHBoxLayout()
    row.setSpacing(10)
    row.setContentsMargins(0, 0, 0, 0)

    label = QLabel(title)

    combo = QComboBox()
    combo.setPlaceholderText(placeholder)
    combo.setCurrentIndex(-1)

    refresh_options_btn = QPushButton("Refresh")

    # Add widgets
    row.addWidget(label)
    row.addWidget(combo, 1)
    row.addWidget(refresh_options_btn)

    combo.currentIndexChanged.connect(on_select)
    refresh_options_btn.clicked.connect(lambda: on_refresh(combo))

    on_refresh(combo)
    return row


def fill_input_devices_combo(combo: QComboBox):
    combo.clear()
    for index, name in list_input_devices():
        combo.addItem(name, index)


def fill_output_devices_combo(combo: QComboBox):
    combo.clear()
    output_devices = get_available_devices()

    if type(output_devices) is dict:
        combo.addItem(output_devices["name"])
    else:
        for d in output_devices:
            combo.addItem(d["name"])
