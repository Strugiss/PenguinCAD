%global __os_install_post %{nil}
%global _build_id_links none

Name:           penguincad
Version:        1.3.1
Release:        1
Summary:        CAD 3D per stampa 3D (port Linux di TriviumCAD)
License:        MIT
Group:          Applications/Graphics
BuildArch:      x86_64
# Bundle PyInstaller autocontenuto: niente dipendenze automatiche dalle soname
# interne (es. libgeos-<hash>.so non esistono come pacchetti di sistema).
AutoReqProv:    no
Provides:       application(penguincad.desktop)
Provides:       mimehandler(application/x-n47)
Requires:       glibc, libgcc, libstdc++, zlib, mesa-libGL, libX11, libX11-xcb, libxcb, libxkbcommon, libxkbcommon-x11, dbus-libs, fontconfig, freetype, glib2

%description
PenguinCAD e' un ambiente integrato per la modellazione 3D, la
progettazione meccanica, la generazione di percorsi utensile (CAM) e
l'invio diretto delle stampe alle stampanti 3D.

Sviluppato in Python con PyQt5, OpenGL e trimesh.

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/opt/penguincad
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/icons/hicolor/256x256/apps
cp -a %{_sourcedir}/dist/PenguinCAD/. %{buildroot}/opt/penguincad/
ln -s /opt/penguincad/PenguinCAD %{buildroot}/usr/bin/penguincad
cp %{_sourcedir}/packaging/penguincad.desktop %{buildroot}/usr/share/applications/penguincad.desktop
cp %{_sourcedir}/packaging/penguincad-256.png %{buildroot}/usr/share/icons/hicolor/256x256/apps/penguincad.png

%files
/opt/penguincad
/usr/bin/penguincad
/usr/share/applications/penguincad.desktop
/usr/share/icons/hicolor/256x256/apps/penguincad.png

%changelog
* Sat Nov 22 2026 N47Lab Team (Alessandro Tulli) - 1.3.1-1
- Pacchetto RPM per PenguinCAD 1.3.1 (port Linux di TriviumCAD).
