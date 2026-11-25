# -*- coding: utf-8 -*-
"""Test delle costanti di PenguinCAD — fase F2 (allineamento a TriviumCAD 1.3.0).

Verifica che:
1. la palette additiva per 2PenAxE (20 nomi) esista, sia fatta di stringhe
   non vuote e abbia i valori esatti di TriviumCAD 1.3.0;
2. il tema chiaro resti invariato (BACKGROUND_COLOR == "#AEC8E0");
3. identità (APP_NAME, VERSION) e alias legacy restino invariati;
4. NEUTRAL_COLORS, SHAPE_LIBRARY e PRINTER_PROFILES restino invariati.

Nota F6: gli alias legacy sono ora rimappati sulla palette scura per contratto
(il tema chiaro non è più atteso); il test verifica il nuovo mapping.

Percorsi derivati da __file__: nessun percorso assoluto.
Eseguibile con pytest e con `python test_costanti_palette.py`.
"""
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import core.constants as C  # noqa: E402

# Valori copiati alla lettera da TriviumCAD 1.3.0 (core/constants.py).
PALETTE_ATTESA = {
    "BG_PAGE": "#0C1E36",
    "BG_PANEL": "#10243F",
    "BG_CARD": "#132A47",
    "BG_ELEV": "#173258",
    "BORDER_SOFT": "rgba(120, 160, 220, 0.18)",
    "AMBER": "#f0b429",
    "AMBER_LIGHT": "#f7c948",
    "AMBER_DARK": "#8a6118",
    "AMBER_DIM": "#d9a23c",
    "AMBER_FAINT": "rgba(240, 180, 41, 0.14)",
    "BRASS": "#b87333",
    "BRASS_LIGHT": "#d4944a",
    "TEXT_ON_AMBER": "#101014",
    "GREEN_CRT": "#33ff33",
    "GREEN_DIM": "#1a9e1a",
    "TEXT_BODY": "#dde6f5",
    "TEXT_MUTED": "#9fb3cc",
    "FONT_HEAD": "'Orbitron', 'Inter', sans-serif",
    "FONT_BODY": "'Inter', 'Open Sans', sans-serif",
    "FONT_MONO": "'Share Tech Mono', 'Courier New', monospace",
}

NOMI_COLORI_HEX = [
    "BG_PAGE", "BG_PANEL", "BG_CARD", "BG_ELEV",
    "AMBER", "AMBER_LIGHT", "AMBER_DARK", "AMBER_DIM",
    "BRASS", "BRASS_LIGHT", "TEXT_ON_AMBER",
    "GREEN_CRT", "GREEN_DIM", "TEXT_BODY", "TEXT_MUTED",
]
NOMI_COLORI_RGBA = ["BORDER_SOFT", "AMBER_FAINT"]
NOMI_FONT = ["FONT_HEAD", "FONT_BODY", "FONT_MONO"]

RE_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
RE_RGBA = re.compile(r"^rgba\(\s*\d+,\s*\d+,\s*\d+,\s*(0|1|0?\.\d+)\s*\)$")

# Alias legacy: da F6 rimappati sulla palette scura (allineamento 1.3.0).
ALIAS_ATTESI = {
    "BACKGROUND_COLOR": "#0C1E36",        # BG_PAGE
    "TEXT_COLOR": "#dde6f5",              # TEXT_BODY
    "BORDER_COLOR": "rgba(120, 160, 220, 0.18)",  # BORDER_SOFT
    "BUTTON_COLOR": "#132A47",            # BG_CARD
    "BUTTON_HOVER": "#173258",            # BG_ELEV
    "BUTTON_PRESSED": "#1d3b66",
}

NEUTRAL_COLORS_ATTESI = [
    [0.7, 0.7, 0.7, 1.0],
    [0.4, 0.6, 0.8, 1.0],
    [0.8, 0.5, 0.5, 1.0],
    [0.5, 0.8, 0.5, 1.0],
    [0.8, 0.8, 0.4, 1.0],
    [0.6, 0.5, 0.8, 1.0],
    [0.5, 0.8, 0.8, 1.0],
    [0.8, 0.6, 0.4, 1.0],
    [0.7, 0.4, 0.7, 1.0],
    [0.4, 0.7, 0.6, 1.0],
    [0.9, 0.6, 0.6, 1.0],
    [0.6, 0.6, 0.9, 1.0],
]

