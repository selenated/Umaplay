#!/bin/bash
# Test Umaplay Wine support in a Python virtual environment

set -e

echo "=========================================="
echo "Umaplay Wine Support - Linux Test"
echo "=========================================="

# Create virtual environment if it doesn't exist
if [ ! -d "venv_test" ]; then
    echo ""
    echo "[1/5] Creating Python virtual environment..."
    python3 -m venv venv_test
fi

# Activate virtual environment
echo ""
echo "[2/5] Activating virtual environment..."
source venv_test/bin/activate

# Install minimal dependencies for testing
echo ""
echo "[3/5] Installing test dependencies..."
pip install -q pywin32-ctypes pynput

# Test Wine helper
echo ""
echo "[4/5] Testing Wine support modules..."
python3 << 'EOF'
print("\n→ Testing wine_helper...")
from core.utils.wine_helper import is_running_under_wine
wine = is_running_under_wine()
print(f"  Wine detected: {wine}")
print("  ✓ Wine helper works")

print("\n→ Testing hotkey_manager...")
from core.utils.hotkey_manager import get_hotkey_manager
mgr = get_hotkey_manager()
print(f"  Using pynput: {mgr.use_pynput}")
print("  ✓ Hotkey manager works")
EOF

# Run full verification
echo ""
echo "[5/5] Running full verification test..."
python3 test_wine_support.py

echo ""
echo "=========================================="
echo "✅ All tests passed in virtual environment!"
echo "=========================================="
echo ""
echo "Virtual environment: venv_test/"
echo "To activate: source venv_test/bin/activate"
echo "To deactivate: deactivate"
