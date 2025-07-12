# kyo_qa_tool_app.py - Definitive fix for UI feedback and review process logic.

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading
import queue
import time

# Local Imports
from config import BRAND_COLORS, ASSETS_DIR
from processing_engine import run_processing_job
from file_utils import open_file, ensure_folders, cleanup_temp_files
from kyo_review_tool import ReviewWindow
from version import VERSION
import logging_utils
from gui_components import (
    create_main_header, create_io_section,
    create_process_controls, create_status_and_log_section
)

logger = logging_utils.setup_logger("app")

def get_led_colors(status):
    """Returns foreground and background colors for the status LED."""
    color_map = {
        "Processing": ("#FFFFFF", BRAND_COLORS.get("accent_blue")),
        "Saving": ("#FFFFFF", BRAND_COLORS.get("accent_blue")),
        "OCR": ("#000000", BRAND_COLORS.get("status_ocr_bg")),
        "AI": ("#FFFFFF", BRAND_COLORS.get("kyocera_red")),
        "Paused": ("#000000", BRAND_COLORS.get("warning_orange")),
        "Ready": ("#FFFFFF", BRAND_COLORS.get("success_green")),
        "Complete": ("#FFFFFF", BRAND_COLORS.get("success_green")),
        "Cancelled": ("#000000", BRAND_COLORS.get("warning_orange")),
        "Error": ("#FFFFFF", BRAND_COLORS.get("fail_red")),
    }
    return color_map.get(status, ("#000000", BRAND_COLORS.get("status_default_bg")))

class KyoQAToolApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.is_processing = False; self.is_paused = False; self.is_fullscreen = True
        self.result_file_path = None; self.start_time = None; self.total_files = 0
        self.reviewable_files = []; self.selected_files_list = []
        
        self.response_queue = queue.Queue()
        self.cancel_event = threading.Event(); self.pause_event = threading.Event()

        self.count_pass = tk.IntVar(); self.count_fail = tk.IntVar()
        self.count_review = tk.IntVar(); self.count_ocr = tk.IntVar()
        self.selected_folder = tk.StringVar(); self.selected_excel = tk.StringVar()
        self.status_current_file = tk.StringVar(value="Ready to process")
        self.progress_value = tk.DoubleVar(); self.import_progress = tk.DoubleVar()
        self.time_remaining_var = tk.StringVar(); self.led_status_var = tk.StringVar(value="●")

        self._load_icons()
        self._setup_window_styles()
        self._create_widgets()

        ensure_folders()
        self.attributes("-fullscreen", self.is_fullscreen)
        self.bind_all("<Escape>", self.toggle_fullscreen)
        self.after(100, self.process_response_queue)
        self.set_led("Ready")

    def _load_icons(self):
        icon_names = ["start", "pause", "stop", "rerun", "open", "browse", "patterns", "exit", "fullscreen"]
        for name in icon_names:
            try: setattr(self, f"{name}_icon", tk.PhotoImage(file=ASSETS_DIR / f"{name}.png"))
            except tk.TclError: setattr(self, f"{name}_icon", None)

    def _setup_window_styles(self):
        self.title(f"Kyocera QA Knowledge Tool v{VERSION}")
        self.geometry("1200x900"); self.minsize(1000, 800)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.configure(bg=BRAND_COLORS["background"])
        self.columnconfigure(0, weight=1); self.rowconfigure(1, weight=1)

        style = ttk.Style(self); style.theme_use("clam")
        style.configure("TFrame", background=BRAND_COLORS["background"])
        style.configure("TLabel", background=BRAND_COLORS["background"], font=("Segoe UI", 10))
        style.configure("Header.TFrame", background="white")
        style.configure("TLabelFrame", background=BRAND_COLORS["background"])
        style.configure("TLabelFrame.Label", background=BRAND_COLORS["background"], font=("Segoe UI", 11, "bold"))
        style.configure("Treeview", font=("Segoe UI", 9), fieldbackground=BRAND_COLORS["frame_background"], rowheight=25)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[('selected', BRAND_COLORS["highlight_blue"])])
        style.configure("Red.TButton", font=("Segoe UI", 12, "bold"), foreground="white")
        style.map("Red.TButton", background=[('active', '#A81F14'), ('!active', BRAND_COLORS["kyocera_red"])])
        style.configure("Blue.Horizontal.TProgressbar", background=BRAND_COLORS["accent_blue"])

        statuses = ["Ready", "Processing", "Saving", "OCR", "AI", "Paused", "Complete", "Cancelled", "Error"]
        for status in statuses:
            fg, bg = get_led_colors(status)
            style.configure(f"{status}.Status.TFrame", background=bg)
            style.configure(f"{status}.LED.TLabel", foreground=fg, background=bg, font=("Segoe UI", 16))
            style.configure(f"{status}.Status.TLabel", foreground=fg, background=bg, font=("Segoe UI", 10))

    def _create_widgets(self):
        create_main_header(self, VERSION, BRAND_COLORS)
        main_frame = ttk.Frame(self, padding=20)
        main_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1); main_frame.rowconfigure(2, weight=1)
        create_io_section(main_frame, self)
        create_process_controls(main_frame, self)
        create_status_and_log_section(main_frame, self)

    def start_processing(self, job=None, is_rerun=False):
        if self.is_processing: return
        input_path = self.selected_folder.get() or self.selected_files_list
        excel_path = self.selected_excel.get()
        if not job and (not input_path or not excel_path):
            messagebox.showwarning("Input Missing", "Please select an Excel file and a folder/files to process.")
            return
        self.update_ui_for_start()
        self.log_message("Starting new processing job...")
        self.start_time = time.time()
        job_info = job or {"excel_path": excel_path, "input_path": input_path, "is_rerun": is_rerun}
        threading.Thread(target=run_processing_job, args=(job_info, self.response_queue, self.cancel_event, self.pause_event), daemon=True).start()

    def process_response_queue(self):
        """Definitive fix for the UI message processing pipeline."""
        try:
            while not self.response_queue.empty():
                msg = self.response_queue.get_nowait()
                msg_type = msg.get("type")

                handlers = {
                    "log": lambda m: self.log_message(m.get("msg", ""), m.get("tag", "info")),
                    "status": self.handle_status,
                    "progress": self.handle_progress,
                    "review_item": self.handle_review_item,
                    "file_complete": self.handle_file_complete,
                    "increment_counter": lambda m: getattr(self, f"count_{m['counter']}", tk.IntVar()).set(getattr(self, f"count_{m['counter']}", tk.IntVar()).get() + 1),
                    "result_path": lambda m: setattr(self, "result_file_path", m.get("path")),
                    "enable_open_result": lambda m: self.open_result_btn.config(state=tk.NORMAL),
                    "finish": lambda m: self.update_ui_for_finish(m.get("status", "Complete")),
                }
                if handler := handlers.get(msg_type):
                    handler(msg)
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_response_queue)

    def handle_status(self, msg):
        self.status_current_file.set(msg.get("msg", ""))
        if "led" in msg:
            self.set_led(msg["led"])

    def handle_progress(self, msg):
        self.total_files = msg.get("total", self.total_files)
        if self.total_files > 0:
            self.progress_value.set((msg.get("current", 0) / self.total_files) * 100)
        self._update_time_remaining()

    def handle_review_item(self, msg):
        data = msg.get("data", {})
        self.reviewable_files.append(data)
        self.review_tree.insert("", "end", values=(data.get("filename", ""), data.get("reason", "")))
        
    def handle_file_complete(self, msg):
        status = msg.get("status")
        if status == "Success": self.count_pass.set(self.count_pass.get() + 1)
        elif status == "Needs Review": self.count_review.set(self.count_review.get() + 1)
        else: self.count_fail.set(self.count_fail.get() + 1)

    def update_ui_for_start(self):
        self.is_processing, self.is_paused = True, False
        self.cancel_event.clear(); self.pause_event.clear()
        self.reviewable_files.clear()
        self.review_tree.delete(*self.review_tree.get_children())
        for var in [self.count_pass, self.count_fail, self.count_review, self.count_ocr]: var.set(0)
        self.process_btn.config(state=tk.DISABLED); self.rerun_btn.config(state=tk.DISABLED)
        self.open_result_btn.config(state=tk.DISABLED); self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL); self.progress_value.set(0)
        self.set_led("Processing")

    def update_ui_for_finish(self, status):
        self.is_processing, self.is_paused = False, False
        self.start_time = None
        self._update_time_remaining()
        self.process_btn.config(state=tk.NORMAL)
        if self.reviewable_files: self.rerun_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED); self.stop_btn.config(state=tk.DISABLED)
        self.set_led("Complete" if status == "Complete" else "Error")

    def log_message(self, message, level="info"):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def _update_time_remaining(self):
        if not self.start_time or not self.is_processing or self.total_files == 0:
            self.time_remaining_var.set(""); return
        processed_count = (self.progress_value.get() / 100.0) * self.total_files
        if processed_count > 0:
            elapsed_time = time.time() - self.start_time
            time_per_file = elapsed_time / processed_count
            remaining_files = self.total_files - processed_count
            remaining_seconds = int(time_per_file * remaining_files)
            if remaining_seconds > 1:
                mins, secs = divmod(remaining_seconds, 60)
                self.time_remaining_var.set(f"~{mins}m {secs:02d}s left")
                return
        self.time_remaining_var.set("")

    def set_led(self, status):
        style_name = f"{status}.Status.TFrame"
        led_style_name = f"{status}.LED.TLabel"
        text_style_name = f"{status}.Status.TLabel"
        self.status_frame.configure(style=style_name)
        self.led_label.configure(style=led_style_name)
        if hasattr(self, 'status_text_label'):
            self.status_text_label.configure(style=text_style_name)

    def on_closing(self):
        if self.is_processing and messagebox.askyesno("Exit Confirmation", "A job is currently running. Are you sure you want to exit?"):
            self.cancel_event.set()
            cleanup_temp_files()
            self.destroy()
        elif not self.is_processing:
            cleanup_temp_files()
            self.destroy()

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)

    def browse_excel(self):
        path = filedialog.askopenfilename(title="Select Excel Template", filetypes=[("Excel Files", "*.xlsx *.xlsm")])
        if path: self.selected_excel.set(path)

    def browse_folder(self):
        path = filedialog.askdirectory(title="Select Folder with PDFs")
        if path:
            self.selected_folder.set(path); self.selected_files_list.clear()
            count = len(list(Path(path).glob("*.pdf")))
            self.files_label.config(text=f"{count} PDFs in folder")

    def browse_files(self):
        paths = filedialog.askopenfilenames(title="Select PDF Files", filetypes=[("PDF Files", "*.pdf")])
        if paths:
            self.selected_files_list = list(paths); self.selected_folder.set("")
            self.files_label.config(text=f"{len(paths)} files selected")

    def toggle_pause(self):
        if not self.is_processing: return
        self.is_paused = not self.is_paused
        self.pause_event.set() if self.is_paused else self.pause_event.clear()
        self.set_led("Paused" if self.is_paused else "Processing")

    def stop_processing(self):
        if self.is_processing: self.cancel_event.set()

    def open_result(self):
        if self.result_file_path: open_file(self.result_file_path)

    def open_pattern_manager(self):
        ReviewWindow(self, "MODEL_PATTERNS", "Model Patterns", None)

    def open_review_for_selected_file(self, event=None):
        """Definitive fix for the review process initiator."""
        selection = self.review_tree.selection()
        if not selection: return
        
        filename = self.review_tree.item(selection[0], "values")[0]
        review_info = next((f for f in self.reviewable_files if f["filename"] == filename), None)
        
        if not review_info:
            messagebox.showerror("Error", f"Could not find review data for '{filename}'.")
            return
            
        # --- DEFINITIVE FIX: Read the text from the provided path ---
        txt_path = Path(review_info.get("txt_path", ""))
        if txt_path.exists():
            review_info['text'] = txt_path.read_text(encoding='utf-8')
        else:
            review_info['text'] = "Error: Could not find the extracted text file for review."
            self.log_message(f"ERROR: Review text file not found at {txt_path}", "error")

        ReviewWindow(self, "MODEL_PATTERNS", "Model Patterns", review_info)
            
    def rerun_flagged_job(self):
        if not self.reviewable_files:
            messagebox.showinfo("No Files", "There are no files flagged for re-run.")
            return
        if not self.result_file_path:
            messagebox.showerror("Error", "The previous result file path is not available for re-run. Please run a full job first.")
            return
        files_to_rerun = [item["pdf_path"] for item in self.reviewable_files]
        self.log_message(f"Re-running {len(files_to_rerun)} flagged files...")
        self.start_processing(job={"excel_path": self.result_file_path, "input_path": files_to_rerun, "is_rerun": True})

if __name__ == '__main__':
    messagebox.showinfo("Launcher", "This script is not meant to be run directly.\nPlease use the 'run.py' script to launch the application.")
