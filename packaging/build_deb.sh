#!/usr/bin/env bash
# build_deb.sh — costruisce penguincad_1.3.1_amd64.deb
#
# Struttura: /opt/penguincad/ (bundle PyInstaller one-folder),
# /usr/bin/penguincad (symlink), desktop + icona in /usr/share.
# Dipendenze: librerie core di sistema + libgl1 (PyOpenGL carica libGL via
# ctypes; PyInstaller bundla X11/xcb/xkb/Qt/fontconfig/dbus/glib).
set -euo pipefail

VERSION="1.3.1"
PROJ="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$PROJ/dist"
WORK="$PROJ/build/deb"
PKGROOT="$WORK/penguincad_${VERSION}_amd64"

if [ ! -x "$DIST/PenguinCAD/PenguinCAD" ]; then
  echo "ERRORE: bundle PyInstaller assente in $DIST/PenguinCAD/ (eseguire prima pyinstaller PenguinCAD.spec)" >&2
  exit 1
fi

rm -rf "$WORK"
mkdir -p "$PKGROOT/opt/penguincad" \
         "$PKGROOT/usr/bin" \
         "$PKGROOT/usr/share/applications" \
         "$PKGROOT/usr/share/icons/hicolor/256x256/apps" \
         "$PKGROOT/DEBIAN"

# 1) bundle PyInstaller in /opt/penguincad
cp -a "$DIST/PenguinCAD/." "$PKGROOT/opt/penguincad/"

# 2) comando penguincad + integrazione desktop
ln -s /opt/penguincad/PenguinCAD "$PKGROOT/usr/bin/penguincad"
cp "$PROJ/packaging/penguincad.desktop" "$PKGROOT/usr/share/applications/penguincad.desktop"
cp "$PROJ/packaging/penguincad-256.png" "$PKGROOT/usr/share/icons/hicolor/256x256/apps/penguincad.png"

# 3) control (Installed-Size in KiB)
SIZE_KB=$(du -sk "$PKGROOT" | cut -f1)
cat > "$PKGROOT/DEBIAN/control" <<EOF
Package: penguincad
Version: $VERSION
Section: graphics
Priority: optional
Architecture: amd64
Maintainer: N47Lab Team (Alessandro Tulli)
Installed-Size: $SIZE_KB
Depends: libc6 (>= 2.35), libgcc-s1, libstdc++6, libgl1, zlib1g, libx11-6, libx11-xcb1, libxcb1, libxkbcommon0, libxkbcommon-x11-0, libdbus-1-3, libfontconfig1, libfreetype6, libglib2.0-0
Description: CAD 3D per stampa 3D (port Linux di TriviumCAD)
 PenguinCAD e' un ambiente integrato per la modellazione 3D, la
 progettazione meccanica, la generazione di percorsi utensile (CAM) e
 l'invio diretto delle stampe alle stampanti 3D.
 .
 Sviluppato in Python con PyQt5, OpenGL e trimesh.
EOF

# 4) script maintainer
cat > "$PKGROOT/DEBIAN/postinst" <<'EOF'
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database -q /usr/share/applications || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi
exit 0
EOF
cat > "$PKGROOT/DEBIAN/postrm" <<'EOF'
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database -q /usr/share/applications || true
fi
exit 0
EOF
chmod 755 "$PKGROOT/DEBIAN/postinst" "$PKGROOT/DEBIAN/postrm"

# 5) pacchetto
OUT="$DIST/penguincad_${VERSION}_amd64.deb"
dpkg-deb --build --root-owner-group -Zxz "$PKGROOT" "$OUT"

echo "== controllo pacchetto:"
dpkg-deb -I "$OUT"
ls -la "$OUT"
