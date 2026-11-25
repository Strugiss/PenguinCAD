#!/usr/bin/env bash
# build_appimage.sh — costruisce PenguinCAD-1.3.1-x86_64.AppImage
#
# Flusso: output PyInstaller one-folder (dist/PenguinCAD/) -> AppDir ->
# linuxdeploy (dipendenze, AppRun, desktop, icona) -> appimagetool (AppImage).
#
# Requisiti: dist/PenguinCAD/ gia' costruito (PenguinCAD.spec), packaging/ con
# desktop e icone, wget, rete. Gli strumenti sono AppImage: vengono eseguiti
# con --appimage-extract-and-run (nessun requisito FUSE).
#
# Nota sul plugin Qt: PyInstaller include gia' PyQt5 (5.15.6) con i plugin
# (platforms/libqxcb.so) nel bundle; deployare anche il Qt di sistema
# (5.15.3) con linuxdeploy-plugin-qt creerebbe un conflitto "Could not load
# the Qt platform plugin xcb". Il plugin viene quindi scaricato ma invocato
# solo se QT_PLUGIN_FORCE=1 (richiede qmake nel PATH).
set -euo pipefail

VERSION="1.3.1"
PROJ="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$PROJ/dist"
WORK="$PROJ/build/appimage"
TOOLS="$WORK/tools"
QTPLUGIN_DIR="$TOOLS/qt-plugin"
APPDIR="$WORK/PenguinCAD.AppDir"

URL_LINUXDEPLOY="https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage"
URL_QTPLUGIN="https://github.com/linuxdeploy/linuxdeploy-plugin-qt/releases/download/continuous/linuxdeploy-plugin-qt-x86_64.AppImage"
URL_APPIMAGETOOL="https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"

mkdir -p "$TOOLS" "$QTPLUGIN_DIR"

fetch() { # fetch <url> <dest>
  if [ -x "$2" ]; then return 0; fi
  echo "[tools] scarico $(basename "$2")"
  wget -q -O "$2" "$1"
  chmod +x "$2"
}

fetch "$URL_LINUXDEPLOY" "$TOOLS/linuxdeploy"
fetch "$URL_QTPLUGIN" "$QTPLUGIN_DIR/linuxdeploy-plugin-qt"
fetch "$URL_APPIMAGETOOL" "$TOOLS/appimagetool"

# AppDir pulita
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin" "$APPDIR/usr/share/applications" \
         "$APPDIR/usr/share/icons/hicolor/256x256/apps"

# 1) output PyInstaller in usr/bin (eseguibile rinominato penguincad = Exec)
cp -a "$DIST/PenguinCAD/." "$APPDIR/usr/bin/"
mv "$APPDIR/usr/bin/PenguinCAD" "$APPDIR/usr/bin/penguincad"

# 2) desktop + icona (nome icona = campo Icon del .desktop)
cp "$PROJ/packaging/penguincad.desktop" "$APPDIR/usr/share/applications/"
cp "$PROJ/packaging/penguincad.desktop" "$APPDIR/penguincad.desktop"
cp "$PROJ/packaging/penguincad-256.png" "$APPDIR/penguincad.png"
cp "$PROJ/packaging/penguincad-256.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/penguincad.png"

# 3) linuxdeploy: dipendenze + AppRun + integrazione desktop/icona
export OUTPUT="$DIST/PenguinCAD-$VERSION-x86_64.AppImage"
"$TOOLS/linuxdeploy" --appimage-extract-and-run \
  --appdir "$APPDIR" \
  --desktop-file "$APPDIR/penguincad.desktop" \
  --icon-file "$APPDIR/penguincad.png"

# 3b) plugin Qt solo su richiesta esplicita (vedi nota in testa)
if [ "${QT_PLUGIN_FORCE:-0}" = "1" ]; then
  echo "[qt] invocazione esplicita di linuxdeploy-plugin-qt"
  "$QTPLUGIN_DIR/linuxdeploy-plugin-qt" --appimage-extract-and-run --appdir "$APPDIR"
fi

# 4) appimagetool: filesystem squashfs + runtime AppImage
"$TOOLS/appimagetool" --appimage-extract-and-run --no-appstream "$APPDIR" "$OUTPUT"

ls -la "$OUTPUT"
