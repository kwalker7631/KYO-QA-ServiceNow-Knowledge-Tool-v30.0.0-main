import os
import sys
import subprocess


def test_script_runs_without_display():
    env = dict(os.environ)
    env.pop('DISPLAY', None)
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'kyo_qa_tool_app.py'))
    result = subprocess.run([sys.executable, script_path], env=env, capture_output=True, text=True)
    assert result.returncode == 0
    assert 'No GUI display' in result.stdout
