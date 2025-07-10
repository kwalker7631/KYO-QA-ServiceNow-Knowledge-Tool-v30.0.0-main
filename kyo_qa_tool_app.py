# kyo_qa_tool_app.py - Final stable version with all UI elements and bug fixes.
# Updated: 2024-07-09 - Restored all UI components and integrated all fixes.
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading
import queue
import time
import importlib
import sys

from config import BRAND_COLORS, ASSETS_DIR
from processing_engine import run_processing_job
from file_utils import open_file, ensure_folders, cleanup_temp_files
from kyo_review_tool import ReviewWindow
from version import VERSION
import logging_utils
from gui_components import (
    create_main_header, create_io_section,
    create_process_controls
)

logger = logging_utils.setup_logger("app")


def get_remaining_seconds(start_time, total_files, processed_files, now=None):
    """Estimate remaining seconds for processing job."""
    if not start_time or processed_files == 0 or total_files == 0:
        return 0
    if now is None:
        now = time.time()
    elapsed = now - start_time
    avg_per_file = elapsed / processed_files
    remaining_files = max(total_files - processed_files, 0)
    return max(int(avg_per_file * remaining_files), 0)

def check_and_create_icons():
    """Auto-generate icons if they don't exist."""
    assets_dir = Path("assets")
    required_icons = ["start.png", "pause.png", "stop.png", "rerun.png", "open.png", "browse.png", "patterns.png", "exit.png", "fullscreen.png"]
    if assets_dir.exists() and all((assets_dir / i).exists() for i in required_icons):
        return True
    
    print("🎨 Attempting to create missing icons...")
    try:
        from PIL import Image, ImageDraw
        assets_dir.mkdir(exist_ok=True)
        icon_defs = {
            "start.png": {"c": (40, 167, 69), "s": "triangle"}, "pause.png": {"c": (255, 193, 7), "s": "bars"},
            "stop.png": {"c": (220, 53, 69), "s": "square"}, "rerun.png": {"c": (0, 123, 255), "s": "circle"},
            "open.png": {"c": (111, 66, 193), "s": "diamond"}, "browse.png": {"c": (23, 162, 184), "s": "folder"},
            "patterns.png": {"c": (253, 126, 20), "s": "grid"}, "exit.png": {"c": (108, 117, 125), "s": "x"},
            "fullscreen.png": {"c": (32, 201, 151), "s": "corners"}
        }
        for name, cfg in icon_defs.items():
            img = Image.new('RGBA', (16, 16), (0,0,0,0))
            draw = ImageDraw.Draw(img)
            shape, color = cfg["s"], cfg["c"]
            if shape == "triangle": draw.polygon([(3, 3), (3, 13), (13, 8)], fill=color)
            elif shape == "bars": draw.rectangle([4, 3, 6, 13], fill=color); draw.rectangle([10, 3, 12, 13], fill=color)
            elif shape == "square": draw.rectangle([4, 4, 12, 12], fill=color)
            elif shape == "circle": draw.ellipse([2, 2, 14, 14], outline=color, width=2); draw.polygon([(12, 4), (12, 8), (14, 6)], fill=color)
            elif shape == "diamond": draw.polygon([(8, 2), (13, 7), (8, 14), (3, 7)], outline=color, width=2)
            elif shape == "folder": draw.rectangle([2, 6, 14, 13], fill=color); draw.polygon([(2, 6), (2, 4), (6, 4), (8, 6)], fill=color)
            elif shape == "grid":
                for i in range(3):
                    for j in range(3): draw.rectangle([3+i*4, 3+j*4, 5+i*4, 5+j*4], fill=color)
            elif shape == "x": draw.line([(4, 4), (12, 12)], fill=color, width=2); draw.line([(12, 4), (4, 12)], fill=color, width=2)
            elif shape == "corners":
                for p in [(2,2,5,2,2,5), (14,2,11,2,14,5), (2,14,5,14,2,11), (14,14,11,14,14,11)]:
                    draw.line([(p[0],p[1]),(p[2],p[3])], fill=color, width=2); draw.line([(p[0],p[1]),(p[4],p[5])], fill=color, width=2)
            img.save(assets_dir / name, 'PNG')
        return True
    except Exception as e:
        print(f"⚠️ Could not create icons: {e}. Buttons may be blank.")
        return False

