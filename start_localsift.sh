#!/bin/bash
cd "$(dirname "$0")"
# ============================================================
#  LocalSift Launcher — local RAG file analysis
#  Simply Linux / ALT / Ubuntu / Debian — everything stays local
# ============================================================
APP_NAME="LocalSift"
SERVER="localsift_server.py"
PORT=8200
SERVER_PID=""

cleanup() {
    echo "Stopping $APP_NAME..."
    [ -n "$SERVER_PID" ] && kill "$SERVER_PID" 2>/dev/null
    rm -f localsift.pid
    echo "All services stopped. Logs: localsift.log"
    exit 0
}
# EXIT also covers closing the terminal window
trap cleanup EXIT INT TERM HUP

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 not found. Install: sudo apt-get install python3"
    read -r -p "Press ENTER to exit."; exit 1
fi

# stop leftovers from a previous crashed run
[ -f localsift.pid ] && { kill "$(cat localsift.pid)" 2>/dev/null; rm -f localsift.pid; }

port_open() {
    python3 -c 'import socket,sys; s=socket.socket(); sys.exit(0 if s.connect_ex(("127.0.0.1",int(sys.argv[1])))==0 else 1)' "$1" 2>/dev/null
}

if port_open "$PORT"; then
    echo "Port $PORT already in use: reusing the running LocalSift server."
else
    echo "Starting $APP_NAME server (port $PORT)..."
    python3 "$SERVER" > localsift.log 2>&1 &
    SERVER_PID=$!
    echo "$SERVER_PID" > localsift.pid
    echo -n "Waiting for the server "
    for i in $(seq 1 30); do port_open "$PORT" && break; echo -n "."; sleep 1; done
    if ! port_open "$PORT"; then
        echo " ERROR: server did not start. Check localsift.log"
        exit 1
    fi
    echo " ready!"
fi

echo "Opening browser... (if it doesn't open: http://127.0.0.1:$PORT/index.html)"
xdg-open "http://127.0.0.1:$PORT/index.html" 2>/dev/null

echo
echo "$APP_NAME is running. Press ENTER (or Ctrl+C) to stop everything."
read -r
