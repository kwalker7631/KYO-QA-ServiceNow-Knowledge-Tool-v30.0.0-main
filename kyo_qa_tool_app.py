# kyo_qa_tool_app.py - Enhanced with auto icon generation and better error handling
# Updated: 2024-07-08 - Added auto icon generation, enhanced error reporting, better counters
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
    create_process_controls, create_status_and_log_section
)

logger = logging_utils.setup_logger("app")

def check_and_create_icons():
    """Auto-generate icons if they don't exist."""
    assets_dir = Path("assets")
    
    # List of required icons
    required_icons = [
        "start.png", "pause.png", "stop.png", "rerun.png", 
        "open.png", "browse.png", "patterns.png", "exit.png", "fullscreen.png"
    ]
    
    # Check if assets folder exists and has all icons
    if assets_dir.exists():
        missing_icons = [icon for icon in required_icons if not (assets_dir / icon).exists()]
        if not missing_icons:
            return True
        else:
            print(f"⚠️ Missing {len(missing_icons)} icons: {', '.join(missing_icons)}")
    else:
        print("📁 Assets folder not found")
        missing_icons = required_icons
    
    # Create missing icons
    print("🎨 Creating missing icons...")
    return create_simple_icons_auto()

def create_simple_icons_auto():
    """Create simple icons automatically without user interaction."""
    try:
        from PIL import Image, ImageDraw
        print("📦 PIL found, creating quality icons...")
    except ImportError:
        try:
            print("📦 Installing PIL for icon generation...")
            import subprocess
            import sys
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Pillow'], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            from PIL import Image, ImageDraw
            print("✅ PIL installed successfully")
        except Exception as e:
            print(f"⚠️ Could not install PIL: {e}")
            return create_minimal_icons()
    
    # Create assets folder
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # Icon definitions
    icons = {
        "start.png": {"color": (40, 167, 69), "shape": "triangle"},
        "pause.png": {"color": (255, 193, 7), "shape": "bars"},
        "stop.png": {"color": (220, 53, 69), "shape": "square"},
        "rerun.png": {"color": (0, 123, 255), "shape": "circle"},
        "open.png": {"color": (111, 66, 193), "shape": "diamond"},
        "browse.png": {"color": (23, 162, 184), "shape": "folder"},
        "patterns.png": {"color": (253, 126, 20), "shape": "grid"},
        "exit.png": {"color": (108, 117, 125), "shape": "x"},
        "fullscreen.png": {"color": (32, 201, 151), "shape": "corners"}
    }
    
    success_count = 0
    
    for filename, config in icons.items():
        try:
            # Create 16x16 image with transparent background
            img = Image.new('RGBA', (16, 16), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            color = config["color"]
            shape = config["shape"]
            
            # Draw shapes
            if shape == "triangle":  # Start/Play
                draw.polygon([(3, 3), (3, 13), (13, 8)], fill=color)
            elif shape == "bars":  # Pause
                draw.rectangle([4, 3, 6, 13], fill=color)
                draw.rectangle([10, 3, 12, 13], fill=color)
            elif shape == "square":  # Stop
                draw.rectangle([4, 4, 12, 12], fill=color)
            elif shape == "circle":  # Rerun/Refresh
                draw.ellipse([2, 2, 14, 14], outline=color, width=2)
                draw.polygon([(12, 4), (12, 8), (14, 6)], fill=color)
            elif shape == "diamond":  # Open/File
                draw.polygon([(8, 2), (13, 7), (8, 14), (3, 7)], outline=color, width=2)
                draw.line([(6, 5), (10, 5)], fill=color, width=1)
                draw.line([(6, 8), (10, 8)], fill=color, width=1)
            elif shape == "folder":  # Browse
                draw.rectangle([2, 6, 14, 13], fill=color)
                draw.polygon([(2, 6), (2, 4), (6, 4), (8, 6)], fill=color)
            elif shape == "grid":  # Patterns
                for i in range(3):
                    for j in range(3):
                        x = 3 + i * 4
                        y = 3 + j * 4
                        draw.rectangle([x, y, x+2, y+2], fill=color)
            elif shape == "x":  # Exit
                draw.line([(4, 4), (12, 12)], fill=color, width=2)
                draw.line([(12, 4), (4, 12)], fill=color, width=2)
            elif shape == "corners":  # Fullscreen
                # Four corner brackets
                draw.line([(2, 2), (2, 5)], fill=color, width=2)
                draw.line([(2, 2), (5, 2)], fill=color, width=2)
                draw.line([(14, 2), (14, 5)], fill=color, width=2)
                draw.line([(14, 2), (11, 2)], fill=color, width=2)
                draw.line([(2, 14), (2, 11)], fill=color, width=2)
                draw.line([(2, 14), (5, 14)], fill=color, width=2)
                draw.line([(14, 14), (14, 11)], fill=color, width=2)
                draw.line([(14, 14), (11, 14)], fill=color, width=2)
            
            # Save the image
            file_path = assets_dir / filename
            img.save(file_path, 'PNG')
            success_count += 1
            
        except Exception as e:
            print(f"⚠️ Failed to create {filename}: {e}")
            return create_minimal_icons()
    
    if success_count == len(icons):
        print(f"✅ Created {success_count} quality icons")
        return True
    else:
        return create_minimal_icons()

def create_minimal_icons():
    """Create minimal valid PNG files as fallback."""
    print("🔧 Creating minimal icons as fallback...")
    
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # Minimal valid 16x16 PNG file data
    minimal_png = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
        0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x10,
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0xF3, 0xFF, 0x61,
        0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41, 0x54,
        0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00, 0x05, 0x00, 0x01,
        0x0D, 0x0A, 0x2D, 0xB4, 0x00, 0x00, 0x00, 0x00,
        0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82
    ])
    
    icon_files = [
        "start.png", "pause.png", "stop.png", "rerun.png", 
        "open.png", "browse.png", "patterns.png", "exit.png", "fullscreen.png"
    ]
    
    success_count = 0
    for filename in icon_files:
        try:
            file_path = assets_dir / filename
            with open(file_path, 'wb') as f:
                f.write(minimal_png)
            success_count += 1
        except Exception as e:
            print(f"❌ Failed to create {filename}: {e}")
    
    if success_count == len(icon_files):
        print(f"✅ Created {success_count} minimal icons")
        return True
    else:
        print(f"❌ Only created {success_count}/{len(icon_files)} icons")
        return False

class KyoQAToolApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Initialize counters for different processing outcomes
        self.count_pass = tk.IntVar(value=0)
        self.count_fail = tk.IntVar(value=0)
        self.count_review = tk.IntVar(value=0)
        self.count_ocr = tk.IntVar(value=0)
        self.count_protected = tk.IntVar(value=0)
        self.count_corrupted = tk.IntVar(value=0)
        self.count_ocr_failed = tk.IntVar(value=0)
        self.count_no_text = tk.IntVar(value=0)
        
        # Backward compatibility
        self.count_needs_review = self.count_review

        # Processing state variables
        self.is_processing = False
        self.is_paused = False
        self.result_file_path = None
        self.reviewable_files = []
        self.start_time = None
        self.last_run_info = {}
        self.response_queue = queue.Queue()
        self.cancel_event = threading.Event()
        self.pause_event = threading.Event()
        
        # Input/Output variables
        self.selected_folder = tk.StringVar()
        self.selected_excel = tk.StringVar()
        self.selected_files_list = []
        
        # UI state variables
        self.status_current_file = tk.StringVar(value="Ready to process")
        self.progress_value = tk.DoubleVar(value=0)
        self.time_remaining_var = tk.StringVar(value="")
        self.led_status_var = tk.StringVar(value="●")
        self.is_fullscreen = True

        # Auto-generate icons if needed
        self._ensure_icons_available()

        # Load icons with error handling
        self.start_icon = self._load_icon("start.png")
        self.pause_icon = self._load_icon("pause.png")
        self.stop_icon = self._load_icon("stop.png")
        self.rerun_icon = self._load_icon("rerun.png")
        self.open_icon = self._load_icon("open.png")
        self.browse_icon = self._load_icon("browse.png")
        self.patterns_icon = self._load_icon("patterns.png")
        self.exit_icon = self._load_icon("exit.png")
        self.fullscreen_icon = self._load_icon("fullscreen.png")

        # Setup UI
        self.style = ttk.Style(self)
        self._setup_window_styles()
        self._create_widgets()

        # Initialize application
        ensure_folders()
        self.attributes("-fullscreen", self.is_fullscreen)
        self.bind_all("<Escape>", self.toggle_fullscreen)
        self.after(100, self.process_response_queue)
        self.set_led("Ready")

    def _ensure_icons_available(self):
        """Auto-generate icons if they don't exist."""
        try:
            icons_ready = check_and_create_icons()
            if icons_ready:
                print("✅ Icons ready for application")
            else:
                print("⚠️ Some icons may be missing")
        except Exception as e:
            print(f"⚠️ Auto icon generation failed: {e}")

    def _load_icon(self, filename):
        """Load a PhotoImage icon, returning None if the file is not found."""
        try:
            return tk.PhotoImage(file=ASSETS_DIR / filename)
        except tk.TclError:
            # No longer print warning since we auto-generate icons
            return None

    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode."""
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)
        return "break"

    def _setup_window_styles(self):
        """Setup window appearance and styles."""
        self.title(f"Kyocera QA Knowledge Tool v{VERSION}")
        self.geometry("1200x900")
        self.minsize(1000, 800)

        # Try to set application icon
        try:
            icon_path = Path(__file__).parent / "icon.ico"
            if icon_path.exists():
                self.iconbitmap(icon_path)
        except:
            pass
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.configure(bg=BRAND_COLORS["background"])
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Configure TTK styles
        self.style.theme_use("clam")
        self.style.configure("TFrame", background=BRAND_COLORS["background"])
        self.style.configure("Header.TFrame", background=BRAND_COLORS["frame_background"])
        self.style.configure("TLabel", background=BRAND_COLORS["background"], font=("Segoe UI", 10))
        self.style.configure("TLabelFrame", background=BRAND_COLORS["background"], borderwidth=1, relief="groove")
        self.style.configure("TLabelFrame.Label", background=BRAND_COLORS["background"], font=("Segoe UI", 11, "bold"))
        self.style.configure("Blue.Horizontal.TProgressbar", background=BRAND_COLORS["accent_blue"])
        self.style.configure("Treeview", font=("Segoe UI", 9), fieldbackground=BRAND_COLORS["frame_background"])
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        # Entry styles
        self.style.configure("TEntry", fieldbackground=BRAND_COLORS["frame_background"], borderwidth=1, relief="solid")
        self.style.map("TEntry",
            bordercolor=[("focus", BRAND_COLORS["highlight_blue"]), ('!focus', 'grey')],
            lightcolor=[("focus", BRAND_COLORS["highlight_blue"])],
            darkcolor=[("focus", BRAND_COLORS["highlight_blue"])]
        )

        # Log text tags for colored output
        self.log_text_tags = {
            "info": ("#00529B", "white"), 
            "warning": ("#9F6000", "#FEEFB3"),
            "error": ("#D8000C", "#FFD2D2"), 
            "success": ("#4F8A10", "#DFF2BF")
        }

        # Button styles
        self.style.configure("TButton", font=("Segoe UI", 10), padding=6, relief="raised")
        self.style.map("TButton", 
            background=[('active', '#e0e0e0'), ('!active', '#f0f0f0')], 
            foreground=[('active', 'black'), ('!active', 'black')]
        )
        self.style.configure("Red.TButton", font=("Segoe UI", 12, "bold"), foreground="white")
        self.style.map("Red.TButton", 
            background=[('active', '#A81F14'), ('!active', BRAND_COLORS["kyocera_red"])], 
            foreground=[('active', 'white'), ('!active', 'white')]
        )

        # Status frame styles
        self.style.configure("Status.TFrame", background=BRAND_COLORS["status_default_bg"], relief="sunken", borderwidth=1)
        self.style.configure("Status.TLabel", font=("Segoe UI", 10))
        self.style.configure("Status.Header.TLabel", font=("Segoe UI", 10, "bold"))
        self.style.configure("LED.TLabel", font=("Segoe UI", 16))
        
        # Counter label styles
        self.style.configure("Count.Green.TLabel", foreground=BRAND_COLORS["success_green"], font=("Segoe UI", 10, "bold"))
        self.style.configure("Count.Red.TLabel", foreground=BRAND_COLORS["fail_red"], font=("Segoe UI", 10, "bold"))
        self.style.configure("Count.Orange.TLabel", foreground=BRAND_COLORS["warning_orange"], font=("Segoe UI", 10, "bold"))
        self.style.configure("Count.Blue.TLabel", foreground=BRAND_COLORS["accent_blue"], font=("Segoe UI", 10, "bold"))
        self.style.configure("Count.Gray.TLabel", foreground="gray", font=("Segoe UI", 10, "bold"))
        self.style.configure("Count.Purple.TLabel", foreground="purple", font=("Segoe UI", 10, "bold"))

    def _create_widgets(self):
        """Create and layout all GUI widgets."""
        create_main_header(self, VERSION, BRAND_COLORS)
        
        main_frame = ttk.Frame(self, padding=20)
        main_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        create_io_section(main_frame, self)
        create_process_controls(main_frame, self)
        self._create_enhanced_status_section(main_frame)
        
        # Configure log text tags
        self.log_text.tag_configure("timestamp", foreground="grey")
        for tag, (fg, bg) in self.log_text_tags.items():
            self.log_text.tag_configure(f"{tag}_fg", foreground=fg)
            self.log_text.tag_configure(f"{tag}_line", background=bg, selectbackground=BRAND_COLORS["highlight_blue"])

    def _create_enhanced_status_section(self, parent):
        """Create enhanced status section with additional counters."""
        stat = ttk.LabelFrame(parent, text="3. Status & Logs", padding=10)
        stat.grid(row=2, column=0, sticky="nsew", pady=5)
        stat.columnconfigure(0, weight=1)
        stat.rowconfigure(4, weight=1)

        # Status frame
        self.status_frame = ttk.Frame(stat, style="Status.TFrame", padding=5)
        self.status_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        self.status_frame.columnconfigure(1, weight=1)
        self.led_label = ttk.Label(self.status_frame, textvariable=self.led_status_var, style="LED.TLabel")
        self.led_label.grid(row=0, column=0, sticky="w")
        ttk.Label(self.status_frame, textvariable=self.status_current_file, style="Status.TLabel").grid(row=0, column=1, sticky="ew", padx=5)

        # Progress frame
        prog_frame = ttk.Frame(stat)
        prog_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(5,10))
        prog_frame.columnconfigure(0, weight=1)
        self.progress_bar = ttk.Progressbar(prog_frame, variable=self.progress_value, style="Blue.Horizontal.TProgressbar")
        self.progress_bar.grid(row=0, column=0, sticky="ew")
        ttk.Label(prog_frame, textvariable=self.time_remaining_var).grid(row=0, column=1, sticky="e", padx=10)

        # Enhanced counters frame
        sum_frame = ttk.Frame(stat)
        sum_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=2)
        
        # Primary counters (first row)
        counters_row1 = [
            ("Pass:", self.count_pass, "Green"), 
            ("Fail:", self.count_fail, "Red"), 
            ("Review:", self.count_review, "Orange"), 
            ("OCR:", self.count_ocr, "Blue")
        ]
        
        for i, (text, var, color) in enumerate(counters_row1):
            ttk.Label(sum_frame, text=text, style="Status.Header.TLabel").pack(side="left", padx=(15, 2))
            ttk.Label(sum_frame, textvariable=var, style=f"Count.{color}.TLabel").pack(side="left")

        # Secondary counters (second row)
        sum_frame2 = ttk.Frame(stat)
        sum_frame2.grid(row=3, column=0, sticky="ew", padx=5, pady=2)
        
        counters_row2 = [
            ("Protected:", self.count_protected, "Gray"),
            ("Corrupted:", self.count_corrupted, "Purple"),
            ("OCR Failed:", self.count_ocr_failed, "Red"),
            ("No Text:", self.count_no_text, "Orange")
        ]
        
        for i, (text, var, color) in enumerate(counters_row2):
            ttk.Label(sum_frame2, text=text, style="Status.Header.TLabel").pack(side="left", padx=(15, 2))
            ttk.Label(sum_frame2, textvariable=var, style=f"Count.{color}.TLabel").pack(side="left")

        # Enhanced review frame
        rev_frame = ttk.Frame(stat)
        rev_frame.grid(row=4, column=0, sticky="nsew", padx=5, pady=2)
        rev_frame.rowconfigure(1, weight=1)
        rev_frame.columnconfigure(0, weight=1)
        
        ttk.Label(rev_frame, text="Files to Review:", style="Status.Header.TLabel").grid(row=0, column=0, sticky="w")
        self.review_file_btn = ttk.Button(rev_frame, text="Review Selected", command=self.open_review_for_selected_file, state=tk.DISABLED)
        self.review_file_btn.grid(row=0, column=1, sticky="e")
        
        # Enhanced review tree with failure reason column
        self.review_tree = ttk.Treeview(rev_frame, columns=('file', 'reason'), show='headings', height=4)
        self.review_tree.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=2)
        self.review_tree.heading('file', text='File Name')
        self.review_tree.heading('reason', text='Failure Reason')
        self.review_tree.column('file', width=200, minwidth=150)
        self.review_tree.column('reason', width=400, minwidth=200)
        self.review_tree.bind("<<TreeviewSelect>>", lambda e: self.review_file_btn.config(state=tk.NORMAL if self.review_tree.selection() else tk.DISABLED))

        # Scrollbar for review tree
        rev_scrollbar = ttk.Scrollbar(rev_frame, orient="vertical", command=self.review_tree.yview)
        rev_scrollbar.grid(row=1, column=2, sticky="ns", pady=2)
        self.review_tree.config(yscrollcommand=rev_scrollbar.set)

        # Log frame
        log_frame = ttk.Frame(stat)
        log_frame.grid(row=5, column=0, sticky="nsew", padx=5, pady=(10,2))
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD, state=tk.DISABLED, relief="solid", borderwidth=1, font=("Consolas", 9))
        self.log_text.grid(row=0, column=0, sticky="nsew")
        
        log_scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        log_scroll.grid(row=0, column=1, sticky="ns")
        self.log_text.config(yscrollcommand=log_scroll.set)

    def log_message(self, message, level="info"):
        """Add a timestamped message to the log display."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        
        start_index = self.log_text.index(tk.END)
        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.log_text.insert(tk.END, f"{message}\n", f"{level}_fg")
        end_index = self.log_text.index(tk.END)
        
        if level in ["warning", "error", "success"]:
             self.log_text.tag_add(f"{level}_line", start_index, end_index)
             
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_processing(self, job=None, is_rerun=False):
        """Start processing job with validation."""
        if self.is_processing: 
            return
            
        # Validate inputs
        if not job:
            input_path = self.selected_folder.get() or self.selected_files_list
            if not input_path:
                messagebox.showwarning("Input Missing", "Please select files or a folder.")
                return
                
            excel_path = self.selected_excel.get()
            if not excel_path:
                messagebox.showwarning("Input Missing", "Please select a base Excel file.")
                return
                
            job = {"excel_path": excel_path, "input_path": input_path}
            self.last_run_info = job
            
        job["is_rerun"] = is_rerun
        
        # Update UI and start processing
        self.update_ui_for_start()
        self.log_message("Starting processing job with enhanced data harvesting...", "info")
        self.start_time = time.time()
        
        # Start processing thread
        threading.Thread(
            target=run_processing_job, 
            args=(job, self.response_queue, self.cancel_event, self.pause_event), 
            daemon=True
        ).start()

    def rerun_flagged_job(self):
        """Re-run files that need review."""
        if not self.reviewable_files:
            messagebox.showwarning("No Files", "No files need re-running.")
            return
            
        if not self.result_file_path:
            messagebox.showerror("Error", "Previous result file not found.")
            return
            
        files = [item["pdf_path"] for item in self.reviewable_files]
        self.log_message(f"Re-running {len(files)} flagged files with improved harvesting...", "info")
        self.start_processing(
            job={"excel_path": self.result_file_path, "input_path": files}, 
            is_rerun=True
        )

    def browse_excel(self):
        """Browse for Excel template file."""
        path = filedialog.askopenfilename(
            title="Select Excel Template", 
            filetypes=[("Excel Files", "*.xlsx *.xlsm"), ("All Files", "*.*")]
        )
        if path:
            self.selected_excel.set(path)
            self.log_message(f"Excel selected: {Path(path).name}", "info")

    def browse_folder(self):
        """Browse for folder containing PDFs."""
        path = filedialog.askdirectory(title="Select Folder with PDFs")
        if path:
            self.selected_folder.set(path)
            self.selected_files_list = []
            pdf_count = len(list(Path(path).glob("*.pdf")))
            self.files_label.config(text=f"{pdf_count} PDFs in folder")
            self.log_message(f"Folder selected: {path} ({pdf_count} PDFs)", "info")

    def browse_files(self):
        """Browse for individual PDF files."""
        paths = filedialog.askopenfilenames(
            title="Select PDF Files", 
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if paths:
            self.selected_files_list = list(paths)
            self.selected_folder.set("")
            self.files_label.config(text=f"{len(paths)} files selected")
            self.log_message(f"{len(paths)} PDF files selected", "info")

    def toggle_pause(self):
        """Toggle processing pause state."""
        if not self.is_processing: 
            return
            
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.pause_event.set()
            self.pause_btn.config(text=" Resume")
            self.log_message("Processing paused", "warning")
            self.set_led("Paused")
        else:
            self.pause_event.clear()
            self.pause_btn.config(text=" Pause")
            self.log_message("Processing resumed", "info")
            self.set_led("Processing")

    def stop_processing(self):
        """Stop the current processing job."""
        if not self.is_processing: 
            return
            
        if messagebox.askyesno("Confirm Stop", "Stop the current processing job?"):
            self.cancel_event.set()
            self.log_message("Stopping processing...", "warning")
            self.set_led("Stopping")

    def on_closing(self):
        """Handle application closing."""
        if self.is_processing:
            if not messagebox.askyesno("Exit", "A processing job is running. Are you sure you want to exit?"):
                return

        print("Closing application...")
        self.cancel_event.set()
        cleanup_temp_files()
        self.destroy()

    def open_result(self):
        """Open the result Excel file."""
        if self.result_file_path and Path(self.result_file_path).exists():
            try:
                open_file(self.result_file_path)
                self.log_message(f"Opened result file: {Path(self.result_file_path).name}", "info")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{e}")
        else:
            messagebox.showwarning("Not Found", "Result file not found or has been moved.")

    def open_pattern_manager(self):
        """Open pattern management dialog."""
        dialog = tk.Toplevel(self)
        dialog.title("Select Pattern Type")
        dialog.geometry("300x150")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        x = (self.winfo_screenwidth() // 2) - 150
        y = (self.winfo_screenheight() // 2) - 75
        dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(dialog, text="Which patterns do you want to manage?", font=("Segoe UI", 10)).pack(pady=20)
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def open_review(pattern_name, label):
            dialog.destroy()
            file_info = self.reviewable_files[0] if self.reviewable_files else None
            ReviewWindow(self, pattern_name, label, file_info)
            
        ttk.Button(
            button_frame, 
            text="Model Patterns", 
            command=lambda: open_review("MODEL_PATTERNS", "Model Patterns")
        ).pack(side="left", padx=10)
        
        ttk.Button(
            button_frame, 
            text="QA Patterns", 
            command=lambda: open_review("QA_NUMBER_PATTERNS", "QA Number Patterns")
        ).pack(side="left", padx=10)

    def set_led(self, status):
        """Update LED status indicator with color and background."""
        led_config = {
            "Ready": ("#107C10", BRAND_COLORS["status_default_bg"]),
            "Processing": (BRAND_COLORS["accent_blue"], BRAND_COLORS["status_processing_bg"]),
            "OCR": (BRAND_COLORS["accent_blue"], BRAND_COLORS["status_ocr_bg"]),
            "AI": (BRAND_COLORS["accent_blue"], BRAND_COLORS["status_ai_bg"]),
            "Paused": (BRAND_COLORS["warning_orange"], BRAND_COLORS["status_default_bg"]),
            "Stopping": (BRAND_COLORS["fail_red"], BRAND_COLORS["status_default_bg"]),
            "Error": (BRAND_COLORS["fail_red"], BRAND_COLORS["status_default_bg"]),
            "Complete": ("#107C10", BRAND_COLORS["status_default_bg"]),
            "Queued": ("grey", BRAND_COLORS["status_default_bg"]),
            "Saving": ("#107C10", BRAND_COLORS["status_default_bg"]),
            "Protected": ("orange", BRAND_COLORS["status_default_bg"]),
            "Corrupted": ("purple", BRAND_COLORS["status_default_bg"]),
        }
        
        color, bg_color = led_config.get(status, ("grey", BRAND_COLORS["status_default_bg"]))
        
        self.led_label.config(foreground=color)
        self.status_frame.config(style="Status.TFrame")
        self.style.configure("Status.TFrame", background=bg_color)
        
        for child in self.status_frame.winfo_children():
            child.configure(style="Status.TLabel")
        self.style.configure("Status.TLabel", background=bg_color)

    def update_ui_for_start(self):
        """Update UI state when processing starts."""
        self.is_processing = True
        self.is_paused = False
        self.cancel_event.clear()
        self.pause_event.clear()
        
        # Reset all counters
        counters = [
            self.count_pass, self.count_fail, self.count_review, self.count_ocr,
            self.count_protected, self.count_corrupted, self.count_ocr_failed, self.count_no_text
        ]
        for var in counters:
            var.set(0)
        
        # Clear review items
        self.reviewable_files.clear()
        self.review_tree.delete(*self.review_tree.get_children())
        
        # Update button states
        self.process_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL, text=" Pause")
        self.stop_btn.config(state=tk.NORMAL)
        self.review_btn.config(state=tk.DISABLED)
        self.open_result_btn.config(state=tk.DISABLED)
        self.exit_btn.config(state=tk.DISABLED)
        self.rerun_btn.config(state=tk.DISABLED)
        self.review_file_btn.config(state=tk.DISABLED)
        
        # Reset progress
        self.status_current_file.set("Initializing...")
        self.time_remaining_var.set("Calculating...")
        self.progress_value.set(0)
        self.set_led("Processing")

    def update_ui_for_finish(self, status):
        """Update UI state when processing finishes."""
        self.is_processing = False
        self.is_paused = False
        
        # Update button states
        self.process_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED, text=" Pause")
        self.stop_btn.config(state=tk.DISABLED)
        self.exit_btn.config(state=tk.NORMAL)
        self.review_btn.config(state=tk.NORMAL)
        
        if self.result_file_path: 
            self.open_result_btn.config(state=tk.NORMAL)
        if self.reviewable_files: 
            self.rerun_btn.config(state=tk.NORMAL)
        
        # Update status
        final_status = "Complete" if status == "Complete" else "Error"
        self.status_current_file.set(f"Job {status}")
        self.time_remaining_var.set("Done!")
        self.set_led(final_status)
        self.progress_value.set(100)

    def open_review_for_selected_file(self):
        """Open review window for selected file."""
        selection = self.review_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file to review.")
            return
            
        item_id = selection[0]
        # Get filename from the first column
        filename = self.review_tree.item(item_id, "values")[0]
        
        # Find the review info for this file
        review_info = next((f for f in self.reviewable_files if f['filename'] == filename), None)
        if review_info:
            ReviewWindow(self, "MODEL_PATTERNS", "Model Patterns", review_info)
        else:
            messagebox.showerror("Error", "Could not find review information for the selected file.")

    def update_progress(self, current, total):
        """Update progress bar and time estimation."""
        if total > 0:
            percent = (current / total) * 100
            self.progress_value.set(percent)
            
            if self.start_time and current > 0:
                elapsed = time.time() - self.start_time
                rate = current / elapsed
                remaining = (total - current) / rate if rate > 0 else 0
                
                if remaining > 60: 
                    self.time_remaining_var.set(f"~{int(remaining/60)}m {int(remaining%60)}s left")
                else: 
                    self.time_remaining_var.set(f"~{int(remaining)}s left")

    def process_response_queue(self):
        """Process messages from the processing thread."""
        try:
            while not self.response_queue.empty():
                msg = self.response_queue.get_nowait()
                mtype = msg.get("type")
                
                if mtype == "log":
                    self.log_message(msg.get("msg", ""), msg.get("tag", "info"))
                    
                elif mtype == "status":
                    self.status_current_file.set(msg.get("msg", ""))
                    if "led" in msg: 
                        self.set_led(msg["led"])
                        
                elif mtype == "progress": 
                    self.update_progress(msg.get("current", 0), msg.get("total", 1))
                    
                elif mtype == "increment_counter":
                    counter_name = f"count_{msg.get('counter')}"
                    var = getattr(self, counter_name, None)
                    if var: 
                        var.set(var.get() + 1)
                        
                elif mtype == "file_complete":
                    status = msg.get("status", "").lower().replace(" ", "_")
                    
                    # Map status to counter variables
                    status_mapping = {
                        "pass": "count_pass",
                        "fail": "count_fail", 
                        "needs_review": "count_review",
                        "protected": "count_protected",
                        "corrupted": "count_corrupted",
                        "ocr_failed": "count_ocr_failed",
                        "no_text": "count_no_text"
                    }
                    
                    counter_name = status_mapping.get(status)
                    if counter_name:
                        var = getattr(self, counter_name, None)
                        if var: 
                            var.set(var.get() + 1)
                            
                elif mtype == "review_item":
                    data = msg.get("data", {})
                    self.reviewable_files.append(data)
                    
                    # Insert with both filename and failure reason
                    filename = data.get('filename', 'Unknown')
                    reason = data.get('reason', 'Unknown error')
                    self.review_tree.insert('', 'end', values=(filename, reason))
                    
                elif mtype == "result_path": 
                    self.result_file_path = msg.get("path")
                    
                elif mtype == "finish":
                    status = msg.get("status", "Complete")
                    elapsed = time.time() - self.start_time if self.start_time else 0
                    self.log_message(
                        f"Job finished: {status} (Time: {int(elapsed/60)}m {int(elapsed%60)}s)", 
                        "success" if status == "Complete" else "error"
                    )
                    self.update_ui_for_finish(status)
                    
        except queue.Empty: 
            pass
        except Exception as e: 
            self.log_message(f"Error processing queue: {e}", "error")
        
        # Schedule next queue check
        self.after(100, self.process_response_queue)


if __name__ == "__main__":
    try:
        app = KyoQAToolApp()
        app.mainloop()
    except Exception as e:
        import traceback
        print(f"Failed to start application: {e}\n{traceback.format_exc()}")
        input("Press Enter to exit...")
