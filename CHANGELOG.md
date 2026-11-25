# Changelog PenguinCAD

Tutte le modifiche notevoli del progetto PenguinCAD sono documentate in questo file.

Il formato segue [Keep a Changelog](https://keepachangelog.com/it/1.1.0/);
versioning semantico: `MAJOR.MINOR.PATCH`.

## [1.3.1] - 2026-11-22

### Sette fix ereditati

- **Oggetti nascosti non selezionabili**: click e box select ignorano gli oggetti
  con `visible=False`; restano in scena e nell'outliner, esclusi dall'export.
- **Console e cache GL**: un comando dalla console invalida le cache GL; i VBO
  differiti vengono ricostruiti al paint successivo per tutta la scena.
- **Valore numerico nell'overlay misura**: distanza e angolo mostrano il valore
  nel badge, persistente tra i click e aggiornato al resize (contrasto 10,68:1).
- **Rinomina dall'outliner**: doppio click e menu contestuale rinomina l'oggetto;
  il nome resta dopo Annulla e viene salvato.
- **Scala uniforme ancorata a Z=0**: il dialog "Misura — Scala forma" mantiene il
  minimo a Z=0 e applica la stessa scala su X/Y/Z, con undo.
- **Pannello Proprietà Layer/Shape**: il pannello riflette layer e forma della
  selezione singola e multipla; collasso e resize coerenti.
- **Misura 3D reale su Z≠0**: i punti di misura sono l'intersezione del raggio
  con la mesh visibile (ray-cast), con distanza e angolo 3D; fallback dichiarato
  al piano Z=0 solo se il raggio non colpisce geometria.

### Test

- **98/98** (`pytest Test -q -p no:cacheprovider`), Windows e Linux.

## [1.3.0] - 2026-11-22

### Allineamento a TriviumCAD 1.3.0 (F1–F6c)

- **2PenAxE — sketch 2D multi-piano** (`sketch.py`, `Test/test_sketch.py`): finestra modale con due pannelli, piani XY/XZ/YZ, strumenti linea/polilinea/rettangolo/cerchio/arco, snap ad ancore, quote in mm reali, undo/redo. Entità JSON-safe; persistenza `.n47` con retrocompatibilità (file senza `sketch_2d` → lista/stato vuoti).
- **Integrazione GUI 2PenAxE**: pulsante in toolbar con icona asset e fallback QPainter, overlay ambra in scena (`_draw_sketch_2d`), apertura (`_open_2penaxe`) e live update (`_apply_sketch_2d`), `Ctrl+N` su Nuovo, titolo del dialog con il prodotto.
- **Integrità dati ed export**: filettatura esterna e interna conserva i 6 metadata dell'oggetto e rimuove le cache GL; testo 3D con `visible=True`/`locked=False`; export (STL/OBJ/PLY/3MF/GLB), export con profilo e invio stampante includono solo gli oggetti visibili.
- **Interazione e UI minore**: Ctrl+click su oggetto = toggle di multi-selezione (sul vuoto orbita), Shift+click invariato; outliner aggiorna nome e icone anche a parità di conteggio; Snap/Magneti sincronizzati menu↔toolbar; pannelli laterali collassabili con linguette; dock Outliner non chiudibile.
- **Overlay misura**: widget trasparente sopra la viewport disegnato con QPainter (niente QPainter in `paintGL` per la misura), linee half-pixel anti-sdoppiamento, aggiornamento su click, Esc e resize.
- **Restyle scuro**: alias legacy rimappati sulla palette N47Lab (`BG_PAGE`, `TEXT_BODY`, `BORDER_SOFT`, ...), QSS globale in `_app_stylesheet()`, dialoghi/pannelli/console/tutorial/splash scuri, contrasto WCAG AA verificato, font fallback Linux (`sans-serif`/`monospace`), toolbar a icone QPainter senza emoji.
- **Rifiniture**: freccia scura su tutte le tendine (asset `Immagini/freccia_giu.png`, dichiarato nello spec), titolo Tutorial senza emoji, pulsante Booleane con larghezza e padding corretti.
- **Test**: 65/65 (`pytest Test -q -p no:cacheprovider`).

### Port Linux (dettaglio)

- **Rinomina prodotto**: il progetto è **PenguinCAD** in codice, interfaccia, log e documentazione.
- **Fix percorsi test (relativi)**: i test in `Test/` risolvono la root del progetto da `__file__` (nessun percorso assoluto).
- **Desktop portabile (QStandardPaths)**: l'invio "solo file" copia sul Desktop tramite `QStandardPaths.writableLocation` con fallback `~`.
- **Dipendenze Linux**: aggiunto `requirements.txt` con dipendenze principali e opzionali.
- **Fix viewport nera su Linux/Mesa**: il contesto OpenGL richiesto torna legacy 2.1/NoProfile (fixed-function): risolto il fallimento di `initializeGL` (contesto Core) che impediva il disegno di griglia e scena.
- **Fix collaudo — 8 aree**:
  - `_generate_blender_arc`: il taglio a semipiano generava sempre ~180°; ora il settore rispetta l'`apertura` (360° = anello pieno).
  - `_generate_blender_hollow_box`: l'`except` non fallisce più in silenzio (log su stdout); con networkx la cavità è generata correttamente (30×20×20, muro 2.5 → volume 4875, watertight).
  - `_UndoManager.undo/redo`: anche gli stati con 0 oggetti sono salvati negli stack (dopo un delete totale `redo()` ripristina la scena vuota).
  - `_adapt_text_to_shape`: posizione camera corretta secondo la convenzione di PyOpenGL (`-mv[:3,:3] @ mv[3,:3]`); eliminato il falso "Camera troppo vicina alla forma".
  - `_simplify_contour`: campionamento a indici equidistanti (rispetta `max_pts`, es. 1000→400).
  - `_new`: conferma "Creare una nuova scena comunque?" (Annulla/Crea, default Annulla) solo con scena non vuota; invalidazione VBO della scena precedente.
  - `_send_fileonly`: rimosso l'`import os` locale che rompeva il fallback `~` (`UnboundLocalError`); lo status "File pronto" compare solo se la copia riesce, altrimenti status d'errore.
  - `PrinterConnectDialog`: il cambio protocollo passa il codice (`currentData()`), non la label: help e campi credenziali corretti.
  - `_run_blocking`: le eccezioni del worker sono segnalate all'utente (warning), non solo nel traceback.
  - `_cad_repair`: il messaggio di errore non è più sovrascritto da "Nessun oggetto riparato"; log su stdout.
- **Fix collaudo — campo Utente/Email (`PrinterConnectDialog`)**: `_on_protocol_change` abilita il campo utente anche per `anycubic_cloud` (prima solo ftp/smb), con label/placeholder dedicati ("Email (Anycubic Cloud):" / "es. nome@email.com"), coerente con `_send_anycubic_cloud` che legge l'email da lì; gli altri protocolli restano invariati (ftp/smb: utente+password; octoprint/bambulab/prusalink: codice/API key; creality/file: nessun campo). Verificato in VM: `user_entry.isEnabled()==True` per Anycubic Cloud.
- **Fix collaudo 2 — UI/import/gizmo**:
  - **Menu Modifica — Taglia/Copia/Incolla**: aggiunte le voci collegate ai metodi reali di `GLWidget` (`_cut_selected`, `_copy_selected`, `_paste_clipboard`) con le scorciatoie standard `Ctrl+X`/`Ctrl+C`/`Ctrl+V`; verificato che agiscano sulla selezione corrente (Taglia → clipboard + rimozione, Incolla → nuovo oggetto).
  - **Import 2D/immagini**: `File → Importa` ora indirizza esplicitamente a "Da 2D a 3D" quando si seleziona un file SVG/DXF/immagine, al posto dell'errore di `trimesh` ("file_type 'png' not supported"); il percorso ufficiale per i 2D resta il pulsante "Da 2D a 3D" della toolbar (`_import_2d_to_3d`), con import immagine verificato (PNG cerchio nero su bianco → mesh watertight).
  - **Hit-test del gizmo**: i quadratini di rotazione (`rh*`) usano una tolleranza di pick dedicata (15 px invece di 30 px): non intercettano più il trascinamento del corpo dell'oggetto, che torna a traslare (handle centrale `DRAG_HANDLE`/`DRAG_OBJECT`) con snap XY. Verificato: click a 15 px dal quadratino → traslazione (`center`), click sul quadratino → rotazione (`rot_z`).
  - **Scatola vuota — volume confermato (nessuna modifica)**: 4144 mm³ è coerente coi parametri reali di `SHAPE_LIBRARY` (30×20×20, muro 2.0): fondo 1200 + pareti (600−416)×16 = 2944 → 4144, watertight. Il valore 4875 si riferisce a muro 2.5 (prova precedente), non ai parametri del click.
  - **Import SVG — esito VM (punto 3)**: con la copia sincronizzata il `TypeError` segnalato dal collaudo non si riproduce: `_import_vector_to_3d` produce mesh valide da tutti gli SVG di `Test/` (`test_import.svg`: 8 verts/12 faces, watertight; `scudo_aprilia.svg`: 10/16, watertight; `test_hole.svg`: 16/32, watertight) con Python 3.10.12 + trimesh 5.1.0 + svg.path 7.1. Per evitare drift dell'ambiente, `requirements.txt` blocca `trimesh==5.1.0` e `svg.path==7.1` (versioni verificate in VM).
- **Fix collaudo 3 — pannello Parametri (sincronizzazione selezione)**: i campi X/Y/Z e Rot X/Y/Z ora riflettono l'oggetto selezionato (prima restavano a 0.00: `_create_right_panel` non esponeva alcun `update_ui`, quindi `CADWindow.update_ui` non li toccava mai). X/Y/Z = centroide della mesh, stessa base di `_apply_param` (che trasla di `value - centroid`: il valore mostrato è riapplicabile senza scatti); Rot X/Y/Z = `obj.metadata["rot_*"]`, unico stato di rotazione tracciato dal pannello (le rotazioni via gizmo non aggiornano il metadata: i campi Rot riflettono l'ultima rotazione applicata da lì). Aggiornamento programmatico con `blockSignals`, nessun loop di segnali. Verificato in VM (offscreen): oggetto traslato a (37.00, −32.00, 10.00) → campi 37.00/−32.00/10.00; digitazione X=50 → centroide X=50.00; Rot Z=45 stabile dopo `update_ui`; 0 emissioni `valueChanged` durante `update_ui` programmatico, 1 alla digitazione utente; nessuna eccezione senza selezione o con selezione multipla.
- **Fix audit F2 — layout/UI**:
  - **Pannello sinistro scrollabile**: avvolto in `QScrollArea` (`widgetResizable=True`, pattern `PropertiesPanel`): a finestra 1280×720 la sezione Filettatura (e Affetta/Arrotonda/CAM) è raggiungibile via scroll, con widget a dimensione piena (combo ≥28 px) invece che compressi/clippati.
  - **Contrasto dialogo stampante**: pulsante "Invia alla stampante" `#4CAF50` → `#2E7D32` (bianco su verde, contrasto ≥4,5:1 WCAG AA); label info protocollo `#3060A0` → `#1F4E79` (≥4,5:1 su `#AEC8E0`).
  - **Placeholder "Inserisci testo..."** (Testo 3D): colore esplicito `#6E6E6E` via `QPalette.PlaceholderText` (prima grigio di default, 4,0:1).
  - **Console Python**: rimossa la cornice ASCII dal titolo (glifo "║" tagliato dal bordo del campo).
