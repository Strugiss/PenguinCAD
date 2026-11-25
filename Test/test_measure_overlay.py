# -*- coding: utf-8 -*-
"""Test F5a: overlay misura (_MeasureOverlay) su CADWindow offscreen.

Non è una GUI reale: verifica classe, mostra/nascondi, disegno con painter,
Esc, Ctrl+M / Ctrl+Shift+M e che paintGL non disegni più la misura direttamente.
F5a-3: il valore numerico (_testo_misura) e il suo badge nel painter.
F5a-3b: la misura completata resta in scena (measurement_done) finché Esc o
una nuova misura non la chiudono; badge e status bar coerenti.
Le verifiche visive (linea non sdoppiata, testo leggibile, compositing
Windows/Linux) restano al Collaudatore.

Percorsi da `__file__`.
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import ast
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import numpy as np
from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtGui import QColor, QImage, QKeyEvent, QPainter, QPixmap
from PyQt5.QtWidgets import QApplication

import penguincad

_APP = None


def _finestra():
    """Crea (una sola volta) la QApplication e una CADWindow offscreen."""
    global _APP
    if QApplication.instance() is None:
        _APP = QApplication([])
    return penguincad.CADWindow()


def _seleziona_box(w):
    obj = w.scene.add_shape("box", {"larghezza": 10.0, "altezza": 10.0, "profondità": 10.0})
    w.scene.selected_objects = [obj]
    return obj


def test_overlay_creato_e_tragparente_ai_mouse():
    """Il widget overlay esiste, è figlio del GLWidget e lascia passare i click."""
    w = _finestra()
    try:
        gl = w.gl_widget
        ov = gl._measure_overlay
        assert isinstance(ov, penguincad._MeasureOverlay)
        assert ov.parent() is gl
        assert ov.testAttribute(Qt.WA_TransparentForMouseEvents) is True
        assert ov.testAttribute(Qt.WA_TranslucentBackground) is True
        assert ov.isHidden() is True
    finally:
        w.close()


def test_update_mostra_e_nasconde():
    """Con modalità e punti l'overlay appare; senza punti torna nascosto."""
    w = _finestra()
    try:
        gl = w.gl_widget
        ov = gl._measure_overlay
        gl.scene.measurement_mode = "distance"
        gl.scene.measurement_points = [[0.0, 0.0, 0.0], [10.0, 0.0, 0.0]]
        gl._update_measure_overlay()
        assert ov.isHidden() is False

        gl.scene.measurement_mode = None
        gl.scene.measurement_points = []
        gl._update_measure_overlay()
        assert ov.isHidden() is True

        # Solo modalità senza punti: resta nascosto.
        gl.scene.measurement_mode = "angle"
        gl._update_measure_overlay()
        assert ov.isHidden() is True
    finally:
        w.close()


def test_draw_con_painter_non_solleva():
    """_draw_measurement_overlay(painter) non solleva e non chiude il painter."""
    w = _finestra()
    try:
        gl = w.gl_widget
        gl._modelview_matrix = np.eye(4)
        gl._projection_matrix = np.eye(4)
        gl._viewport = (0, 0, 120, 120)
        gl.scene.measurement_mode = "distance"
        gl.scene.measurement_points = [[0.0, 0.0, 0.0], [5.0, 0.0, 0.0]]

        pix = QPixmap(120, 120)
        pix.fill(QColor(0, 0, 0, 0))
        p = QPainter(pix)
        gl._draw_measurement_overlay(p)
        assert p.isActive(), "il painter passato è stato chiuso dal metodo"
        p.end()

        # Nessun punto: ritorno immediato, nessuna eccezione.
        gl.scene.measurement_points = []
        p = QPainter(pix)
        gl._draw_measurement_overlay(p)
        p.end()
    finally:
        w.close()


def test_esc_pulisce_e_nasconde_overlay():
    """Esc annulla la misura, svuota i punti e nasconde l'overlay."""
    w = _finestra()
    try:
        gl = w.gl_widget
        ov = gl._measure_overlay
        gl.scene.measurement_mode = "distance"
        gl.scene.measurement_points = [[1.0, 1.0, 0.0]]
        gl._update_measure_overlay()
        assert ov.isHidden() is False

        gl.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier))
        assert gl.scene.measurement_mode is None
        assert gl.scene.measurement_points == []
        assert ov.isHidden() is True
    finally:
        w.close()


