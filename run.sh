#!/bin/bash
# -------------------------------------------------------------------
# Universal Competitor Intelligence Platform - Launcher
# Multi-Industry Competitive Radar for Any Sector
# -------------------------------------------------------------------
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# Launch in native window mode (completely independent of Safari or Chrome)
exec "$DIR/run_native_app.sh"
