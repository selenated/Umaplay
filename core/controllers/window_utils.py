"""Cross-platform window utilities for controllers.

This module wraps `pygetwindow` on platforms where available (Windows/macOS).
On Linux, `pygetwindow` may not be supported; in that case we attempt to use
`xdotool` to find windows and provide a minimal wrapper with the properties used
elsewhere in the code (left/top/width/height/_hWnd/title/minimize/activate/restore).

This avoids importing pygetwindow directly in controllers and causing NotImplementedError
when run on unsupported platforms.
"""
from __future__ import annotations

import logging
import psutil
import shutil
import subprocess
import shlex
from typing import List, Optional


logger = logging.getLogger(__name__)


try:
    import pygetwindow as gw  # type: ignore
    HAS_PYGETWINDOW = True
except Exception:
    HAS_PYGETWINDOW = False

# Optional: pywinctl for process-based window discovery (works on many Linux desktops)
try:
    import pywinctl as pwc  # type: ignore
    HAS_PYWINTCL = True
except Exception:
    pwc = None  # type: ignore
    HAS_PYWINTCL = False


class WindowDummy:
    def __init__(self, winid: int, title: str, left: int, top: int, width: int, height: int, pid: Optional[int] = None):
        self._hWnd = int(winid)
        self.title = title
        self.wm_class = ""
        self.left = int(left)
        self.top = int(top)
        self.width = int(width)
        self.height = int(height)
        self.isMinimized = False
        self.isActive = False
        self.pid = int(pid) if pid is not None else None

    def activate(self):
        try:
            subprocess.check_call(["xdotool", "windowactivate", str(self._hWnd)])
        except Exception:
            pass

    def restore(self):
        # best-effort: activate should un-minimize
        try:
            subprocess.check_call(["xdotool", "windowactivate", str(self._hWnd)])
        except Exception:
            pass

    def minimize(self):
        try:
            subprocess.check_call(["xdotool", "windowminimize", str(self._hWnd)])
        except Exception:
            pass


def _run_cmd(cmd: List[str]) -> Optional[str]:
    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8", errors="ignore")
    except Exception:
        return None


def _parse_geometry_output(out: str) -> Optional[dict]:
    # parse xdotool "getwindowgeometry --shell" output
    fields = {}
    for line in out.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            fields[k.strip()] = v.strip()
    if not fields:
        return None
    return fields


