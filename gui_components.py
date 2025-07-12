# gui_components.py - Corrected to restore the 'Review Selected' button
# and fix other minor layout issues.

import tkinter as tk
from tkinter import ttk

def create_main_header(parent, version, colors):
    """Creates the main header for the application."""
    header = ttk.Frame(parent, style="Header.TFrame", padding=(10, 10))
    header.grid(row=0, column=0, sticky="ew")
    ttk.Separator(header, orient='horizontal').pack(side="bottom", fill="x")
    ttk.Label(header, text="KYOCERA", foreground=colors["kyocera_red"], font=("Arial Black", 22), background="white").pack(side=tk.LEFT, padx=(10, 0))
    ttk.Label(header, text=f"QA Knowledge Tool v{version}", font=("Segoe UI", 16, "bold"), background="white").pack(side=tk.LEFT, padx=(15, 0))

def create_io_section(parent, app):
    """Creates the input selection section (Excel, PDFs)."""
    io = ttk.LabelFrame(parent, text="1. Select Inputs", padding=10)
    io.grid(row=0, column=0, sticky="ew", pady=5)
    io.columnconfigure(1, weight=1)

    ttk.Label(io, text="Excel to Clone:").grid(row=0, column=0, sticky="w", pady=2, padx=5)
    ttk.Entry(io, textvariable=app.selected_excel).grid(row=0, column=1, sticky="ew", padx=5)
    ttk.Button(io, image=app.browse_icon, text=" Browse...", compound="left", command=app.browse_excel).grid(row=0, column=2, padx=5)

    ttk.Label(io, text="PDFs Folder:").grid(row=1, column=0, sticky="w", pady=2, padx=5)
    ttk.Entry(io, textvariable=app.selected_folder).grid(row=1, column=1, sticky="ew", padx=5)
    ttk.Button(io, image=app.browse_icon, text=" Browse...", compound="left", command=app.browse_folder).grid(row=1, column=2, padx=5)

    app.files_label = ttk.Label(io, text="Or select individual files -->")
    app.files_label.grid(row=2, column=1, sticky="e", padx=5, pady=(5,0))
    ttk.Button(io, image=app.browse_icon, text=" Browse Files...", compound="left", command=app.browse_files).grid(row=2, column=2, padx=5, pady=(5,0))

    app.import_progress_bar = ttk.Progressbar(io, variable=app.import_progress, style="Blue.Horizontal.TProgressbar")
    app.import_progress_bar.grid(row=3, column=0, columnspan=3, sticky="ew", padx=5, pady=(10, 0))

def create_process_controls(parent, app):
    """Creates the main control buttons for processing."""
    ctrl = ttk.LabelFrame(parent, text="2. Process & Manage", padding=10)
    ctrl.grid(row=1, column=0, sticky="ew", pady=5)
    ctrl.columnconfigure((0, 1, 2, 3), weight=1)

    app.process_btn = ttk.Button(ctrl, text=" START", image=app.start_icon, compound="left", command=app.start_processing, style="Red.TButton")
    app.process_btn.grid(row=0, column=0, columnspan=4, sticky="ew", pady=5, ipady=5)

    app.pause_btn = ttk.Button(ctrl, text=" Pause", image=app.pause_icon, compound="left", command=app.toggle_pause, state=tk.DISABLED)
    app.pause_btn.grid(row=1, column=0, sticky="ew", padx=2, pady=2)
    app.stop_btn = ttk.Button(ctrl, text=" Stop", image=app.stop_icon, compound="left", command=app.stop_processing, state=tk.DISABLED)
    app.stop_btn.grid(row=1, column=1, sticky="ew", padx=2, pady=2)
    
    app.rerun_btn = ttk.Button(ctrl, text=" Re-run Flagged", image=app.rerun_icon, compound="left", command=app.rerun_flagged_job, state=tk.DISABLED)
    app.rerun_btn.grid(row=1, column=2, sticky="ew", padx=2, pady=2)
    app.open_result_btn = ttk.Button(ctrl, text=" Open Result", image=app.open_icon, compound="left", command=app.open_result, state=tk.DISABLED)
    app.open_result_btn.grid(row=1, column=3, sticky="ew", padx=2, pady=2)
    
    app.review_btn = ttk.Button(ctrl, text=" Manage Patterns", image=app.patterns_icon, compound="left", command=app.open_pattern_manager)
    app.review_btn.grid(row=2, column=0, columnspan=2, sticky="ew", padx=2, pady=5)
    app.fullscreen_btn = ttk.Button(ctrl, text=" Fullscreen", image=app.fullscreen_icon, compound="left", command=app.toggle_fullscreen)
    app.fullscreen_btn.grid(row=2, column=2, sticky="ew", padx=2, pady=5)
    app.exit_btn = ttk.Button(ctrl, text=" Exit", image=app.exit_icon, compound="left", command=app.on_closing)
    app.exit_btn.grid(row=2, column=3, sticky="ew", padx=2, pady=5)

