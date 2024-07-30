# ui.py

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import pyperclip
from core import PromptForgeCore
import logging

class SubjectFrame(ttk.Frame):
    def __init__(self, master, core):
        super().__init__(master)
        self.core = core
        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self, text="Subject Name:").grid(row=0, column=0, sticky="w")
        self.name_entry = ttk.Entry(self)
        self.name_entry.grid(row=0, column=1, sticky="ew")

        ttk.Label(self, text="Category:").grid(row=1, column=0, sticky="w")
        self.category_combo = ttk.Combobox(self, values=["Main Character", "Supporting Character", "Location", "Object"])
        self.category_combo.grid(row=1, column=1, sticky="ew")

        ttk.Label(self, text="Description:").grid(row=2, column=0, sticky="w")
        self.description_text = scrolledtext.ScrolledText(self, height=4)
        self.description_text.grid(row=2, column=1, sticky="nsew")

        self.add_button = ttk.Button(self, text="Add Subject", command=self.add_subject)
        self.add_button.grid(row=3, column=1, sticky="e")

        self.subjects_listbox = tk.Listbox(self)
        self.subjects_listbox.grid(row=4, column=0, columnspan=2, sticky="nsew")

        self.toggle_button = ttk.Button(self, text="Toggle Active", command=self.toggle_subject)
        self.toggle_button.grid(row=5, column=0, sticky="w")

        self.remove_button = ttk.Button(self, text="Remove Subject", command=self.remove_subject)
        self.remove_button.grid(row=5, column=1, sticky="e")

    def add_subject(self):
        name = self.name_entry.get()
        category = self.category_combo.get()
        description = self.description_text.get("1.0", tk.END).strip()
        if name and category and description:
            self.core.add_subject(name, category, description)
            self.subjects_listbox.insert(tk.END, name)
            self.clear_inputs()

    def remove_subject(self):
        selection = self.subjects_listbox.curselection()
        if selection:
            name = self.subjects_listbox.get(selection[0])
            self.core.remove_subject(name)
            self.subjects_listbox.delete(selection[0])

    def toggle_subject(self):
        selection = self.subjects_listbox.curselection()
        if selection:
            name = self.subjects_listbox.get(selection[0])
            self.core.toggle_subject(name)

    def clear_inputs(self):
        self.name_entry.delete(0, tk.END)
        self.category_combo.set('')
        self.description_text.delete("1.0", tk.END)

class AutomatedAnalysisFrame(ttk.Frame):
    def __init__(self, master, core):
        super().__init__(master)
        self.core = core
        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self, text="Script File:").grid(row=0, column=0, sticky="w")
        self.script_path = ttk.Entry(self, width=50)
        self.script_path.grid(row=0, column=1, sticky="ew")
        ttk.Button(self, text="Browse", command=self.browse_script).grid(row=0, column=2)

        ttk.Label(self, text="Director Style:").grid(row=1, column=0, sticky="w")
        self.style_combo = ttk.Combobox(self, values=list(self.core.meta_chain.director_styles.keys()))
        self.style_combo.grid(row=1, column=1, sticky="ew")

        ttk.Button(self, text="Analyze Script", command=self.analyze_script).grid(row=2, column=1, sticky="e")

        self.results_text = scrolledtext.ScrolledText(self, height=10, width=60)
        self.results_text.grid(row=3, column=0, columnspan=3, sticky="nsew")

    def browse_script(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            self.script_path.delete(0, tk.END)
            self.script_path.insert(0, filename)

    def analyze_script(self):
        script_path = self.script_path.get()
        director_style = self.style_combo.get()
        if not script_path or not director_style:
            messagebox.showerror("Error", "Please select a script file and a director style.")
            return
        
        with open(script_path, 'r') as file:
            script_content = file.read()
        
        results = self.core.meta_chain.generate_prompt_spreadsheet(script_content, director_style)
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, results)

