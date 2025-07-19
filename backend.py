"""Simple synchronous wrapper around :func:`run_processing_job`."""

import tempfile
import shutil
from queue import Queue

from processing_engine import run_processing_job


def process_job(excel_path: str, pdf_paths: list[str], *, is_rerun: bool = False) -> dict:
    """Run the PDF→Excel pipeline and wait for completion.

    Parameters
    ----------
    excel_path : str
        Path to the Excel template to use.
    pdf_paths : list[str]
        Paths of PDF files to process.
    is_rerun : bool, optional
        If ``True``, ignore cached data and re-process PDFs, by default ``False``.

    Returns
    -------
    dict
        Dictionary containing ``status``, ``results`` and ``output_path`` keys.
    """

    job = {"excel_path": excel_path, "input_path": pdf_paths, "is_rerun": is_rerun}
    q = Queue()
    run_processing_job(job, q)

    final: dict = {}
    while True:  # Consume progress messages until the job finishes
        try:
            msg = q.get(timeout=10)  # Add a timeout to prevent indefinite blocking
        except queue.Empty:
            raise RuntimeError("Timeout waiting for job to finish. No message received.")
        if msg.get("type") == "finish":
            final["status"] = msg.get("status")
            final["results"] = msg.get("results", [])
            break

    final["output_path"] = excel_path
    return final
