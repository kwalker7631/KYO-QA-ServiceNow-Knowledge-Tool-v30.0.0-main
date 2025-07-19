import io
import pytest

pytest.importorskip("flask")

import server


def test_api_process(monkeypatch):
    called = {}

    def fake_process(excel, pdfs):
        called["excel"] = excel
        called["pdfs"] = pdfs
        return {"status": "OK", "results": [], "output_path": excel}

    monkeypatch.setattr(server, "process_job", fake_process)

    client = server.app.test_client()
    data = {
        "excel": (io.BytesIO(b"excel"), "template.xlsx"),
        "pdfs[]": [
            (io.BytesIO(b"pdf1"), "a.pdf"),
            (io.BytesIO(b"pdf2"), "b.pdf"),
        ],
    }
    resp = client.post("/api/process", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    assert called["pdfs"][0].endswith("a.pdf")
    assert resp.data == b"excel"




def test_index_page():
    client = server.app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert "QA Tool" in text
    assert "app.js" in text
