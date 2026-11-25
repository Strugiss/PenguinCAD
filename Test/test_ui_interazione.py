# -*- coding: utf-8 -*-
"""Test F5c: interazione e UI minore (outliner, snap/magneti, pannelli, dock).

Costruisce `CADWindow` reale in modalità **offscreen**: non è una GUI reale e
non avvia `main()`. Ctrl+click e i pannelli su GUI reale restano al Collaudatore.

Percorsi da `__file__`.
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QDockWidget, QLabel, QPushButton

import penguincad

_APP = None


def _finestra():
    """Crea (una sola volta) la QApplication e una CADWindow offscreen."""
    global _APP
    if QApplication.instance() is None:
        _APP = QApplication([])
    return penguincad.CADWindow()


def test_snap_menu_e_toolbar_sincronizzati_nei_due_sensi():
    """Menu e pulsante Snap non divergono, in entrambe le direzioni."""
    w = _finestra()
    try:
        w._toggle_snap(True)
        assert w.scene.snap_grid is True
        assert w._snap_act.isChecked() is True
        assert w._snap_btn.isChecked() is True

        # Senso menu -> scena e toolbar.
        w._snap_act.trigger()
        assert w.scene.snap_grid is False
        assert w._snap_act.isChecked() is False
        assert w._snap_btn.isChecked() is False

        # Senso toolbar -> scena e menu.
        w._snap_btn.click()
        assert w.scene.snap_grid is True
        assert w._snap_act.isChecked() is True
        assert w._snap_btn.isChecked() is True
    finally:
        w.close()


def test_magneti_menu_e_toolbar_sincronizzati_nei_due_sensi():
    """Menu e pulsante Magneti non divergono, in entrambe le direzioni."""
    w = _finestra()
    try:
        w._toggle_magnetic(True)
        assert w.scene.magnetic_snap is True
        assert w._magnet_act.isChecked() is True
        assert w._magnet_btn.isChecked() is True

        w._magnet_act.trigger()
        assert w.scene.magnetic_snap is False
        assert w._magnet_act.isChecked() is False
        assert w._magnet_btn.isChecked() is False

        w._magnet_btn.click()
        assert w.scene.magnetic_snap is True
        assert w._magnet_act.isChecked() is True
        assert w._magnet_btn.isChecked() is True
    finally:
        w.close()


def test_outliner_aggiorna_nome_e_icone_a_conteggio_invariato():
    """Rinomina e cambio visibilità/lock aggiornano l'item esistente."""
    w = _finestra()
    try:
        obj = w.scene.add_shape("box", {"larghezza": 10.0, "altezza": 10.0, "profondità": 10.0})
        obj.metadata["name"] = "Prima"
        w._refresh_outliner()
        assert w.outliner_list.count() == 1

        item = w.outliner_list.item(0)
        widget = w.outliner_list.itemWidget(item)
        assert widget is not None
        nome = widget.findChild(QLabel, "outliner_name")
        vis_btn = widget.findChild(QPushButton, "outliner_vis")
        lock_btn = widget.findChild(QPushButton, "outliner_lock")
        assert nome is not None and nome.text() == "Prima"
        assert vis_btn is not None and lock_btn is not None, "objectName outliner mancanti"

        # Rinomina a parità di conteggio: il testo deve aggiornarsi.
        obj.metadata["name"] = "Dopo"
        w._sync_outliner_selection()
        assert nome.text() == "Dopo", "il nome nell'outliner è rimasto vecchio"

        # Icone di stato: devono cambiare insieme ai metadata.
        occhi_prima = vis_btn.icon().cacheKey()
        lucchetto_prima = lock_btn.icon().cacheKey()
        obj.metadata["visible"] = False
        obj.metadata["locked"] = True
        w._sync_outliner_selection()
        assert vis_btn.icon().cacheKey() != occhi_prima, "icona visibilità non aggiornata"
        assert lock_btn.icon().cacheKey() != lucchetto_prima, "icona lock non aggiornata"
    finally:
        w.close()