SHAPE_LIBRARY_ATTESA = {
    "Cubo": {"type": "box", "params": {"larghezza": 20.0, "altezza": 20.0, "profondità": 20.0}},
    "Cilindro": {"type": "cylinder", "params": {"raggio": 10.0, "altezza": 30.0, "sezioni": 64}},
    "Sfera": {"type": "sphere", "params": {"raggio": 15.0, "suddivisioni": 4}},
    "Cono": {"type": "cone", "params": {"raggio_base": 12.0, "altezza": 30.0, "sezioni": 64}},
    "collare": {"type": "collare", "params": {"raggio_esterno": 20.0, "raggio_interno": 12.0, "altezza": 8.0}},
    "Esagono": {"type": "hexagon", "params": {"raggio": 10.0, "altezza": 30.0}},
    "Spirale": {"type": "spiral", "params": {"raggio": 15.0, "altezza": 30.0, "giri": 4, "spessore": 3.0}},
    "Arco": {"type": "arc", "params": {"raggio_est": 20.0, "raggio_int": 16.0, "apertura": 90.0, "altezza": 8.0}},
    "Scatola vuota": {"type": "hollow_box", "params": {"larghezza": 30.0, "altezza": 20.0, "profondità": 20.0, "spessore_muro": 2.0}},
}

PRINTER_PROFILES_ATTESI = {
    "Bambu Lab X1C": {
        "brand": "Bambu Lab", "model": "X1 Carbon",
        "build_volume": (256, 256, 256), "nozzle": [0.4, 0.6, 0.8],
        "max_temp": 300, "bed_temp": 100,
        "protocols": ["mqtt_ftps"],
        "default_layer": 0.16, "default_infill": 15,
    },
    "Bambu Lab P1S": {
        "brand": "Bambu Lab", "model": "P1S",
        "build_volume": (256, 256, 256), "nozzle": [0.4, 0.6, 0.8],
        "max_temp": 300, "bed_temp": 100,
        "protocols": ["mqtt_ftps"],
        "default_layer": 0.20, "default_infill": 15,
    },
    "Bambu Lab A1": {
        "brand": "Bambu Lab", "model": "A1",
        "build_volume": (256, 256, 256), "nozzle": [0.4, 0.6, 0.8],
        "max_temp": 260, "bed_temp": 80,
        "protocols": ["mqtt_ftps"],
        "default_layer": 0.20, "default_infill": 15,
    },
    "Bambu Lab A1 Mini": {
        "brand": "Bambu Lab", "model": "A1 Mini",
        "build_volume": (180, 180, 180), "nozzle": [0.4],
        "max_temp": 260, "bed_temp": 80,
        "protocols": ["mqtt_ftps"],
        "default_layer": 0.20, "default_infill": 15,
    },
    "Anycubic Kobra 3": {
        "brand": "Anycubic", "model": "Kobra 3",
        "build_volume": (250, 250, 260), "nozzle": [0.4],
        "max_temp": 260, "bed_temp": 95,
        "protocols": ["ftp", "smb", "octoprint", "anycubic_cloud", "file"],
        "default_layer": 0.20, "default_infill": 15,
    },
    "Anycubic Kobra 2": {
        "brand": "Anycubic", "model": "Kobra 2",
        "build_volume": (220, 220, 250), "nozzle": [0.4],
        "max_temp": 260, "bed_temp": 95,
        "protocols": ["ftp", "smb", "octoprint", "file"],
        "default_layer": 0.20, "default_infill": 15,
    },
    "Anycubic Vyper": {
        "brand": "Anycubic", "model": "Vyper",
        "build_volume": (245, 245, 260), "nozzle": [0.4],
        "max_temp": 260, "bed_temp": 95,
        "protocols": ["ftp", "smb", "octoprint", "file"],
        "default_layer": 0.20, "default_infill": 15,
    },
    "Creality K1 Max": {
        "brand": "Creality", "model": "K1 Max",
        "build_volume": (300, 300, 300), "nozzle": [0.4],
        "max_temp": 300, "bed_temp": 100,
        "protocols": ["creality_http", "ftp", "octoprint", "file"],
        "default_layer": 0.20, "default_infill": 15,
    },
    "Creality K1": {
        "brand": "Creality", "model": "K1",
        "build_volume": (220, 220, 250), "nozzle": [0.4],
        "max_temp": 300, "bed_temp": 100,
        "protocols": ["creality_http", "ftp", "octoprint", "file"],
        "default_layer": 0.20, "default_infill": 15,
    },
    "Creality Ender 3 V3": {
        "brand": "Creality", "model": "Ender 3 V3",
        "build_volume": (220, 220, 250), "nozzle": [0.4],
        "max_temp": 260, "bed_temp": 100,
        "protocols": ["ftp", "smb", "octoprint", "file"],
        "default_layer": 0.20, "default_infill": 15,
    },
    "Prusa i3 MK3S+": {
        "brand": "Prusa", "model": "i3 MK3S+",
        "build_volume": (250, 210, 210), "nozzle": [0.25, 0.4, 0.6],
        "max_temp": 280, "bed_temp": 100,
        "protocols": ["prusalink", "ftp", "octoprint", "file"],
        "default_layer": 0.15, "default_infill": 15,
    },
    "Prusa XL": {
        "brand": "Prusa", "model": "XL",
        "build_volume": (360, 360, 360), "nozzle": [0.4, 0.6],
        "max_temp": 290, "bed_temp": 110,
        "protocols": ["prusalink", "ftp", "octoprint", "file"],
        "default_layer": 0.20, "default_infill": 15,
    },
}