def test_ctrl_m_e_ctrl_shift_m_attivano_le_modalita():
    """Ctrl+M attiva distanza (2 click), Ctrl+Shift+M l'angolo (3 click)."""
    w = _finestra()
    try:
        gl = w.gl_widget
        _seleziona_box(w)

        gl.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_M, Qt.ControlModifier))
        assert gl.scene.measurement_mode == "distance"
        assert gl.scene.measurement_points == []

        gl.scene.measurement_mode = None
        gl.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_M,
                                   Qt.ControlModifier | Qt.ShiftModifier))
        assert gl.scene.measurement_mode == "angle"
        assert gl.scene.measurement_points == []
    finally:
        w.close()


def test_paintgl_non_disegna_piu_la_misura_direttamente():
    """paintGL aggiorna l'overlay ma non chiama più _draw_measurement_overlay()."""
    sorgente = (BASE_DIR / "penguincad.py").read_text(encoding="utf-8")
    albero = ast.parse(sorgente)
    paintgl = None
    for nodo in ast.walk(albero):
        if isinstance(nodo, ast.FunctionDef) and nodo.name == "paintGL":
            paintgl = nodo
            break
    assert paintgl is not None, "paintGL non trovato"
    corpo = ast.get_source_segment(sorgente, paintgl)
    assert "_draw_measurement_overlay(" not in corpo, \
        "paintGL disegna ancora la misura direttamente"
    assert "_measure_overlay" in corpo, \
        "paintGL non aggiorna il widget overlay"


# --- F5a-3: valore numerico nell'overlay -------------------------------------

def test_testo_misura_distanza():
    """Distanza 3D in mm con due decimali: la Z entra nella misura."""
    assert penguincad.GLWidget._testo_misura(
        "distance", [[0, 0, 0], [3, 4, 0]]) == "5.00 mm"
    assert penguincad.GLWidget._testo_misura(
        "distance", [[0, 0, 0], [10, 0, 0]]) == "10.00 mm"
    # Due punti sulla faccia Z=20 a 10 mm: 10.00, non 13.03 (proiezione Z=0).
    assert penguincad.GLWidget._testo_misura(
        "distance", [[0, 0, 20], [10, 0, 20]]) == "10.00 mm"
    # La Z entra nella distanza: sqrt(3^2+4^2+123^2) = 123.10 mm.
    assert penguincad.GLWidget._testo_misura(
        "distance", [[0, 0, 0], [3, 4, 123.0]]) == "123.10 mm"


def test_testo_misura_angolo():
    """Angolo al vertice (secondo punto) in gradi con un decimale."""
    assert penguincad.GLWidget._testo_misura(
        "angle", [[0, 0, 0], [1, 0, 0], [1, 1, 0]]) == "90.0°"
    assert penguincad.GLWidget._testo_misura(
        "angle", [[1, 0, 0], [0, 0, 0], [1, 1, 0]]) == "45.0°"
    # Punti 3D su piani diversi: 90° reali (la vecchia formula XY dava 0°).
    assert penguincad.GLWidget._testo_misura(
        "angle", [[0, 0, 20], [0, 0, 0], [10, 0, 0]]) == "90.0°"


def test_testo_misura_pochi_punti_o_modo_sconosciuto():
    """Punti insufficienti o modo sconosciuto: stringa vuota, nessuna eccezione."""
    assert penguincad.GLWidget._testo_misura("distance", []) == ""
    assert penguincad.GLWidget._testo_misura("distance", [[0, 0, 0]]) == ""
    assert penguincad.GLWidget._testo_misura("angle", [[0, 0, 0], [1, 0, 0]]) == ""
    assert penguincad.GLWidget._testo_misura("angle", []) == ""
    assert penguincad.GLWidget._testo_misura(None, [[0, 0, 0], [1, 0, 0]]) == ""
    assert penguincad.GLWidget._testo_misura("boh", [[0, 0, 0], [1, 0, 0]]) == ""


def test_testo_misura_stessa_formula_della_status_bar():
    """Il valore del badge coincide con il calcolo della status bar/dialog."""
    import math

    w = _finestra()
    try:
        gl = w.gl_widget
        pts_d = [[1.0, 2.0, 20.0], [4.0, 6.0, 23.0]]
        atteso = math.dist(pts_d[0], pts_d[1])
        testo = gl._testo_misura("distance", pts_d)
        assert abs(float(testo.split()[0]) - atteso) < 0.005

        pts_a = [[2.0, 1.0, 0.0], [0.0, 0.0, 0.0], [1.0, 3.0, 0.0]]
        atteso_a = math.degrees(gl._angle_between(*pts_a))
        testo_a = gl._testo_misura("angle", pts_a)
        assert abs(float(testo_a[:-1]) - atteso_a) < 0.05
    finally:
        w.close()


