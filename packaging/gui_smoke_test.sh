#!/usr/bin/env bash
# Smoke test GUI per PenguinCAD: avvia un comando sotto Xvfb, attende,
# verifica che il processo sia vivo e che esista una finestra col nome atteso,
# cattura uno screenshot. Uso:
#   gui_smoke_test.sh <comando> <nome_finestra> <screenshot.png> [attesa_sec]
# Esito su stdout: ALIVE=<SI|NO> WINDOWS=<id...> SHOT=<path>
set -u
CMD="$1"
NAME="$2"
SHOT="$3"
WAIT="${4:-20}"
DISP="${DISPLAY_NUM:-:99}"

Xvfb "$DISP" -screen 0 1280x720x24 >/tmp/xvfb.log 2>&1 &
XVFB_PID=$!
sleep 2

export DISPLAY="$DISP"
eval "$CMD" >/tmp/gui_app.log 2>&1 &
APP_PID=$!

sleep "$WAIT"
ALIVE=NO
if kill -0 "$APP_PID" 2>/dev/null; then ALIVE=SI; fi
WIN=$(DISPLAY="$DISP" xdotool search --name "$NAME" 2>/dev/null | head -3 | tr '\n' ' ')
DISPLAY="$DISP" scrot -o "$SHOT" 2>/tmp/scrot.log || true

kill "$APP_PID" 2>/dev/null || true
sleep 1
kill -9 "$APP_PID" 2>/dev/null || true
kill "$XVFB_PID" 2>/dev/null || true

echo "ALIVE=$ALIVE WINDOWS=$WIN SHOT=$SHOT"
exit 0
