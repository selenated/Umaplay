# core/controllers/steam.py
import time
from typing import Any, Optional, Tuple, Union

# Import wine_helper FIRST to patch pygetwindow before it's imported
try:
    from core.utils import wine_helper
except ImportError:
    pass

from core.controllers.base import pyautogui
from core.controllers.window_utils import (
    get_all_windows,
    get_windows_with_title,
    find_window_by_process_name
)

# Optional pywin32 on Windows; preferred when available (Wine uses pywin32-ctypes)
try:
    import win32con  # type: ignore
    import win32gui  # type: ignore
    HAS_WIN32 = True
except Exception:
    win32con = None  # type: ignore
    win32gui = None  # type: ignore
    HAS_WIN32 = False

from core.controllers.base import IController, RegionXYWH
from core.types import XYXY


class SteamController(IController):
    """
    - focus(): restores & foregrounds the target window.
    - screenshot(): by default captures the window's *client area* only (much faster than full screen).
      Keeps track of the last capture origin so you can translate local coords -> screen coords.
    """

    def __init__(
        self, window_title: str = "Umamusume", capture_client_only: bool = True
    ):
        super().__init__(
            window_title=window_title, capture_client_only=capture_client_only
        )

    # --- window discovery ---
    def _find_window(self):
        logger = __import__('logging').getLogger(__name__)
        # First try exact title match
        try:
            win_list = get_windows_with_title(self.window_title)
            if win_list:
                # Prefer exact match
                exact = [w for w in win_list if getattr(w, "title", "").strip() == self.window_title]
                if exact:
                    return exact[0]
                return win_list[0]
        except Exception as e:
            logger.debug(f"[Steam] Title-based window search failed: {e}")
        
        # Fallback: enumerate all windows
        wins = get_all_windows()
        exact = [w for w in wins if getattr(w, "title", "").strip() == self.window_title]
        if exact:
            return exact[0]
        
        # Try process-based detection for Steam games
        # Steam games on Linux often run under proton/wine processes with game-specific names
        for process_hint in ["UmamusumePretty", "Umamusume", self.window_title, "steam", "proton", "wine"]:
            try:
                w = find_window_by_process_name(process_hint)
                if w:
                    title = (getattr(w, "title", "") or "").strip().lower()
                    wm_class = (getattr(w, "wm_class", "") or "").strip().lower()
                    target = self.window_title.lower().strip()
                    # Avoid accepting empty titles ("", None), which can match everything.
                    if title and (target in title or title in target):
                        logger.debug(f"[Steam] Found by process name '{process_hint}': title={getattr(w, 'title', None)}")
                        return w
                    if wm_class and (target in wm_class or wm_class in target):
                        logger.debug(f"[Steam] Found by process name '{process_hint}': title={getattr(w, 'title', None)}")
                        return w
            except Exception as e:
                logger.debug(f"[Steam] Process-based detection for '{process_hint}' failed: {e}")
        
        return None

    def _get_hwnd(self) -> Optional[int]:
        w = self._find_window()
        return int(w._hWnd) if w else None  # pygetwindow stores the HWND on _hWnd

    # --- focusing / restore ---
    def focus(self) -> bool:
        try:
            w = self._find_window()
            if not w:
                return False

            # Restore if minimized
            if w.isMinimized:
                if HAS_WIN32:
                    win32gui.ShowWindow(int(w._hWnd), win32con.SW_RESTORE)
                    time.sleep(0.15)
                else:
                    try:
                        w.restore()
                        time.sleep(0.15)
                    except Exception:
                        # Ignore errors if restore fails; fallback restore is best-effort only.
                        pass

            # Bring to foreground
            try:
                if HAS_WIN32:
                    win32gui.SetForegroundWindow(int(w._hWnd))
                else:
                    w.activate()
            except Exception:
                # Fallback via minimize/restore trick
                w.minimize()
                time.sleep(0.1)
                w.restore()
                time.sleep(0.2)

            # Activate via pygetwindow too
            try:
                w.activate()
            except Exception:
                pass

            time.sleep(0.1)
            return True
        except Exception:
            return False

    # --- geometry helpers ---

    def _client_bbox_screen_xywh(self) -> Optional[RegionXYWH]:
        """
        Returns (left, top, width, height) of the *client area* in SCREEN coordinates.
        """
        hwnd = self._get_hwnd()
        if not hwnd:
            return None
        
        if HAS_WIN32:
            try:
                if not win32gui.IsWindow(hwnd) or not win32gui.IsWindowVisible(hwnd):
                    return None
            except Exception:
                return None

            # Client rect is (0,0)-(w,h) in client coords
            try:
                left_top = win32gui.ClientToScreen(hwnd, (0, 0))
                right_bottom = win32gui.ClientToScreen(
                    hwnd, win32gui.GetClientRect(hwnd)[2:]
                )
                left, top = left_top
                right, bottom = right_bottom
                width, height = max(0, right - left), max(0, bottom - top)
                if width == 0 or height == 0:
                    return None
                return (left, top, width, height)
            except Exception:
                return None
        else:
            # Linux: use window geometry directly
            try:
                w = self._find_window()
                if not w:
                    return None
                left, top = int(w.left), int(w.top)
                width, height = int(w.width), int(w.height)
                if width == 0 or height == 0:
                    return None
                return (left, top, width, height)
            except Exception:
                return None

    def scroll(
        self,
        delta_or_xyxy: Union[int, XYXY],
        *,
        steps: int = 1,
        duration_range: Optional[Tuple[float, float]] = None,
        end_hold_range: Optional[Tuple[float, float]] = None,
        **kwargs: Any,
    ) -> bool:
        if isinstance(delta_or_xyxy, (tuple, list)) and len(delta_or_xyxy) == 4:
            _, y1, _, y2 = delta_or_xyxy
            delta = int(y2 - y1)
        else:
            delta = int(delta_or_xyxy)

        remaining = delta
        total_steps = max(1, int(steps))
        for i in range(total_steps):
            divisor = total_steps - i
            chunk = remaining // divisor if divisor else remaining
            if chunk == 0 and remaining != 0:
                chunk = 1 if remaining > 0 else -1
            pyautogui.scroll(chunk)
            remaining -= chunk
            if duration_range:
                time.sleep(max(0.0, float(duration_range[0])))

        return True

    # convenience: left half bbox in screen coords
    def left_half_bbox(self) -> Optional[RegionXYWH]:
        xywh = self._client_bbox_screen_xywh()
        if not xywh:
            return None
        L, T, W, H = xywh
        return (L, T, W // 2, H)

    # convenience: capture left half (also updates last_origin)
    def screenshot_left_half(self):
        xywh = self.left_half_bbox()
        if not xywh:
            # fall back to full client area which also sets last_origin
            return self.screenshot()
        return self.screenshot(region=xywh)
