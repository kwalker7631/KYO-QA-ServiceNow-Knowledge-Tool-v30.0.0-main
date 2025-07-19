import pytest
import types



def test_launch_app_removed():
    """Verify the old Tkinter app module is no longer available."""
    with pytest.raises(ImportError):
        __import__("kyo_qa_tool_app")


def test_launch_main_starts_webview(monkeypatch):
    import importlib
    import sys

    calls = []

    def create_window(*a, **k):
        fallback_url = a[1] if len(a) > 1 else ""
        calls.append(k.get("url", fallback_url))

    stub_webview = types.SimpleNamespace(
        create_window=create_window,
        start=lambda: calls.append("webview"),
    )
    monkeypatch.setitem(sys.modules, "webview", stub_webview)

    import launch
    importlib.reload(launch)

    def fake_thread(target, daemon=False):
        calls.append("thread")

        class Dummy:
            def start(self):
                calls.append("start")
                # Run target immediately to avoid creating new thread
                target()

        return Dummy()

    monkeypatch.setattr(launch, "threading", types.SimpleNamespace(Thread=fake_thread))
    monkeypatch.setattr(launch, "time", types.SimpleNamespace(sleep=lambda x: None))
    monkeypatch.setattr(launch.subprocess, "run", lambda *a, **k: calls.append("run"))

    monkeypatch.setenv("SERVER_URL", "http://example.com")
    launch.main()

    assert "run" in calls
    assert "http://example.com" in calls
    assert "webview" in calls

