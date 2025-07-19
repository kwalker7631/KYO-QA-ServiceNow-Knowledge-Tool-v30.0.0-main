from queue import Queue
from processing_engine import run_processing_job


def process_job(excel_path: str, pdf_paths: list[str], is_rerun: bool = False) -> dict:
    """Runs the full PDF→Excel pipeline synchronously.
    Returns a dict with keys: status, results, output_path."""
    job = {"excel_path": excel_path, "input_path": pdf_paths, "is_rerun": is_rerun}
    q = Queue()
    run_processing_job(job, q)
    final = {}
    while True:
        try:
            msg = q.get(timeout=10)  # Timeout after 10 seconds
        except queue.Empty:
            raise TimeoutError("Processing job timed out waiting for a 'finish' message.")
        except Exception as e:
            raise RuntimeError(f"An error occurred while processing the job: {e}")
        if msg.get("type") == "finish":
            final["status"] = msg.get("status")
            final["results"] = msg.get("results", [])
            break
    final["output_path"] = excel_path
    return final
