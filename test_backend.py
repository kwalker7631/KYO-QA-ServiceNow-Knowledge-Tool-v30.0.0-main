import types
import sys

# Provide stub module before importing backend
pe_stub = types.ModuleType('processing_engine')
pe_stub.run_processing_job = lambda job, q: None
sys.modules['processing_engine'] = pe_stub

import backend


def test_process_job(monkeypatch):
    msgs = [
        {"type": "log", "msg": "starting"},
        {"type": "finish", "status": "Complete", "results": [1, 2, 3]},
    ]

    def fake_run_processing_job(job, q):
        for m in msgs:
            q.put(m)

    monkeypatch.setattr(backend, "run_processing_job", fake_run_processing_job)

    result = backend.process_job("out.xlsx", ["a.pdf"], False)
    assert result == {"status": "Complete", "results": [1, 2, 3], "output_path": "out.xlsx"}