def test_palette_venti_nomi_presenti_e_non_vuoti():
    """Tutti i 20 nomi della palette esistono e sono stringhe non vuote."""
    assert len(PALETTE_ATTESA) == 20, "lo snapshot deve contenere 20 nomi"
    for nome in PALETTE_ATTESA:
        assert hasattr(C, nome), "costante '%s' assente" % nome
        valore = getattr(C, nome)
        assert isinstance(valore, str), "'%s' non è una stringa" % nome
        assert valore.strip(), "'%s' è vuota" % nome


def test_palette_colori_hex_formato():
    """I 15 colori esadecimali rispettano il formato #RRGGBB."""
    assert len(NOMI_COLORI_HEX) == 15
    for nome in NOMI_COLORI_HEX:
        valore = getattr(C, nome)
        assert RE_HEX.match(valore), "'%s' non è #RRGGBB: %r" % (nome, valore)


def test_palette_colori_rgba_formato():
    """I 2 colori con trasparenza rispettano il formato rgba(...)."""
    assert len(NOMI_COLORI_RGBA) == 2
    for nome in NOMI_COLORI_RGBA:
        valore = getattr(C, nome)
        assert RE_RGBA.match(valore), "'%s' non è rgba(...): %r" % (nome, valore)


def test_palette_font_contengono_famiglia_attesa():
    """I 3 font citano la famiglia attesa da TriviumCAD 1.3.0."""
    famiglie = {
        "FONT_HEAD": "Orbitron",
        "FONT_BODY": "Inter",
        "FONT_MONO": "Share Tech Mono",
    }
    for nome, famiglia in famiglie.items():
        valore = getattr(C, nome)
        assert famiglia in valore, "'%s' non cita '%s': %r" % (nome, famiglia, valore)


def test_palette_valori_identici_a_trivium():
    """I 20 valori coincidono alla lettera con TriviumCAD 1.3.0."""
    for nome, atteso in PALETTE_ATTESA.items():
        assert getattr(C, nome) == atteso, \
            "'%s' = %r, atteso %r" % (nome, getattr(C, nome), atteso)


def test_tema_scuro_allineato():
    """BACKGROUND_COLOR è rimappato su BG_PAGE: tema scuro, non più chiaro."""
    assert C.BACKGROUND_COLOR == C.BG_PAGE
    assert C.BACKGROUND_COLOR == "#0C1E36"
    assert C.BACKGROUND_COLOR != "#AEC8E0"
    assert C.TEXT_COLOR == C.TEXT_BODY


def test_identita_invariata():
    """Nome e versione di PenguinCAD non cambiano."""
    assert C.APP_NAME == "PenguinCAD"
    assert C.VERSION == "1.3.1"


def test_alias_legacy_invariati():
    """I sei alias legacy del tema chiaro restano identici a PenguinCAD 1.3.1."""
    for nome, atteso in ALIAS_ATTESI.items():
        assert getattr(C, nome) == atteso, \
            "alias '%s' = %r, atteso %r" % (nome, getattr(C, nome), atteso)


def test_neutral_colors_invariati():
    """La tabella dei colori neutri non è stata toccata."""
    assert C.NEUTRAL_COLORS == NEUTRAL_COLORS_ATTESI


def test_shape_library_invariata():
    """La libreria forme non è stata toccata."""
    assert C.SHAPE_LIBRARY == SHAPE_LIBRARY_ATTESA


def test_printer_profiles_invariati():
    """I profili stampanti non sono stati toccati."""
    assert C.PRINTER_PROFILES == PRINTER_PROFILES_ATTESI


def main():
    tests = [
        test_palette_venti_nomi_presenti_e_non_vuoti,
        test_palette_colori_hex_formato,
        test_palette_colori_rgba_formato,
        test_palette_font_contengono_famiglia_attesa,
        test_palette_valori_identici_a_trivium,
        test_tema_scuro_allineato,
        test_identita_invariata,
        test_alias_legacy_invariati,
        test_neutral_colors_invariati,
        test_shape_library_invariata,
        test_printer_profiles_invariati,
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
