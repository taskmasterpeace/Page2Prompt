# ui.py

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from tkinter.ttk import Frame, Scrollbar
import pyperclip
from core import PromptForgeCore
import logging

class SubjectFrame(ttk.Frame):
    def __init__(self, master, core):
        super().__init__(master)
        self.core = core
        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self, text="Subject Name:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.name_entry = ttk.Entry(self)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(self, text="Category:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.category_combo = ttk.Combobox(self, values=["Main Character", "Supporting Character", "Location", "Object"])
        self.category_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(self, text="Description:").grid(row=2, column=0, sticky="nw", padx=5, pady=2)
        self.description_text = scrolledtext.ScrolledText(self, height=3, width=30)
        self.description_text.grid(row=2, column=1, sticky="nsew", padx=5, pady=2)

        self.add_button = ttk.Button(self, text="Add Subject", command=self.add_subject)
        self.add_button.grid(row=3, column=1, sticky="e", padx=5, pady=5)

        self.subjects_listbox = tk.Listbox(self, height=5)
        self.subjects_listbox.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=5, pady=2)

        button_frame = ttk.Frame(self)
        button_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.toggle_button = ttk.Button(button_frame, text="Toggle Active", command=self.toggle_subject)
        self.toggle_button.pack(side="left", padx=2)

        self.remove_button = ttk.Button(button_frame, text="Remove Subject", command=self.remove_subject)
        self.remove_button.pack(side="right", padx=2)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(4, weight=1)

    # ... (rest of the SubjectFrame methods remain unchanged)

class AutomatedAnalysisFrame(ttk.Frame):
    def __init__(self, master, core):
        super().__init__(master)
        self.core = core
        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self, text="Script File:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.script_path = ttk.Entry(self, width=50)
        self.script_path.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(self, text="Browse", command=self.browse_script).grid(row=0, column=2, padx=5, pady=2)

        ttk.Label(self, text="Director Style:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.style_combo = ttk.Combobox(self, values=list(self.core.meta_chain.director_styles.keys()))
        self.style_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        ttk.Button(self, text="Analyze Script", command=self.analyze_script).grid(row=2, column=1, sticky="e", padx=5, pady=5)

        self.results_text = scrolledtext.ScrolledText(self, height=8, width=60)
        self.results_text.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=5, pady=2)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)

    # ... (rest of the AutomatedAnalysisFrame methods remain unchanged)