def _get_linux_windows(visible_only: bool = True) -> List[WindowDummy]:
    # Use xdotool to list windows. The 'search --onlyvisible --name ".*"' returns visible windows
    # Prefer xdotool if available
    wins = []
    if shutil.which("xdotool"):
        logger.debug("Using xdotool to enumerate windows")
        if visible_only:
            out = _run_cmd(["xdotool", "search", "--onlyvisible", "--name", ".*"])
        else:
            out = _run_cmd(["xdotool", "search", "--name", ".*"])
        if out:
            for line in out.splitlines():
                winid = line.strip()
                if not winid:
                    continue
                geom_out = _run_cmd(["xdotool", "getwindowgeometry", "--shell", winid])
                if not geom_out:
                    # fall back to xwininfo
                    geom_out = _run_cmd(["xwininfo", "-id", winid]) or ""
                parsed = _parse_geometry_output(geom_out) if geom_out and "=" in geom_out else None
                title = _run_cmd(["xdotool", "getwindowname", winid]) or ""
                # try to get class name via xprop or xdotool
                wclass = _run_cmd(["xdotool", "getwindowclassname", winid]) or ""
                left = int(parsed.get("X", 0)) if parsed else 0
                top = int(parsed.get("Y", 0)) if parsed else 0
                width = int(parsed.get("WIDTH", 0)) if parsed else 0
                height = int(parsed.get("HEIGHT", 0)) if parsed else 0
                # try to get pid via xprop when available
                pid = None
                try:
                    pid_out = _run_cmd(["xprop", "-id", winid, "_NET_WM_PID"]) or ""
                    if pid_out and "_NET_WM_PID" in pid_out and "=" in pid_out:
                        pid = int(pid_out.split("=", 1)[1].strip())
                except Exception:
                    pid = None
                w = WindowDummy(winid, title.strip(), left, top, width, height, pid=pid)
                if wclass:
                    w.wm_class = wclass.strip()
                logger.debug(f"[window_utils] xdotool found: id={winid} title={w.title!r} class={w.wm_class!r}")
                wins.append(w)
            return wins
    # Fallback to wmctrl
    logger.debug("xdotool returned no windows or not present. Trying wmctrl.")
    if shutil.which("wmctrl"):
        # -x includes the WM_CLASS in column 4: class.code
        wm_out = _run_cmd(["wmctrl", "-lx"]) or ""
        for line in wm_out.splitlines():
            parts = line.split(None, 3)
            if len(parts) < 4:
                continue
            hexid = parts[0]
            try:
                winid_dec = str(int(hexid, 16))
            except Exception:
                winid_dec = hexid
            # wmctrl -lx format: 'hexid desktop host class.code title'
            # parts[3] contains 'class.code title' -> we split the first token for class
            title_part = parts[3].strip()
            title = title_part
            # split off class if provided
            wc = ""
            try:
                # wmctrl -lx format: 'hexid desktop host class.code title'
                # We'll try to parse class from the 4th field if it contains '.'
                first_part = title_part.split(None, 1)[0]
                if "." in first_part:
                    wc = first_part.split(".")[0]
            except Exception:
                wc = ""
            # get geometry via xwininfo
            geom_out = _run_cmd(["xwininfo", "-id", hexid]) or ""
            parsed = _parse_geometry_output(geom_out) if geom_out and "=" in geom_out else None
            left = int(parsed.get("X", 0)) if parsed else 0
            top = int(parsed.get("Y", 0)) if parsed else 0
            width = int(parsed.get("WIDTH", 0)) if parsed else 0
            height = int(parsed.get("HEIGHT", 0)) if parsed else 0
            pid = None
            try:
                pid_out = _run_cmd(["xprop", "-id", hexid, "_NET_WM_PID"]) or ""
                if pid_out and "_NET_WM_PID" in pid_out and "=" in pid_out:
                    pid = int(pid_out.split("=", 1)[1].strip())
            except Exception:
                pid = None
            w = WindowDummy(winid_dec, title, left, top, width, height, pid=pid)
            if wc:
                w.wm_class = wc
            logger.debug(f"[window_utils] wmctrl found: id={winid_dec} title={w.title!r} class={w.wm_class!r}")
            wins.append(w)
        if wins:
            return wins

    # Try to enumerate windows using python-xlib as a last resort
    try:
        from Xlib import display as xdisplay

        logger.debug("Using python-xlib for enumeration")
        d = xdisplay.Display()
        root = d.screen().root
        children = root.query_tree().children
        for c in children:
            try:
                winid = str(c.id)
                title = (c.get_wm_name() or "").strip()
                try:
                    wclass = (c.get_wm_class() or [None, None])[0] or ""
                except Exception:
                    wclass = ""
                geom = c.get_geometry()
                # try to extract PID via xprop (best effort)
                pid = None
                try:
                    pid_out = _run_cmd(["xprop", "-id", winid, "_NET_WM_PID"]) or ""
                    if pid_out and "_NET_WM_PID" in pid_out and "=" in pid_out:
                        pid = int(pid_out.split("=", 1)[1].strip())
                except Exception:
                    pid = None
                w = WindowDummy(winid, title, geom.x, geom.y, geom.width, geom.height, pid=pid)
                if wclass:
                    w.wm_class = wclass
                logger.debug(f"[window_utils] xlib found: id={winid} title={w.title!r} class={w.wm_class!r}")
                wins.append(w)
            except Exception:
                continue
        if wins:
            return wins
    except Exception:
        logger.debug("python-xlib not available or enumeration failed")

    # Last resort: use pywinctl which wraps OS-specific APIs to enumerate windows and link to processes
    if HAS_PYWINTCL and pwc is not None:
        try:
            logger.debug("Trying pywinctl fallback for window enumeration")
            for val in pwc.getAllWindows():  # type: ignore[union-attr]
                try:
                    # try to get handle or id
                    nid = None
                    getter = getattr(val, 'getHandle', None)
                    if callable(getter):
                        nid = getter()
                    else:
                        nid = getattr(val, 'handle', None) or getattr(val, 'hwnd', None)
                except Exception:
                    nid = getattr(val, 'handle', None) or getattr(val, 'hwnd', None) or 0
                try:
                    title = getattr(val, 'title', None) or (getattr(val, 'getTitle', None) and val.getTitle()) or ''
                except Exception:
                    title = ''
                try:
                    get_pid = getattr(val, 'getPid', None) or getattr(val, 'getPID', None) or getattr(val, 'pid', None)
                    pid = get_pid() if callable(get_pid) else get_pid
                except Exception:
                    pid = None
                try:
                    box = getattr(val, 'box', None) or (getattr(val, 'getClientRect', None) and val.getClientRect())
                    if box:
                        left = getattr(box, 'x', box[0] if isinstance(box, (list, tuple)) else 0)
                        top = getattr(box, 'y', box[1] if isinstance(box, (list, tuple)) else 0)
                        width = getattr(box, 'width', box[2] if isinstance(box, (list, tuple)) and len(box) > 2 else 0)
                        height = getattr(box, 'height', box[3] if isinstance(box, (list, tuple)) and len(box) > 3 else 0)
                    else:
                        left = top = width = height = 0
                except Exception:
                    left = top = width = height = 0
                w = WindowDummy(nid or 0, title or '', int(left or 0), int(top or 0), int(width or 0), int(height or 0))
                try:
                    # get wm_class if supported
                    get_cls = getattr(val, 'getWmClass', None) or getattr(val, 'getProcessName', None)
                    if callable(get_cls):
                        wc = get_cls()
                    else:
                        wc = None
                except Exception:
                    wc = None
                if wc:
                    w.wm_class = str(wc or '').strip()
                if pid is not None:
                    w.pid = int(pid)
                wins.append(w)
            if wins:
                return wins
        except Exception:
            logger.debug("pywinctl enumeration failed")
    return []