def _painter_pronto(gl, lato=240):
    """Painter attivo su QImage trasparente con le matrici GL di test."""
    gl.resize(lato, lato)
    gl._modelview_matrix = np.eye(4)
    gl._projection_matrix = np.eye(4)
    gl._viewport = (0, 0, lato, lato)
    img = QImage(lato, lato, QImage.Format_ARGB32)
    img.fill(QColor(0, 0, 0, 0))
    p = QPainter(img)
    return img, p


def _pixel_opachi(img):
    return sum(1 for y in range(img.height()) for x in range(img.width())
               if img.pixelColor(x, y).alpha() > 0)


def test_draw_con_painter_due_e_tre_punti():
    """Con 2 e 3 punti il disegno non solleva e non chiude il painter."""
    w = _finestra()
    try:
        gl = w.gl_widget
        for modo, punti in (
            ("distance", [[-0.5, -0.3, 0.0], [0.4, 0.2, 0.0]]),
            ("angle", [[-0.5, -0.3, 0.0], [0.0, 0.2, 0.0], [0.5, -0.3, 0.0]]),
        ):
            gl.scene.measurement_mode = modo
            gl.scene.measurement_points = punti
            img, p = _painter_pronto(gl)
            gl._draw_measurement_overlay(p)
            assert p.isActive(), "il painter è stato chiuso dal metodo"
            p.end()
            assert _pixel_opachi(img) > 0
    finally:
        w.close()


def test_draw_disegna_il_testo_nel_painter():
    """Il badge del valore aggiunge pixel: senza testo l'immagine è più vuota."""
    w = _finestra()
    try:
        gl = w.gl_widget
        gl.scene.measurement_mode = "distance"
        gl.scene.measurement_points = [[-0.5, -0.3, 0.0], [0.4, 0.2, 0.0]]

        img_con, p = _painter_pronto(gl)
        gl._draw_measurement_overlay(p)
        assert p.isActive()
        p.end()
        con_testo = _pixel_opachi(img_con)

        gl._testo_misura = lambda mode, points: ""
        try:
            img_senza, p = _painter_pronto(gl)
            gl._draw_measurement_overlay(p)
            assert p.isActive()
            p.end()
            senza_testo = _pixel_opachi(img_senza)
        finally:
            gl.__dict__.pop("_testo_misura", None)

        assert con_testo > senza_testo, (
            f"nessun pixel di testo: con={con_testo} senza={senza_testo}")
    finally:
        w.close()

# --- F5a-3b: la misura completata resta in scena -----------------------------

def _click_sequenza(gl, punti):
    """Simula i click di misura con coordinate di sketch controllate."""
    residui = list(punti)

    def _coord(_pos):
        return residui.pop(0)

    gl._get_sketch_coords = _coord
    try:
        for _ in punti:
            gl._measure_click(QPoint(0, 0))
    finally:
        gl.__dict__.pop("_get_sketch_coords", None)


def test_distanza_completata_resta_in_scena():
    """2 punti: done, modalità e punti restano, overlay visibile, badge e status."""
    w = _finestra()
    try:
        gl = w.gl_widget
        gl.scene.measurement_mode = "distance"
        gl.scene.measurement_points = []
        gl.scene.measurement_done = False
        gl._update_measure_overlay()

        _click_sequenza(gl, [(0.0, 0.0), (3.0, 4.0)])

        assert gl.scene.measurement_done is True
        assert gl.scene.measurement_mode == "distance"
        assert gl.scene.measurement_points == [[0.0, 0.0, 0.0], [3.0, 4.0, 0.0]]
        assert gl._measure_overlay.isHidden() is False
        assert gl._testo_misura("distance", gl.scene.measurement_points) == "5.00 mm"
        messaggio = w.status_bar.currentMessage()
        assert "5.000" in messaggio
        assert "clicca altri" not in messaggio
    finally:
        w.close()


