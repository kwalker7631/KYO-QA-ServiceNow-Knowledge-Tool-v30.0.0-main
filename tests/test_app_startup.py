import os
import sys
import subprocess


def test_script_runs_without_display():
    env = dict(os.environ)
    env.pop('DISPLAY', None)
    result = subprocess.run([sys.executable, 'kyo_qa_tool_app.py'], env=env, capture_output=True, text=True)
    assert result.returncode == 0
    assert 'No GUI display' in result.stdout