- **Ripristino profilo "Filo" (revert audit F3)**: ripristinato il comportamento originale di TriviumCAD per il profilo Filo (fedeltà su richiesta N47): `_r_mod_profile` e il ramo "Filo" di `_apply_thread_profile` tornano alla scala if/elif e a `np.where` originali (fianchi reali a 44,35°, non 60°); `_get_profile_2d` resta invariata.
  - Nota documentale (nessuna modifica): `_surface_radius_at("cone")` usa `r_top = 0.1·r_base` all'apice — scelta intenzionale per evitare r = 0 (audit F3, difetto D3).
- **Fix audit F6 — documenti/UI**:
  - **Ctrl+D = Duplica** (menu Modifica); la deselezione totale passa a **Ctrl+Shift+D** (handler `GLWidget.keyPressEvent`); documentazione allineata (tutorial interno e TUTORIAL.md).
  - Tutorial interno: "Profili integrati (13)" → **12** (conteggio reale dei profili precaricati).
  - Menu contestuale documentato con le 5 voci reali (Duplica, Elimina, Raggruppa, Separati, Allinea a Z=0).
  - **README.md**: struttura aggiornata (`PenguinCAD/`, voci `Test/`, `Documenti/`, `CHANGELOG.md`, `TUTORIAL.md`, `LICENSE`, `.gitignore`); installazione via `pip install -r requirements.txt`; `scipy`/`pillow` tra le dipendenze principali; sezione PyInstaller etichettata "Build Windows (storico)".
  - **TUTORIAL.md**: avvio `python3 penguincad.py` (rimossi `.exe` e doppio clic `.n47`); "File → Invia alla stampante..."; "Opzioni → Mostra Tutorial..."; "Da2 a 3D"; scorciatoie Ctrl+D/Ctrl+Shift+D.
