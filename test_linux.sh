#!/bin/bash
# Quick Linux test setup for Umaplay Wine support

set -e

echo "=========================================="
echo "Umaplay Wine Support - Linux Test Setup"
echo "=========================================="

# Check if we're on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "⚠️  This script is for Linux systems"
    echo "Current OS: $OSTYPE"
fi

echo ""
echo "[1/4] Installing Python dependencies..."
pip install --user pywin32-ctypes pynput 2>&1 | grep -E "Successfully|already satisfied|Requirement" || true

echo ""
echo "[2/4] Testing Wine helper..."
python3 << 'EOF'
from core.utils.wine_helper import is_running_under_wine
print(f"Wine detected: {is_running_under_wine()}")
print("✓ Wine helper works")
EOF

echo ""
echo "[3/4] Testing hotkey manager..."
python3 << 'EOF'
from core.utils.hotkey_manager import get_hotkey_manager
mgr = get_hotkey_manager()
print(f"Hotkey manager created")
print(f"Using pynput: {mgr.use_pynput}")
print("✓ Hotkey manager works")
EOF

echo ""
echo "[4/4] Running full verification..."
python3 test_wine_support.py

echo ""
echo "=========================================="
echo "✅ Linux test complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Install Wine if not already installed"
echo "  2. Follow docs/README.wine.md for full setup"
echo "  3. Test with actual Umamusume under Wine"