class PromptForgeUI:
    def __init__(self, master):
        self.master = master
        self.core = PromptForgeCore()
        self.setup_ui()

    def setup_ui(self):
        self.master.title("PromptForge - Bring Your Script to Life")
        self.master.geometry("1000x800")

        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        # Style
        ttk.Label(main_frame, text="Style:").grid(column=0, row=0, sticky=tk.W, pady=5)
        self.style_entry = ttk.Entry(main_frame, width=50)
        self.style_entry.grid(column=1, row=0, sticky=(tk.W, tk.E), pady=5)
        self.style_entry.insert(0, "Enter visual style (e.g., Noir, Cyberpunk, Magical Realism)")

        # Shot Description
        ttk.Label(main_frame, text="Shot Description:").grid(column=0, row=1, sticky=tk.W, pady=5)
        self.shot_text = scrolledtext.ScrolledText(main_frame, height=4, width=50, wrap=tk.WORD)
        self.shot_text.grid(column=1, row=1, sticky=(tk.W, tk.E), pady=5)
        self.shot_text.insert(tk.END, "Describe the shot (e.g., Close-up of a weathered hand holding an antique pocket watch)")

        # Camera Move
        ttk.Label(main_frame, text="Camera Move:").grid(column=0, row=2, sticky=tk.W, pady=5)
        self.move_var = tk.StringVar()
        self.move_combo = ttk.Combobox(main_frame, textvariable=self.move_var, values=["None", "Pan", "Tilt", "Zoom", "Dolly", "Truck", "Pedestal"], width=47)
        self.move_combo.grid(column=1, row=2, sticky=(tk.W, tk.E), pady=5)
        self.move_combo.set("None")

        # Director's Notes
        ttk.Label(main_frame, text="Director's Notes:").grid(column=0, row=3, sticky=tk.W, pady=5)
        self.notes_text = scrolledtext.ScrolledText(main_frame, height=4, width=50, wrap=tk.WORD)
        self.notes_text.grid(column=1, row=3, sticky=(tk.W, tk.E), pady=5)
        self.notes_text.insert(tk.END, "Enter director's notes (e.g., Focus on the intricate engravings, convey a sense of time passing)")

        # Script
        ttk.Label(main_frame, text="Script:").grid(column=0, row=4, sticky=tk.W, pady=5)
        self.script_text = scrolledtext.ScrolledText(main_frame, height=10, width=50, wrap=tk.WORD)
        self.script_text.grid(column=1, row=4, sticky=(tk.W, tk.E), pady=5)
        self.script_text.insert(tk.END, "Paste your script here. Highlight the relevant section for this shot.")

        # Stick to Script Checkbox
        self.stick_to_script_var = tk.BooleanVar()
        self.stick_to_script_check = ttk.Checkbutton(main_frame, text="Stick to Script", variable=self.stick_to_script_var)
        self.stick_to_script_check.grid(column=1, row=5, sticky=tk.W, pady=5)

        # Prompt Length
        ttk.Label(main_frame, text="Prompt Length:").grid(column=0, row=6, sticky=tk.W, pady=5)
        self.length_var = tk.StringVar()
        self.length_combo = ttk.Combobox(main_frame, textvariable=self.length_var, values=["short", "medium", "long"], width=47)
        self.length_combo.grid(column=1, row=6, sticky=(tk.W, tk.E), pady=5)
        self.length_combo.set("medium")

        # Generate Button
        self.generate_button = ttk.Button(main_frame, text="Generate Prompt", command=self.handle_generate_button_click)
        self.generate_button.grid(column=1, row=7, sticky=tk.E, pady=10)

        # Results
        ttk.Label(main_frame, text="Generated Prompt:").grid(column=0, row=8, sticky=tk.W, pady=5)
        self.results_text = scrolledtext.ScrolledText(main_frame, height=8, width=50, wrap=tk.WORD)
        self.results_text.grid(column=1, row=8, sticky=(tk.W, tk.E), pady=5)

        # Save Prompt Button
        self.save_button = ttk.Button(main_frame, text="Save Prompt", command=self.save_prompt)
        self.save_button.grid(column=1, row=9, sticky=tk.E, pady=10)

        # Copy to Clipboard Button
        self.copy_button = ttk.Button(main_frame, text="Copy to Clipboard", command=self.copy_prompt_to_clipboard)
        self.copy_button.grid(column=1, row=10, sticky=tk.E, pady=10)

        # Add Subject Frame
        self.subject_frame = SubjectFrame(main_frame, self.core)
        self.subject_frame.grid(column=0, row=11, columnspan=2, sticky="nsew")

        # Add Automated Analysis Frame
        automated_frame = ttk.LabelFrame(main_frame, text="Automated Script Analysis")
        automated_frame.grid(column=0, row=12, columnspan=2, sticky="nsew", pady=10)
        self.automated_frame = AutomatedAnalysisFrame(automated_frame, self.core)
        self.automated_frame.pack(fill=tk.BOTH, expand=True)

        # Configure grid
        for child in main_frame.winfo_children():
            child.grid_configure(padx=5)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(8, weight=1)

    def generate_prompt(self):
        try:
            self.core.set_style(self.style_entry.get())
            self.core.process_shot(self.shot_text.get("1.0", tk.END).strip())
            self.core.process_directors_notes(self.notes_text.get("1.0", tk.END).strip())
            
            try:
                highlighted_text = self.script_text.get("sel.first", "sel.last")
            except tk.TclError:
                highlighted_text = ""

            full_script = self.script_text.get("1.0", tk.END).strip()
            stick_to_script = self.stick_to_script_var.get()
            
            self.core.process_script(highlighted_text, full_script, stick_to_script)
            
            prompt = self.core.generate_prompt(self.length_var.get())
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert(tk.END, prompt)
            
            return prompt
        except Exception as e:
            logging.exception("Error in generate_prompt")
            messagebox.showerror("Error", f"Failed to generate prompt: {str(e)}")
            return None

    def handle_generate_button_click(self):
        prompt = self.generate_prompt()
        if prompt:
            messagebox.showinfo("Generated Prompt", f"Your generated prompt is:\n\n{prompt}")

    def save_prompt(self):
        prompt = self.results_text.get("1.0", tk.END)
        components = {
            "style": self.style_entry.get(),
            "shot": self.shot_text.get("1.0", tk.END),
            "camera_move": self.move_var.get(),
            "directors_notes": self.notes_text.get("1.0", tk.END),
            "script": self.script_text.get("1.0", tk.END),
            "highlighted_text": self.script_text.get("sel.first", "sel.last"),
            "stick_to_script": self.stick_to_script_var.get(),
            "length": self.length_var.get()
        }
        self.core.save_prompt(prompt, components)
        messagebox.showinfo("Success", "Prompt saved successfully!")

    def copy_prompt_to_clipboard(self):
        prompt = self.results_text.get("1.0", tk.END).strip()
        if prompt:
            pyperclip.copy(prompt)
            messagebox.showinfo("Copied", "The prompt has been copied to your clipboard.")
        else:
            messagebox.showwarning("No Prompt", "There's no prompt to copy. Generate a prompt first.")

def main():
    root = tk.Tk()
    app = PromptForgeUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()