def test_angolo_completato_resta_in_scena():
    """3 punti: il badge ha i 3 punti al paint, overlay visibile e status coerente."""
    w = _finestra()
    try:
        gl = w.gl_widget
        gl.scene.measurement_mode = "angle"
        gl.scene.measurement_points = []
        gl.scene.measurement_done = False
        gl._update_measure_overlay()

        _click_sequenza(gl, [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)])

        assert gl.scene.measurement_done is True
        assert gl.scene.measurement_mode == "angle"
        assert len(gl.scene.measurement_points) == 3, \
            "i 3 punti sono stati azzerati prima del paint"
        assert gl._measure_overlay.isHidden() is False
        assert gl._testo_misura("angle", gl.scene.measurement_points) == "90.0°"
        messaggio = w.status_bar.currentMessage()
        assert "90.00°" in messaggio
        assert "clicca altri" not in messaggio
    finally:
        w.close()


def test_esc_chiude_la_misura_completata():
    """Esc azzera done, punti e modalità e nasconde l'overlay."""
    w = _finestra()
    try:
        gl = w.gl_widget
        gl.scene.measurement_mode = "distance"
        gl.scene.measurement_points = [[0.0, 0.0, 0.0], [5.0, 0.0, 0.0]]
        gl.scene.measurement_done = True
        gl._update_measure_overlay()
        assert gl._measure_overlay.isHidden() is False

        gl.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier))

        assert gl.scene.measurement_done is False
        assert gl.scene.measurement_points == []
        assert gl.scene.measurement_mode is None
        assert gl._measure_overlay.isHidden() is True
    finally:
        w.close()


def test_nuova_misura_riparte_pulita():
    """Ctrl+M / Ctrl+Shift+M azzerano done, punti e nascondono l'overlay."""
    w = _finestra()
    try:
        gl = w.gl_widget
        gl.scene.measurement_mode = "distance"
        gl.scene.measurement_points = [[0.0, 0.0, 0.0], [5.0, 0.0, 0.0]]
        gl.scene.measurement_done = True
        gl._update_measure_overlay()
        _seleziona_box(w)

        gl.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_M, Qt.ControlModifier))
        assert gl.scene.measurement_done is False
        assert gl.scene.measurement_points == []
        assert gl.scene.measurement_mode == "distance"
        assert gl._measure_overlay.isHidden() is True

        gl.scene.measurement_points = [[0.0, 0.0, 0.0], [5.0, 0.0, 0.0]]
        gl.scene.measurement_done = True
        gl._update_measure_overlay()
        gl.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_M,
                                   Qt.ControlModifier | Qt.ShiftModifier))
        assert gl.scene.measurement_done is False
        assert gl.scene.measurement_points == []
        assert gl.scene.measurement_mode == "angle"
        assert gl._measure_overlay.isHidden() is True
    finally:
        w.close()


def test_click_dopo_completamento_non_aggiunge_punti():
    """A misura completata i click non vengono nemmeno letti."""
    w = _finestra()
    try:
        gl = w.gl_widget
        gl.scene.measurement_mode = "distance"
        gl.scene.measurement_points = [[0.0, 0.0, 0.0], [5.0, 0.0, 0.0]]
        gl.scene.measurement_done = True

        chiamate = []

        def _coord(pos):
            chiamate.append(pos)
            return (9.0, 9.0)

        gl._get_sketch_coords = _coord
        try:
            gl._measure_click(QPoint(0, 0))
        finally:
            gl.__dict__.pop("_get_sketch_coords", None)

        assert chiamate == [], "il click è stato letto dopo la misura completata"
        assert len(gl.scene.measurement_points) == 2
    finally:
        w.close()


def test_painter_dopo_completamento_disegna_il_badge():
    """Dopo i click la misura resta disegnata: il badge è nel painter."""
    w = _finestra()
    try:
        gl = w.gl_widget
        gl.scene.measurement_mode = "distance"
        gl.scene.measurement_points = []
        gl.scene.measurement_done = False

        _click_sequenza(gl, [(-0.3, -0.2), (0.2, 0.3)])
        assert gl.scene.measurement_done is True
        assert gl._testo_misura("distance", gl.scene.measurement_points) == "0.71 mm"

        img, p = _painter_pronto(gl)
        gl._draw_measurement_overlay(p)
        assert p.isActive()
        p.end()

        badge = 0
        for y in range(img.height()):
            for x in range(img.width()):
                c = img.pixelColor(x, y)
                if (c.alpha() >= 200 and c.red() < 40
                        and 20 < c.green() < 55 and 40 < c.blue() < 75):
                    badge += 1
        assert badge > 0, "badge assente dopo la misura completata"
    finally:
        w.close()
