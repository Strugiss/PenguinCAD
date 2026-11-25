# PenguinCAD — CAD 3D per stampa 3D (by N47Lab)

**CAD 3D parametrico/mesh gratuito per stampa 3D — in italiano**

PenguinCAD è un ambiente integrato per la modellazione 3D, la progettazione meccanica,
la generazione di percorsi utensile (CAM) e l'invio diretto delle stampe alla
stampante 3D. Sviluppato in **Python** con **PyQt5 + OpenGL + trimesh**, è pensato
per chi vuole passare dall'idea al file stampabile senza cambiare programma.

- Versione: **1.3.1**
- Sviluppato da: **N47Lab Team (Alessandro Tulli)** — © 2026
- Licenza: **MIT** (vedi [LICENSE](LICENSE))

---

## Funzionalità chiave

| Funzionalità | Descrizione |
|---|---|
| ⭐ **Filettatura analitica** | Filettatura esterna e interna con 3 profili (Filo ISO 60°, Trapezio, Arrotondato) e 5 modalità (Auto, Metrico, UNF, UNC, Gas). Per 9 forme native la filettatura segue il profilo reale della superficie, non il bounding box. |
| ⭐ **Invio diretto alle stampanti** | 8 modalità di invio: 7 protocolli diretti (Bambu Lab MQTT+FTP, Creality HTTP, PrusaLink, OctoPrint, FTP, SMB, Anycubic Cloud) + esportazione con profilo stampante. 12 profili precaricati (Bambu Lab X1C/P1S/A1/A1 Mini, Anycubic Kobra 3/Kobra 2/Vyper, Creality K1 Max/K1/Ender 3 V3, Prusa i3 MK3S+/XL) con volume di stampa, ugelli e impostazioni di default. |
| ⭐ **Import 2D → 3D con buchi** | Importa SVG, DXF e immagini (anche foto di silhouette): l'esterno diventa un solido estruso e i contorni interni diventano buchi automaticamente (binarizzazione + rilevamento contorni, fino a 400 punti per contorno). |
| **2PenAxE — sketch 2D** | Finestra multi-piano (XY/XZ/YZ) con linea, polilinea, rettangolo, cerchio, arco, snap ad ancore, quote live e undo/redo; le entità si vedono in scena e si salvano in `.n47`. |
| **Tema scuro N47Lab** | Interfaccia scura con accenti ambra/ottone e contrasto WCAG AA; tendine con freccia, icone QPainter, nessuna emoji nella toolbar. |
| Primitive | 9 primitive parametriche: Cubo, Cilindro, Sfera, Cono, Collare, Esagono, Spirale, Arco, Scatola vuota. |
| Testo 3D | Creazione testo, adattamento alla superficie della forma e bassorilievo. |
| Booleane | Unione, sottrazione, intersezione con 6 livelli di fallback per mesh difficili. |
| Guscio e fillet | Guscio su forme cave/aperte e arrotondamento spigoli (Taubin pesato con edge detection). |
| Slicer | Taglio a fette lungo gli assi con offset e numero di pezzi. |
| CAM | Percorsi utensile adattivi zig-zag (diametro utensile, passo laterale, quota di sicurezza, avanzamento). |
| Gizmo | Sposta, scala e ruota con goniometro a tacche (15°/45°); trascina le facce per allungare la forma. |
| Selezione | Click ray-cast, box select, Ctrl/Shift+Click per multi-selezione. |
| Undo/Redo | Fino a 50 passi (Ctrl+Z / Ctrl+Y). |
| Export | STL, OBJ, PLY, 3MF, GLB. |
| Console | Console Python integrata con accesso diretto a scena e oggetti selezionati. |
| Tutorial | Wizard di 11 pagine all'avvio, richiamabile da Opzioni/Aiuto. |
| Misura distanza/angolo | Ctrl+M (2 clic) e Ctrl+Shift+M (3 clic) su punti 3D reali della superficie; popup "Misura — Scala forma" con scala uniforme ancorata a Z=0 e undo. |
| Snap griglia | Allineamento al reticolo (Opzioni → Snap Griglia). |
| Chamfer | Smussatura spigoli (Menu Modifica → Chamfer…). |
| Pattern lineare/circolare | Copie di oggetti su riga o in cerchio (Menu Modifica → Pattern lineare… / Pattern circolare…). |
| Mirror | Specchiatura lungo gli assi (Menu Modifica → Specchia). |
| Smooth/Subdivide/Decimate | Rifinitura della mesh (Menu Mesh). |
| Riparazione mesh | Ricostruzione di mesh non watertight (Menu Mesh → Ripara). |

---

## Installazione

Richiede **Python 3.10+** (Windows, macOS, Linux).

```bash
pip install -r requirements.txt
```

Dipendenze **principali** (in `requirements.txt`): `numpy`, `trimesh`, `manifold3d`,
`shapely`, `PyQt5`, `PyOpenGL`, `scipy`, `pillow`, `networkx`, `rtree`, `lxml`,
`fast_simplification`, `svg.path`.

Dipendenze **opzionali** (funzionano in fallback se assenti, ma attivano funzioni extra):

