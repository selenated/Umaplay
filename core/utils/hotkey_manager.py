"""Cross-platform hotkey manager with Wine/Linux compatibility."""

import logging
import sys
from typing import Callable, Set, Optional

logger = logging.getLogger(__name__)

# Try to detect the best keyboard library
_use_pynput = False
_keyboard_available = False
_pynput_keyboard = None

try:
    import keyboard
    _keyboard_available = True
    logger.debug("keyboard library available")
except ImportError:
    logger.debug("keyboard library not available")

try:
    from pynput import keyboard as pynput_keyboard
    _pynput_keyboard = pynput_keyboard
    _use_pynput = True
    logger.debug("pynput library available")
except ImportError:
    logger.debug("pynput library not available")

# Auto-detect Wine environment
try:
    from core.utils.wine_helper import is_running_under_wine
    if is_running_under_wine() and _use_pynput:
        logger.info("Wine detected - using pynput for hotkeys")
        _keyboard_available = False  # Force pynput under Wine
except ImportError:
    pass


class HotkeyManager:
    """
    Cross-platform hotkey manager that abstracts keyboard library usage.
    Automatically selects between 'keyboard' and 'pynput' based on platform.
    """
    
    def __init__(self):
        self.use_pynput = not _keyboard_available and _use_pynput
        self.registered_keys: Set[str] = set()
        self._pynput_listener = None
        self._pynput_callbacks = {}
        
        if self.use_pynput:
            logger.info("Using pynput for hotkey management")
        elif _keyboard_available:
            logger.info("Using keyboard library for hotkey management")
        else:
            logger.warning("No keyboard library available!")
    
    def add_hotkey(self, key: str, callback: Callable, suppress: bool = False, 
                   trigger_on_release: bool = True) -> bool:
        """
        Register a hotkey with a callback.
        
        Args:
            key: Key combination (e.g., 'F2', 'ctrl+a')
            callback: Function to call when key is pressed
            suppress: Whether to suppress the key event (not supported in pynput)
            trigger_on_release: Whether to trigger on key release
            
        Returns:
            True if registration succeeded, False otherwise
        """
        try:
            if self.use_pynput:
                return self._add_hotkey_pynput(key, callback, trigger_on_release)
            elif _keyboard_available:
                keyboard.add_hotkey(key, callback, suppress=suppress, 
                                   trigger_on_release=trigger_on_release)
                self.registered_keys.add(key)
                return True
            else:
                logger.error(f"Cannot register hotkey '{key}' - no keyboard library available")
                return False
        except Exception as e:
            logger.warning(f"Failed to register hotkey '{key}': {e}")
            return False
    
    def _add_hotkey_pynput(self, key: str, callback: Callable, 
                          trigger_on_release: bool) -> bool:
        """Register hotkey using pynput."""
        # Convert key string to pynput Key object
        key_obj = self._parse_key(key)
        if key_obj is None:
            return False
        
        self._pynput_callbacks[key_obj] = (callback, trigger_on_release)
        self.registered_keys.add(key)
        
        # Start listener if not already running
        if self._pynput_listener is None:
            self._start_pynput_listener()
        
        return True
    
    def _parse_key(self, key_str: str):
        """Convert key string to pynput Key object."""
        if _pynput_keyboard is None:
            return None
            
        key_str = key_str.lower()
        
        # Function keys
        if key_str.startswith('f') and key_str[1:].isdigit():
            fn_num = int(key_str[1:])
            return getattr(_pynput_keyboard.Key, f'f{fn_num}', None)
        
        # Special keys
        key_map = {
            'esc': _pynput_keyboard.Key.esc,
            'enter': _pynput_keyboard.Key.enter,
            'space': _pynput_keyboard.Key.space,
            'tab': _pynput_keyboard.Key.tab,
        }
        
        return key_map.get(key_str, key_str)
    
    def _start_pynput_listener(self):
        """Start the pynput keyboard listener."""
        if _pynput_keyboard is None:
            logger.error("Cannot start pynput listener - pynput not available")
            return
            
        def on_press(key):
            for registered_key, (callback, trigger_on_release) in self._pynput_callbacks.items():
                if key == registered_key and not trigger_on_release:
                    try:
                        callback()
                    except Exception as e:
                        logger.error(f"Hotkey callback error: {e}")
        
        def on_release(key):
            for registered_key, (callback, trigger_on_release) in self._pynput_callbacks.items():
                if key == registered_key and trigger_on_release:
                    try:
                        callback()
                    except Exception as e:
                        logger.error(f"Hotkey callback error: {e}")
        
        self._pynput_listener = _pynput_keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        self._pynput_listener.start()
        logger.debug("Started pynput keyboard listener")
    
    def is_pressed(self, key: str) -> bool:
        """
        Check if a key is currently pressed.
        
        Args:
            key: Key to check
            
        Returns:
            True if key is pressed, False otherwise
        """
        try:
            if self.use_pynput:
                # pynput doesn't have a direct is_pressed equivalent
                # This is a limitation - polling doesn't work well with pynput
                return False
            elif _keyboard_available:
                return keyboard.is_pressed(key)
            else:
                return False
        except Exception as e:
            logger.debug(f"Error checking key state for '{key}': {e}")
            return False
    
    def stop(self):
        """Stop the hotkey manager and clean up resources."""
        if self._pynput_listener:
            self._pynput_listener.stop()
            self._pynput_listener = None
        self.registered_keys.clear()
        self._pynput_callbacks.clear()


# Global instance
_manager: Optional[HotkeyManager] = None


def get_hotkey_manager() -> HotkeyManager:
    """Get the global hotkey manager instance."""
    global _manager
    if _manager is None:
        _manager = HotkeyManager()
    return _manager
