from core.controllers import window_utils


class _Proc:
    def __init__(self, pid, name):
        self.info = {"pid": pid, "name": name}


def test_find_window_by_process_name_handles_missing_process_names(monkeypatch):
    monkeypatch.setattr(
        window_utils.psutil,
        "process_iter",
        lambda _attrs: [_Proc(100, None), _Proc(200, "")],
    )
    monkeypatch.setattr(window_utils, "HAS_PYWINTCL", False)
    monkeypatch.setattr(window_utils, "get_all_windows", lambda visible_only=False: [])

    assert window_utils.find_window_by_process_name("steam") is None
