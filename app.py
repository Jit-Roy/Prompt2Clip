"""
Prompt2Clip — Desktop UI
Premium PyQt5 interface for the Viral Clip Extractor pipeline.
All icons are hand-crafted inline SVGs — zero emoji / unicode symbols.
Run with: python ui_app.py
"""

import sys
import os
from pathlib import Path
from io import StringIO
from contextlib import redirect_stdout

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QScrollArea, QFrame, QFileDialog,
    QDoubleSpinBox, QSpinBox, QProgressBar, QGroupBox, QGridLayout,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QByteArray, QRectF
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QPainter, QPen, QBrush,
    QLinearGradient, QCursor, QPixmap, QImage,
)
from PyQt5.QtSvg import QSvgRenderer, QSvgWidget


# ─────────────────────────── COLOUR TOKENS ────────────────────────────────

BG_DEEP        = "#0a0c12"
BG_PANEL       = "#111318"
BG_CARD        = "#181c25"
BG_CARD_HOVER  = "#1e2432"
BG_INPUT       = "#1a1f2e"
ACCENT_VIOLET  = "#7c3aed"
ACCENT_CYAN    = "#06b6d4"
ACCENT_GREEN   = "#10b981"
ACCENT_RED     = "#ef4444"
ACCENT_AMBER   = "#f59e0b"
TEXT_PRIMARY   = "#f1f5f9"
TEXT_SECONDARY = "#94a3b8"
TEXT_MUTED     = "#4b5563"
BORDER_DIM     = "#1e2535"
BORDER_BRIGHT  = "#2d3748"
BUBBLE_USER    = "#1d1040"
BUBBLE_BOT     = "#131820"

PHASE_NAMES = [
    "Feature Extraction",
    "Signal Fusion",
    "Candidate Generation",
    "LLM Analysis",
    "Export",
]


# ═══════════════════════════════════════════════════════════════════════════
#  SVG ICON LIBRARY — every icon is a hand-crafted 24×24 SVG string
# ═══════════════════════════════════════════════════════════════════════════

def _svg(body: str, vb: str = "0 0 24 24") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" '
        f'fill="none" stroke-linecap="round" stroke-linejoin="round">'
        f'{body}</svg>'
    )


