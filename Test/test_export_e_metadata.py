# -*- coding: utf-8 -*-
"""Test F5b: integrità dati (filettatura, testo 3D) ed export filtrato.

Costruisce `CADWindow` reale in modalità **offscreen**: non è una GUI reale e
non avvia `main()`. Verifica i metadata preservati, l'assenza delle cache GL e
il volume dell'STL esportato con un oggetto nascosto.

Percorsi da `__file__`; file temporanei via fixture `tmp_path`.
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pytest
import trimesh
from PyQt5.QtWidgets import QApplication

import penguincad

METADATI = ("name", "layer", "color", "visible", "locked", "shape_type")
CACHE_GL = ("_gl_verts", "_gl_normals", "_gl_vbo_verts", "_gl_vbo_normals")

_APP = None


def _finestra():
    """Crea (una sola volta) la QApplication e una CADWindow offscreen."""
    global _APP
    if QApplication.instance() is None:
        _APP = QApplication([])
    return penguincad.CADWindow()


def _cilindro(w, nome, visible=True, locked=True):
    """Cilindro con 6 metadata espliciti e cache GL finte."""
    obj = w.scene.add_shape("cylinder", {"raggio": 10.0, "altezza": 30.0, "sezioni": 64})
    obj.metadata.update({
        "name": nome,
        "layer": "Default",
        "color": [0.5, 0.8, 0.5, 1.0],
        "visible": visible,
        "locked": locked,
        "shape_type": "cylinder",
    })
    for chiave in CACHE_GL:
        obj.metadata[chiave] = 1
    w.scene.selected_objects = [obj]
    return obj


def _verifica_metadata_filettato(obj, nome_atteso, visible, locked):
    assert obj.metadata.get("name") == "%s_filettato" % nome_atteso
    assert obj.metadata.get("layer") == "Default"
    assert obj.metadata.get("color") == [0.5, 0.8, 0.5, 1.0]
    assert obj.metadata.get("visible") is visible
    assert obj.metadata.get("locked") is locked
    assert obj.metadata.get("shape_type") == "cylinder"
    for chiave in CACHE_GL:
        assert chiave not in obj.metadata, "cache GL '%s' non rimossa" % chiave


class _BoxSpia:
    """Sostituto di QMessageBox: registra le chiamate senza aprire finestre."""

    def __init__(self):
        self.eventi = []

    def warning(self, *args, **kwargs):
        self.eventi.append(("warning", args))

    def critical(self, *args, **kwargs):
        self.eventi.append(("critical", args))

    def information(self, *args, **kwargs):
        self.eventi.append(("information", args))


def test_filettatura_esterna_preserva_metadata():
    """Ramo Esterna: 6 metadata copiati, nome _filettato, cache GL assenti."""
    w = _finestra()
    try:
        obj = _cilindro(w, "Cilindro", visible=True, locked=False)
        w.thread_type.setCurrentText("Esterna")
        w._run_threading()
        assert len(w.scene.objects) == 1
        risultato = w.scene.objects[0]
        assert risultato is not obj, "l'oggetto non è stato sostituito"
        _verifica_metadata_filettato(risultato, "Cilindro", True, False)
    finally:
        w.close()


def test_filettatura_interna_preserva_metadata():
    """Ramo Interna: stessi metadata, inclusi visible=False e locked=True."""
    w = _finestra()
    try:
        obj = _cilindro(w, "Tubo", visible=False, locked=True)
        w.thread_type.setCurrentText("Interna")
        w._run_threading()
        assert len(w.scene.objects) == 1
        risultato = w.scene.objects[0]
        assert risultato is not obj, "l'oggetto non è stato sostituito"
        _verifica_metadata_filettato(risultato, "Tubo", False, True)
        assert risultato.is_watertight, "la filettatura interna non è watertight"
    finally:
        w.close()


def test_testo_3d_visible_e_locked():
    """Il testo 3D nasce visible=True e locked=False."""
    w = _finestra()
    try:
        w.text_entry.setPlainText("A")
        w._add_text_mesh()
        testi = [o for o in w.scene.objects if o.metadata.get("shape_type") == "text"]
        assert len(testi) == 1, "testo 3D non creato"
        meta = testi[0].metadata
        assert meta.get("visible") is True
        assert meta.get("locked") is False
        for campo in ("name", "layer", "color", "shape_type"):
            assert meta.get(campo) is not None, "metadata '%s' mancante" % campo
    finally:
        w.close()


def test_export_esclude_oggetti_nascosti(tmp_path, monkeypatch):
    """Due box: 10 mm visibile, 20 mm nascosto e selezionato -> STL da 1000 mm³."""
    w = _finestra()
    try:
        piccolo = w.scene.add_shape("box", {"larghezza": 10.0, "altezza": 10.0, "profondità": 10.0})
        piccolo.metadata.update({
            "name": "Piccolo", "layer": "Default", "color": [0.4, 0.6, 0.8, 1.0],
            "visible": True, "locked": False, "shape_type": "box",
        })
        grande = w.scene.add_shape("box", {"larghezza": 20.0, "altezza": 20.0, "profondità": 20.0})
        grande.metadata.update({
            "name": "Grande", "layer": "Default", "color": [0.8, 0.5, 0.5, 1.0],
            "visible": False, "locked": False, "shape_type": "box",
        })
        # Il nascosto è anche selezionato: l'export non deve includerlo.
        w.scene.selected_objects = [grande]

        uscita = tmp_path / "export_filtrato.stl"
        monkeypatch.setattr(
            penguincad.QFileDialog, "getSaveFileName",
            staticmethod(lambda *a, **k: (str(uscita), "")),
        )
        spia = _BoxSpia()
        monkeypatch.setattr(penguincad, "QMessageBox", spia)

        w._export()

        assert spia.eventi == [], "export ha segnalato un errore: %r" % (spia.eventi,)
        assert uscita.exists(), "STL non creato"
        mesh = trimesh.load(str(uscita), force="mesh")
        assert abs(float(mesh.volume) - 1000.0) < 0.5, \
            "volume esportato %.3f mm³, atteso 1000 (il box nascosto è finito nel file?)" % mesh.volume
    finally:
        w.close()
