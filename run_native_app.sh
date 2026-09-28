#!/bin/bash
# -------------------------------------------------------------------
# Native macOS App Launcher for Universal Competitor Intelligence Radar
# Starts Streamlit in headless background mode on port 8503 and opens dedicated Cocoa window.
# Completely independent of Safari, Chrome, or any external web browser.
# -------------------------------------------------------------------

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# 1. Kill any existing instance on port 8503
lsof -ti:8503 | xargs kill -9 2>/dev/null

# 2. Check virtual environment
if [ -d "$DIR/../competitor_intelligence_app/venv" ]; then
    VENV_PY="$DIR/../competitor_intelligence_app/venv/bin/python"
    VENV_STREAMLIT="$DIR/../competitor_intelligence_app/venv/bin/streamlit"
elif [ -d "$DIR/venv" ]; then
    VENV_PY="$DIR/venv/bin/python"
    VENV_STREAMLIT="$DIR/venv/bin/streamlit"
else
    echo "[*] Initializing dedicated virtual environment..."
    python3 -m venv "$DIR/venv"
    "$DIR/venv/bin/pip" install --quiet -r "$DIR/requirements.txt"
    VENV_PY="$DIR/venv/bin/python"
    VENV_STREAMLIT="$DIR/venv/bin/streamlit"
fi

# Ensure native window binary exists; compile if missing
if [ ! -f "$DIR/Universal_Radar_Window" ]; then
    /usr/bin/swiftc -O -o "$DIR/Universal_Radar_Window" "$DIR/window.swift"
fi

# 3. Launch Streamlit headlessly (no browser redirect to Safari or Chrome)
"$VENV_STREAMLIT" run "$DIR/app.py" --server.headless true --server.address localhost --server.port 8503 > /dev/null 2>&1 &
STREAMLIT_PID=$!

# 4. Wait until the local server responds (up to 15 seconds)
for i in {1..30}; do
    if curl -s http://localhost:8503 >/dev/null 2>&1; then
        break
    fi
    sleep 0.5
done

# 5. Open native macOS Cocoa Window
"$DIR/Universal_Radar_Window"

# 6. When the window is closed, cleanly terminate the background server
kill -9 $STREAMLIT_PID 2>/dev/null