- **Packaging Linux (AppImage + .deb + .rpm)**: pacchetti `penguincad` 1.2.0 x86_64 (storico, costruiti prima del bump 1.3.0) su Ubuntu 22.04 (glibc 2.35) e testati in VM:
  - `PenguinCAD-1.2.0-x86_64.AppImage` (PyInstaller one-folder + linuxdeploy/appimagetool; avvio verificato con `--appimage-extract-and-run` sotto Xvfb);
  - `penguincad_1.2.0_amd64.deb` (`/opt/penguincad` + symlink `/usr/bin/penguincad` + desktop/icona; installazione, avvio GUI e rimozione verificati);
  - `penguincad-1.2.0-1.x86_64.rpm` (spec con `AutoReqProv: no`; installazione in root di prova con `rpm --root` verificata);
  - script in `packaging/` (`build_appimage.sh`, `build_deb.sh`, `build_rpm.sh`, `penguincad-rpm.spec`, `make_icons.py`, `gui_smoke_test.sh`), icone `penguincad-256.png`/`penguincad-512.png` generate da `favicon.ico`;
  - `PenguinCAD.spec` con `upx=False` per i pacchetti Linux; README: nuova sezione "Installazione Linux (AppImage, .deb, .rpm)".
- **Misura 3D reale (fix 7)**: i click di misura salvano il punto di intersezione del raggio con la mesh visibile colpita (`_pick_surface_point`), con la Z reale; distanza `math.dist` 3D e angolo con vettori 3D in `_angle_between`; overlay proiettato con `_world_to_screen`; fallback dichiarato al piano Z=0 solo se il raggio non colpisce geometria. Il dialog "Misura — Scala forma" usa la distanza 3D e la scala resta ancorata a Z=0 (undo). Cubo 20 mm: due punti a 10 mm sulla faccia Z=20 → **10.00 mm** (prima 13.03 mm per proiezione a Z=0). Suite: 98/98.