def test_pannelli_collassabili_sinistro_e_destro():
    """Le linguette collassano e riaprono i due pannelli, senza perdere il body."""
    w = _finestra()
    try:
        for nome in ("_make_panel_edge_button", "_toggle_left_panel", "_toggle_right_panel"):
            assert hasattr(w, nome), "metodo '%s' mancante" % nome

        assert w.left_body.isHidden() is False
        assert w.left_tab.isHidden() is True
        w._toggle_left_panel()
        assert w.left_body.isHidden() is True
        assert w.left_tab.isHidden() is False
        w._toggle_left_panel()
        assert w.left_body.isHidden() is False
        assert w.left_tab.isHidden() is True

        assert w.right_body.isHidden() is False
        assert w.right_tab.isHidden() is True
        w._toggle_right_panel()
        assert w.right_body.isHidden() is True
        assert w.right_tab.isHidden() is False
        w._toggle_right_panel()
        assert w.right_body.isHidden() is False
        assert w.right_tab.isHidden() is True
    finally:
        w.close()


def test_outliner_dock_non_chiudibile():
    """L'Outliner resta movibile ma non chiudibile."""
    w = _finestra()
    try:
        features = w.outliner_dock.features()
        assert not (features & QDockWidget.DockWidgetClosable), "il dock Outliner è ancora chiudibile"
        assert features & QDockWidget.DockWidgetMovable, "il dock Outliner non è più movibile"
    finally:
        w.close()


# --- Rinomina dall'Outliner (fix 4, 1.3.1) ---

def _oggetto_con_nome(w, nome="Prima"):
    obj = w.scene.add_shape("box", {"larghezza": 10.0, "altezza": 10.0, "profondità": 10.0})
    obj.metadata["name"] = nome
    w._refresh_outliner()
    return obj


def _label_nome(w, riga=0):
    item = w.outliner_list.item(riga)
    widget = w.outliner_list.itemWidget(item)
    assert widget is not None
    lbl = widget.findChild(QLabel, "outliner_name")
    assert lbl is not None, "label outliner_name mancante"
    return lbl


def test_rinomina_outliner_da_dialogo_aggiorna_metadata_e_label():
    """Conferma non vuota: metadata e label aggiornati, selezione invariata."""
    w = _finestra()
    try:
        obj = _oggetto_con_nome(w, "Prima")
        w.scene.selected_objects = [obj]
        w._refresh_outliner()
        nome = _label_nome(w)
        assert nome.text() == "Prima"

        with patch.object(penguincad.QInputDialog, "getText",
                          return_value=("NuovoNome", True)) as mock_get:
            w._rename_object(obj)

        assert mock_get.call_count == 1
        assert mock_get.call_args.kwargs.get("text") == "Prima", \
            "il dialogo deve partire dal nome corrente"
        assert obj.metadata["name"] == "NuovoNome"
        assert _label_nome(w).text() == "NuovoNome", "l'outliner non mostra il nuovo nome"
        assert w.scene.selected_objects == [obj], "la rinomina non deve cambiare la selezione"
    finally:
        w.close()


@pytest.mark.parametrize("risposta", [("", True), ("   ", True), ("Altro", False)])
def test_rinomina_outliner_annulla_o_vuoto_non_cambia(risposta):
    """Annulla o testo vuoto: il nome resta quello di prima."""
    w = _finestra()
    try:
        obj = _oggetto_con_nome(w, "Prima")
        with patch.object(penguincad.QInputDialog, "getText", return_value=risposta):
            w._rename_object(obj)
        assert obj.metadata["name"] == "Prima"
        assert _label_nome(w).text() == "Prima"
    finally:
        w.close()


def test_rinomina_outliner_doppio_click_sulla_label():
    """Il doppio click sulla QLabel del nome apre la rinomina (percorso reale)."""
    w = _finestra()
    try:
        obj = _oggetto_con_nome(w, "Prima")
        nome = _label_nome(w)
        with patch.object(penguincad.QInputDialog, "getText",
                          return_value=("DaDoppioClick", True)) as mock_get:
            QTest.mouseDClick(nome, Qt.LeftButton)
        assert mock_get.call_count == 1, "il doppio click sulla label non ha aperto la rinomina"
        assert obj.metadata["name"] == "DaDoppioClick"
        assert _label_nome(w).text() == "DaDoppioClick"
    finally:
        w.close()