class KyoQAToolApp(tk.Tk):
    def __init__(self):
        super().__init__()
        # Counters
        self.count_pass, self.count_fail, self.count_review, self.count_ocr = tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar()
        self.count_protected, self.count_corrupted, self.count_ocr_failed, self.count_no_text = tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar()
        self.count_needs_review = self.count_review
        # State
        self.is_processing, self.is_paused, self.result_file_path, self.start_time, self.is_fullscreen = False, False, None, None, True
        self.last_run_info, self.reviewable_files, self.selected_files_list = {}, [], []
        self.total_files = 0
        self.response_queue, self.cancel_event, self.pause_event = queue.Queue(), threading.Event(), threading.Event()
        # UI Vars
        self.selected_folder, self.selected_excel = tk.StringVar(), tk.StringVar()
        self.status_current_file, self.progress_value = tk.StringVar(value="Ready to process"), tk.DoubleVar()
        self.time_remaining_var, self.led_status_var = tk.StringVar(), tk.StringVar(value="●")

        check_and_create_icons()
        self._load_icons()
        self._setup_window_styles()
        self._create_widgets()

        ensure_folders()
        self.attributes("-fullscreen", self.is_fullscreen)
        self.bind_all("<Escape>", self.toggle_fullscreen)
        self.after(100, self.process_response_queue)
        self.set_led("Ready")

    def _update_time_remaining(self):
        processed = sum(v.get() for v in [
            self.count_pass,
            self.count_fail,
            self.count_review,
            self.count_protected,
            self.count_corrupted,
            self.count_ocr_failed,
            self.count_no_text,
        ])
        remaining_seconds = get_remaining_seconds(self.start_time, self.total_files, processed)
        mins, secs = divmod(remaining_seconds, 60)
        if self.is_processing and remaining_seconds:
            self.time_remaining_var.set(f"{mins}:{secs:02d} remaining")
        elif not self.is_processing:
            self.time_remaining_var.set("")

    def _load_icon(self, filename):
        try:
            return tk.PhotoImage(file=ASSETS_DIR / filename)
        except tk.TclError:
            return None

    def _load_icons(self):
        self.start_icon = self._load_icon("start.png")
        self.pause_icon = self._load_icon("pause.png")
        self.stop_icon = self._load_icon("stop.png")
        self.rerun_icon = self._load_icon("rerun.png")
        self.open_icon = self._load_icon("open.png")
        self.browse_icon = self._load_icon("browse.png")
        self.patterns_icon = self._load_icon("patterns.png")
        self.exit_icon = self._load_icon("exit.png")
        self.fullscreen_icon = self._load_icon("fullscreen.png")

    def _setup_window_styles(self):
        self.title(f"Kyocera QA Knowledge Tool v{VERSION}")
        self.geometry("1200x900"); self.minsize(1000, 800)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.configure(bg=BRAND_COLORS["background"])
        self.columnconfigure(0, weight=1); self.rowconfigure(1, weight=1)
        self.style = ttk.Style(self); self.style.theme_use("clam")
        self.style.configure("TFrame", background=BRAND_COLORS["background"])
        self.style.configure("TLabel", background=BRAND_COLORS["background"], font=("Segoe UI", 10))
        self.style.configure("TLabelFrame.Label", background=BRAND_COLORS["background"], font=("Segoe UI", 11, "bold"))
        self.style.configure("Treeview", font=("Segoe UI", 9), fieldbackground=BRAND_COLORS["frame_background"], rowheight=25)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        self.style.map("Treeview", background=[('selected', BRAND_COLORS["highlight_blue"])])
        self.style.configure("Red.TButton", font=("Segoe UI", 12, "bold"), foreground="white")
        self.style.map("Red.TButton", background=[('active', '#A81F14'), ('!active', BRAND_COLORS["kyocera_red"])])
        self.style.configure("Status.TFrame", background=BRAND_COLORS["status_default_bg"])
        self.style.configure("Status.TLabel", font=("Segoe UI", 10), background=BRAND_COLORS["status_default_bg"])
        self.style.configure("LED.TLabel", font=("Segoe UI", 16), background=BRAND_COLORS["status_default_bg"])
        for color_name, color_hex in {"Green": "success_green", "Red": "fail_red", "Orange": "warning_orange", "Blue": "accent_blue", "Gray": "gray", "Purple": "purple"}.items():
            self.style.configure(f"Count.{color_name}.TLabel", foreground=BRAND_COLORS.get(color_hex, "black"), font=("Segoe UI", 10, "bold"), background=BRAND_COLORS["background"])

    def _create_widgets(self):
        create_main_header(self, VERSION, BRAND_COLORS)
        main_frame = ttk.Frame(self, padding=20)
        main_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1); main_frame.rowconfigure(2, weight=1)
        create_io_section(main_frame, self)
        create_process_controls(main_frame, self)
        self._create_enhanced_status_section(main_frame)

    def _create_enhanced_status_section(self, parent):
        stat = ttk.LabelFrame(parent, text="3. Status & Logs", padding=10)
        stat.grid(row=2, column=0, sticky="nsew", pady=5)
        stat.columnconfigure(0, weight=1); stat.rowconfigure(4, weight=1)
        
        # Status and Progress Bar
        self.status_frame = ttk.Frame(stat, style="Status.TFrame", padding=5)
        self.status_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        self.status_frame.columnconfigure(1, weight=1)
        self.led_label = ttk.Label(self.status_frame, textvariable=self.led_status_var, style="LED.TLabel")
        self.led_label.grid(row=0, column=0, sticky="w")
        ttk.Label(self.status_frame, textvariable=self.status_current_file, style="Status.TLabel").grid(row=0, column=1, sticky="ew", padx=5)
        prog_frame = ttk.Frame(stat)
        prog_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(5,10))
        prog_frame.columnconfigure(0, weight=1)
        self.progress_bar = ttk.Progressbar(prog_frame, variable=self.progress_value, style="Blue.Horizontal.TProgressbar")
        self.progress_bar.grid(row=0, column=0, sticky="ew")
        ttk.Label(prog_frame, textvariable=self.time_remaining_var).grid(row=0, column=1, sticky="e", padx=10)

        # Counters
        sum_frame = ttk.Frame(stat)
        sum_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=2)
        counters = [
            ("Pass:", self.count_pass, "Green"), ("Fail:", self.count_fail, "Red"), ("Review:", self.count_review, "Orange"), 
            ("OCR:", self.count_ocr, "Blue"), ("Protected:", self.count_protected, "Gray"), ("Corrupted:", self.count_corrupted, "Purple"),
            ("OCR Failed:", self.count_ocr_failed, "Red"), ("No Text:", self.count_no_text, "Orange")
        ]
        for i, (text, var, color) in enumerate(counters):
            f = ttk.Frame(sum_frame)
            f.pack(side="left", padx=(15, 2))
            ttk.Label(f, text=text).pack(side="left")
            ttk.Label(f, textvariable=var, style=f"Count.{color}.TLabel").pack(side="left")

        # Review Section
        rev_frame = ttk.LabelFrame(stat, text="Files to Review (Double-click a file to fix patterns)")
        rev_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=10)
        rev_frame.rowconfigure(0, weight=1); rev_frame.columnconfigure(0, weight=1)
        self.review_tree = ttk.Treeview(rev_frame, columns=('file', 'reason'), show='headings', height=4)
        self.review_tree.grid(row=0, column=0, sticky="nsew")
        self.review_tree.heading('file', text='File Name'); self.review_tree.heading('reason', text='Failure Reason')
        self.review_tree.column('file', width=250); self.review_tree.column('reason', width=400)
        self.review_tree.bind("<Double-1>", self.open_review_for_selected_file)
        rev_scrollbar = ttk.Scrollbar(rev_frame, orient="vertical", command=self.review_tree.yview)
        rev_scrollbar.grid(row=0, column=1, sticky="ns"); self.review_tree.config(yscrollcommand=rev_scrollbar.set)

        # Log Section
        log_frame = ttk.Frame(stat); log_frame.grid(row=4, column=0, sticky="nsew", padx=5, pady=2)
        log_frame.rowconfigure(0, weight=1); log_frame.columnconfigure(0, weight=1)
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD, state=tk.DISABLED, relief="solid", borderwidth=1, font=("Consolas", 9))
        self.log_text.grid(row=0, column=0, sticky="nsew")
        log_scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        log_scroll.grid(row=0, column=1, sticky="ns"); self.log_text.config(yscrollcommand=log_scroll.set)

    def start_processing(self, job=None, is_rerun=False):
        if self.is_processing: return
        input_path = self.selected_folder.get() or self.selected_files_list
        excel_path = self.selected_excel.get()
        if not job and (not input_path or not excel_path):
            return messagebox.showwarning("Input Missing", "Please select both a base Excel file and a folder/files to process.")
        job = job or {"excel_path": excel_path, "input_path": input_path}
        self.last_run_info = job; job["is_rerun"] = is_rerun
        inp = job["input_path"]
        if isinstance(inp, list):
            self.total_files = len(inp)
        else:
            self.total_files = len(list(Path(inp).glob("*.pdf")))
        self.update_ui_for_start(); self.log_message("Starting processing job..."); self.start_time = time.time()
        threading.Thread(target=run_processing_job, args=(job, self.response_queue, self.cancel_event, self.pause_event), daemon=True).start()

    def rerun_flagged_job(self):
        if not self.reviewable_files: return messagebox.showinfo("No Files", "There are no files to re-run.")
        if not self.result_file_path: return messagebox.showerror("Error", "Previous result file not found.")
        files = [item["pdf_path"] for item in self.reviewable_files]
        self.log_message(f"Re-running {len(files)} flagged files...")
        self.start_processing(job={"excel_path": self.result_file_path, "input_path": files}, is_rerun=True)

    def open_review_for_selected_file(self, event=None):
        selection = self.review_tree.selection()
        if not selection: return
        filename = self.review_tree.item(selection[0], "values")[0]
        review_info = next((f for f in self.reviewable_files if f['filename'] == filename), None)
        if review_info:
            ReviewWindow(self, "MODEL_PATTERNS", "Model Patterns", review_info)
        else:
            messagebox.showerror("Error", f"Could not find review info for '{filename}'.")

    def process_response_queue(self):
        try:
            while not self.response_queue.empty():
                msg = self.response_queue.get_nowait()
                mtype = msg.get("type")
                if mtype == "log": self.log_message(msg.get("msg", ""))
                elif mtype == "status": self.status_current_file.set(msg.get("msg", ""))
                elif mtype == "review_item":
                    data = msg.get("data", {})
                    self.reviewable_files.append(data)
                    self.review_tree.insert('', 'end', values=(data.get('filename', 'N/A'), data.get('reason', 'N/A')))
                elif mtype == "finish":
                    status = msg.get("status", "Complete")
                    self.log_message(f"Job finished: {status}")
                    self.update_ui_for_finish(status)
                elif mtype == "file_complete":
                    status = msg.get("status", "")
                    mapping = {
                        "Pass": self.count_pass,
                        "Fail": self.count_fail,
                        "Needs Review": self.count_review,
                        "Protected": self.count_protected,
                        "Corrupted": self.count_corrupted,
                        "OCR Failed": self.count_ocr_failed,
                        "No Text": self.count_no_text,
                    }
                    var = mapping.get(status)
                    if var:
                        var.set(var.get() + 1)
                elif mtype == "result_path": self.result_file_path = msg.get("path")
                elif mtype == "increment_counter":
                    counter_name = f"count_{msg.get('counter')}"
                    if hasattr(self, counter_name):
                        getattr(self, counter_name).set(getattr(self, counter_name).get() + 1)
        except queue.Empty: pass
        self._update_time_remaining()
        self.after(100, self.process_response_queue)

    def update_ui_for_start(self):
        self.is_processing = True; self.is_paused = False
        self.cancel_event.clear(); self.pause_event.clear()
        for var in [self.count_pass, self.count_fail, self.count_review, self.count_ocr, self.count_protected, self.count_corrupted, self.count_ocr_failed, self.count_no_text]: var.set(0)
        self.reviewable_files.clear(); self.review_tree.delete(*self.review_tree.get_children())
        self.process_btn.config(state=tk.DISABLED); self.rerun_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL); self.stop_btn.config(state=tk.NORMAL)
        self.time_remaining_var.set("")

    def update_ui_for_finish(self, status):
        self.is_processing = False; self.is_paused = False
        self.process_btn.config(state=tk.NORMAL)
        if self.reviewable_files: self.rerun_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED); self.stop_btn.config(state=tk.DISABLED)
        self.time_remaining_var.set("")

    def log_message(self, message, level="info"):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END); self.log_text.config(state=tk.DISABLED)
    
    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)
    def on_closing(self):
        if self.is_processing and not messagebox.askyesno("Exit", "Job is running. Exit anyway?"):
            return
        self.destroy()
    def browse_excel(self):
        path = filedialog.askopenfilename(title="Select Excel Template", filetypes=[("Excel Files", "*.xlsx *.xlsm")])
        if path: self.selected_excel.set(path)
    def browse_folder(self):
        path = filedialog.askdirectory(title="Select Folder with PDFs")
        if path:
            self.selected_folder.set(path)
            self.selected_files_list.clear()
            if hasattr(self, 'files_label'):
                self.files_label.config(text=f"{len(list(Path(path).glob('*.pdf')))} PDFs in folder")
    def browse_files(self):
        paths = filedialog.askopenfilenames(title="Select PDF Files", filetypes=[("PDF Files", "*.pdf")])
        if paths:
            self.selected_files_list = list(paths)
            self.selected_folder.set("")
            if hasattr(self, 'files_label'):
                self.files_label.config(text=f"{len(paths)} files selected")
    def toggle_pause(self):
        if not self.is_processing: return
        self.is_paused = not self.is_paused
        self.pause_event.set() if self.is_paused else self.pause_event.clear()
    def stop_processing(self):
        if self.is_processing: self.cancel_event.set()
    def open_result(self):
        if self.result_file_path: open_file(self.result_file_path)
    def open_pattern_manager(self):
        ReviewWindow(self, "MODEL_PATTERNS", "Model Patterns", None)
    def set_led(self, status): pass

if __name__ == "__main__":
    try:
        app = KyoQAToolApp()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"A fatal error occurred:\n\n{e}")