def get_all_windows(visible_only: bool = True):
    """Return a list of Window-like objects compatible with the codebase.

    On Windows/macOS this returns the `pygetwindow` objects; on Linux we return
    `WindowDummy` objects from xdotool.
    """
    if HAS_PYGETWINDOW:
        try:
            return gw.getAllWindows()
        except Exception:
            return _get_linux_windows(visible_only=visible_only)
    else:
        return _get_linux_windows(visible_only=visible_only)


def get_windows_with_title(title: str, visible_only: bool = True):
    """Return windows that match the given title exactly (or substring when exact not found).
    The return objects are compatible windows (either pygetwindow or WindowDummy).
    """
    if HAS_PYGETWINDOW:
        try:
            wins = gw.getWindowsWithTitle(title)
            if wins:
                return wins
        except Exception:
            pass

    # Fallback: use substring matching over the xdotool windows
    all_windows = get_all_windows(visible_only=visible_only)
    exact = [w for w in all_windows if getattr(w, "title", "").strip() == title or getattr(w, "wm_class", "").strip() == title]
    if exact:
        return exact
    # substring case-insensitive
    sub = [w for w in all_windows if title.lower() in getattr(w, "title", "").lower() or title.lower() in getattr(w, "wm_class", "").lower()]
    return sub


def find_window(title: str):
    wins = get_windows_with_title(title)
    if wins:
        return wins[0]
    # fallback: try to match by process name (e.g. scrcpy, steam) if pywinctl available
    try:
        p_win = _get_windows_by_process_name(title)
        if p_win:
            return p_win[0]
    except Exception:
        pass
    return None


def _get_windows_by_process_name(proc_name: str) -> List[WindowDummy]:
    """Return windows whose process name matches (substring) proc_name using pywinctl if available."""
    if not HAS_PYWINTCL:
        # Fallback: attempt to match by PID found via xprop or other enumerators
        out = []
        try:
            wins = get_all_windows(visible_only=False)
        except Exception:
            wins = []
        for w in wins:
            try:
                pid = getattr(w, 'pid', None)
                if not pid:
                    continue
                proc = psutil.Process(int(pid))
                pname = proc.name() or ''
                if proc_name.lower() in pname.lower():
                    out.append(w)
            except Exception:
                continue
        return out
    out = []
    for val in pwc.getAllWindows():  # type: ignore[union-attr]
        try:
            get_pid = getattr(val, 'getPid', None) or getattr(val, 'getPID', None) or getattr(val, 'pid', None)
            pid = get_pid() if callable(get_pid) else get_pid
        except Exception:
            pid = None
        if not pid:
            continue
        try:
            proc = psutil.Process(pid)
            pname = proc.name() or ''
        except Exception:
            pname = ''
        if proc_name.lower() in pname.lower():
            try:
                # Build WindowDummy similar to enumeration above
                nid = None
                getter = getattr(val, 'getHandle', None)
                if callable(getter):
                    nid = getter()
                else:
                    nid = getattr(val, 'handle', None) or getattr(val, 'hwnd', None) or 0
                title = getattr(val, 'title', None) or (getattr(val, 'getTitle', None) and val.getTitle()) or ''
                box = getattr(val, 'box', None) or (getattr(val, 'getClientRect', None) and val.getClientRect())
                if box:
                    left = getattr(box, 'x', box[0] if isinstance(box, (list, tuple)) else 0)
                    top = getattr(box, 'y', box[1] if isinstance(box, (list, tuple)) else 0)
                    width = getattr(box, 'width', box[2] if isinstance(box, (list, tuple)) and len(box) > 2 else 0)
                    height = getattr(box, 'height', box[3] if isinstance(box, (list, tuple)) and len(box) > 3 else 0)
                else:
                    left = top = width = height = 0
                w = WindowDummy(nid or 0, title or '', int(left or 0), int(top or 0), int(width or 0), int(height or 0))
                if pid is not None:
                    w.pid = int(pid)
                out.append(w)
            except Exception:
                continue
    return out


