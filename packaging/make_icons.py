#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera le icone PNG di PenguinCAD a partire da favicon.ico.

Uso: python3 make_icons.py [sorgente.ico] [cartella_output]
Produce penguincad-256.png e penguincad-512.png (RGBA, ridimensionate con
LANCZOS se il sorgente non contiene gia' quella dimensione).
"""
import sys
from pathlib import Path

from PIL import Image


def main() -> int:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("favicon.ico")
    outdir = Path(sys.argv[2]) if len(sys.argv) > 2 else src.parent
    if not src.is_file():
        print(f"ERRORE: sorgente non trovato: {src}")
        return 1
    outdir.mkdir(parents=True, exist_ok=True)

    img = Image.open(src)
    print(f"Sorgente: {src} — formati interni: {sorted(img.info.get('sizes', [img.size]))}")
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    for size in (256, 512):
        out = outdir / f"penguincad-{size}.png"
        img.resize((size, size), Image.LANCZOS).save(out, "PNG")
        print(f"OK {out} ({out.stat().st_size} byte)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
