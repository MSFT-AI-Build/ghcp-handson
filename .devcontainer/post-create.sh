#!/usr/bin/env bash
set -euo pipefail

# -------------------------------------------
# 1. GitHub Copilot CLI (standalone binary via npm)
# -------------------------------------------
echo ""
echo "[1/1] Installing GitHub Copilot CLI..."
npm install -g @github/copilot
echo "  -> Done."