SVG_AUDIO = _svg(
    '<rect x="2" y="8" width="2" height="8" rx="1" fill="#7c3aed"/>'
    '<rect x="6" y="4" width="2" height="16" rx="1" fill="#7c3aed"/>'
    '<rect x="10" y="6" width="2" height="12" rx="1" fill="#06b6d4"/>'
    '<rect x="14" y="3" width="2" height="18" rx="1" fill="#06b6d4"/>'
    '<rect x="18" y="7" width="2" height="10" rx="1" fill="#7c3aed"/>'
)
SVG_MERGE = _svg(
    '<path d="M3 6h5l3 5h2l3-5h5" stroke="#7c3aed" stroke-width="2"/>'
    '<path d="M3 18h5l3-5h4l3 5h5" stroke="#06b6d4" stroke-width="2"/>'
    '<circle cx="12" cy="12" r="2" fill="#7c3aed"/>'
)
SVG_PIN = _svg(
    '<path d="M12 2a5 5 0 0 1 5 5c0 3.5-5 10-5 10S7 10.5 7 7a5 5 0 0 1 5-5z" '
    'fill="#7c3aed" stroke="#7c3aed" stroke-width="1.5"/>'
    '<circle cx="12" cy="7" r="2" fill="white"/>'
    '<line x1="12" y1="17" x2="12" y2="22" stroke="#06b6d4" stroke-width="2"/>'
)
SVG_ROBOT = _svg(
    '<rect x="5" y="9" width="14" height="10" rx="3" stroke="#7c3aed" stroke-width="2"/>'
    '<rect x="9" y="13" width="2" height="2" rx="1" fill="#06b6d4"/>'
    '<rect x="13" y="13" width="2" height="2" rx="1" fill="#06b6d4"/>'
    '<line x1="12" y1="9" x2="12" y2="6" stroke="#7c3aed" stroke-width="2"/>'
    '<circle cx="12" cy="5" r="1.5" fill="#7c3aed"/>'
    '<line x1="5" y1="14" x2="2" y2="14" stroke="#06b6d4" stroke-width="2"/>'
    '<line x1="19" y1="14" x2="22" y2="14" stroke="#06b6d4" stroke-width="2"/>'
)
SVG_SAVE = _svg(
    '<rect x="3" y="3" width="18" height="18" rx="3" stroke="#7c3aed" stroke-width="2"/>'
    '<path d="M8 3v5h8V3" fill="#7c3aed"/>'
    '<rect x="6" y="13" width="12" height="7" rx="1.5" '
    'stroke="#06b6d4" stroke-width="1.5"/>'
    '<line x1="12" y1="15" x2="12" y2="18" stroke="#06b6d4" stroke-width="1.5"/>'
    '<line x1="10.5" y1="16.5" x2="12" y2="15" stroke="#06b6d4" stroke-width="1.5"/>'
    '<line x1="13.5" y1="16.5" x2="12" y2="15" stroke="#06b6d4" stroke-width="1.5"/>'
)
SVG_FOLDER = _svg(
    '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z" '
    'stroke="#94a3b8" stroke-width="1.8"/>'
    '<line x1="3" y1="12" x2="21" y2="12" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="3 2"/>'
)
SVG_FOLDER_OUT = _svg(
    '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z" '
    'stroke="#94a3b8" stroke-width="1.8"/>'
    '<line x1="12" y1="15" x2="12" y2="11" stroke="#94a3b8" stroke-width="1.8"/>'
    '<polyline points="10,13 12,11 14,13" stroke="#94a3b8" stroke-width="1.8" fill="none"/>'
)
SVG_SEND = _svg(
    '<line x1="22" y1="2" x2="11" y2="13" stroke="white" stroke-width="2"/>'
    '<polygon points="22,2 15,22 11,13 2,9" fill="white"/>'
)
SVG_CHECK_SMALL = _svg(
    '<polyline points="4,12 9,17 20,7" stroke="#10b981" stroke-width="2.5" fill="none"/>'
)
SVG_CROSS_SMALL = _svg(
    '<line x1="5" y1="5" x2="19" y2="19" stroke="#ef4444" stroke-width="2.5"/>'
    '<line x1="19" y1="5" x2="5" y2="19" stroke="#ef4444" stroke-width="2.5"/>'
)
SVG_DOT_GREEN = _svg(
    '<circle cx="12" cy="12" r="6" fill="#10b981"/>'
    '<circle cx="12" cy="12" r="10" fill="none" stroke="#10b98150" stroke-width="2"/>'
)
SVG_DOT_AMBER = _svg(
    '<circle cx="12" cy="12" r="6" fill="#f59e0b"/>'
    '<circle cx="12" cy="12" r="10" fill="none" stroke="#f59e0b50" stroke-width="2"/>'
)
SVG_DOT_RED = _svg(
    '<circle cx="12" cy="12" r="6" fill="#ef4444"/>'
    '<circle cx="12" cy="12" r="10" fill="none" stroke="#ef444450" stroke-width="2"/>'
)
SVG_STAR = _svg(
    '<polygon points="12,2 15.1,8.3 22,9.3 17,14.1 18.2,21 12,17.8 5.8,21 7,14.1 2,9.3 8.9,8.3" '
    'fill="#f59e0b" stroke="#f59e0b" stroke-width="1"/>'
)
SVG_FILM = _svg(
    '<rect x="2" y="4" width="20" height="16" rx="2" stroke="#7c3aed" stroke-width="2"/>'
    '<rect x="6" y="4" width="2" height="16" fill="#7c3aed" opacity="0.4"/>'
    '<rect x="16" y="4" width="2" height="16" fill="#7c3aed" opacity="0.4"/>'
    '<rect x="9" y="8" width="6" height="8" rx="1" fill="#06b6d4" opacity="0.7"/>'
    '<polygon points="11,10 11,14 14,12" fill="white"/>'
)
SVG_SCISSORS = _svg(
    '<circle cx="6" cy="7" r="3" stroke="#06b6d4" stroke-width="2"/>'
    '<circle cx="6" cy="17" r="3" stroke="#06b6d4" stroke-width="2"/>'
    '<line x1="8.5" y1="8.5" x2="21" y2="4" stroke="#7c3aed" stroke-width="2"/>'
    '<line x1="8.5" y1="15.5" x2="21" y2="20" stroke="#7c3aed" stroke-width="2"/>'
)
SVG_TAG = _svg(
    '<path d="M3 3h8l9 9-8 8-9-9V3z" stroke="#06b6d4" stroke-width="1.8"/>'
    '<circle cx="8" cy="8" r="1.5" fill="#06b6d4"/>'
)
SVG_USER = _svg(
    '<circle cx="12" cy="8" r="4" stroke="#7c3aed" stroke-width="2"/>'
    '<path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" stroke="#7c3aed" stroke-width="2"/>'
)
SVG_INFO = _svg(
    '<circle cx="12" cy="12" r="10" fill="#7c3aed20" stroke="#7c3aed" stroke-width="1.8"/>'
    '<line x1="12" y1="16" x2="12" y2="11" stroke="#7c3aed" stroke-width="2"/>'
    '<circle cx="12" cy="8" r="1" fill="#7c3aed"/>'
)

PHASE_SVGS = [SVG_AUDIO, SVG_MERGE, SVG_PIN, SVG_ROBOT, SVG_SAVE]


# ═══════════════════════════════════════════════════════════════════════════
#  SVG RENDER HELPER  — renders SVG string to QPixmap (safe: no C++ objects
#  stored at module level; renderer is created fresh each call)
# ═══════════════════════════════════════════════════════════════════════════

def svg_to_pixmap(svg_str: str, size: int) -> QPixmap:
    """Render an SVG string into a QPixmap of the given square size."""
    renderer = QSvgRenderer(QByteArray(svg_str.encode("utf-8")))
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.Antialiasing)
    renderer.render(painter)
    painter.end()
    return pm


# ═══════════════════════════════════════════════════════════════════════════
#  SVG ICON WIDGET  — uses QLabel + QPixmap (avoids custom paintEvent)
# ═══════════════════════════════════════════════════════════════════════════

class SvgIcon(QLabel):
    """
    Displays an SVG icon as a pre-rendered QPixmap on a QLabel.
    Safe: no custom paintEvent, no C++ objects stored across events.
    """
    def __init__(self, svg_str: str, size: int = 20, parent=None):
        super().__init__(parent)
        self._svg_str = svg_str
        self._size    = size
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignCenter)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent; border: none;")
        self._refresh()

    def set_svg(self, svg_str: str):
        self._svg_str = svg_str
        self._refresh()

    def _refresh(self):
        pm = svg_to_pixmap(self._svg_str, self._size)
        self.setPixmap(pm)


