#!/usr/bin/env bash
# build_rpm.sh — costruisce penguincad-1.3.1-1.x86_64.rpm
#
# Usa rpmbuild di sistema se presente; altrimenti la toolchain portatile in
# ~/toolchain/rpmroot (estratta dai .deb di rpm con dpkg-deb -x, senza root).
# Lo spec e' packaging/penguincad-rpm.spec (%files da /opt/penguincad +
# desktop + icona; niente strip/debuginfo sui binari gia' distribuiti).
set -euo pipefail

VERSION="1.3.1"
RELEASE="1"
PROJ="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$PROJ/dist"
WORK="$PROJ/build/rpm"
TOOLCHAIN="$HOME/toolchain/rpmroot"
SPEC="$PROJ/packaging/penguincad-rpm.spec"

if [ ! -x "$DIST/PenguinCAD/PenguinCAD" ]; then
  echo "ERRORE: bundle PyInstaller assente in $DIST/PenguinCAD/" >&2
  exit 1
fi

if command -v rpmbuild >/dev/null 2>&1; then
  RPMBUILD="$(command -v rpmbuild)"
  echo "[toolchain] rpmbuild di sistema: $RPMBUILD"
elif [ -x "$TOOLCHAIN/usr/bin/rpmbuild" ]; then
  RPMBUILD="$TOOLCHAIN/usr/bin/rpmbuild"
  export RPM_CONFIGDIR="$TOOLCHAIN/usr/lib/rpm"
  export LD_LIBRARY_PATH="$TOOLCHAIN/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
  echo "[toolchain] rpmbuild portatile: $RPMBUILD"
else
  echo "ERRORE: rpmbuild assente. Installare 'rpm' (sudo apt install rpm) oppure" >&2
  echo "        predisporre $TOOLCHAIN (vedi README)." >&2
  exit 1
fi

rm -rf "$WORK"
mkdir -p "$WORK/BUILD" "$WORK/BUILDROOT" "$WORK/RPMS" "$WORK/SOURCES" "$WORK/SPECS" "$WORK/SRPMS"

"$RPMBUILD" -bb \
  --define "_topdir $WORK" \
  --define "_sourcedir $PROJ" \
  "$SPEC"

OUT="$WORK/RPMS/x86_64/penguincad-${VERSION}-${RELEASE}.x86_64.rpm"
cp "$OUT" "$DIST/"
ls -la "$DIST/penguincad-${VERSION}-${RELEASE}.x86_64.rpm"
