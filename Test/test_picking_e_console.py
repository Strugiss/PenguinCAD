# -*- coding: utf-8 -*-
"""Test F7: picking/box select escludono i nascosti e la console invalida le cache GL.

Costruisce `CADWindow` reale in modalità **offscreen**: non è una GUI reale e
non avvia `main()`. Click e box select sul viewport reale restano al Collaudatore.

Percorsi da `__file__`; nessun percorso assoluto.
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import numpy as np
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QApplication

import penguincad

_APP = None


def _finestra():
    """Crea (una sola volta) la QApplication e una CADWindow offscreen."""
    global _APP
    if QApplication.instance() is None:
        _APP = QApplication([])
    return penguincad.CADWindow()


def _box(w, nome, lato, x, visible=True):
    """Box cubico posizionato sull'asse X, con i metadata usati dal picking."""
    obj = w.scene.add_shape("box", {"larghezza": lato, "altezza": lato, "profondità": lato})
    obj.metadata.update({
        "name": nome,
        "layer": "Default",
        "color": [0.5, 0.8, 0.5, 1.0],
        "visible": visible,
        "locked": False,
        "shape_type": "box",
    })
    obj.apply_translation([x, 0.0, 0.0])
    return obj


def test_pick_ignora_oggetto_nascosto(monkeypatch):
    """Il click sul punto del box nascosto non lo seleziona; il visibile resta pickabile."""
    w = _finestra()
    try:
        visibile = _box(w, "Visibile", 10.0, 0.0, visible=True)
        nascosto = _box(w, "Nascosto", 20.0, 50.0, visible=False)

        # Raggio deterministico: x < 25 -> asse del visibile, x >= 25 -> asse del nascosto.
        def raggio_finto(x, y):
            target_x = 50.0 if x >= 25 else 0.0
            return np.array([target_x, 0.0, 50.0]), np.array([0.0, 0.0, -1.0])

        monkeypatch.setattr(w.gl_widget, "_screen_to_ray", raggio_finto)

        assert w.gl_widget._pick_object(QPoint(10, 10)) is visibile
        assert w.gl_widget._pick_object(QPoint(200, 10)) is None, \
            "il box nascosto è ancora selezionabile con _pick_object"
        assert nascosto in w.scene.objects, "il box nascosto è stato rimosso dalla scena"
    finally:
        w.close()


def test_box_select_ignora_oggetto_nascosto(monkeypatch):
    """Il box select seleziona solo il visibile; il nascosto resta in scena."""
    w = _finestra()
    try:
        visibile = _box(w, "Visibile", 10.0, 0.0, visible=True)
        nascosto = _box(w, "Nascosto", 20.0, 50.0, visible=False)

        gl = w.gl_widget
        gl._viewport = [0, 0, 400, 400]
        gl._modelview_matrix = np.eye(4)
        gl._projection_matrix = np.eye(4)
        # Proiezione finta ma sufficiente: ogni vertice cade dentro il rettangolo.
        monkeypatch.setattr(
            penguincad, "gluProject",
            lambda x, y, z, mv, pr, vp: (x + 100.0, y + 100.0, 0.0),
        )

        gl._select_objects_in_box(QPoint(0, 0), QPoint(400, 400))

        assert w.scene.selected_objects == [visibile], \
            "il box select ha selezionato anche l'oggetto nascosto"
        assert nascosto in w.scene.objects, "il box nascosto è stato rimosso dalla scena"
    finally:
        w.close()


def test_console_modifica_geometria_e_invalida_cache_gl():
    """Dopo un comando console che scala l'oggetto, le cache _gl_* non esistono più."""
    w = _finestra()
    dlg = None
    try:
        obj = _box(w, "DaConsole", 10.0, 0.0, visible=True)
        for chiave in penguincad._GL_CACHE_KEYS:
            obj.metadata[chiave] = 1
        obj.metadata["_gl_vbo_count"] = 36

        w.scene.selected_objects = [obj]
        volume_prima = float(obj.volume)

        w._toggle_console(True)
        dlg = w.console_dialog
        dlg.input.setText("obj.apply_scale(0.5)")
        dlg._execute()

        volume_dopo = float(obj.volume)
        assert abs(volume_dopo - volume_prima / 8.0) < 1e-6, \
            "il comando console non ha modificato la geometria"

        for chiave in penguincad._GL_CACHE_KEYS:
            assert chiave not in obj.metadata, "cache GL '%s' ancora presente" % chiave
        assert "_gl_vbo_count" not in obj.metadata, "contatore VBO ancora presente"
        assert w.gl_widget._vbo_pendenti, "gli id VBO non sono stati accodati per la cancellazione"
    finally:
        if dlg is not None:
            dlg.close()
        w.close()