| Pacchetto | Necessario per |
|---|---|
| `scikit-image` | Import immagini → 3D (rilevamento contorni e buchi) |
| `requests` | Invio a stampanti via HTTP (Creality, PrusaLink, OctoPrint, Anycubic Cloud) |
| `paho-mqtt` | Invio a stampanti Bambu Lab (MQTT + FTP over TLS) |

## Avvio

```bash
python penguincad.py
```

## Installazione Linux (AppImage, .deb, .rpm)

Pacchetti per Linux **x86_64** (build su Ubuntu 22.04, glibc 2.35) nella cartella
`dist/`. Nome pacchetto: `penguincad`, versione `1.3.1`.

### AppImage — nessuna installazione, massima portabilità

```bash
chmod +x PenguinCAD-1.3.1-x86_64.AppImage
./PenguinCAD-1.3.1-x86_64.AppImage                              # con FUSE
./PenguinCAD-1.3.1-x86_64.AppImage --appimage-extract-and-run   # senza FUSE
```

### Debian/Ubuntu (.deb, amd64)

```bash
sudo dpkg -i penguincad_1.3.1_amd64.deb
sudo apt-get -f install     # solo se mancano dipendenze
penguincad                  # avvio (comando in /usr/bin)
sudo dpkg -r penguincad     # rimozione
```

### Fedora/RHEL/openSUSE (.rpm, x86_64)

```bash
sudo rpm -ivh penguincad-1.3.1-1.x86_64.rpm
penguincad
sudo rpm -e penguincad
```

`.deb` e `.rpm` installano il bundle in `/opt/penguincad/`, il comando
`/usr/bin/penguincad`, il desktop file
(`/usr/share/applications/penguincad.desktop`) e l'icona
(`/usr/share/icons/hicolor/256x256/apps/penguincad.png`).

## Struttura del progetto

```
PenguinCAD/
├── penguincad.py         # Applicazione completa: UI (PyQt5), rendering OpenGL, logica
├── sketch.py             # 2PenAxE: sketch 2D multi-piano (geometria pura + dialog)
├── core/                 # Modulo core, senza dipendenze Qt
│   ├── constants.py      # Costanti, palette, libreria forme, profili stampante
│   ├── primitives.py     # Generazione mesh primitive e testo 3D
│   ├── mesh_ops.py       # Booleane, fillet, validazione mesh
│   ├── thread.py         # Filettatura (profili, mesh, sottrazione)
│   ├── cam.py            # Percorsi utensile adattivi
│   ├── scene.py          # Scena, undo/redo, operazioni, scanner
│   └── utils.py          # Utility (es. NumpyEncoder)
├── Immagini/             # Icone applicative (2PenAxE, freccia tendine)
├── Test/                 # Test automatici (pytest) e file di prova (SVG/DXF)
├── Documenti/            # Report di collaudo e documentazione storica
├── packaging/            # Script e risorse di packaging Linux (AppImage/deb/rpm)
├── dist/                 # Pacchetti distribuiti (AppImage, .deb, .rpm)
├── CHANGELOG.md          # Storico delle versioni
├── TUTORIAL.md           # Guida completa all'uso
├── LICENSE               # Licenza MIT
├── .gitignore            # Esclusioni Git
├── PenguinCAD.spec       # Build PyInstaller (Windows/Linux, one-folder)
└── requirements.txt      # Dipendenze Python
```

Il modulo `core/` è stato estratto dalla UI in modo da poter essere testato e
riutilizzato senza caricare Qt.

## Build

### Build Windows (storico) — Eseguibile (PyInstaller)

```bash
pyinstaller PenguinCAD.spec
```

Output in `dist\PenguinCAD\` (collezione one-folder con `PenguinCAD.exe`, icona `favicon.ico`).

### Build pacchetti Linux (Ubuntu 22.04)

```bash
pip install pyinstaller
pyinstaller PenguinCAD.spec          # bundle in dist/PenguinCAD/
bash packaging/build_appimage.sh     # dist/PenguinCAD-1.3.1-x86_64.AppImage
bash packaging/build_deb.sh          # dist/penguincad_1.3.1_amd64.deb
bash packaging/build_rpm.sh          # dist/penguincad-1.3.1-1.x86_64.rpm
```

Note: `PenguinCAD.spec` usa `upx=False` (UPX non richiesto); `build_rpm.sh`
usa `rpmbuild` di sistema se presente, altrimenti la toolchain portatile in
`~/toolchain/rpmroot` (estratta dai `.deb` di rpm, senza root).

### Installer Windows (Inno Setup) — storico

Lo script Inno Setup del rilascio Windows è conservato come storico in
`Documenti/` (associazione `.n47`, installazione e scorciatoie). Per il port
Linux vedi la sezione "Installazione Linux (AppImage, .deb, .rpm)".

## Screenshot

*(Sezione riservata: le immagini verranno aggiunte qui.)*

## Changelog

Vedi [CHANGELOG.md](CHANGELOG.md) per lo storico delle versioni.

## Tutorial

Guida completa all'uso: [TUTORIAL.md](TUTORIAL.md).

## Licenza

MIT — vedi [LICENSE](LICENSE). © 2026 N47Lab Team.