# ═══════════════════════════════════════════════════════════════════════════
#  QSS STYLESHEET
# ═══════════════════════════════════════════════════════════════════════════

APP_STYLE = f"""
QWidget {{
    background-color: {BG_DEEP};
    color: {TEXT_PRIMARY};
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
}}
QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{
    background: {BG_PANEL};
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {TEXT_MUTED};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ background: {BG_PANEL}; height: 6px; border-radius: 3px; }}
QScrollBar::handle:horizontal {{ background: {TEXT_MUTED}; border-radius: 3px; }}

QPushButton {{
    background-color: {ACCENT_VIOLET};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
}}
QPushButton:hover {{ background-color: #6d28d9; }}
QPushButton:pressed {{ background-color: #5b21b6; }}
QPushButton:disabled {{ background-color: {TEXT_MUTED}; color: #6b7280; }}

QPushButton#secondary {{
    background-color: {BG_CARD};
    color: {TEXT_SECONDARY};
    border: 1px solid {BORDER_BRIGHT};
}}
QPushButton#secondary:hover {{
    background-color: {BG_CARD_HOVER};
    color: {TEXT_PRIMARY};
}}

QLineEdit {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_DIM};
    border-radius: 10px;
    padding: 10px 14px;
    selection-background-color: {ACCENT_VIOLET};
}}
QLineEdit:focus {{ border: 1px solid {ACCENT_VIOLET}; }}

QDoubleSpinBox, QSpinBox {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_DIM};
    border-radius: 6px;
    padding: 4px 8px;
}}
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button,
QSpinBox::up-button, QSpinBox::down-button {{
    background: {BORDER_BRIGHT}; border: none; width: 16px;
}}

QProgressBar {{
    background: {BG_INPUT};
    border-radius: 4px;
    color: transparent;
    border: none;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT_VIOLET}, stop:1 {ACCENT_CYAN});
    border-radius: 4px;
}}

QGroupBox {{
    border: 1px solid {BORDER_DIM};
    border-radius: 8px;
    margin-top: 8px;
    padding-top: 10px;
    color: {TEXT_SECONDARY};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
}}
QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 6px; }}
QLabel#muted {{ color: {TEXT_MUTED}; font-size: 11px; }}
"""


# ═══════════════════════════════════════════════════════════════════════════
#  WORKER THREAD
# ═══════════════════════════════════════════════════════════════════════════

class ClipWorker(QThread):
    phase_started  = pyqtSignal(int, str)
    phase_done     = pyqtSignal(int, str)
    phase_failed   = pyqtSignal(int, str, str)
    log_line       = pyqtSignal(str)
    results_ready  = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, video_path, query, settings):
        super().__init__()
        self.video_path = video_path
        self.query      = query
        self.settings   = settings

    def run(self):
        try:
            from main import ClipExtractor
        except Exception as e:
            self.error_occurred.emit(f"Failed to import ClipExtractor:\n{e}")
            return
        try:
            extractor = ClipExtractor(
                audio_weight=self.settings.get("audio_weight", 0.5),
                video_weight=self.settings.get("video_weight", 0.5),
                use_cache=True,
                output_dir=self.settings.get("output_dir", "output"),
            )
        except Exception as e:
            self.error_occurred.emit(f"Initialization error:\n{e}")
            return

        captured_log = []

        def _emit_log(text):
            for line in str(text).split("\n"):
                if line.strip():
                    self.log_line.emit(line)
                    captured_log.append(line)

        def _phase(idx, fn, *args, **kwargs):
            self.phase_started.emit(idx, PHASE_NAMES[idx])
            try:
                class TerminalTee(StringIO):
                    def write(self, s):
                        super().write(s)
                        sys.__stdout__.write(s)
                        sys.__stdout__.flush()
                buf = TerminalTee()
                with redirect_stdout(buf):
                    result = fn(*args, **kwargs)
                if buf.getvalue():
                    _emit_log(buf.getvalue())
                self.phase_done.emit(idx, PHASE_NAMES[idx])
                return result
            except Exception as e:
                self.phase_failed.emit(idx, PHASE_NAMES[idx], str(e))
                raise

        try:
            feats = _phase(0, extractor.extract_features,
                self.video_path, self.settings.get("target_fps", 2))
            if not feats:
                raise RuntimeError("Feature extraction returned empty results.")

            ts, combined, a_sc, v_sc = _phase(
                1, extractor.fuse_signals, feats.get("audio"), feats.get("video"))
            candidates = _phase(2, extractor.generate_candidate_clips,
                ts, combined, feats.get("transcription", []),
                self.settings.get("min_duration", 5),
                self.settings.get("max_duration", 60))
            final = _phase(3, extractor.llm_analysis,
                candidates, self.query, a_sc, v_sc)
            exported = _phase(4, extractor.export_clips, self.video_path, final)

            self.results_ready.emit({
                "video_path": self.video_path,
                "user_query": self.query,
                "clips": final,
                "exported": exported,
                "log": captured_log,
            })
        except Exception:
            import traceback
            self.error_occurred.emit(traceback.format_exc())

    def abort(self):
        self.terminate()


# ═══════════════════════════════════════════════════════════════════════════
#  GRADIENT LABEL  (custom paintEvent — safe because QPixmap approach used)
# ═══════════════════════════════════════════════════════════════════════════