def create_status_and_log_section(parent, app):
    """Creates the status, counters, review, and log section."""
    stat = ttk.LabelFrame(parent, text="3. Status & Logs", padding=10)
    stat.grid(row=2, column=0, sticky="nsew", pady=5)
    stat.columnconfigure(0, weight=1)
    stat.rowconfigure(4, weight=1) 

    app.status_frame = ttk.Frame(stat, style="Ready.Status.TFrame", padding=5)
    app.status_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
    app.status_frame.columnconfigure(1, weight=1)
    
    app.led_label = ttk.Label(app.status_frame, textvariable=app.led_status_var, style="Ready.LED.TLabel")
    app.led_label.grid(row=0, column=0, sticky="w")
    
    app.status_text_label = ttk.Label(app.status_frame, textvariable=app.status_current_file, style="Ready.Status.TLabel")
    app.status_text_label.grid(row=0, column=1, sticky="ew", padx=5)

    prog_frame = ttk.Frame(stat)
    prog_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(5,10))
    prog_frame.columnconfigure(0, weight=1)
    app.progress_bar = ttk.Progressbar(prog_frame, variable=app.progress_value, style="Blue.Horizontal.TProgressbar")
    app.progress_bar.grid(row=0, column=0, sticky="ew")
    ttk.Label(prog_frame, textvariable=app.time_remaining_var).grid(row=0, column=1, sticky="e", padx=10)

    sum_frame = ttk.Frame(stat)
    sum_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=(5, 10))
    counters = [("Pass:", app.count_pass), ("Fail:", app.count_fail), ("Review:", app.count_review), ("OCR:", app.count_ocr)]
    for i, (text, var) in enumerate(counters):
        sum_frame.columnconfigure(i, weight=1)
        f = ttk.Frame(sum_frame, style="TFrame") 
        f.grid(row=0, column=i, sticky="ew")
        ttk.Label(f, text=text).pack(side="left", padx=(15, 2))
        ttk.Label(f, textvariable=var).pack(side="left")

    # --- FIX: Restore the review button and its associated logic ---
    rev_frame = ttk.LabelFrame(stat, text="Files Flagged for Review")
    rev_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=2)
    rev_frame.rowconfigure(1, weight=1); rev_frame.columnconfigure(0, weight=1)
    
    rev_top_frame = ttk.Frame(rev_frame)
    rev_top_frame.grid(row=0, column=0, sticky="ew")
    ttk.Label(rev_top_frame, text="Select a file to open the review tool:").pack(side="left", padx=5)
    
    # This is the restored button
    app.review_file_btn = ttk.Button(rev_top_frame, text="Review Selected File", command=app.open_review_for_selected_file, state=tk.DISABLED)
    app.review_file_btn.pack(side="right", padx=5)
    
    app.review_tree = ttk.Treeview(rev_frame, columns=('file', 'reason'), show='headings', height=4)
    app.review_tree.grid(row=1, column=0, sticky="nsew", pady=(5,0))
    app.review_tree.heading('file', text='File Name'); app.review_tree.heading('reason', text='Reason for Review')
    app.review_tree.column('file', width=250, anchor='w'); app.review_tree.column('reason', width=400, anchor='w')
    
    # Bind selection to enable the button
    app.review_tree.bind("<<TreeviewSelect>>", lambda e: app.review_file_btn.config(state=tk.NORMAL))
    app.review_tree.bind("<Double-1>", app.open_review_for_selected_file) # Keep double-click for convenience
    
    rev_scroll = ttk.Scrollbar(rev_frame, orient="vertical", command=app.review_tree.yview)
    rev_scroll.grid(row=1, column=1, sticky="ns", pady=(5,0))
    app.review_tree.config(yscrollcommand=rev_scroll.set)

    log_frame = ttk.Frame(stat)
    log_frame.grid(row=4, column=0, sticky="nsew", padx=5, pady=(10,2))
    log_frame.rowconfigure(0, weight=1); log_frame.columnconfigure(0, weight=1)
    app.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD, state=tk.DISABLED, relief="solid", borderwidth=1, font=("Consolas", 9))
    app.log_text.grid(row=0, column=0, sticky="nsew")
    log_scroll = ttk.Scrollbar(log_frame, command=app.log_text.yview)
    log_scroll.grid(row=0, column=1, sticky="ns")
    app.log_text.config(yscrollcommand=log_scroll.set)