def test_rinomina_outliner_item_double_clicked():
    """Il percorso `itemDoubleClicked` porta alla stessa rinomina, senza duplicati."""
    w = _finestra()
    try:
        obj = _oggetto_con_nome(w, "Prima")
        item = w.outliner_list.item(0)
        with patch.object(penguincad.QInputDialog, "getText",
                          return_value=("DaItem", True)) as mock_get:
            w.outliner_list.itemDoubleClicked.emit(item)
        assert mock_get.call_count == 1
        assert obj.metadata["name"] == "DaItem"
        assert _label_nome(w).text() == "DaItem"
    finally:
        w.close()


def test_outliner_menu_contestuale_abilitato_e_risolve_oggetto():
    """Policy del menu contestuale attiva e item -> oggetto coerente."""
    w = _finestra()
    try:
        obj = _oggetto_con_nome(w, "Prima")
        assert w.outliner_list.contextMenuPolicy() == Qt.CustomContextMenu
        item = w.outliner_list.item(0)
        assert w._outliner_object_from_item(item) is obj
        assert w._outliner_object_from_item(None) is None
    finally:
        w.close()


# --- Pannello Proprietà: Layer e Shape (fix 6, 1.3.1) ---

def _cubo(w, layer=None, shape="box"):
    obj = w.scene.add_shape(shape, {"larghezza": 10.0, "altezza": 10.0, "profondità": 10.0}
                            if shape == "box" else {"raggio": 5.0, "altezza": 10.0, "sezioni": 16})
    if layer is not None:
        obj.metadata["layer"] = layer
    return obj


def test_proprieta_layer_e_shape_seguono_selezione_e_deselezione():
    """Cubo selezionato: Layer/Shape reali; deselezionato: entrambe '—'."""
    w = _finestra()
    try:
        assert w.prop_layer.text() == "—"
        assert w.prop_shape.text() == "—"
        assert w.findChild(QLabel, "prop_layer") is w.prop_layer
        assert w.findChild(QLabel, "prop_shape") is w.prop_shape

        obj = _cubo(w)
        w.scene.selected_objects = [obj]
        w.update_ui()
        assert w.prop_layer.text() == "Default"
        assert w.prop_shape.text() == "box"

        w.scene.clear_selection()
        w.update_ui()
        assert w.prop_layer.text() == "—"
        assert w.prop_shape.text() == "—"
    finally:
        w.close()


def test_proprieta_cambia_con_il_secondo_oggetto():
    """Selezionando un oggetto con layer/shape diversi, le label cambiano."""
    w = _finestra()
    try:
        primo = _cubo(w)
        secondo = _cubo(w, layer="Supporti", shape="cylinder")

        w.scene.selected_objects = [primo]
        w.update_ui()
        assert (w.prop_layer.text(), w.prop_shape.text()) == ("Default", "box")

        w.scene.selected_objects = [secondo]
        w.update_ui()
        assert (w.prop_layer.text(), w.prop_shape.text()) == ("Supporti", "cylinder")
    finally:
        w.close()


def test_proprieta_selezione_multipla_comune_o_trattino():
    """Multi-selezione: valore comune se tutte uguali, altrimenti '—'."""
    w = _finestra()
    try:
        a = _cubo(w)
        b = _cubo(w)

        w.scene.selected_objects = [a, b]
        w.update_ui()
        assert (w.prop_layer.text(), w.prop_shape.text()) == ("Default", "box")

        b.metadata["layer"] = "Supporti"
        w.update_ui()
        assert (w.prop_layer.text(), w.prop_shape.text()) == ("—", "box")

        b.metadata["shape_type"] = "cylinder"
        w.update_ui()
        assert (w.prop_layer.text(), w.prop_shape.text()) == ("—", "—")
    finally:
        w.close()
