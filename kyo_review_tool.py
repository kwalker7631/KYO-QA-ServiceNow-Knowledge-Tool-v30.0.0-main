# kyo_review_tool.py - Fixed pattern saving and loading
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from pathlib import Path
import re
import importlib
import sys

from config import BRAND_COLORS
import config as config_module 

def generate_regex_from_sample(sample: str) -> str:
    """
    Analyzes a sample string and generates a precise regex pattern by keeping
    all letters and symbols literal and only generalizing the numbers.
    """
    if not sample or not sample.strip():
        return ""

    # Step 1: Escape any special regex characters in the user's sample text.
    escaped_sample = re.escape(sample.strip())

    # Step 2: In the escaped string, find all digit sequences and replace them
    # with the regex token for one or more digits, `\d+`.
    pattern_with_digit_wildcard = re.sub(r'\\?\d+', r'\\d+', escaped_sample)
    
    # Step 3: Construct the final pattern with word boundaries
    return f"\\b{pattern_with_digit_wildcard}\\b"

class ReviewWindow(tk.Toplevel):
    """Enhanced regex pattern management tool with robust pattern saving/loading."""
    
    def __init__(self, parent, pattern_name: str, pattern_label: str, file_info: dict = None):
        super().__init__(parent)
        
        self.pattern_name = pattern_name
        self.pattern_label = pattern_label
        self.file_info = file_info
        self.custom_patterns_path = Path("custom_patterns.py")
        
        self.title(f"Manage Custom: {self.pattern_label}")
        self.geometry("1200x800")
        self.configure(bg=BRAND_COLORS["background"])
        
        # Make window resizable
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Create main container
        main_container = ttk.Frame(self, padding=10)
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(0, weight=1)

        # Create left panel for pattern management
        self._create_pattern_management_panel(main_container)
        
        # Create right panel for text display and error info
        self._create_text_display_panel(main_container)
        
        # Load patterns and text
        self.load_patterns_from_config()
        if self.file_info:
            self.load_text_file()
        else:
            self._disable_text_features()

    def _create_pattern_management_panel(self, parent):
        """Create the pattern management panel on the left side."""
        manager_frame = ttk.LabelFrame(parent, text="Pattern Management", padding=10)
        manager_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        manager_frame.columnconfigure(0, weight=1)
        manager_frame.rowconfigure(2, weight=1)
        
        # Pattern type label
        ttk.Label(manager_frame, text=self.pattern_label, font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Debug info
        self.debug_label = ttk.Label(manager_frame, text="", font=("Segoe UI", 8), foreground="gray")
        self.debug_label.grid(row=1, column=0, sticky="w", pady=(0, 5))
        
        # Pattern list
        list_frame = ttk.Frame(manager_frame)
        list_frame.grid(row=2, column=0, sticky="nsew", pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.pattern_listbox = tk.Listbox(list_frame, font=("Consolas", 9), height=15)
        self.pattern_listbox.grid(row=0, column=0, sticky="nsew")
        self.pattern_listbox.bind("<<ListboxSelect>>", self.on_pattern_select)
        
        pattern_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.pattern_listbox.yview)
        pattern_scrollbar.grid(row=0, column=1, sticky="ns")
        self.pattern_listbox.config(yscrollcommand=pattern_scrollbar.set)
        
        # Buttons frame
        btn_frame = ttk.Frame(manager_frame)
        btn_frame.grid(row=3, column=0, pady=10, sticky="ew")
        
        ttk.Button(btn_frame, text="Add as New", command=self.add_pattern).pack(side="left", padx=5)
        self.remove_btn = ttk.Button(btn_frame, text="Remove Selected", command=self.remove_pattern, state=tk.DISABLED)
        self.remove_btn.pack(side="left", padx=5)
        
        # Pattern editor
        ttk.Label(manager_frame, text="Test / Edit Pattern:", font=("Segoe UI", 10, "bold")).grid(row=4, column=0, sticky="w", pady=(10,5))
        self.pattern_entry = ttk.Entry(manager_frame, font=("Consolas", 10))
        self.pattern_entry.grid(row=5, column=0, sticky="ew", pady=(0,10))
        
        # Test and save buttons
        test_save_frame = ttk.Frame(manager_frame)
        test_save_frame.grid(row=6, column=0, sticky="ew", pady=(0,10))
        
        self.suggest_btn = ttk.Button(test_save_frame, text="Suggest from Highlight", command=self.on_suggest_pattern)
        self.suggest_btn.pack(side="left", padx=5)
        self.test_btn = ttk.Button(test_save_frame, text="Test Pattern", command=self.test_pattern)
        self.test_btn.pack(side="left", padx=5)
        ttk.Button(test_save_frame, text="Update List", command=self.update_pattern_in_list).pack(side="left", padx=5)
        
        # Save button with debug info
        save_frame = ttk.Frame(manager_frame)
        save_frame.grid(row=7, column=0, sticky="ew", pady=10)
        ttk.Button(save_frame, text="Save All Patterns", style="Red.TButton", command=self.save_patterns_to_config).pack(fill="x")
        
        # Debug button
        ttk.Button(save_frame, text="Debug Patterns", command=self.debug_patterns).pack(fill="x", pady=(5,0))

    def _create_text_display_panel(self, parent):
        """Create the text display panel on the right side with error information."""
        text_frame = ttk.LabelFrame(parent, text="Document Content & Error Details", padding=10)
        text_frame.grid(row=0, column=1, sticky="nsew")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(1, weight=1)
        
        # Error information panel (if available)
        if self.file_info:
            self._create_error_info_panel(text_frame)
        
        # Text display area
        text_display_frame = ttk.Frame(text_frame)
        text_display_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        text_display_frame.columnconfigure(0, weight=1)
        text_display_frame.rowconfigure(0, weight=1)
        
        self.pdf_text = tk.Text(text_display_frame, wrap="word", font=("Consolas", 9), relief="solid", borderwidth=1)
        self.pdf_text.grid(row=0, column=0, sticky="nsew")
        
        text_scrollbar = ttk.Scrollbar(text_display_frame, orient="vertical", command=self.pdf_text.yview)
        text_scrollbar.grid(row=0, column=1, sticky="ns")
        self.pdf_text.config(yscrollcommand=text_scrollbar.set)
        
        # Configure text highlighting
        self.pdf_text.tag_configure("highlight", background="yellow", foreground="black")
        self.pdf_text.tag_configure("error_highlight", background="lightcoral", foreground="white")

    def _create_error_info_panel(self, parent):
        """Create an information panel showing error details."""
        info_frame = ttk.LabelFrame(parent, text="File Information", padding=10)
        info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        # File name
        ttk.Label(info_frame, text="File:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Label(info_frame, text=self.file_info.get('filename', 'Unknown'), font=("Segoe UI", 10)).grid(row=0, column=1, sticky="w")
        
        # Failure reason
        ttk.Label(info_frame, text="Issue:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(5, 0))
        reason_text = self.file_info.get('reason', 'Unknown error')
        reason_label = ttk.Label(info_frame, text=reason_text, font=("Segoe UI", 10), foreground="red")
        reason_label.grid(row=1, column=1, sticky="w", pady=(5, 0))
        
        # Processing details
        details_frame = ttk.Frame(info_frame)
        details_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        ocr_used = self.file_info.get('ocr_used', False)
        status = self.file_info.get('status', 'Unknown')
        
        ttk.Label(details_frame, text=f"Status: {status}", font=("Segoe UI", 9)).pack(side="left", padx=(0, 20))
        ttk.Label(details_frame, text=f"OCR Used: {'Yes' if ocr_used else 'No'}", font=("Segoe UI", 9)).pack(side="left")

    def _disable_text_features(self):
        """Disable text-related features when no file is available."""
        self.suggest_btn.config(state=tk.DISABLED)
        self.test_btn.config(state=tk.DISABLED)
        self.pdf_text.insert("1.0", "No file selected for review.\n\nYou can still manage patterns using the panel on the left.")
        self.pdf_text.config(state=tk.DISABLED)

    def debug_patterns(self):
        """Debug the current patterns system."""
        debug_info = []
        debug_info.append("🔍 PATTERN DEBUG INFO")
        debug_info.append("=" * 30)
        
        # Check file existence
        debug_info.append(f"File exists: {self.custom_patterns_path.exists()}")
        if self.custom_patterns_path.exists():
            debug_info.append(f"File size: {self.custom_patterns_path.stat().st_size} bytes")
        
        # Check patterns in listbox
        patterns_in_listbox = list(self.pattern_listbox.get(0, tk.END))
        debug_info.append(f"Patterns in UI: {len(patterns_in_listbox)}")
        
        # Try to load from file
        try:
            if 'custom_patterns' in sys.modules:
                del sys.modules['custom_patterns']
            import custom_patterns as custom_module
            file_patterns = getattr(custom_module, self.pattern_name, [])
            debug_info.append(f"Patterns in file: {len(file_patterns)}")
        except Exception as e:
            debug_info.append(f"Error loading from file: {e}")
        
        # Show debug info
        debug_text = "\n".join(debug_info)
        messagebox.showinfo("Debug Information", debug_text, parent=self)
        
        # Update debug label
        self.debug_label.config(text=f"UI: {len(patterns_in_listbox)} patterns")

    def load_patterns_from_config(self):
        """Load patterns from the custom_patterns.py file with better error handling."""
        self.pattern_listbox.delete(0, tk.END)
        patterns_to_load = []
        
        # Ensure file exists
        if not self.custom_patterns_path.exists():
            self._create_default_patterns_file()
        
        try:
            # Clear from cache to force reload
            if 'custom_patterns' in sys.modules:
                del sys.modules['custom_patterns']
            
            import custom_patterns as custom_module
            patterns_to_load = getattr(custom_module, self.pattern_name, [])
            
            self.debug_label.config(text=f"✅ Loaded {len(patterns_to_load)} patterns", foreground="green")
            
        except ImportError as e:
            self.debug_label.config(text=f"❌ Import error: {e}", foreground="red")
        except SyntaxError as e:
            self.debug_label.config(text=f"❌ Syntax error in file", foreground="red")
        except AttributeError as e:
            self.debug_label.config(text=f"❌ Missing {self.pattern_name}", foreground="red")
        except Exception as e:
            self.debug_label.config(text=f"❌ Unknown error: {e}", foreground="red")
            
        for pattern in patterns_to_load:
            self.pattern_listbox.insert(tk.END, pattern)

    def _create_default_patterns_file(self):
        """Create a default custom_patterns.py file."""
        default_content = '''# custom_patterns.py
# This file stores user-defined regex patterns.

MODEL_PATTERNS = [
    # Add your custom model patterns here
    # Example: r'\\bCustom-\\d+\\b',
]

QA_NUMBER_PATTERNS = [
    # Add your custom QA number patterns here  
    # Example: r'\\bQA-\\d+\\b',
]
'''
        try:
            self.custom_patterns_path.write_text(default_content, encoding='utf-8')
            print(f"✅ Created default custom_patterns.py")
        except Exception as e:
            print(f"❌ Failed to create default file: {e}")
    
    def save_patterns_to_config(self):
        """Save all pattern lists to the custom_patterns.py file with robust error handling."""
        all_patterns_in_listbox = list(self.pattern_listbox.get(0, tk.END))
        
        # Validate patterns before saving
        valid_patterns = []
        invalid_patterns = []
        
        for pattern in all_patterns_in_listbox:
            try:
                re.compile(pattern)
                valid_patterns.append(pattern)
            except re.error as e:
                invalid_patterns.append(f"{pattern} (Error: {e})")
        
        if invalid_patterns:
            error_msg = f"Found {len(invalid_patterns)} invalid patterns:\n\n"
            error_msg += "\n".join(invalid_patterns[:5])  # Show first 5
            if len(invalid_patterns) > 5:
                error_msg += f"\n... and {len(invalid_patterns) - 5} more"
            error_msg += "\n\nDo you want to save only the valid patterns?"
            
            if not messagebox.askyesno("Invalid Patterns Found", error_msg, parent=self):
                return
        
        msg = f"This will save {len(valid_patterns)} valid patterns to the {self.pattern_name} list in custom_patterns.py.\n\nAre you sure?"
        
        if not messagebox.askyesno("Confirm Save", msg, parent=self):
            return

        try:
            # Load existing patterns for other lists
            all_lists_to_save = {}
            all_possible_pattern_names = ["MODEL_PATTERNS", "QA_NUMBER_PATTERNS"]
            
            # Initialize with current patterns
            all_lists_to_save[self.pattern_name] = valid_patterns
            
            # Preserve other pattern lists
            try:
                if 'custom_patterns' in sys.modules:
                    del sys.modules['custom_patterns']
                import custom_patterns as custom_module
                
                for name in all_possible_pattern_names:
                    if name != self.pattern_name:
                        existing_patterns = getattr(custom_module, name, [])
                        all_lists_to_save[name] = existing_patterns
                        
            except Exception as e:
                print(f"Warning: Could not load existing patterns: {e}")
                # Initialize missing lists as empty
                for name in all_possible_pattern_names:
                    if name not in all_lists_to_save:
                        all_lists_to_save[name] = []

            # Generate file content
            file_lines = [
                "# custom_patterns.py",
                "# This file stores user-defined regex patterns.",
                ""
            ]
            
            for name, patterns in all_lists_to_save.items():
                file_lines.append(f"{name} = [")
                for pattern in patterns:
                    # Escape backslashes and quotes properly
                    safe_pattern = pattern.replace("\\", "\\\\").replace("'", "\\'")
                    file_lines.append(f"    r'{safe_pattern}',")
                file_lines.append("]")
                file_lines.append("")
            
            file_content = "\n".join(file_lines)
            
            # Write to file
            self.custom_patterns_path.write_text(file_content, encoding='utf-8')
            
            # Verify the save worked
            try:
                if 'custom_patterns' in sys.modules:
                    del sys.modules['custom_patterns']
                import custom_patterns as test_module
                saved_patterns = getattr(test_module, self.pattern_name, [])
                
                if len(saved_patterns) == len(valid_patterns):
                    success_msg = f"✅ Successfully saved {len(valid_patterns)} patterns!\n\nChanges will apply on the next processing run."
                    if invalid_patterns:
                        success_msg += f"\n\nNote: {len(invalid_patterns)} invalid patterns were skipped."
                else:
                    success_msg = f"⚠️ Patterns saved but verification failed.\nExpected {len(valid_patterns)}, found {len(saved_patterns)}."
                    
            except Exception as e:
                success_msg = f"⚠️ Patterns saved but verification failed: {e}"
            
            messagebox.showinfo("Save Result", success_msg, parent=self)
            self.debug_label.config(text=f"✅ Saved {len(valid_patterns)} patterns", foreground="green")
            
            if messagebox.askyesno("Close Window", "Patterns saved successfully. Close this window?", parent=self):
                self.destroy()
            
        except Exception as e:
            error_msg = f"❌ Failed to save patterns to file:\n\n{str(e)}\n\nThe file may be locked or you may not have write permissions."
            messagebox.showerror("Save Failed", error_msg, parent=self)
            self.debug_label.config(text="❌ Save failed", foreground="red")

    def update_pattern_in_list(self):
        """Update or add a pattern to the list."""
        new_pattern = self.pattern_entry.get().strip()
        if not new_pattern:
            messagebox.showwarning("Input Error", "Test/Edit Pattern box is empty.", parent=self)
            return
        
        # Validate the pattern
        try:
            re.compile(new_pattern)
        except re.error as e:
            messagebox.showerror("Invalid Pattern", f"The regex pattern is invalid:\n{e}", parent=self)
            return
            
        selection_indices = self.pattern_listbox.curselection()
        if not selection_indices:
            # Add as new pattern
            self.pattern_listbox.insert(tk.END, new_pattern)
            self.pattern_listbox.selection_clear(0, tk.END)
            self.pattern_listbox.selection_set(tk.END)
            self.pattern_listbox.see(tk.END)
        else:
            # Update existing pattern
            idx = selection_indices[0]
            self.pattern_listbox.delete(idx)
            self.pattern_listbox.insert(idx, new_pattern)
            self.pattern_listbox.selection_set(idx)

    def on_pattern_select(self, event):
        """Handle pattern selection in the listbox."""
        selection_indices = self.pattern_listbox.curselection()
        if not selection_indices:
            self.remove_btn.config(state=tk.DISABLED)
            self.pattern_entry.delete(0, tk.END)
            return
            
        selected_pattern = self.pattern_listbox.get(selection_indices[0])
        self.pattern_entry.delete(0, tk.END)
        self.pattern_entry.insert(0, selected_pattern)
        self.remove_btn.config(state=tk.NORMAL)

    def add_pattern(self):
        """Add a new pattern to the list."""
        new_pattern = self.pattern_entry.get().strip()
        if not new_pattern:
            messagebox.showwarning("Input Error", "Test/Edit Pattern box is empty. Cannot add.", parent=self)
            return
        
        # Validate the pattern
        try:
            re.compile(new_pattern)
        except re.error as e:
            messagebox.showerror("Invalid Pattern", f"The regex pattern is invalid:\n{e}", parent=self)
            return
        
        self.pattern_listbox.insert(tk.END, new_pattern)
        self.pattern_entry.delete(0, tk.END)
        # Select the new pattern
        self.pattern_listbox.selection_clear(0, tk.END)
        self.pattern_listbox.selection_set(tk.END)
        self.pattern_listbox.see(tk.END)

    def remove_pattern(self):
        """Remove the selected pattern from the list."""
        selection_indices = self.pattern_listbox.curselection()
        if not selection_indices: 
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to remove the selected pattern?", parent=self):
            self.pattern_listbox.delete(selection_indices[0])
            self.on_pattern_select(None)

    def test_pattern(self):
        """Test the current pattern against the document text."""
        # Clear previous highlights
        self.pdf_text.tag_remove("highlight", "1.0", "end")
        self.pdf_text.tag_remove("error_highlight", "1.0", "end")
        
        pattern_str = self.pattern_entry.get().strip()
        if not pattern_str:
            messagebox.showwarning("Warning", "Test Pattern box cannot be empty.", parent=self)
            return
            
        try:
            # Validate pattern first
            re.compile(pattern_str)
            
            content = self.pdf_text.get("1.0", "end")
            matches = list(re.finditer(pattern_str, content, re.IGNORECASE))
            
            if not matches:
                messagebox.showinfo("No Matches", "The pattern did not find any matches in the text.", parent=self)
                return
                
            # Highlight all matches
            for match in matches:
                start, end = match.span()
                self.pdf_text.tag_add("highlight", f"1.0+{start}c", f"1.0+{end}c")
            
            # Scroll to first match
            first_match_pos = f"1.0+{max(0, matches[0].start()-100)}c"
            self.pdf_text.see(first_match_pos)
            
            # Show results
            match_list = [match.group() for match in matches]
            unique_matches = list(set(match_list))
            
            result_msg = f"Found {len(matches)} match(es):\n\n"
            result_msg += f"Unique matches: {', '.join(unique_matches[:10])}"
            if len(unique_matches) > 10:
                result_msg += f" ... and {len(unique_matches) - 10} more"
                
            messagebox.showinfo("Pattern Test Results", result_msg, parent=self)
            
        except re.error as e:
            messagebox.showerror("Invalid Pattern", f"The regular expression is invalid:\n{e}", parent=self)
            
    def on_suggest_pattern(self):
        """Generate a pattern from highlighted text."""
        try:
            selected_text = self.pdf_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if not selected_text or not selected_text.strip():
                messagebox.showwarning("No Selection", "Please highlight text to generate a pattern.", parent=self)
                return
                
            suggested_pattern = generate_regex_from_sample(selected_text)
            self.pattern_entry.delete(0, tk.END)
            self.pattern_entry.insert(0, suggested_pattern)
            
            messagebox.showinfo("Pattern Suggested", 
                              f"Generated pattern: {suggested_pattern}\n\n"
                              "A pattern has been generated in the 'Test / Edit' box. "
                              "Click 'Test Pattern' to verify it works correctly.", 
                              parent=self)
                              
        except tk.TclError:
            messagebox.showwarning("No Selection", "Please highlight text to generate a pattern.", parent=self)
            
    def load_text_file(self):
        """Load and display the text file content."""
        try:
            if self.file_info and "txt_path" in self.file_info:
                txt_path = Path(self.file_info["txt_path"])
                
                if txt_path.exists():
                    with open(txt_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    self.pdf_text.insert("1.0", content)
                    
                else:
                    raise FileNotFoundError(f"Text file not found: {txt_path}")
            else:
                raise ValueError("No file information was provided to load.")
                
        except Exception as e:
            error_msg = f"Error: Could not load text file for review.\n\nDetails: {str(e)}"
            self.pdf_text.insert("1.0", error_msg)
            self.pdf_text.config(state=tk.DISABLED)
            messagebox.showerror("Error", f"Failed to load text file:\n{e}", parent=self)