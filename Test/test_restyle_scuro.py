# -*- coding: utf-8 -*-
"""Test F6: restyle scuro (QSS globale, inline, contrasto WCAG, font, toolbar).

I test offscreen costruiscono widget reali ma non sono GUI reale: verificano
che il foglio venga applicato e che i dialoghi si costruiscano senza eccezioni.
La resa visiva resta al Collaudatore (Windows/Linux).

Percorsi da `__file__`.
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication

import penguincad
from core import constants as C
from core.scene import Scene
from sketch import SketchDialog

_APP = None

SELETTORI_RICHIESTI = (
    "QMainWindow", "QDialog", "QDockWidget", "QGroupBox", "QPushButton",
    "QComboBox", "QLineEdit", "QTextEdit", "QListWidget", "QScrollArea",
    "QStatusBar", "QMenuBar", "QMenu", "QToolTip", "QSlider", "QSpinBox",
    "QDoubleSpinBox", "QCheckBox", "QTabWidget", "QMessageBox",
    "QInputDialog", "QSplashScreen",
)

COLORI_CHIARI_VIETATI = (
    "#AEC8E0", "#F2F6FB", "#B8D4EC", "#A0B8D0", "#6080A0",
    "#2C4A6E", "#1F4E79", "#e0e0e0", "#3A7FAA", "#2E7D32",
    "#1e1e1e", "#252526", "#0C1E36", "#2C5F8A",
)


def _app():
    global _APP
    applicazione = QApplication.instance()
    if applicazione is None:
        _APP = QApplication([])
        applicazione = _APP
    return applicazione


def _sorgente():
    return (BASE_DIR / "penguincad.py").read_text(encoding="utf-8")


def _luminanza(colore):
    h = colore.lstrip("#")
    if len(h) != 6:
        raise ValueError("colore non #RRGGBB: %r" % colore)
    canali = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        canali.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = canali
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrasto(a, b):
    la, lb = _luminanza(a), _luminanza(b)
    alto, basso = max(la, lb), min(la, lb)
    return (alto + 0.05) / (basso + 0.05)


def test_stylesheet_globale_palette_scura():
    """Il QSS globale contiene i selettori richiesti e la palette scura."""
    qss = penguincad._app_stylesheet()
    for selettore in SELETTORI_RICHIESTI:
        assert selettore in qss, "selettore '%s' assente dal QSS" % selettore
    assert C.BG_PAGE in qss and C.BG_CARD in qss and C.AMBER in qss
    for chiaro in ("#AEC8E0", "#F2F6FB", "#C8DCF0", "#2C5F8A"):
        assert chiaro not in qss, "colore chiaro '%s' ancora nel QSS" % chiaro


def test_inline_senza_colori_chiari():
    """In penguincad.py non restano i letterali del tema chiaro."""
    src = _sorgente()
    for colore in COLORI_CHIARI_VIETATI:
        assert colore not in src, "colore chiaro '%s' ancora inline" % colore


def test_contrasto_wcag_aa():
    """Coppie testo/sfondo ≥4,5:1; icone secondarie ≥3:1."""
    coppie_testo = (
        (C.TEXT_BODY, C.BG_PAGE),
        (C.TEXT_BODY, C.BG_CARD),
        (C.TEXT_BODY, C.BG_ELEV),
        (C.TEXT_MUTED, C.BG_PANEL),
        (C.TEXT_MUTED, C.BG_CARD),
        (C.AMBER, C.BG_CARD),
        (C.AMBER, C.BG_PAGE),
        (C.AMBER_LIGHT, C.BG_ELEV),
        (C.AMBER_DIM, C.BG_PAGE),
        (C.TEXT_ON_AMBER, C.AMBER),
        (C.GREEN_CRT, C.BG_CARD),
        (C.BRASS_LIGHT, C.BG_CARD),
    )
    for testo, sfondo in coppie_testo:
        rapporto = _contrasto(testo, sfondo)
        assert rapporto >= 4.5, "%s su %s: contrasto %.2f < 4.5" % (testo, sfondo, rapporto)

    coppie_icone = (
        ("#b8960a", C.BG_CARD),
        ("#999999", C.BG_CARD),
        (C.TEXT_MUTED, C.BG_CARD),
    )
    for icona, sfondo in coppie_icone:
        rapporto = _contrasto(icona, sfondo)
        assert rapporto >= 3.0, "icona %s su %s: contrasto %.2f < 3.0" % (icona, sfondo, rapporto)


def test_toolbar_senza_emoji():
    """La toolbar usa icone QPainter e testi ASCII, senza emoji."""
    src = _sorgente()
    inizio = src.index("def _setup_toolbar")
    fine = src.index("def _make_panel_edge_button")
    blocco = src[inizio:fine]
    for emoji in ("❤", "🧊", "🆕", "📂", "💾", "🅱", "🛡", "🎯", "🧲", "💖", "🌐"):
        assert emoji not in blocco, "emoji '%s' ancora nella toolbar" % emoji


def test_font_fallback_linux():
    """Nessun font Windows-only nel sorgente: fallback disponibili su Linux."""
    src = _sorgente()
    assert "Segoe UI" not in src, "font 'Segoe UI' ancora presente"
    assert "Consolas" not in src, "font 'Consolas' ancora presente"


def test_tendine_con_freccia_scura():
    """Il QSS definisce la freccia delle tendine e l'asset esiste ed è leggibile."""
    _app()
    qss = penguincad._app_stylesheet()
    assert "QComboBox::down-arrow" in qss, "regola down-arrow assente"
    assert "freccia_giu.png" in qss, "asset freccia non referenziato nel QSS"
    percorso = BASE_DIR / "Immagini" / "freccia_giu.png"
    assert percorso.is_file(), "asset Immagini/freccia_giu.png assente"
    pixmap = QPixmap(str(percorso))
    assert not pixmap.isNull(), "asset freccia non caricabile"
    assert pixmap.width() > 0 and pixmap.height() > 0


