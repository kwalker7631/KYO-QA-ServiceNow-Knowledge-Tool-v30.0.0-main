# kyo_review_tool.py - Definitive fix with an improved workflow.
# Now automatically highlights pattern matches for instant feedback.

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import re
from pathlib import Path
import importlib

# Local Imports
try:
    import custom_patterns
except ImportError:
    from types import ModuleType
    custom_patterns = ModuleType("custom_patterns")
    custom_patterns.MODEL_PATTERNS = []; custom_patterns.QA_NUMBER_PATTERNS = []

class ReviewWindow(tk.Toplevel):
    def __init__(self, parent, pattern_type, title, review_info=None):
        super().__init__(parent)
        self.parent = parent
        self.pattern_type = pattern_type
        
        self.title(f"Manage & Test Patterns: {title}")
        self.geometry("1100x750")
        self.transient(parent); self.grab_set()

        self._create_widgets()
        self.load_patterns()

        if review_info and review_info.get('text'):
            self.file_info_label.config(text=f"File: {review_info.get('filename', 'N/A')}")
            self.document_text.config(state=tk.NORMAL)
            self.document_text.delete('1.0', tk.END)
            self.document_text.insert('1.0', review_info['text'])
            self.document_text.config(state=tk.DISABLED)
            self.status_label.config(text=f"Issue: {review_info.get('reason', 'N/A')}", foreground="red")

    def _create_widgets(self):
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        left_frame = ttk.Frame(main_pane, width=350); main_pane.add(left_frame, weight=1)
        right_frame = ttk.Frame(main_pane); main_pane.add(right_frame, weight=3)
        
        left_frame.rowconfigure(1, weight=1); left_frame.columnconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1); right_frame.rowconfigure(1, weight=1)

        ttk.Label(left_frame, text="Custom Model Patterns", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, pady=5, sticky='w')
        self.pattern_listbox = tk.Listbox(left_frame, selectmode=tk.SINGLE, exportselection=False, font=("Consolas", 10))
        self.pattern_listbox.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.pattern_listbox.bind("<<ListboxSelect>>", self.on_pattern_select)

        details_frame = ttk.LabelFrame(right_frame, text="Document Content & Error Details")
        details_frame.grid(row=0, column=0, sticky="ew", pady=5)
        self.file_info_label = ttk.Label(details_frame, text="File: N/A"); self.file_info_label.pack(anchor="w", padx=5)
        self.status_label = ttk.Label(details_frame, text="Status: Ready"); self.status_label.pack(anchor="w", padx=5)
        
        self.document_text = scrolledtext.ScrolledText(right_frame, height=15, wrap=tk.WORD, state=tk.DISABLED, font=("Segoe UI", 9))
        self.document_text.grid(row=1, column=0, sticky="nsew", pady=5)
        self.document_text.tag_configure("highlight", background="yellow", foreground="black")

        editor_frame = ttk.LabelFrame(right_frame, text="Test & Edit Pattern")
        editor_frame.grid(row=2, column=0, sticky="ew", pady=5)
        editor_frame.columnconfigure(0, weight=1)
        self.pattern_entry = ttk.Entry(editor_frame, font=("Consolas", 10))
        self.pattern_entry.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        self.pattern_entry.bind("<KeyRelease>", self.test_and_highlight_pattern)
        
        button_frame = ttk.Frame(editor_frame)
        button_frame.grid(row=1, column=0, columnspan=3, sticky='ew')
        ttk.Button(button_frame, text="Suggest from Highlight", command=self.suggest_from_highlight).pack(side=tk.LEFT, padx=5)
        self.update_btn = ttk.Button(button_frame, text="Update In List", command=self.update_pattern_in_list, state=tk.DISABLED)
        self.update_btn.pack(side=tk.RIGHT, padx=5)

        bottom_frame = ttk.Frame(self); bottom_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(bottom_frame, text="Add New Pattern to List", command=self.add_new_pattern).pack(side=tk.LEFT)
        self.remove_btn = ttk.Button(bottom_frame, text="Remove Selected from List", command=self.remove_selected_pattern, state=tk.DISABLED)
        self.remove_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="Save and Close", command=self.save_all_patterns, style="Red.TButton").pack(side=tk.RIGHT)

    def load_patterns(self):
        self.pattern_listbox.delete(0, tk.END)
        try:
            importlib.reload(custom_patterns)
            patterns = getattr(custom_patterns, self.pattern_type, [])
            for p in patterns: self.pattern_listbox.insert(tk.END, p)
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load patterns: {e}", parent=self)

    def on_pattern_select(self, event=None):
        if selection := self.pattern_listbox.curselection():
            self.pattern_entry.delete(0, tk.END)
            self.pattern_entry.insert(0, self.pattern_listbox.get(selection[0]))
            self.update_btn.config(state=tk.NORMAL)
            self.remove_btn.config(state=tk.NORMAL)
            self.test_and_highlight_pattern()

    def suggest_from_highlight(self):
        try:
            selected_text = self.document_text.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
            if not selected_text: return
            pattern = re.escape(selected_text)
            pattern = re.sub(r'(\d+)', r'\\d+', pattern)
            final_pattern = f"\\b{pattern}\\b"
            self.pattern_entry.delete(0, tk.END)
            self.pattern_entry.insert(0, final_pattern)
            self.test_and_highlight_pattern()
        except tk.TclError:
            messagebox.showwarning("No Selection", "Please highlight text to suggest a pattern.", parent=self)

    def test_and_highlight_pattern(self, event=None):
        """IMPROVEMENT: Automatically highlights all matches in the text."""
        self.document_text.tag_remove("highlight", "1.0", tk.END)
        pattern = self.pattern_entry.get()
        if not pattern: return
        
        try:
            re.compile(pattern)
        except re.error:
            return # Don't highlight on invalid regex

        text = self.document_text.get("1.0", tk.END)
        for match in re.finditer(pattern, text, re.IGNORECASE):
            start, end = match.span()
            self.document_text.tag_add("highlight", f"1.0 + {start}c", f"1.0 + {end}c")

    def add_new_pattern(self):
        if pattern := self.pattern_entry.get():
            self.pattern_listbox.insert(tk.END, pattern)
            self.pattern_entry.delete(0, tk.END)

    def update_pattern_in_list(self):
        if selection := self.pattern_listbox.curselection():
            if new_pattern := self.pattern_entry.get():
                self.pattern_listbox.delete(selection[0])
                self.pattern_listbox.insert(selection[0], new_pattern)

    def remove_selected_pattern(self):
        if selection := self.pattern_listbox.curselection():
            self.pattern_listbox.delete(selection[0])
            self.pattern_entry.delete(0, tk.END)
            self.update_btn.config(state=tk.DISABLED)
            self.remove_btn.config(state=tk.DISABLED)

    def save_all_patterns(self):
        patterns = self.pattern_listbox.get(0, tk.END)
        all_patterns_data = {}
        try:
            importlib.reload(custom_patterns)
            if hasattr(custom_patterns, "MODEL_PATTERNS"): all_patterns_data["MODEL_PATTERNS"] = custom_patterns.MODEL_PATTERNS
            if hasattr(custom_patterns, "QA_NUMBER_PATTERNS"): all_patterns_data["QA_NUMBER_PATTERNS"] = custom_patterns.QA_NUMBER_PATTERNS
        except Exception: pass
        all_patterns_data[self.pattern_type] = list(patterns)

        file_content = "# custom_patterns.py\n# This file is auto-generated.\n\n"
        for key, value in all_patterns_data.items():
            file_content += f"{key} = [\n"
            for p in value: file_content += f"    {repr(p)},\n"
            file_content += "]\n\n"

        try:
            Path("custom_patterns.py").write_text(file_content, encoding="utf-8")
            messagebox.showinfo("Success", "Patterns saved successfully.", parent=self)
            self.parent.log_message("Custom patterns updated. Re-run flagged items to apply changes.", "info")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save patterns: {e}", parent=self)
