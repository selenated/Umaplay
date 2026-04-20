from types import SimpleNamespace

from core.controllers import steam as steam_mod


def test_find_window_ignores_empty_process_window_titles(monkeypatch):
    ctrl = steam_mod.SteamController(window_title="Umamusume")

    monkeypatch.setattr(steam_mod, "get_windows_with_title", lambda _title: [])
    monkeypatch.setattr(steam_mod, "get_all_windows", lambda: [])
    monkeypatch.setattr(
        steam_mod,
        "find_window_by_process_name",
        lambda _hint: SimpleNamespace(title="", wm_class="", _hWnd=1),
    )

    assert ctrl._find_window() is None


def test_find_window_can_match_process_window_class(monkeypatch):
    ctrl = steam_mod.SteamController(window_title="Umamusume")

    window = SimpleNamespace(
        title="",
        wm_class="UmamusumePretty",
        _hWnd=123,
    )

    monkeypatch.setattr(steam_mod, "get_windows_with_title", lambda _title: [])
    monkeypatch.setattr(steam_mod, "get_all_windows", lambda: [])
    monkeypatch.setattr(steam_mod, "find_window_by_process_name", lambda _hint: window)

    assert ctrl._find_window() is window