def test_titolo_tutorial_ascii():
    """Il titolo del Tutorial non contiene emoji (niente tofu su Linux)."""
    w = penguincad.CADWindow()
    try:
        dlg = penguincad.TutorialDialog(w)
        try:
            assert dlg.windowTitle() == "Tutorial PenguinCAD"
            assert dlg.windowTitle().isascii()
        finally:
            dlg.close()
    finally:
        w.close()


def test_pulsante_booleane_padding_menu():
    """Booleane: menu, padding destro 22 e larghezza sufficiente al testo completo."""
    from PyQt5.QtWidgets import QPushButton, QStyle
    app = _app()
    app.setStyleSheet(penguincad._app_stylesheet())
    w = penguincad.CADWindow()
    try:
        pulsanti = [b for b in w.findChildren(QPushButton) if b.text() == "Booleane"]
        assert len(pulsanti) == 1, "pulsante Booleane non trovato o duplicato"
        pulsante = pulsanti[0]
        assert pulsante.menu() is not None, "menu Booleane assente"
        assert "padding: 5px 22px 5px 10px" in pulsante.styleSheet(), \
            "padding destro non ricalibrato a 22 px"
        assert pulsante.minimumWidth() >= 144, "larghezza minima sotto i 144 px"

        pulsante.ensurePolished()
        avanzamento = pulsante.fontMetrics().horizontalAdvance("Booleane")
        indicatore = pulsante.style().pixelMetric(QStyle.PM_MenuButtonIndicator, None, pulsante)
        richiesto = avanzamento + indicatore + 10 + 22 + 4  # padding sx/dx + bordo
        larghezza = max(pulsante.minimumWidth(), pulsante.sizeHint().width())
        assert larghezza >= richiesto, \
            "larghezza %d < richiesta %d (testo %d + indicatore %d + padding)" % (
                larghezza, richiesto, avanzamento, indicatore)
    finally:
        w.close()


def test_stylesheet_e_dialoghi_offscreen():
    """QSS applicato e dialoghi costruiti senza eccezioni (non GUI reale)."""
    app = _app()
    app.setStyleSheet(penguincad._app_stylesheet())
    w = penguincad.CADWindow()
    aperti = []
    try:
        aperti.append(penguincad.TutorialDialog(w))
        aperti.append(penguincad.PrinterConnectDialog(w))
        aperti.append(SketchDialog(w, Scene(), on_change=lambda e, s: None))
        console = penguincad.ConsoleDialog(w.scene, w.gl_widget, w)
        aperti.append(console)
        assert app.styleSheet()
    finally:
        for finestra in aperti:
            finestra.close()
        w.close()
