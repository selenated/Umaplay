"""Cross-platform keyboard handling.

On Windows, the 'keyboard' library works without root.
On Linux, 'keyboard' requires root, so we use 'pynput' instead.
"""
from __future__ import annotations

import sys
import threading
from typing import Set, Optional
import logging

logger = logging.getLogger(__name__)

# Detect platform and choose appropriate library
if sys.platform == "win32":
    try:
        import keyboard as kb  # type: ignore
        HAS_KEYBOARD = True
        HAS_PYNPUT = False
    except ImportError:
        HAS_KEYBOARD = False
        HAS_PYNPUT = False
else:
    # Linux/macOS: use pynput (doesn't require root)
    HAS_KEYBOARD = False
    try:
        from pynput import keyboard as pynput_kb  # type: ignore
        HAS_PYNPUT = True
    except ImportError:
        HAS_PYNPUT = False


class KeyboardHandler:
    """Cross-platform keyboard handler that works without root on Linux."""
    
    def __init__(self):
        self._pressed_keys: Set[str] = set()
        self._listener: Optional[object] = None
        self._lock = threading.Lock()
        
        if HAS_PYNPUT:
            # Use pynput for Linux/macOS
            self._listener = pynput_kb.Listener(
                on_press=self._on_press_pynput,
                on_release=self._on_release_pynput
            )
            self._listener.start()
            logger.debug("[KeyboardHandler] Using pynput for keyboard handling")
        elif HAS_KEYBOARD:
            # Use keyboard for Windows
            logger.debug("[KeyboardHandler] Using keyboard library for keyboard handling")
        else:
            logger.warning("[KeyboardHandler] No keyboard library available")
    
    def _normalize_key(self, key) -> str:
        """Normalize key representation across libraries."""
        if HAS_PYNPUT and hasattr(key, 'name'):
            # pynput.keyboard.Key enum (e.g., Key.f9)
            name = key.name
            # Map pynput names to keyboard library format
            if name.startswith('f') and name[1:].isdigit():
                return name.lower()  # f9 -> f9
            return name.lower()
        elif HAS_PYNPUT and hasattr(key, 'char'):
            # Regular character key
            return str(key.char).lower() if key.char else ''
        else:
            # keyboard library or string
            return str(key).lower()
    
    def _on_press_pynput(self, key):
        """Handle key press in pynput."""
        try:
            normalized = self._normalize_key(key)
            if normalized:
                with self._lock:
                    self._pressed_keys.add(normalized)
        except Exception as e:
            logger.debug(f"[KeyboardHandler] Error in _on_press_pynput: {e}")
    
    def _on_release_pynput(self, key):
        """Handle key release in pynput."""
        try:
            normalized = self._normalize_key(key)
            if normalized:
                with self._lock:
                    self._pressed_keys.discard(normalized)
        except Exception as e:
            logger.debug(f"[KeyboardHandler] Error in _on_release_pynput: {e}")
    
    def is_pressed(self, key: str) -> bool:
        """Check if a key is currently pressed.
        
        Args:
            key: Key name (e.g., 'F9', 'ctrl', 'a')
        
        Returns:
            True if the key is currently pressed, False otherwise
        """
        if HAS_KEYBOARD:
            try:
                return kb.is_pressed(key)
            except Exception as e:
                logger.debug(f"[KeyboardHandler] keyboard.is_pressed error: {e}")
                return False
        elif HAS_PYNPUT:
            with self._lock:
                # Check both lowercase and uppercase variants
                return (key.lower() in self._pressed_keys or 
                        key.upper() in self._pressed_keys)
        else:
            return False
    
    def cleanup(self):
        """Clean up resources."""
        if HAS_KEYBOARD:
            try:
                kb.unhook_all_hotkeys()
            except Exception as e:
                logger.debug(f"[KeyboardHandler] kb.unhook_all_hotkeys error: {e}")
        elif HAS_PYNPUT and self._listener:
            try:
                self._listener.stop()
            except Exception as e:
                logger.debug(f"[KeyboardHandler] Error stopping listener: {e}")
        with self._lock:
            self._pressed_keys.clear()


# Global singleton instance
_handler: Optional[KeyboardHandler] = None


def get_keyboard_handler() -> KeyboardHandler:
    """Get the global keyboard handler instance."""
    global _handler
    if _handler is None:
        _handler = KeyboardHandler()
    return _handler


def is_pressed(key: str) -> bool:
    """Check if a key is currently pressed (convenience function)."""
    return get_keyboard_handler().is_pressed(key)


def cleanup():
    """Clean up keyboard handler resources."""
    global _handler
    if _handler:
        _handler.cleanup()
        _handler = None