class PromptForgeUI:
    def __init__(self, master):
        self.master = master
        self.core = PromptForgeCore()
        self.setup_ui()
        self.all_prompts_window = None
        self.all_prompts_text = None

    def setup_ui(self):
        self.master.title("PromptForge - Bring Your Script to Life")
        self.master.geometry("1200x800")
        self.master.configure(bg='#f0f0f0')  # Light gray background

        style = ttk.Style()
        style.theme_use('clam')  # Use a modern-looking theme
        style.configure("TFrame", background='#f0f0f0')
        style.configure("TLabel", background='#f0f0f0', font=('Helvetica', 10))
        style.configure("TButton", font=('Helvetica', 10))
        style.configure("TEntry", font=('Helvetica', 10))
        style.configure("TCombobox", font=('Helvetica', 10))

        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Left Frame Contents
        self.create_input_fields(left_frame)

        # Right Frame Contents
        self.create_output_area(right_frame)
        self.create_subject_frame(right_frame)
        self.create_automated_analysis_frame(right_frame)

    def create_input_fields(self, parent):
        input_frame = ttk.LabelFrame(parent, text="Input", padding="10")
        input_frame.pack(fill="both", expand=True)

        # Style
        ttk.Label(input_frame, text="Style:").grid(column=0, row=0, sticky=tk.W, pady=5)
        self.style_entry = ttk.Entry(input_frame, width=50)
        self.style_entry.grid(column=1, row=0, sticky=(tk.W, tk.E), pady=5)
        self.style_entry.insert(0, "Enter visual style (e.g., Noir, Cyberpunk, Magical Realism)")

        # Shot Description
        ttk.Label(input_frame, text="Shot Description:").grid(column=0, row=1, sticky=tk.W, pady=5)
        self.shot_text = scrolledtext.ScrolledText(input_frame, height=4, width=50, wrap=tk.WORD)
        self.shot_text.grid(column=1, row=1, sticky=(tk.W, tk.E), pady=5)
        self.shot_text.insert(tk.END, "Describe the shot (e.g., Close-up of a weathered hand holding an antique pocket watch)")

        # Camera Move
        ttk.Label(input_frame, text="Camera Move:").grid(column=0, row=2, sticky=tk.W, pady=5)
        self.move_var = tk.StringVar()
        self.move_combo = ttk.Combobox(input_frame, textvariable=self.move_var, values=["None", "Pan", "Tilt", "Zoom", "Dolly", "Truck", "Pedestal"], width=47)
        self.move_combo.grid(column=1, row=2, sticky=(tk.W, tk.E), pady=5)
        self.move_combo.set("None")

        # Director's Notes
        ttk.Label(input_frame, text="Director's Notes:").grid(column=0, row=3, sticky=tk.W, pady=5)
        self.notes_text = scrolledtext.ScrolledText(input_frame, height=4, width=50, wrap=tk.WORD)
        self.notes_text.grid(column=1, row=3, sticky=(tk.W, tk.E), pady=5)
        self.notes_text.insert(tk.END, "Enter director's notes (e.g., Focus on the intricate engravings, convey a sense of time passing)")

        # Script
        ttk.Label(input_frame, text="Script:").grid(column=0, row=4, sticky=tk.W, pady=5)
        self.script_text = scrolledtext.ScrolledText(input_frame, height=10, width=50, wrap=tk.WORD)
        self.script_text.grid(column=1, row=4, sticky=(tk.W, tk.E), pady=5)
        self.script_text.insert(tk.END, "Paste your script here. Highlight the relevant section for this shot.")

        # Stick to Script Checkbox
        self.stick_to_script_var = tk.BooleanVar()
        self.stick_to_script_check = ttk.Checkbutton(input_frame, text="Stick to Script", variable=self.stick_to_script_var)
        self.stick_to_script_check.grid(column=1, row=5, sticky=tk.W, pady=5)

        # Prompt Length
        ttk.Label(input_frame, text="Prompt Length:").grid(column=0, row=6, sticky=tk.W, pady=5)
        self.length_var = tk.StringVar()
        self.length_combo = ttk.Combobox(input_frame, textvariable=self.length_var, values=["short", "medium", "long"], width=47)
        self.length_combo.grid(column=1, row=6, sticky=(tk.W, tk.E), pady=5)
        self.length_combo.set("medium")

        # AI Model Selection
        ttk.Label(input_frame, text="AI Model:").grid(column=0, row=7, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(input_frame, textvariable=self.model_var, values=["gpt-3.5-turbo", "gpt-4"], width=47)
        self.model_combo.grid(column=1, row=7, sticky=(tk.W, tk.E), pady=5)
        self.model_combo.set("gpt-3.5-turbo")

        # Generate Button
        self.generate_button = ttk.Button(input_frame, text="Generate Prompt", command=self.handle_generate_button_click)
        self.generate_button.grid(column=1, row=8, sticky=tk.E, pady=10)

        input_frame.columnconfigure(1, weight=1)

    def create_output_area(self, parent):
        output_frame = ttk.LabelFrame(parent, text="Generated Prompt", padding="10")
        output_frame.pack(fill="both", expand=True)

        self.results_text = scrolledtext.ScrolledText(output_frame, height=10, width=50, wrap=tk.WORD)
        self.results_text.pack(fill="both", expand=True, pady=5)

        button_frame = ttk.Frame(output_frame)
        button_frame.pack(fill="x", pady=5)

        self.save_button = ttk.Button(button_frame, text="Save Prompt", command=self.save_prompt)
        self.save_button.pack(side="left", padx=2)

        self.copy_button = ttk.Button(button_frame, text="Copy to Clipboard", command=self.copy_prompt_to_clipboard)
        self.copy_button.pack(side="left", padx=2)

        self.show_prompts_button = ttk.Button(button_frame, text="Show All Prompts", command=self.show_all_prompts)
        self.show_prompts_button.pack(side="left", padx=2)

    def create_subject_frame(self, parent):
        subject_frame = ttk.LabelFrame(parent, text="Subjects", padding="10")
        subject_frame.pack(fill="both", expand=True, pady=(10, 0))
        self.subject_frame = SubjectFrame(subject_frame, self.core)
        self.subject_frame.pack(fill="both", expand=True)

    def create_automated_analysis_frame(self, parent):
        automated_frame = ttk.LabelFrame(parent, text="Automated Script Analysis", padding="10")
        automated_frame.pack(fill="both", expand=True, pady=(10, 0))
        self.automated_frame = AutomatedAnalysisFrame(automated_frame, self.core)
        self.automated_frame.pack(fill="both", expand=True)

    # ... (rest of the PromptForgeUI methods remain unchanged)

def main():
    root = tk.Tk()
    app = PromptForgeUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
