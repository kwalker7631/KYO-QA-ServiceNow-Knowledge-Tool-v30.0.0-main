import pytest


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

