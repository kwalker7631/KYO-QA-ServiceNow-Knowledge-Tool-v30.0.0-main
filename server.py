import os
import shutil
import tempfile
from flask import Flask, request, abort, send_file, render_template
from werkzeug.utils import secure_filename

from backend import process_job

app = Flask(__name__, static_folder="web", template_folder="web")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/process", methods=["POST"])
def api_process():
    excel = request.files.get("excel")
    pdfs = request.files.getlist("pdfs[]")
    if not excel or not pdfs:
        missing_fields = []
        if not excel:
            missing_fields.append("excel file")
        if not pdfs:
            missing_fields.append("pdfs[] array")
        return abort(400, f"Required fields missing: {', '.join(missing_fields)}. Ensure you upload an 'excel' file and a 'pdfs[]' array.")

    workdir = tempfile.mkdtemp(prefix="qa_tool_")
    try:
        excel_fname = secure_filename(excel.filename)
        excel_path = os.path.join(workdir, excel_fname)
        excel.save(excel_path)

        pdf_paths = []
        for f in pdfs:
            p = os.path.join(workdir, secure_filename(f.filename))
            f.save(p)
            pdf_paths.append(p)

        _ = process_job(excel_path, pdf_paths)

        return send_file(
            excel_path,
            as_attachment=True,
            download_name=excel_fname,
        )
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