## [1.2.0] - 2026-09-07

### Nome del prodotto

**Rinomina del prodotto** (il nome N47Lab resta al laboratorio/autor: 'by N47Lab').

### Fix

**Camera — "scatto piano" risolto**

- Eliminato lo stato residuo della modalità "release" che faceva scattare la
  vista al click successivo.
- Perno di rotazione asse Z (ROT_Z) corretto durante l'orbita.
- Guardie anti-jitter su trascinamento e orbita.
- Clamp della rotella di zoom (limiti minimo/massimo rispettati).

**Testo 3D — 12 difetti corretti**

- "Adatta" poteva proiettare il testo sulla faccia sbagliata della forma.
- Profondità incisione errata nel bassorilievo.
- Testo multilinea mal gestito.
- Dimensioni frazionarie non rispettate.
- Font mancante sul sistema: fallback gestito.
- Mesh del testo non sempre watertight.
- Crash su import SVG con geometria non valida.
- Import dei componenti del testo (caratteri/parole) corretto.

**Critici corretti**

- Doppia finalizzazione operazioni: eliminata la chiamata duplicata
  (`end_operation` + `cancel_operation` nel `finally`).
- Smooth/Subdivide non crashano più sulle mesh sostituite: il riferimento
  originale viene salvato prima della sostituzione dell'oggetto.
- Rotazione dal pannello Proprietà: le spinbox `rot_x`/`rot_y`/`rot_z` ora
  ruotano effettivamente l'oggetto.
- `_notify()` collegato alla **status bar**: i feedback delle operazioni sono
  visibili all'utente (prima finivano solo su stdout).
- Status bar: il **timer FPS** non sovrascrive più i messaggi di misura e le
  notifiche delle operazioni.

### Aggiunto (funzioni attivate)

- **Misura distanza/angolo**: `Ctrl+M` (2 clic) e `Ctrl+Shift+M` (3 clic) con
  popup **"Misura — Scala forma"** (scala uniforme centrata, con undo).