class GradientLabel(QWidget):
    """App title rendered with violet→cyan gradient text via QPainter."""

    def __init__(self, text: str, size: int = 18, parent=None):
        super().__init__(parent)
        self._text = text
        self._font = QFont("Segoe UI", size, QFont.Bold)
        self.setFixedHeight(size + 14)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        grad = QLinearGradient(0, 0, r.width(), 0)
        grad.setColorAt(0.0, QColor(ACCENT_VIOLET))
        grad.setColorAt(0.6, QColor("#a855f7"))
        grad.setColorAt(1.0, QColor(ACCENT_CYAN))
        p.setFont(self._font)
        p.setPen(QPen(QBrush(grad), 0))
        p.drawText(r, Qt.AlignCenter, self._text)
        p.end()


# ═══════════════════════════════════════════════════════════════════════════
#  SPINNER WIDGET
# ═══════════════════════════════════════════════════════════════════════════

class SpinnerWidget(QWidget):
    """Animated gradient arc spinner."""

    def __init__(self, size: int = 20, parent=None):
        super().__init__(parent)
        self._angle = 0
        self._size  = size
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def start(self):
        self._timer.start(28)

    def stop(self):
        self._timer.stop()

    def _tick(self):
        self._angle = (self._angle + 14) % 360
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        s = self._size
        m = 2
        p.setPen(QPen(QColor(BORDER_BRIGHT), 2, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(m, m, s - 2*m, s - 2*m, 0, 360 * 16)
        grad = QLinearGradient(0, 0, s, s)
        grad.setColorAt(0, QColor(ACCENT_VIOLET))
        grad.setColorAt(1, QColor(ACCENT_CYAN))
        p.setPen(QPen(QBrush(grad), 2, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(m, m, s - 2*m, s - 2*m, self._angle * 16, 260 * 16)
        p.end()


# ═══════════════════════════════════════════════════════════════════════════
#  STATUS DOT  — uses SvgIcon (QLabel + QPixmap, safe)
# ═══════════════════════════════════════════════════════════════════════════

class StatusDot(SvgIcon):
    def __init__(self, parent=None):
        super().__init__(SVG_DOT_GREEN, 14, parent)

    def set_state(self, state: str):
        if state == "running":
            self.set_svg(SVG_DOT_AMBER)
        elif state == "error":
            self.set_svg(SVG_DOT_RED)
        else:
            self.set_svg(SVG_DOT_GREEN)


# ═══════════════════════════════════════════════════════════════════════════
#  PHASE CARD
# ═══════════════════════════════════════════════════════════════════════════

class PhaseCard(QFrame):
    STATUS_IDLE    = "idle"
    STATUS_RUNNING = "running"
    STATUS_DONE    = "done"
    STATUS_FAILED  = "failed"

    def __init__(self, idx: int, name: str, svg_str: str, parent=None):
        super().__init__(parent)
        self._status = self.STATUS_IDLE
        self.setObjectName("phaseCard")
        self.setFixedHeight(50)
        self._set_border(BORDER_DIM)

        row = QHBoxLayout(self)
        row.setContentsMargins(12, 6, 12, 6)
        row.setSpacing(12)

        # Phase SVG icon
        self._icon = SvgIcon(svg_str, 20)
        row.addWidget(self._icon)

        # Name
        lbl = QLabel(name)
        lbl.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: 600; background: transparent;")
        row.addWidget(lbl, 1)

        # Right: spinner OR status icon
        self._spinner     = SpinnerWidget(18)
        self._status_icon = SvgIcon(SVG_CHECK_SMALL, 18)
        self._status_icon.hide()
        row.addWidget(self._spinner)
        row.addWidget(self._status_icon)
        self._spinner.hide()

    def _set_border(self, color: str):
        self.setStyleSheet(f"""
            QFrame#phaseCard {{
                background: {BG_CARD};
                border: 1px solid {color};
                border-radius: 10px;
            }}
        """)

    def set_running(self):
        self._status_icon.hide()
        self._spinner.show()
        self._spinner.start()
        self._set_border(ACCENT_VIOLET)

    def set_done(self):
        self._spinner.stop()
        self._spinner.hide()
        self._status_icon.set_svg(SVG_CHECK_SMALL)
        self._status_icon.show()
        self._set_border(ACCENT_GREEN + "66")

    def set_failed(self):
        self._spinner.stop()
        self._spinner.hide()
        self._status_icon.set_svg(SVG_CROSS_SMALL)
        self._status_icon.show()
        self._set_border(ACCENT_RED + "66")

    def reset(self):
        self._spinner.stop()
        self._spinner.hide()
        self._status_icon.hide()
        self._set_border(BORDER_DIM)


# ═══════════════════════════════════════════════════════════════════════════
#  MESSAGE BUBBLE
# ═══════════════════════════════════════════════════════════════════════════

class MessageBubble(QFrame):
    def __init__(self, text: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        outer = QHBoxLayout(self)
        outer.setContentsMargins(4, 3, 4, 3)
        outer.setSpacing(8)

        avatar = SvgIcon(SVG_USER if is_user else SVG_INFO, 22)

        bubble = QFrame()
        bubble.setObjectName("bubble")
        bg     = BUBBLE_USER if is_user else BUBBLE_BOT
        border = ACCENT_VIOLET + "66" if is_user else BORDER_DIM
        bubble.setStyleSheet(f"""
            QFrame#bubble {{
                background: {bg};
                border: 1px solid {border};
                border-radius: 14px;
            }}
        """)
        inner = QVBoxLayout(bubble)
        inner.setContentsMargins(14, 10, 14, 10)

        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lbl.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 13px;"
            "background: transparent; border: none;")
        lbl.setMaximumWidth(520)
        inner.addWidget(lbl)

        if is_user:
            outer.addStretch(1)
            outer.addWidget(bubble)
            outer.addWidget(avatar)
        else:
            outer.addWidget(avatar)
            outer.addWidget(bubble)
            outer.addStretch(1)


class LogBubble(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        row = QHBoxLayout(self)
        row.setContentsMargins(8, 1, 8, 1)
        lbl = QLabel(
            f'<span style="color:{TEXT_MUTED};'
            f'font-family:Consolas,monospace;font-size:10px;">'
            f'{text.replace("<", "&lt;").replace(">", "&gt;")}</span>'
        )
        lbl.setWordWrap(True)
        lbl.setMaximumWidth(580)
        lbl.setTextFormat(Qt.RichText)
        row.addStretch(1)
        row.addWidget(lbl)


# ═══════════════════════════════════════════════════════════════════════════
#  CLIP RESULT CARD
# ═══════════════════════════════════════════════════════════════════════════

class ClipResultCard(QFrame):
    def __init__(self, idx: int, clip: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("clipCard")
        self.setStyleSheet(f"""
            QFrame#clipCard {{
                background: {BG_CARD};
                border: 1px solid {BORDER_DIM};
                border-radius: 12px;
            }}
            QFrame#clipCard:hover {{
                border: 1px solid {ACCENT_VIOLET}88;
                background: {BG_CARD_HOVER};
            }}
        """)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(7)

        # Header
        hdr = QHBoxLayout()
        hdr.setSpacing(8)
        hdr.addWidget(SvgIcon(SVG_FILM, 18))

        num = QLabel(f"Clip #{idx:02d}")
        num.setStyleSheet(
            f"color: {ACCENT_VIOLET}; font-size: 14px; font-weight: 800; background: transparent;")
        hdr.addWidget(num)
        hdr.addStretch()

        start = clip.get("start", clip.get("final_start", 0))
        end   = clip.get("end",   clip.get("final_end",   0))
        dur   = end - start

        tl = QLabel(f"{self._fmt(start)}  ->  {self._fmt(end)}")
        tl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        hdr.addWidget(tl)

        db = QLabel(f" {dur:.1f}s ")
        db.setStyleSheet(f"""
            background: {ACCENT_VIOLET}22; color: {ACCENT_CYAN};
            font-size: 10px; font-weight: 700; border-radius: 4px; padding: 2px 4px;
        """)
        hdr.addWidget(db)
        layout.addLayout(hdr)

        # Score bar
        score = clip.get("llm_interest_score", clip.get("avg_score", 0))
        if score:
            score_row = QHBoxLayout()
            score_row.setSpacing(6)
            score_row.addWidget(SvgIcon(SVG_STAR, 14))
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(int(score * 10))
            bar.setFixedHeight(5)
            bar.setTextVisible(False)
            score_row.addWidget(bar, 1)
            sl = QLabel(f"{score:.1f}/10")
            sl.setStyleSheet(
                f"color: {ACCENT_AMBER}; font-size: 11px; font-weight: 700;")
            score_row.addWidget(sl)
            layout.addLayout(score_row)

        # Transcript
        transcript = clip.get("transcript", "")
        if transcript:
            excerpt = transcript[:160] + ("..." if len(transcript) > 160 else "")
            tx_row = QHBoxLayout()
            tx_row.setSpacing(6)
            tx_row.addWidget(SvgIcon(SVG_SCISSORS, 13))
            txl = QLabel(f'"{excerpt}"')
            txl.setWordWrap(True)
            txl.setStyleSheet(
                f"color: {TEXT_SECONDARY}; font-size: 12px; font-style: italic; background: transparent;")
            tx_row.addWidget(txl, 1)
            layout.addLayout(tx_row)

        # Reason
        reason = clip.get("reason", "")
        if reason:
            rl = QLabel(reason[:130] + ("..." if len(reason) > 130 else ""))
            rl.setWordWrap(True)
            rl.setStyleSheet(
                f"color: {TEXT_MUTED}; font-size: 11px; background: transparent;")
            layout.addWidget(rl)

        # Tags
        tags = clip.get("tags", [])
        if tags:
            tag_row = QHBoxLayout()
            tag_row.setSpacing(5)
            tag_row.addWidget(SvgIcon(SVG_TAG, 13))
            for tag in tags[:6]:
                t = QLabel(f" {tag} ")
                t.setStyleSheet(f"""
                    background: {ACCENT_CYAN}18; color: {ACCENT_CYAN};
                    font-size: 10px; font-weight: 600;
                    border-radius: 4px; padding: 2px 5px;
                """)
                tag_row.addWidget(t)
            tag_row.addStretch()
            layout.addLayout(tag_row)

    @staticmethod
    def _fmt(s: float) -> str:
        m, sec = divmod(int(s), 60)
        return f"{m:02d}:{sec:02d}"


# ═══════════════════════════════════════════════════════════════════════════
#  SEND BUTTON  — round button with SVG icon pre-rendered to pixmap
# ═══════════════════════════════════════════════════════════════════════════

class SendButton(QPushButton):
    """Circular send button; icon rendered from SVG into QPixmap."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(46, 46)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self._busy = False
        self._build_icon()
        self.setStyleSheet("""
            QPushButton {
                border-radius: 23px;
                background: #7c3aed;
                border: none;
            }
            QPushButton:hover { background: #6d28d9; }
            QPushButton:pressed { background: #5b21b6; }
            QPushButton:disabled { background: #4b5563; }
        """)
        self._refresh_icon()

    def _build_icon(self):
        self._pm_idle = svg_to_pixmap(SVG_SEND, 22)
        self._pm_busy = svg_to_pixmap(SVG_STAR, 22)   # placeholder while running

    def _refresh_icon(self):
        pm = self._pm_busy if self._busy else self._pm_idle
        self.setIcon(self.style().standardIcon(0))   # clear
        self.setIconSize(pm.size())
        from PyQt5.QtGui import QIcon
        self.setIcon(QIcon(pm))

    def set_busy(self, busy: bool):
        self._busy = busy
        self.setEnabled(not busy)
        self._refresh_icon()


# ═══════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════

class Sidebar(QWidget):
    file_selected    = pyqtSignal(str)
    settings_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(280)
        self.setStyleSheet(
            f"background: {BG_PANEL}; border-right: 1px solid {BORDER_DIM};")

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 22, 16, 18)
        root.setSpacing(14)

        root.addWidget(GradientLabel("Prompt2Clip", 17))

        tl = QLabel("AI-powered viral clip extractor")
        tl.setAlignment(Qt.AlignCenter)
        tl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        root.addWidget(tl)
        root.addWidget(self._sep())

        # Video picker
        fg = QGroupBox("Source Video")
        fgl = QVBoxLayout(fg)
        fgl.setContentsMargins(10, 14, 10, 10)
        fgl.setSpacing(6)

        self._file_lbl = QLabel("No file selected")
        self._file_lbl.setObjectName("muted")
        self._file_lbl.setWordWrap(True)
        self._file_lbl.setAlignment(Qt.AlignCenter)
        fgl.addWidget(self._file_lbl)

        browse_btn = self._icon_btn(SVG_FOLDER, "Browse Video")
        browse_btn.clicked.connect(self._pick_file)
        fgl.addWidget(browse_btn)
        root.addWidget(fg)

        # Pipeline settings
        sg = QGroupBox("Pipeline Settings")
        sgl = QGridLayout(sg)
        sgl.setContentsMargins(10, 14, 10, 10)
        sgl.setSpacing(8)

        sgl.addWidget(self._lbl("Audio Weight"), 0, 0)
        self._audio_w = QDoubleSpinBox()
        self._audio_w.setRange(0.0, 1.0)
        self._audio_w.setSingleStep(0.1)
        self._audio_w.setValue(0.5)
        self._audio_w.setDecimals(1)
        sgl.addWidget(self._audio_w, 0, 1)

        sgl.addWidget(self._lbl("Video Weight"), 1, 0)
        self._video_w = QDoubleSpinBox()
        self._video_w.setRange(0.0, 1.0)
        self._video_w.setSingleStep(0.1)
        self._video_w.setValue(0.5)
        self._video_w.setDecimals(1)
        sgl.addWidget(self._video_w, 1, 1)

        sgl.addWidget(self._lbl("Min Duration (s)"), 2, 0)
        self._min_dur = QSpinBox()
        self._min_dur.setRange(1, 60)
        self._min_dur.setValue(5)
        sgl.addWidget(self._min_dur, 2, 1)

        sgl.addWidget(self._lbl("Max Duration (s)"), 3, 0)
        self._max_dur = QSpinBox()
        self._max_dur.setRange(10, 300)
        self._max_dur.setValue(60)
        sgl.addWidget(self._max_dur, 3, 1)

        sgl.addWidget(self._lbl("Analysis FPS"), 4, 0)
        self._fps = QSpinBox()
        self._fps.setRange(1, 10)
        self._fps.setValue(2)
        sgl.addWidget(self._fps, 4, 1)
        root.addWidget(sg)

        # Output dir
        og = QGroupBox("Output Directory")
        ogl = QVBoxLayout(og)
        ogl.setContentsMargins(10, 14, 10, 10)
        ogl.setSpacing(6)

        self._out_lbl = QLabel("./output")
        self._out_lbl.setObjectName("muted")
        self._out_lbl.setWordWrap(True)
        ogl.addWidget(self._out_lbl)

        out_btn = self._icon_btn(SVG_FOLDER_OUT, "Change Output Dir")
        out_btn.clicked.connect(self._pick_outdir)
        ogl.addWidget(out_btn)
        root.addWidget(og)

        root.addStretch()

        ver = QLabel("v1.0  |  Powered by AI")
        ver.setAlignment(Qt.AlignCenter)
        ver.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px;")
        root.addWidget(ver)

        self._video_path = None
        self._out_path   = "output"

    def _sep(self):
        f = QFrame()
        f.setFrameShape(QFrame.HLine)
        f.setStyleSheet(f"color: {BORDER_DIM};")
        return f

    def _lbl(self, text):
        l = QLabel(text)
        l.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        return l

    def _icon_btn(self, svg_str: str, label: str) -> QPushButton:
        """QPushButton with SVG icon rendered as pixmap — no custom layout."""
        btn = QPushButton(label)
        btn.setObjectName("secondary")
        pm = svg_to_pixmap(svg_str, 16)
        from PyQt5.QtGui import QIcon
        btn.setIcon(QIcon(pm))
        btn.setIconSize(pm.size())
        btn.setFixedHeight(36)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        return btn

    def _pick_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Video", "",
            "Video Files (*.mp4 *.mov *.avi *.mkv *.webm);;All Files (*)")
        if path:
            self._video_path = path
            self._file_lbl.setText(Path(path).name)
            self._file_lbl.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 11px;")
            self.file_selected.emit(path)

    def _pick_outdir(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self._out_path = path
            self._out_lbl.setText(Path(path).name)

    def get_settings(self):
        return {
            "audio_weight": self._audio_w.value(),
            "video_weight": self._video_w.value(),
            "min_duration": self._min_dur.value(),
            "max_duration": self._max_dur.value(),
            "target_fps":   self._fps.value(),
            "output_dir":   self._out_path,
        }

    def get_video_path(self):
        return self._video_path


# ═══════════════════════════════════════════════════════════════════════════
#  RESULTS PANEL
# ═══════════════════════════════════════════════════════════════════════════

class ResultsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(270)
        self.setMaximumWidth(370)
        self.setStyleSheet(
            f"background: {BG_PANEL}; border-left: 1px solid {BORDER_DIM};")

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 16, 12, 16)
        root.setSpacing(10)

        hdr_row = QHBoxLayout()
        hdr_row.addWidget(SvgIcon(SVG_FILM, 18))
        ht = QLabel("  Results")
        ht.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 15px; font-weight: 700;")
        hdr_row.addWidget(ht)
        hdr_row.addStretch()
        root.addLayout(hdr_row)

        self._count_lbl = QLabel("No clips yet")
        self._count_lbl.setObjectName("muted")
        root.addWidget(self._count_lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: {BORDER_DIM};")
        root.addWidget(sep)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._container = QWidget()
        self._cl = QVBoxLayout(self._container)
        self._cl.setContentsMargins(0, 0, 0, 0)
        self._cl.setSpacing(10)

        # Empty state
        self._empty = QWidget()
        ev = QVBoxLayout(self._empty)
        ev.setAlignment(Qt.AlignCenter)
        ev.addWidget(SvgIcon(SVG_FILM, 48), 0, Qt.AlignCenter)
        el = QLabel("Your extracted clips\nwill appear here")
        el.setAlignment(Qt.AlignCenter)
        el.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; margin-top: 10px;")
        ev.addWidget(el)
        self._cl.addWidget(self._empty)
        self._cl.addStretch()

        self._scroll.setWidget(self._container)
        root.addWidget(self._scroll)

    def populate(self, clips, exported):
        while self._cl.count() > 1:
            item = self._cl.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not clips:
            self._count_lbl.setText("No clips generated")
            self._cl.insertWidget(0, self._empty)
            self._empty.show()
            return

        self._empty.hide()
        n = len(clips)
        self._count_lbl.setText(f"{n} clip{'s' if n != 1 else ''} extracted")
        self._count_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 12px;")
        for i, clip in enumerate(clips, 1):
            self._cl.insertWidget(i - 1, ClipResultCard(i, clip))


# ═══════════════════════════════════════════════════════════════════════════
#  CHAT PANEL
# ═══════════════════════════════════════════════════════════════════════════

class ChatPanel(QWidget):
    run_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {BG_DEEP};")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Top bar
        top = QFrame()
        top.setFixedHeight(52)
        top.setStyleSheet(
            f"background: {BG_PANEL}; border-bottom: 1px solid {BORDER_DIM};")
        tb = QHBoxLayout(top)
        tb.setContentsMargins(20, 0, 20, 0)
        tb.addWidget(SvgIcon(SVG_SCISSORS, 20))
        title = QLabel("  Chat")
        title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 15px; font-weight: 700;")
        tb.addWidget(title)
        tb.addStretch()
        self._dot = StatusDot()
        tb.addWidget(self._dot)
        self._status_lbl = QLabel("  Ready")
        self._status_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        tb.addWidget(self._status_lbl)
        root.addWidget(top)

        # Phase progress section (hidden initially)
        self._phase_frame = QFrame()
        self._phase_frame.setStyleSheet(
            f"background: {BG_PANEL}; border-bottom: 1px solid {BORDER_DIM};")
        pfl = QVBoxLayout(self._phase_frame)
        pfl.setContentsMargins(16, 10, 16, 10)
        pfl.setSpacing(6)

        hdr_lbl = QLabel("PIPELINE PROGRESS")
        hdr_lbl.setStyleSheet(
            f"color: {TEXT_MUTED}; font-size: 9px; font-weight: 700; letter-spacing: 1.5px;")
        pfl.addWidget(hdr_lbl)

        self._phase_cards = []
        for i, (name, svg) in enumerate(zip(PHASE_NAMES, PHASE_SVGS)):
            card = PhaseCard(i, name, svg)
            pfl.addWidget(card)
            self._phase_cards.append(card)

        self._phase_frame.hide()
        root.addWidget(self._phase_frame)

        # Chat scroll
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._chat_w = QWidget()
        self._chat_l = QVBoxLayout(self._chat_w)
        self._chat_l.setContentsMargins(16, 16, 16, 16)
        self._chat_l.setSpacing(8)
        self._chat_l.addStretch()

        self._scroll.setWidget(self._chat_w)
        root.addWidget(self._scroll, 1)

        # Input bar
        inf = QFrame()
        inf.setFixedHeight(70)
        inf.setStyleSheet(
            f"background: {BG_PANEL}; border-top: 1px solid {BORDER_DIM};")
        inl = QHBoxLayout(inf)
        inl.setContentsMargins(16, 12, 16, 12)
        inl.setSpacing(10)

        self._input = QLineEdit()
        self._input.setPlaceholderText(
            'e.g. "Give me 5 interesting clips under 30 seconds"')
        self._input.setFixedHeight(44)
        self._input.returnPressed.connect(self._send)
        inl.addWidget(self._input, 1)

        self._send_btn = SendButton()
        self._send_btn.clicked.connect(self._send)
        inl.addWidget(self._send_btn)
        root.addWidget(inf)

        # Welcome message
        self._post_system(
            "Welcome to Prompt2Clip!\n\n"
            "1. Select a video file in the sidebar.\n"
            "2. Adjust pipeline weights if needed.\n"
            "3. Type your clip request and press Send."
        )

    def _insert(self, w):
        self._chat_l.insertWidget(self._chat_l.count() - 1, w)
        QTimer.singleShot(40, lambda: self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()))

    def _post_system(self, text):
        self._insert(MessageBubble(text, is_user=False))

    def _send(self):
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self.run_requested.emit(text)

    # Public API
    def add_user_message(self, text):
        self._insert(MessageBubble(text, is_user=True))

    def add_system_message(self, text):
        self._post_system(text)

    def add_log_line(self, text):
        self._insert(LogBubble(text))

    def show_phases(self):
        self._phase_frame.show()

    def reset_phases(self):
        for c in self._phase_cards:
            c.reset()

    def phase_started(self, idx):
        if 0 <= idx < len(self._phase_cards):
            self._phase_cards[idx].set_running()

    def phase_done(self, idx):
        if 0 <= idx < len(self._phase_cards):
            self._phase_cards[idx].set_done()

    def phase_failed(self, idx):
        if 0 <= idx < len(self._phase_cards):
            self._phase_cards[idx].set_failed()

    def set_status(self, text, state="ready"):
        self._status_lbl.setText(f"  {text}")
        self._dot.set_state(state)

    def set_running(self, running):
        self._send_btn.set_busy(running)
        self._input.setEnabled(not running)


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ═══════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prompt2Clip")
        self.setMinimumSize(1100, 680)
        self.resize(1320, 800)
        self._worker = None

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._sidebar = Sidebar()
        self._sidebar.file_selected.connect(self._on_file)
        layout.addWidget(self._sidebar)

        self._chat = ChatPanel()
        self._chat.run_requested.connect(self._on_run)
        layout.addWidget(self._chat, 1)

        self._results = ResultsPanel()
        layout.addWidget(self._results)

    def _on_file(self, path):
        self._chat.add_system_message(
            f"Video loaded: {Path(path).name}\nPath: {path}")

    def _on_run(self, query):
        vp = self._sidebar.get_video_path()
        if not vp:
            self._chat.add_system_message(
                "Please select a video file from the sidebar first.")
            return
        self._chat.add_user_message(query)
        self._chat.add_system_message(
            f"Starting pipeline on: {Path(vp).name}\nQuery: {query}")
        settings = self._sidebar.get_settings()
        self._chat.set_running(True)
        self._chat.set_status("Processing...", "running")
        self._chat.reset_phases()
        self._chat.show_phases()

        self._worker = ClipWorker(vp, query, settings)
        self._worker.phase_started.connect(lambda idx, _: self._chat.phase_started(idx))
        self._worker.phase_done.connect(lambda idx, _: self._chat.phase_done(idx))
        self._worker.phase_failed.connect(
            lambda idx, name, err: (self._chat.phase_failed(idx),
                                    self._chat.add_system_message(
                                        f"Phase '{name}' failed:\n{err}")))
        self._worker.log_line.connect(self._chat.add_log_line)
        self._worker.results_ready.connect(self._on_results)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.start()

    def _on_results(self, results):
        clips, exported = results.get("clips", []), results.get("exported", [])
        self._chat.set_running(False)
        self._chat.set_status("Done", "ready")
        self._chat.add_system_message(
            f"Pipeline complete!\n"
            f"{len(clips)} clip(s) selected  |  {len(exported)} exported.")
        self._results.populate(clips, exported)
        self._worker = None

    def _on_error(self, msg):
        self._chat.set_running(False)
        self._chat.set_status("Error", "error")
        self._chat.add_system_message(f"Fatal error:\n{msg}")
        self._worker = None

    def closeEvent(self, event):
        if self._worker and self._worker.isRunning():
            self._worker.abort()
        event.accept()


# ═══════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

def main():
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    app = QApplication(sys.argv)
    app.setApplicationName("Prompt2Clip")
    app.setStyleSheet(APP_STYLE)

    palette = QPalette()
    palette.setColor(QPalette.Window,          QColor(BG_DEEP))
    palette.setColor(QPalette.WindowText,      QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Base,            QColor(BG_INPUT))
    palette.setColor(QPalette.AlternateBase,   QColor(BG_PANEL))
    palette.setColor(QPalette.Text,            QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Button,          QColor(BG_CARD))
    palette.setColor(QPalette.ButtonText,      QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Highlight,       QColor(ACCENT_VIOLET))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
