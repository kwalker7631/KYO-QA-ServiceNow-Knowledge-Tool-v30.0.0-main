import logging
logging.getLogger(__name__).setLevel(logging.DEBUG)

"""UI helper functions used by kyo_qa_tool_app.
This simplified implementation defines all create_* functions referenced
by the application.  Widgets are created with basic layouts so tests can
import these functions without requiring the full original UI code.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

# Use an absolute import so this module works both as part of a package and
# when run from the repository root.
try:
    from branding import KyoceraColors
except Exception:  # pragma: no cover - support running outside package
    KyoceraColors = None

# ---------------------------------------------------------------------------
# Style helpers
# ---------------------------------------------------------------------------

def setup_high_contrast_styles(root: tk.Misc, colors: Optional[KyoceraColors] = None) -> None:
    """Initialize some simple ttk styles for accessibility."""
    logging.debug("Configuring high contrast styles")
    style = ttk.Style(root)
    style.theme_use("clam")
    fg = colors.kyocera_black if colors else "#000000"
    bg = colors.status_default_bg if colors else "#FFFFFF"
    style.configure("TFrame", background=bg)
    style.configure("TLabel", background=bg, foreground=fg)

# ---------------------------------------------------------------------------
# Header and sections
# ---------------------------------------------------------------------------

def create_main_header(parent: tk.Widget, version: str, colors: dict) -> ttk.Frame:
    frame = ttk.Frame(parent, style="Header.TFrame")
    frame.grid(row=0, column=0, sticky="ew")
    ttk.Label(frame, text="KYOCERA", foreground=colors.get("kyocera_red", "#DA291C"), font=("Arial Black", 22)).pack(side=tk.LEFT, padx=(10, 5))
    ttk.Label(frame, text=f"QA Knowledge Tool v{version}", font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT)
    return frame


def create_io_section(parent: tk.Widget, app) -> ttk.LabelFrame:
    frame = ttk.LabelFrame(parent, text="1. Select Inputs")
    frame.grid(row=0, column=0, sticky="ew", pady=5)
    frame.columnconfigure(1, weight=1)
    ttk.Label(frame, text="Excel to Clone:").grid(row=0, column=0, sticky="w", padx=5)
    ttk.Entry(frame, textvariable=app.selected_excel).grid(row=0, column=1, sticky="ew", padx=5)
    ttk.Button(frame, text="Browse", command=app.browse_excel).grid(row=0, column=2, padx=5)
    ttk.Label(frame, text="PDFs Folder:").grid(row=1, column=0, sticky="w", padx=5)
    ttk.Entry(frame, textvariable=app.selected_folder).grid(row=1, column=1, sticky="ew", padx=5)
    ttk.Button(frame, text="Browse", command=app.browse_folder).grid(row=1, column=2, padx=5)
    return frame


def create_controls_section(parent: tk.Widget, app) -> ttk.LabelFrame:
    frame = ttk.LabelFrame(parent, text="2. Process & Manage")
    frame.grid(row=1, column=0, sticky="ew", pady=5)
    frame.columnconfigure((0, 1, 2, 3), weight=1)
    app.process_btn = ttk.Button(frame, text="START", command=app.start_processing)
    app.process_btn.grid(row=0, column=0, columnspan=4, sticky="ew", pady=5)
    app.pause_btn = ttk.Button(frame, text="Pause", command=app.toggle_pause, state=tk.DISABLED)
    app.pause_btn.grid(row=1, column=0, sticky="ew", padx=2)
    app.stop_btn = ttk.Button(frame, text="Stop", command=app.stop_processing, state=tk.DISABLED)
    app.stop_btn.grid(row=1, column=1, sticky="ew", padx=2)
    app.rerun_btn = ttk.Button(frame, text="Re-run Flagged", command=app.rerun_flagged_job, state=tk.DISABLED)
    app.rerun_btn.grid(row=1, column=2, sticky="ew", padx=2)
    app.open_result_btn = ttk.Button(frame, text="Open Result", command=app.open_result, state=tk.DISABLED)
    app.open_result_btn.grid(row=1, column=3, sticky="ew", padx=2)
    return frame


def create_live_status_section(parent: tk.Widget, app):
    frame = ttk.LabelFrame(parent, text="3. Status & Logs")
    frame.grid(row=2, column=0, sticky="nsew", pady=5)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(3, weight=1)
    app.status_frame = ttk.Frame(frame, padding=5, style="Ready.Status.TFrame")
    app.status_frame.grid(row=0, column=0, sticky="ew")
    app.led_label = ttk.Label(app.status_frame, textvariable=app.led_status_var, style="Ready.LED.TLabel")
    app.led_label.grid(row=0, column=0, sticky="w")
    app.status_text_label = ttk.Label(app.status_frame, textvariable=app.status_current_file, style="Ready.Status.TLabel")
    app.status_text_label.grid(row=0, column=1, sticky="ew", padx=5)
    app.progress_bar = ttk.Progressbar(frame, variable=app.progress_value)
    app.progress_bar.grid(row=1, column=0, sticky="ew", padx=5)
    ttk.Label(frame, textvariable=app.time_remaining_var).grid(row=2, column=0, sticky="e", padx=5)
    app.log_text = tk.Text(frame, height=8, state=tk.DISABLED)
    app.log_text.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
    return frame


def create_footer(parent: tk.Widget) -> ttk.Frame:
    frame = ttk.Frame(parent)
    frame.grid(row=99, column=0, sticky="ew")
    ttk.Separator(frame, orient="horizontal").pack(fill="x")
    ttk.Label(frame, text="© Kyocera Document Solutions").pack(side=tk.RIGHT, padx=5)
    return frame

# ---------------------------------------------------------------------------
# Optional tabs used by earlier versions of the application.  These stubs are
# provided for compatibility with tests that simply import them.
# ---------------------------------------------------------------------------

def create_review_tab(notebook: ttk.Notebook, app) -> ttk.Frame:
    tab = ttk.Frame(notebook)
    ttk.Label(tab, text="Review tab placeholder").pack()
    return tab


def create_harvest_tab(notebook: ttk.Notebook, app) -> ttk.Frame:
    tab = ttk.Frame(notebook)
    ttk.Label(tab, text="Harvest tab placeholder").pack()
    return tab


def create_data_harvest_tab(notebook: ttk.Notebook, app) -> ttk.Frame:
    tab = ttk.Frame(notebook)
    ttk.Label(tab, text="Data Harvest tab placeholder").pack()
    return tab