- **Snap griglia** funzionante (Opzioni → Snap Griglia).
- **Chamfer** (Menu Modifica → Chamfer…).
- **Pattern lineare e circolare** (Menu Modifica → Pattern lineare… / Pattern
  circolare…).
- **Mirror / Specchia** lungo X, Y, Z (Menu Modifica → Specchia).
- **Smooth, Subdivide, Decimate** (Menu Mesh).
- **Ripara** (Menu Mesh → Ripara): riparazione di mesh non watertight.
- **Outliner con layer**: elenco oggetti con layer; clic per selezionare,
  Ctrl+clic per multi-selezione.

### Migliorie

- **Core modulare senza Qt**: la logica computazionale è stata estratta in
  `core/` (`constants`, `primitives`, `thread`, `mesh_ops`, `cam`, `scene`,
  `utils`), testabile e riutilizzabile senza caricare l'interfaccia.
- **Documentazione**: aggiunti README.md, TUTORIAL.md e questo CHANGELOG.md;
  i report di sviluppo sono stati raccolti in `Documenti/`.
- **Versione unica**: `VERSION` centralizzata in `core/constants.py`
  (1.2.0) e usata da UI e dialoghi.

## [1.1.0] - 2026-07-18

Riepilogo dello sviluppo 22/06 → 17/07 (da `report_modifiche.txt`).

### Aggiunto

- **Riconoscimento topologico "Sposta Faccia" v2**: selezione della faccia per
  componente connessa (normale allineata all'asse, soglia 40°) e allungamento
  uniforme dal centro senza assottigliare la sezione.
- **Face Handles Gizmo**: 6 maniglie al centro di ogni faccia del bounding box
  (X+/X−, Y+/Y−, Z+/Z−) con frecce 3D, offset proporzionale alla dimensione.
- **Splash screen** con logo "CAD" 3D (QPainterPath, ombra 3D).
- **Stampa 3D diretta**: 12 profili stampante (Bambu Lab X1C/P1S/A1/A1 Mini,
  Anycubic Kobra 3/Kobra 2/Vyper, Creality K1 Max/K1/Ender 3 V3,
  Prusa i3 MK3S+/XL) e protocolli MQTT+FTP, HTTP WiFi, PrusaLink, OctoPrint,
  FTP, SMB, Cloud.
- **Filettatura interna incisa**: booleana DIFFERENZA con volume watertight;
  raggio superficie reale su ogni forma nativa; fallback ray-casting per forme
  importate.
- **Filettatura esterna**: generazione diretta della mesh (N×M sezioni, vertici
  dei tappi condivisi → watertight, ~3600 vertici per cilindro standard);
  profili Filo ISO 60°, Trapezio, Arrotondato.
- **TutorialDialog**: wizard a schede (11 pagine) con navigazione, contatore
  pagina, "Nascondi all'avvio" (QSettings), mostrato dopo lo splash.
- **Adatta Testo**: proiezione radiale dal centro della forma con raycast
  batch, spessore preservato lungo la normale, normali corrette.
- **Sezione 2D→3D completamente riscritta**: SVG/DXF via
  `trimesh.load_path()` + `extrude_polygon()` (fallback `force='mesh'`);
  immagini via `skimage.find_contours()` (fallback ConvexHull);
  rivoluzione, loft e sweep con `trimesh.creation`.
- **Buchi automatici nella silhouette**: binarizzazione (soglia 0.4),
  `unary_union` dei contorni interni + `difference` dall'esterno,
  semplificazione a ~400 punti, normalizzazione poligoni.

### Corretto

- Bug "piano che scatta": `_drag_target` residuo nella `_sync_camera()`.
- Booleane senza Undo e metadata corrotto: `start_operation/end_operation`,
  metadata selettivo e `_refresh_outliner()`.
- Codice duplicato in Adatta Testo (NameError).

### Migliorato

- Performance: display list per il gizmo, `glPushAttrib` ristretto, operazioni
  pesanti (booleane, toolpath, filettatura, fillet) in QThread con progress
  dialog — UI non bloccante.
- Fillet: subdivisione adattiva (max 10 000 facce), edge detection sugli spigoli
  vivi, peso gaussiano + Taubin filter + blend (volume −0.65% ÷ −1.79%).
- Interfaccia: finestra dinamica (1280×720, min 960×540), griglia forme 3×3.

## [1.0.0] - 2026-06-22

Rilascio iniziale (storico non dettagliato; vedi `Documenti/` per i report di
sviluppo precedenti).