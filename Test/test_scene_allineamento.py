# -*- coding: utf-8 -*-
"""Test di allineamento di core/scene.py a TriviumCAD 1.3.0 (fase F1).

Copre i tre fix:
1. Scene espone sketch_2d_entities / sketch_2d_state (attributi letti da
   sketch.py alla root del progetto).
2. ungroup_object rimuove l'assembly da scene.assemblies (niente fantasma).
3. subdivide e decimate preservano i metadata dell'oggetto e scartano le
   cache GL della vecchia geometria.
4. scale_selection_uniform ancora la Z al piano (default 0.0): la base da
   stampa non scende sotto Z=0; undo ripristina posizione e volume.

Usa la Scene reale e le API reali (add_shape, group_selected, subdivide,
decimate); nessun mock. Eseguibile con pytest e con `python test_scene_allineamento.py`.
"""
import os
import sys

import numpy as np
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.scene import Scene  # noqa: E402

CHIAVI_GL = ("_gl_verts", "_gl_normals", "_gl_vbo_verts", "_gl_vbo_normals")
CAMPI_META = ("name", "color", "layer", "visible", "locked", "shape_type")


def _box_con_metadata(scene, nome):
    """Crea un box con metadata completi e cache GL fittizie (geometria vecchia)."""
    obj = scene.add_shape("box", {"size": [10.0, 10.0, 10.0]}, name=nome)
    obj.metadata.update({
        "name": nome,
        "color": [1.0, 0.5, 0.2, 1.0],
        "layer": "Default",
        "visible": True,
        "locked": False,
        "shape_type": "box",
    })
    # Cache GL finte: dopo subdivide/decimate devono sparire, perché riferite
    # ai vertici/normali della geometria precedente.
    obj.metadata["_gl_verts"] = np.zeros((8, 3), dtype=np.float32)
    obj.metadata["_gl_normals"] = np.zeros((8, 3), dtype=np.float32)
    obj.metadata["_gl_vbo_verts"] = 1
    obj.metadata["_gl_vbo_normals"] = 1
    return obj


def _verifica_metadata_e_cache(obj):
    """Controlla metadata preservati e assenza totale delle cache GL."""
    for campo in CAMPI_META:
        assert obj.metadata.get(campo) is not None, "metadata '%s' perso" % campo
    assert obj.metadata["name"] == "Pezzo"
    assert obj.metadata["color"] == [1.0, 0.5, 0.2, 1.0]
    assert obj.metadata["layer"] == "Default"
    assert obj.metadata["visible"] is True
    assert obj.metadata["locked"] is False
    assert obj.metadata["shape_type"] == "box"
    for chiave in CHIAVI_GL:
        assert chiave not in obj.metadata, "cache GL '%s' non rimossa" % chiave


def test_scene_sketch_2d_entities_default():
    """Scene nuova: sketch_2d_entities è una lista vuota."""
    scene = Scene()
    assert scene.sketch_2d_entities == []
    assert isinstance(scene.sketch_2d_entities, list)


def test_scene_sketch_2d_state_default():
    """Scene nuova: sketch_2d_state è un dict vuoto."""
    scene = Scene()
    assert scene.sketch_2d_state == {}
    assert isinstance(scene.sketch_2d_state, dict)


def test_ungroup_object_rimuove_assembly():
    """Dopo la separazione l'id non resta più in scene.assemblies."""
    scene = Scene()
    a = _box_con_metadata(scene, "A")
    b = _box_con_metadata(scene, "B")
    scene.selected_objects = [a, b]

    assembly_id = scene.group_selected()
    assert assembly_id is not None, "group_selected non ha creato l'assembly"
    assert assembly_id in scene.assemblies
    assert a.metadata["assembly"] == assembly_id
    assert b.metadata["assembly"] == assembly_id

    scene.selected_objects = [a]
    scene.ungroup_object()

    assert a.metadata["assembly"] is None
    assert assembly_id not in scene.assemblies, "assembly fantasma ancora registrato"


def test_subdivide_preserva_metadata_e_scarta_cache_gl():
    """subdivide conserva i metadata e rimuove le cache GL della vecchia mesh."""
    scene = Scene()
    obj = _box_con_metadata(scene, "Pezzo")
    facce_prima = len(obj.faces)
    for chiave in CHIAVI_GL:
        assert chiave in obj.metadata, "precondizione: cache GL '%s' assente" % chiave

    scene.selected_objects = [obj]
    assert scene.subdivide(iterations=1) is True

    risultato = scene.selected_objects[0]
    assert scene.objects[0] is risultato
    assert len(risultato.faces) > facce_prima, "la suddivisione non ha aggiunto facce"
    _verifica_metadata_e_cache(risultato)


