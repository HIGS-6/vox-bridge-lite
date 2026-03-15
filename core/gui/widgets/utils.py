from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.services.audio.utils import list_input_devices, list_output_devices
from core.utils import resource_path


def colored_icon(path: str, color: str = "#fff", size: int = 24) -> QIcon:
    with open(resource_path(path), "r") as f:
        svg = f.read().replace('stroke="currentColor"', f'stroke="{color}"')
    renderer = QSvgRenderer(svg.encode())
    pixmap = QPixmap(QSize(size, size))
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


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


def make_col(label: str, hint: str, widget: QWidget | QLayout) -> QFrame:
    frame = QFrame()
    frame.setFrameShape(QFrame.Shape.StyledPanel)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 12, 16, 12)
    layout.setSpacing(0)

    lbl = QLabel(label)
    lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))

    hint_lbl = QLabel(hint)
    hint_lbl.setFont(QFont("Segoe UI", 9))
    hint_lbl.setStyleSheet("color: #4a5568;")

    layout.addWidget(lbl)
    layout.addWidget(hint_lbl)
    layout.addSpacing(10)

    if isinstance(widget, QWidget):
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(widget)
    elif isinstance(widget, QLayout):
        layout.addLayout(widget)

    return frame


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


def build_combo_widget(placeholder, on_select, on_refresh):
    row = QHBoxLayout()
    row.setSpacing(10)
    row.setContentsMargins(0, 0, 0, 0)

    combo = QComboBox()
    combo.setPlaceholderText(placeholder)
    combo.setCurrentIndex(-1)

    refresh_options_btn = QPushButton("  Refresh")
    refresh_options_btn.setIcon(colored_icon("assets/icons/refresh.svg", "#3d6ea8"))
    refresh_options_btn.setProperty("class", "primary")

    # Add widgets
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
    for index, name in list_output_devices():
        combo.addItem(name, index)
