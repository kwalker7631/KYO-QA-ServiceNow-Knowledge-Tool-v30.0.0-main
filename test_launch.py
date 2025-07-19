import pytest
import types



def test_launch_app():
    try:
        from kyo_qa_tool_app import KyoQAToolApp
        app = KyoQAToolApp()
        # immediately destroy to avoid opening window
        app.destroy()
    except Exception as exc:
        # Skip if failure is due to missing GUI display
        if 'display' in str(exc).lower():
            pytest.skip("GUI not available")
        else:
            raise


def test_launch_main_starts_webview(monkeypatch):
    import importlib, sys

    calls = []

    stub_webview = types.SimpleNamespace(
        create_window=lambda *a, **k: calls.append("window"),
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

    launch.main()

    assert "run" in calls
    assert "window" in calls
    assert "webview" in calls