def test_decimate_preserva_metadata_e_scarta_cache_gl():
    """decimate conserva i metadata e rimuove le cache GL della vecchia mesh."""
    scene = Scene()
    obj = _box_con_metadata(scene, "Pezzo")
    # Il box ha 12 facce: il target 6 rende la decimazione effettiva.
    facce_prima = len(obj.faces)
    for chiave in CHIAVI_GL:
        assert chiave in obj.metadata, "precondizione: cache GL '%s' assente" % chiave

    scene.selected_objects = [obj]
    assert scene.decimate(target_faces=6) is True

    risultato = scene.selected_objects[0]
    assert scene.objects[0] is risultato
    assert len(risultato.faces) < facce_prima, "la decimazione non ha ridotto le facce"
    assert len(risultato.faces) > 0, "mesh decimata vuota"
    _verifica_metadata_e_cache(risultato)


# --- Scala uniforme ancorata al piano Z=0 (fix 5, 1.3.1) ---

def _cubo_20(scene, z_min=0.0, nome="Cubo"):
    """Cubo 20 mm con base a `z_min` (add_shape lo crea già con base a Z=0)."""
    obj = scene.add_shape(
        "box", {"larghezza": 20.0, "altezza": 20.0, "profondità": 20.0}, name=nome
    )
    if abs(z_min) > 1e-9:
        obj.apply_translation([0.0, 0.0, z_min])
    scene.selected_objects = [obj]
    return obj


def _z_min_max(obj):
    verts = np.asarray(obj.vertices, dtype=np.float64)
    return float(verts[:, 2].min()), float(verts[:, 2].max())


def test_scala_uniforme_ancora_z0_base_ferma():
    """Cubo Z=0..20, scala 2: la base resta a 0, la cima va a 40, volume x8."""
    scene = Scene()
    obj = _cubo_20(scene, 0.0)
    assert _z_min_max(obj) == (0.0, 20.0)
    volume_prima = obj.volume

    assert scene.scale_selection_uniform(2.0) is True

    z_min, z_max = _z_min_max(obj)
    assert z_min == 0.0, "la base è scesa sotto il piano Z=0: %.6f" % z_min
    assert z_max == 40.0
    assert obj.volume == pytest.approx(volume_prima * 8.0, rel=1e-9)


def test_scala_uniforme_ancora_piano_z0_non_al_minimo():
    """Cubo Z=5..25, scala 2: ancora al piano Z=0 -> Z=10..50, non 5..25.

    Semantica scelta (fix 5): l'ancora è il piano Z=0, non il minimo locale
    dell'oggetto. Un oggetto sollevato resta sollevato in proporzione.
    """
    scene = Scene()
    obj = _cubo_20(scene, 5.0)
    assert _z_min_max(obj) == (5.0, 25.0)

    assert scene.scale_selection_uniform(2.0, ancora_z=0.0) is True

    z_min, z_max = _z_min_max(obj)
    assert z_min == 10.0, "atteso 10 (5*2), ottenuto %.6f" % z_min
    assert z_max == 50.0


def test_scala_uniforme_undo_ripristina_z_e_volume():
    """L'undo riporta geometria e volume allo stato precedente alla scala."""
    scene = Scene()
    obj = _cubo_20(scene, 0.0)
    volume_prima = obj.volume
    assert _z_min_max(obj) == (0.0, 20.0)

    assert scene.scale_selection_uniform(2.0) is True
    assert _z_min_max(obj) == (0.0, 40.0)
    assert obj.volume == pytest.approx(volume_prima * 8.0, rel=1e-9)

    assert scene.undo() is True

    ripristinato = scene.selected_objects[0]
    assert _z_min_max(ripristinato) == (0.0, 20.0), "l'undo non ha ripristinato la Z"
    assert ripristinato.volume == pytest.approx(volume_prima, rel=1e-9)


def main():
    tests = [
        test_scene_sketch_2d_entities_default,
        test_scene_sketch_2d_state_default,
        test_ungroup_object_rimuove_assembly,
        test_subdivide_preserva_metadata_e_scarta_cache_gl,
        test_decimate_preserva_metadata_e_scarta_cache_gl,
        test_scala_uniforme_ancora_z0_base_ferma,
        test_scala_uniforme_ancora_piano_z0_non_al_minimo,
        test_scala_uniforme_undo_ripristina_z_e_volume,
    ]
    ok = 0
    for fn in tests:
        try:
            fn()
            ok += 1
            print("[PASS] %s" % fn.__name__)
        except AssertionError as e:
            print("[FAIL] %s: %s" % (fn.__name__, e))
    print("\nEsito: %d/%d test superati" % (ok, len(tests)))
    sys.exit(0 if ok == len(tests) else 1)


if __name__ == "__main__":
    main()