def find_window_by_process_name(process_name: str):
    """Find a window by the name of its associated process.
    
    This is useful for finding windows like scrcpy where the window title may vary
    but the process name is consistent. Works cross-platform using psutil and pywinctl.
    
    Args:
        process_name: The process name to search for (e.g., 'scrcpy', 'bluestacks', 'steam')
    
    Returns:
        A window object (WindowDummy or pygetwindow Window) if found, None otherwise
    """
    # First, try to find matching PIDs
    matching_pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc_info = getattr(proc, "info", {}) or {}
            pid = proc_info.get("pid")
            name = (proc_info.get("name") or "").strip().lower()
            if pid is not None and name and process_name.lower() in name:
                matching_pids.append(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception:
            continue
    
    if not matching_pids:
        logger.debug(f"[find_window_by_process_name] No process found matching '{process_name}'")
        return None
    
    logger.debug(f"[find_window_by_process_name] Found {len(matching_pids)} process(es) matching '{process_name}': {matching_pids}")
    
    # Now find windows associated with those PIDs
    if HAS_PYWINTCL:
        # Use pywinctl for robust cross-platform window enumeration
        for val in pwc.getAllWindows():  # type: ignore[union-attr]
            try:
                get_pid = getattr(val, 'getPID', None) or getattr(val, 'getPid', None)
                if callable(get_pid):
                    win_pid = get_pid()
                    if win_pid in matching_pids:
                        # Build a compatible WindowDummy object
                        try:
                            nid = None
                            getter = getattr(val, 'getHandle', None)
                            if callable(getter):
                                nid = getter()
                            else:
                                nid = getattr(val, 'handle', None) or getattr(val, 'hwnd', None) or 0
                            title = getattr(val, 'title', None) or (getattr(val, 'getTitle', None) and val.getTitle()) or ''
                            box = getattr(val, 'box', None) or (getattr(val, 'getClientRect', None) and val.getClientRect())
                            if box:
                                left = getattr(box, 'x', box[0] if isinstance(box, (list, tuple)) else 0)
                                top = getattr(box, 'y', box[1] if isinstance(box, (list, tuple)) else 0)
                                width = getattr(box, 'width', box[2] if isinstance(box, (list, tuple)) and len(box) > 2 else 0)
                                height = getattr(box, 'height', box[3] if isinstance(box, (list, tuple)) and len(box) > 3 else 0)
                            else:
                                left = top = width = height = 0
                            w = WindowDummy(nid or 0, title or '', int(left or 0), int(top or 0), int(width or 0), int(height or 0))
                            try:
                                w.pid = int(win_pid)
                            except Exception:
                                pass
                            # Try to get WM_CLASS
                            try:
                                get_cls = getattr(val, 'getWmClass', None) or getattr(val, 'getProcessName', None)
                                if callable(get_cls):
                                    cls_val = get_cls()
                                    if cls_val:
                                        w.wm_class = str(cls_val).strip()
                            except Exception:
                                pass
                            logger.debug(f"[find_window_by_process_name] Found window via pywinctl: title={w.title!r} class={w.wm_class!r} pid={win_pid}")
                            return w
                        except Exception as e:
                            logger.debug(f"[find_window_by_process_name] Error building window object: {e}")
                            continue
            except Exception:
                continue
    
    # Fallback: search through enumerated windows with PID info
    try:
        all_wins = get_all_windows(visible_only=False)
        for w in all_wins:
            win_pid = getattr(w, 'pid', None)
            if win_pid and win_pid in matching_pids:
                logger.debug(f"[find_window_by_process_name] Found window via fallback: title={getattr(w, 'title', '')!r} class={getattr(w, 'wm_class', '')!r} pid={win_pid}")
                return w
    except Exception as e:
        logger.debug(f"[find_window_by_process_name] Fallback enumeration failed: {e}")
    
    logger.debug(f"[find_window_by_process_name] No window found for process '{process_name}' with PIDs {matching_pids}")
    return None
