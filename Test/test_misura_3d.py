# -*- coding: utf-8 -*-
"""Test F7: misura su punti 3D reali (ray-cast), non proiezione su Z=0.

Un click sulla faccia superiore di un cubo 20 mm (Z=0..20) deve salvare il
punto di intersezione [x, y, 20], non [x, y, 0]. Due punti a 10 mm sulla
faccia devono misurare 10.00 mm (prima: 13.025 mm per la proiezione a Z=0).
Il fallback al piano Z=0 resta per i click senza geometria sotto il raggio.

Percorsi da `__file__`; GUI offscreen (il percorso GUI reale e' del
Collaudatore).
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import math
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import numpy as np
import pytest
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor, QImage, QPainter
from PyQt5.QtWidgets import QApplication

import penguincad

_APP = None


def _finestra():
    """QApplication (una sola) e CADWindow offscreen."""
    global _APP
    if QApplication.instance() is None:
        _APP = QApplication([])
    return penguincad.CADWindow()


def _cubo_20(w):
    """Cubo 20x20x20 con base a Z=0 (validate_and_place_mesh): Z=0..20."""
    obj = w.scene.add_shape(
        "box", {"larghezza": 20.0, "altezza": 20.0, "profondità": 20.0})
    w.scene.selected_objects = []
    return obj


def _raggi_faccia_superiore():
    """Due raggi verticali che colpiscono la faccia Z=20 a 10 mm di distanza."""
    raggi = {
        100: (np.array([-5.0, -5.0, 100.0]), np.array([0.0, 0.0, -1.0])),
        200: (np.array([5.0, -5.0, 100.0]), np.array([0.0, 0.0, -1.0])),
    }

    def _ray(x, _y):
        return raggi[x]

    return _ray


def test_click_faccia_z20_salva_punti_3d_e_misura_10mm():
    """Click sulla faccia superiore: punti a Z=20, distanza 10.00 mm."""
    w = _finestra()
    try:
        gl = w.gl_widget
        _cubo_20(w)
        gl._screen_to_ray = _raggi_faccia_superiore()
        gl.scene.measurement_mode = "distance"
        gl.scene.measurement_points = []
        gl.scene.measurement_done = False

        gl._measure_click(QPoint(100, 0))
        gl._measure_click(QPoint(200, 0))

        pts = gl.scene.measurement_points
        assert len(pts) == 2, "la misura non ha raccolto i due click"
        assert pts[0] == pytest.approx([-5.0, -5.0, 20.0], abs=1e-6), \
            "il primo punto non e' l'intersezione 3D della faccia Z=20"
        assert pts[1] == pytest.approx([5.0, -5.0, 20.0], abs=1e-6), \
            "il secondo punto non e' l'intersezione 3D della faccia Z=20"
        assert gl._testo_misura("distance", pts) == "10.00 mm", \
            "la distanza 3D sulla faccia Z=20 non e' 10 mm"
        assert "Distanza: 10.000 mm" in w.status_bar.currentMessage()
        assert gl.scene.measurement_done is True
    finally:
        w.close()


def test_angolo_3d_tre_punti_su_piani_diversi():
    """Angolo al vertice con vettori 3D: 90 gradi reali, non 0."""
    ang = penguincad.GLWidget._angle_between(
        [0, 0, 20], [0, 0, 0], [10, 0, 0])
    assert math.degrees(ang) == pytest.approx(90.0, abs=1e-6)
    assert penguincad.GLWidget._testo_misura(
        "angle", [[0, 0, 20], [0, 0, 0], [10, 0, 0]]) == "90.0°"


def test_click_su_vuoto_fallback_z0_senza_eccezioni():
    """Raggio senza geometria: fallback al piano Z=0, comportamento invariato."""
    w = _finestra()
    try:
        gl = w.gl_widget
        _cubo_20(w)  # geometria presente ma lontana dal raggio

        def _ray(x, _y):
            # Interseca Z=0 in (100, 50 + 10*x): due punti a 10 mm.
            return (np.array([100.0, 50.0 + 10.0 * x, 80.0]),
                    np.array([0.0, 0.0, -1.0]))

        gl._screen_to_ray = _ray
        gl.scene.measurement_mode = "distance"
        gl.scene.measurement_points = []
        gl.scene.measurement_done = False

        gl._measure_click(QPoint(0, 0))
        gl._measure_click(QPoint(1, 0))

        pts = gl.scene.measurement_points
        assert pts[0] == pytest.approx([100.0, 50.0, 0.0], abs=1e-6)
        assert pts[1] == pytest.approx([100.0, 60.0, 0.0], abs=1e-6)
        assert gl._testo_misura("distance", pts) == "10.00 mm"
    finally:
        w.close()


def test_scala_usa_distanza_3d_e_ancora_z0_con_undo(monkeypatch):
    """Il dialog riceve la distanza 3D; la scala resta ancorata a Z=0 e undo."""
    w = _finestra()
    try:
        gl = w.gl_widget
        obj = _cubo_20(w)
        w.scene.selected_objects = [obj]
        gl._screen_to_ray = _raggi_faccia_superiore()
        gl.scene.measurement_mode = "distance"
        gl.scene.measurement_points = []
        gl.scene.measurement_done = False

        visto = {}

        def _get_double(_parent, titolo, label, valore, *args, **kwargs):
            visto["titolo"] = titolo
            visto["label"] = label
            visto["valore"] = valore
            return 20.0, True

        monkeypatch.setattr(
            penguincad.QInputDialog, "getDouble", staticmethod(_get_double))

        chiamate = {}
        orig_scale = w.scene.scale_selection_uniform

        def _spy_scale(factor, ancora_z=0.0):
            chiamate["factor"] = factor
            chiamate["ancora_z"] = ancora_z
            return orig_scale(factor, ancora_z)

        monkeypatch.setattr(w.scene, "scale_selection_uniform", _spy_scale)

        gl._measure_click(QPoint(100, 0))
        gl._measure_click(QPoint(200, 0))

        assert visto["titolo"] == "Misura — Scala forma"
        assert visto["valore"] == pytest.approx(10.0, abs=1e-9), \
            "il dialog di scala non ha ricevuto la distanza 3D"
        assert "Distanza misurata: 10.000 mm" in visto["label"]
        assert chiamate["factor"] == pytest.approx(2.0, abs=1e-9)
        assert chiamate["ancora_z"] == 0.0, "la scala non e' ancorata a Z=0"

        verts = np.asarray(obj.vertices, dtype=np.float64)
        assert verts[:, 2].min() == pytest.approx(0.0, abs=1e-9)
        assert verts[:, 2].max() == pytest.approx(40.0, abs=1e-9)

        assert w.scene.undo() is True
        dopo = np.asarray(
            w.scene.selected_objects[0].vertices, dtype=np.float64)
        assert dopo[:, 2].min() == pytest.approx(0.0, abs=1e-9)
        assert dopo[:, 2].max() == pytest.approx(20.0, abs=1e-9), \
            "l'undo non ha ripristinato l'altezza del cubo"
    finally:
        w.close()


def test_overlay_proietta_i_punti_3d_con_world_to_screen():
    """L'overlay proietta i punti 3D salvati, Z inclusa; il painter non chiude."""
    w = _finestra()
    try:
        gl = w.gl_widget
        gl.resize(200, 200)
        gl._modelview_matrix = np.eye(4)
        gl._projection_matrix = np.eye(4)
        gl._viewport = (0, 0, 200, 200)
        gl.scene.measurement_mode = "distance"
        gl.scene.measurement_points = [[0.0, 0.0, 20.0], [10.0, 0.0, 20.0]]

        visti = []
        orig = gl._world_to_screen

        def _spy(point):
            visti.append(np.asarray(point, dtype=np.float64).copy())
            return orig(point)

        gl._world_to_screen = _spy
        img = QImage(200, 200, QImage.Format_ARGB32)
        img.fill(QColor(0, 0, 0, 0))
        p = QPainter(img)
        gl._draw_measurement_overlay(p)
        assert p.isActive(), "il painter fornito e' stato chiuso"
        p.end()

        assert len(visti) == 2, "i punti non passano da _world_to_screen"
        assert all(v.shape == (3,) for v in visti)
        assert all(v[2] == pytest.approx(20.0) for v in visti), \
            "la Z dei punti e' stata persa prima della proiezione"
    finally:
        w.close()
