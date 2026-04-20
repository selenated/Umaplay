"""Wine detection and compatibility helpers for running Umaplay under Wine/Linux."""

import os
import sys
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def is_running_under_wine() -> bool:
    """
    Detect if the current Python process is running under Wine.
    
    Returns:
        True if running under Wine, False otherwise.
    """
    # Check for Wine-specific environment variables
    if os.environ.get("WINE") or os.environ.get("WINEPREFIX"):
        return True
    
    # Check for Wine registry keys (Windows API available via pywin32-ctypes)
    try:
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Wine")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            pass
    except ImportError:
        pass
    
    # Check if running on Linux but Windows APIs are available (Wine scenario)
    if sys.platform.startswith("linux"):
        try:
            import win32api
            # If we can import win32api on Linux, we're likely under Wine
            return True
        except ImportError:
            pass
    
    return False


def get_wine_window_list():
    """
    Get list of windows under Wine environment.
    Wine may have issues with EnumWindows, so we provide a fallback.
    
    Returns:
        List of window handles or empty list if enumeration fails.
    """
    try:
        import win32gui
        windows = []
        
        def enum_callback(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                results.append(hwnd)
        
        win32gui.EnumWindows(enum_callback, windows)
        return windows
    except Exception as e:
        logger.warning(f"Wine window enumeration failed: {e}")
        return []


def find_window_wine_compatible(window_title: str) -> Optional[int]:
    """
    Find window by title with Wine compatibility.
    
    Args:
        window_title: The window title to search for.
        
    Returns:
        Window handle (HWND) or None if not found.
    """
    try:
        import win32gui
        
        # Try direct FindWindow first
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            return hwnd
        
        # Fallback: enumerate all windows
        windows = get_wine_window_list()
        for hwnd in windows:
            try:
                title = win32gui.GetWindowText(hwnd)
                if title.strip() == window_title:
                    return hwnd
            except Exception:
                continue
                
    except Exception as e:
        logger.error(f"Wine-compatible window search failed: {e}")
    
    return None


def patch_pygetwindow_for_linux():
    """
    Patch pygetwindow to work on Linux using native X11 tools.
    This prevents the NotImplementedError on Linux systems.
    """
    import sys as sys_module
    
    if not sys_module.platform.startswith("linux"):
        return
    
    try:
        import types
        import subprocess
        
        # Create a mock pygetwindow module with Linux functionality
        mock_gw = types.ModuleType('pygetwindow')
        
        class LinuxWindow:
            """Mock Window class for Linux."""
            def __init__(self, wid, title):
                self._wid = wid
                self.title = title
                self._hWnd = wid  # For compatibility
                self.isMinimized = False  # Assume not minimized
                self._geometry = None  # Cache geometry
                
            def get_geometry(self):
                """Get window geometry using xdotool."""
                if self._geometry:
                    return self._geometry
                try:
                    result = subprocess.run(['xdotool', 'getwindowgeometry', str(self._wid)],
                                          capture_output=True, text=True, timeout=1)
                    if result.returncode == 0:
                        # Parse output like: "Position: 100,200 (screen: 0)"
                        #                    "Geometry: 1920x1080"
                        lines = result.stdout.strip().split('\n')
                        pos_line = [l for l in lines if 'Position:' in l]
                        geo_line = [l for l in lines if 'Geometry:' in l]
                        
                        if pos_line and geo_line:
                            # Extract position
                            pos_str = pos_line[0].split('Position:')[1].split('(')[0].strip()
                            x, y = map(int, pos_str.split(','))
                            
                            # Extract size
                            geo_str = geo_line[0].split('Geometry:')[1].strip()
                            w, h = map(int, geo_str.split('x'))
                            
                            self._geometry = (x, y, w, h)
                            logger.debug(f"Window geometry: {self._geometry}")
                            return self._geometry
                except Exception as e:
                    logger.debug(f"Failed to get window geometry: {e}")
                
                # Fallback to dummy values
                return (0, 0, 1920, 1080)
                
            def minimize(self):
                """Minimize window using xdotool."""
                try:
                    subprocess.run(['xdotool', 'windowminimize', str(self._wid)], timeout=1)
                except:
                    pass
                    
            def restore(self):
                """Restore window using wmctrl."""
                try:
                    subprocess.run(['wmctrl', '-i', '-a', str(self._wid)], timeout=1)
                except:
                    pass
                    
            def activate(self):
                """Activate/focus window using xdotool."""
                try:
                    subprocess.run(['xdotool', 'windowactivate', str(self._wid)], timeout=1)
                    logger.debug(f"Activated window {self._wid}")
                except Exception as e:
                    logger.debug(f"Failed to activate window: {e}")
                
            def __repr__(self):
                return f"LinuxWindow(title='{self.title}')"
        
        def getAllWindows():
            """Get all windows using xdotool."""
            try:
                result = subprocess.run(['xdotool', 'search', '--name', '.'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    windows = []
                    for wid in result.stdout.strip().split('\n'):
                        if wid:
                            title_result = subprocess.run(['xdotool', 'getwindowname', wid],
                                                        capture_output=True, text=True, timeout=1)
                            if title_result.returncode == 0:
                                windows.append(LinuxWindow(wid, title_result.stdout.strip()))
                    logger.debug(f"Found {len(windows)} windows on Linux")
                    return windows
            except Exception as e:
                logger.debug(f"xdotool not available: {e}")
            return []
        
        def getWindowsWithTitle(title):
            """Get windows matching title."""
            all_windows = getAllWindows()
            matching = [w for w in all_windows if w.title.strip() == title.strip()]
            logger.debug(f"Found {len(matching)} windows matching '{title}'")
            return matching
        
        mock_gw.getAllWindows = getAllWindows
        mock_gw.getWindowsWithTitle = getWindowsWithTitle
        
        # Inject the mock module
        sys_module.modules['pygetwindow'] = mock_gw
        logger.info("Patched pygetwindow for Linux with xdotool support")
        
    except Exception as e:
        logger.warning(f"Failed to patch pygetwindow for Linux: {e}")


def patch_win32_for_linux():
    """
    Create mock win32 modules for Linux.
    This allows the code to import but not actually use Windows APIs.
    """
    import sys as sys_module
    import subprocess
    
    if not sys_module.platform.startswith("linux"):
        return
    
    try:
        import types
        import ctypes
        
        # Mock ctypes.windll if it doesn't exist
        if not hasattr(ctypes, 'windll'):
            mock_windll = types.SimpleNamespace()
            mock_user32 = types.SimpleNamespace()
            mock_windll.user32 = mock_user32
            ctypes.windll = mock_windll
            logger.debug("Mocked ctypes.windll for Linux")
        
        # Create mock win32 modules
        win32con = types.ModuleType('win32con')
        win32gui = types.ModuleType('win32gui')
        win32api = types.ModuleType('win32api')
        win32process = types.ModuleType('win32process')
        
        # Add common constants
        win32con.SW_RESTORE = 9
        win32con.SW_MINIMIZE = 6
        
        # Add mock functions
        def mock_function(*args, **kwargs):
            logger.debug(f"Mock win32 function called (Linux)")
            return None
        
        def mock_is_window(hwnd):
            """Mock IsWindow - always return True."""
            return True
            
        def mock_is_window_visible(hwnd):
            """Mock IsWindowVisible - always return True."""
            return True
            
        def mock_get_client_rect(hwnd):
            """Mock GetClientRect - try to get real geometry from xdotool."""
            try:
                result = subprocess.run(['xdotool', 'getwindowgeometry', str(hwnd)],
                                      capture_output=True, text=True, timeout=1)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    geo_line = [l for l in lines if 'Geometry:' in l]
                    if geo_line:
                        geo_str = geo_line[0].split('Geometry:')[1].strip()
                        w, h = map(int, geo_str.split('x'))
                        return (0, 0, w, h)
            except:
                pass
            return (0, 0, 1920, 1080)  # Fallback
            
        def mock_client_to_screen(hwnd, point):
            """Mock ClientToScreen - add window position to point."""
            try:
                result = subprocess.run(['xdotool', 'getwindowgeometry', str(hwnd)],
                                      capture_output=True, text=True, timeout=1)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    pos_line = [l for l in lines if 'Position:' in l]
                    if pos_line:
                        pos_str = pos_line[0].split('Position:')[1].split('(')[0].strip()
                        x, y = map(int, pos_str.split(','))
                        return (point[0] + x, point[1] + y)
            except:
                pass
            return point  # Fallback
        
        win32gui.FindWindow = mock_function
        win32gui.SetForegroundWindow = mock_function
        win32gui.ShowWindow = mock_function
        win32gui.GetWindowText = mock_function
        win32gui.IsWindowVisible = mock_is_window_visible
        win32gui.IsWindow = mock_is_window
        win32gui.GetClientRect = mock_get_client_rect
        win32gui.ClientToScreen = mock_client_to_screen
        win32gui.EnumWindows = mock_function
        win32gui.GetWindowRect = mock_function
        
        # Inject mock modules
        sys_module.modules['win32con'] = win32con
        sys_module.modules['win32gui'] = win32gui
        sys_module.modules['win32api'] = win32api
        sys_module.modules['win32process'] = win32process
        
        logger.info("Created mock win32 modules for Linux compatibility")
        
    except Exception as e:
        logger.warning(f"Failed to create mock win32 modules: {e}")


def patch_imagegrab_for_linux():
    """
    Patch PIL.ImageGrab to use mss on Linux.
    mss is fast, silent, and works great with multi-monitor setups.
    """
    import sys as sys_module
    
    if not sys_module.platform.startswith("linux"):
        return
    
    try:
        from PIL import ImageGrab, Image
        import mss
        
        # Store original (will fail on Linux anyway)
        _original_grab = ImageGrab.grab
        
        def linux_grab(bbox=None, include_layered_windows=False, all_screens=False, xdisplay=None):
            """Linux-compatible screenshot using mss (fast and silent)."""
            
            try:
                with mss.mss() as sct:
                    if bbox:
                        # bbox is (left, top, right, bottom)
                        left, top, right, bottom = bbox
                        width = right - left
                        height = bottom - top
                        
                        # mss monitor format
                        monitor = {
                            "left": left,
                            "top": top,
                            "width": width,
                            "height": height
                        }
                        
                        # Capture the region
                        screenshot = sct.grab(monitor)
                        
                        # Convert to PIL Image
                        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                        logger.debug(f"Captured region: {img.size}")
                        return img
                    else:
                        # Full screen - capture primary monitor
                        monitor = sct.monitors[1]  # Primary monitor
                        screenshot = sct.grab(monitor)
                        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                        logger.debug(f"Captured full screen: {img.size}")
                        return img
                        
            except Exception as e:
                logger.error(f"Screenshot failed: {e}")
                # Return a blank image as fallback
                return Image.new('RGB', (100, 100), color='black')
        
        # Replace ImageGrab.grab
        ImageGrab.grab = linux_grab
        logger.info("Patched PIL.ImageGrab for Linux using mss (fast & silent)")
        
    except Exception as e:
        logger.warning(f"Failed to patch ImageGrab for Linux: {e}")


# Auto-detect and apply patches on import
_is_wine = is_running_under_wine()
if _is_wine:
    logger.info("Wine environment detected - applying compatibility patches")
elif sys.platform.startswith("linux"):
    logger.info("Linux detected - patching for compatibility")
    patch_win32_for_linux()
    patch_pygetwindow_for_linux()
    patch_imagegrab_for_linux()
else:
    logger.debug("Running on native Windows or non-Wine environment")
