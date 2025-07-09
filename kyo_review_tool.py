# kyo_review_tool.py - Final version with corrected pattern saving logic.
# Updated: 2024-07-09 - Rewrote saving/loading logic to permanently fix pattern corruption.
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import re
from pathlib import Path
import importlib

class ReviewWindow(tk.Toplevel):
    def __init__(self, parent, pattern_type, title, review_info=None):
        super().__init__(parent)
        self.parent = parent
        self.pattern_type = pattern_type
        
        self.title(f"Manage Custom: {title}")
        self.geometry("1000x700")
        self.transient(parent)
        self.grab_set()

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
        # Main layout
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        left_frame = ttk.Frame(main_pane, width=300); main_pane.add(left_frame, weight=1)
        right_frame = ttk.Frame(main_pane); main_pane.add(right_frame, weight=3)
        right_frame.columnconfigure(0, weight=1); right_frame.rowconfigure(1, weight=1)

        # Left: Pattern List
        ttk.Label(left_frame, text="Model Patterns", font=("Segoe UI", 12, "bold")).pack(pady=5)
        self.pattern_listbox = tk.Listbox(left_frame, selectmode=tk.SINGLE, exportselection=False, font=("Consolas", 10))
        self.pattern_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.pattern_listbox.bind("<<ListboxSelect>>", self.on_pattern_select)

        # Right Top: Document Info
        details_frame = ttk.LabelFrame(right_frame, text="Document Content & Error Details")
        details_frame.grid(row=0, column=0, sticky="ew", pady=5)
        self.file_info_label = ttk.Label(details_frame, text="File: N/A"); self.file_info_label.pack(anchor="w", padx=5)
        self.status_label = ttk.Label(details_frame, text="Status: Ready"); self.status_label.pack(anchor="w", padx=5)
        
        # Right Middle: Document Text
        self.document_text = scrolledtext.ScrolledText(right_frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
        self.document_text.grid(row=1, column=0, sticky="nsew", pady=5)

        # Right Bottom: Pattern Editor
        editor_frame = ttk.LabelFrame(right_frame, text="Test / Edit Pattern")
        editor_frame.grid(row=2, column=0, sticky="ew", pady=5)
        editor_frame.columnconfigure(0, weight=1)
        self.pattern_entry = ttk.Entry(editor_frame, font=("Consolas", 10))
        self.pattern_entry.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        ttk.Button(editor_frame, text="Suggest from Highlight", command=self.suggest_from_highlight).grid(row=1, column=0, sticky="w")
        ttk.Button(editor_frame, text="Test Pattern", command=self.test_pattern).grid(row=1, column=1)
        self.update_btn = ttk.Button(editor_frame, text="Update List", command=self.update_pattern_in_list, state=tk.DISABLED)
        self.update_btn.grid(row=1, column=2, sticky="e")

        # Main Bottom Buttons
        bottom_frame = ttk.Frame(self); bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(bottom_frame, text="Add as New", command=self.add_new_pattern).pack(side=tk.LEFT)
        self.remove_btn = ttk.Button(bottom_frame, text="Remove Selected", command=self.remove_selected_pattern, state=tk.DISABLED)
        self.remove_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="Save All Patterns", command=self.save_all_patterns, style="Red.TButton").pack(side=tk.RIGHT)

    def load_patterns(self):
        self.pattern_listbox.delete(0, tk.END)
        try:
            import custom_patterns
            importlib.reload(custom_patterns)
            patterns = getattr(custom_patterns, self.pattern_type, [])
            for p in patterns:
                # Load the pattern exactly as it is.
                self.pattern_listbox.insert(tk.END, p)
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load patterns:\n{e}")

    def on_pattern_select(self, event=None):
        if selection := self.pattern_listbox.curselection():
            self.pattern_entry.delete(0, tk.END)
            self.pattern_entry.insert(0, self.pattern_listbox.get(selection[0]))
            self.update_btn.config(state=tk.NORMAL)
            self.remove_btn.config(state=tk.NORMAL)

    def suggest_from_highlight(self):
        try:
            selected_text = self.document_text.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
            if not selected_text: return
            # Create a simple, robust pattern from the selection
            pattern = re.escape(selected_text)
            pattern = re.sub(r'(\d+)', r'\\d+', pattern) # Generalize numbers
            final_pattern = f"\\b{pattern}\\b"
            self.pattern_entry.delete(0, tk.END)
            self.pattern_entry.insert(0, final_pattern)
        except tk.TclError:
            messagebox.showwarning("No Selection", "Please highlight text first.")

    def test_pattern(self):
        pattern = self.pattern_entry.get()
        if not pattern: return
        try:
            document = self.document_text.get('1.0', tk.END)
            matches = re.findall(pattern, document, re.IGNORECASE)
            if matches:
                messagebox.showinfo("Test Results", f"Found {len(matches)} match(es):\n\n" + "\n".join(matches[:5]))
            else:
                messagebox.showinfo("Test Results", "No matches found.")
        except re.error as e:
            messagebox.showerror("Invalid Pattern", f"Regex error:\n{e}")

    def add_new_pattern(self):
        if pattern := self.pattern_entry.get():
            self.pattern_listbox.insert(tk.END, pattern)

    def update_pattern_in_list(self):
        if selection := self.pattern_listbox.curselection():
            if new_pattern := self.pattern_entry.get():
                self.pattern_listbox.delete(selection[0])
                self.pattern_listbox.insert(selection[0], new_pattern)

    def remove_selected_pattern(self):
        if selection := self.pattern_listbox.curselection():
            self.pattern_listbox.delete(selection[0])

    def save_all_patterns(self):
        patterns = self.pattern_listbox.get(0, tk.END)
        # Construct the file content, saving each pattern as a raw string literal
        file_content = f"# custom_patterns.py\n# This file is auto-generated.\n\n"
        file_content += f"{self.pattern_type} = [\n"
        for p in patterns:
            # This ensures the pattern is written as r'...' which is what Python needs
            file_content += f"    r'{p}',\n"
        file_content += "]\n"

        try:
            Path("custom_patterns.py").write_text(file_content, encoding="utf-8")
            messagebox.showinfo("Success", "Patterns saved successfully.", parent=self)
            self.parent.log_message("Custom patterns updated. Re-run flagged items to apply changes.", "info")
            self.destroy() # Close the window after saving
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save patterns:\n{e}", parent=self)
