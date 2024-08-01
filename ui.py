# ui.py

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from tkinter.ttk import Frame, Scrollbar
import pyperclip
from core import PromptForgeCore
import logging
import os
import asyncio
import random
from styles import predefined_styles
from tkinter import messagebox

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip, text=self.text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class SubjectFrame(ttk.Frame):
    def __init__(self, master, core):
        super().__init__(master)
        self.core = core
        self.setup_ui()

    def update_subjects(self, subjects):
        self.subjects_listbox.delete(0, tk.END)
        for subject in subjects:
            status = 'Active' if subject['active'] else 'Inactive'
            self.subjects_listbox.insert(tk.END, f"{subject['name']} ({subject['category']}) ({status})")

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

    def add_subject(self):
        try:
            name = self.name_entry.get().strip()
            category = self.category_combo.get()
            description = self.description_text.get("1.0", tk.END).strip()

            if not name or not category or not description:
                raise ValueError("All fields must be filled")

            self.core.add_subject(name, category, description)
            self.subjects_listbox.insert(tk.END, f"{name} ({category})")
            self.clear_inputs()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def toggle_subject(self):
        try:
            selected = self.subjects_listbox.curselection()
            if not selected:
                raise ValueError("No subject selected")
            
            index = selected[0]
            subject = self.subjects_listbox.get(index)
            name = subject.split(" (")[0]
            self.core.toggle_subject(name)
            
            # Update the listbox to reflect the change
            current_status = 'Active' if '(Inactive)' in subject else 'Inactive'
            new_text = f"{name} ({subject.split(' (')[1].split(')')[0]}) ({current_status})"
            self.subjects_listbox.delete(index)
            self.subjects_listbox.insert(index, new_text)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def remove_subject(self):
        try:
            selected = self.subjects_listbox.curselection()
            if not selected:
                raise ValueError("No subject selected")
            
            index = selected[0]
            subject = self.subjects_listbox.get(index)
            name = subject.split(" (")[0]
            self.core.remove_subject(name)
            self.subjects_listbox.delete(index)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_inputs(self):
        self.name_entry.delete(0, tk.END)
        self.category_combo.set("")
        self.description_text.delete("1.0", tk.END)

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

    def browse_script(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            self.script_path.delete(0, tk.END)
            self.script_path.insert(0, filename)

    def analyze_script(self):
        script_path = self.script_path.get()
        director_style = self.style_combo.get()
        
        if not script_path or not director_style:
            messagebox.showerror("Error", "Please select a script file and director style.")
            return
        
        try:
            with open(script_path, 'r') as file:
                script_content = file.read()
            
            result = self.core.analyze_script(script_content, director_style)
            self.results_text.delete('1.0', tk.END)
            self.results_text.insert(tk.END, result)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    # ... (rest of the AutomatedAnalysisFrame methods remain unchanged)

class Page2PromptUI:
    def __init__(self, master, core):
        self.master = master
        self.core = core
        self.loop = asyncio.get_event_loop()
        self.setup_ui()
        self.all_prompts_window = None
        self.all_prompts_text = None

    def setup_ui(self):
        self.master.title("Page 2 Prompt - Bring Your Script to Life")
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

        # API Key
        ttk.Label(input_frame, text="API Key:").grid(column=0, row=0, sticky=tk.W, pady=5)
        self.api_key_entry = ttk.Entry(input_frame, width=50, show="*")
        self.api_key_entry.grid(column=1, row=0, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(input_frame, text="Save API Key", command=self.save_api_key).grid(column=2, row=0, sticky=tk.W, pady=5)

        # Shot Description
        ttk.Label(input_frame, text="Shot Description:").grid(column=0, row=1, sticky=tk.W, pady=5)
        self.shot_text = scrolledtext.ScrolledText(input_frame, height=4, width=50, wrap=tk.WORD)
        self.shot_text.grid(column=1, row=1, sticky=(tk.W, tk.E), pady=5)
        self.shot_text.insert(tk.END, "")

        # Director's Notes
        ttk.Label(input_frame, text="📝 Director's Notes:").grid(column=0, row=2, sticky=tk.W, pady=5)
        self.notes_text = scrolledtext.ScrolledText(input_frame, height=4, width=50, wrap=tk.WORD)
        self.notes_text.grid(column=1, row=2, sticky=(tk.W, tk.E), pady=5)
        self.notes_text.insert(tk.END, "")

        # Style
        style_frame = ttk.Frame(input_frame)
        style_frame.grid(column=0, row=3, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(style_frame, text="🎨 Style:").grid(column=0, row=0, sticky=tk.W)
        self.style_combo = ttk.Combobox(style_frame, width=30)
        self.style_combo.grid(column=1, row=0, sticky=(tk.W, tk.E))
        style_names = ["None"] + self.core.style_manager.get_style_names()
        self.style_combo['values'] = style_names
        self.style_combo.set("None")
        self.style_combo.bind("<<ComboboxSelected>>", self.on_style_selected)

        generate_style_btn = ttk.Button(style_frame, text="Generate Random Style", command=self.generate_random_style)
        generate_style_btn.grid(column=2, row=0, sticky=tk.W, padx=5)
        ToolTip(generate_style_btn, "Generate a random predefined style")

        save_style_btn = ttk.Button(style_frame, text="Save Style", command=self.save_current_style)
        save_style_btn.grid(column=3, row=0, sticky=tk.W, padx=5)
        ToolTip(save_style_btn, "Save the current style settings")

        ttk.Label(style_frame, text="Prefix:").grid(column=0, row=1, sticky=tk.W, pady=5)
        self.style_prefix_entry = ttk.Entry(style_frame, width=50)
        self.style_prefix_entry.grid(column=1, row=1, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        ToolTip(self.style_prefix_entry, "Enter the style prefix")

        ttk.Label(style_frame, text="Suffix:").grid(column=0, row=2, sticky=tk.W, pady=5)
        self.style_suffix_entry = ttk.Entry(style_frame, width=50)
        self.style_suffix_entry.grid(column=1, row=2, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        ToolTip(self.style_suffix_entry, "Enter the style suffix")

        generate_details_btn = ttk.Button(style_frame, text="Generate Style Details", command=self.generate_style_details)
        generate_details_btn.grid(column=1, row=3, sticky=tk.E, pady=5)
        ToolTip(generate_details_btn, "Generate a suffix based on the entered prefix")

        # Script
        ttk.Label(input_frame, text="📜 Script:").grid(column=0, row=4, sticky=tk.W, pady=5)
        self.script_text = scrolledtext.ScrolledText(input_frame, height=10, width=50, wrap=tk.WORD)
        self.script_text.grid(column=1, row=4, sticky=(tk.W, tk.E), pady=5)
        self.script_text.insert(tk.END, "")
        self.script_text.bind("<<Selection>>", self.on_script_selection)

        # Stick to Script Checkbox
        self.stick_to_script_var = tk.BooleanVar()
        self.stick_to_script_check = ttk.Checkbutton(input_frame, text="📌 Stick to Script", variable=self.stick_to_script_var)
        self.stick_to_script_check.grid(column=1, row=5, sticky=tk.W, pady=5)

        # Camera Shot
        ttk.Label(input_frame, text="📷 Camera Shot:").grid(column=0, row=6, sticky=tk.W, pady=5)
        self.shot_var = tk.StringVar()
        self.shot_combo = ttk.Combobox(input_frame, textvariable=self.shot_var, values=[
            "None", "Wide Shot", "Long Shot", "Full Shot", "Medium Shot", "Close-up", "Extreme Close-up",
            "Point of View Shot", "Over the Shoulder Shot", "Low Angle Shot", "High Angle Shot",
            "Dutch Angle Shot", "Bird's Eye View", "Worm's Eye View"
        ], width=47)
        self.shot_combo.grid(column=1, row=6, sticky=(tk.W, tk.E), pady=5)
        self.shot_combo.set("None")

        # Camera Move
        ttk.Label(input_frame, text="🎥 Camera Move:").grid(column=0, row=7, sticky=tk.W, pady=5)
        self.move_var = tk.StringVar()
        self.move_combo = ttk.Combobox(input_frame, textvariable=self.move_var, values=[
            "None", "Static", "Pan", "Tilt", "Zoom", "Dolly", "Truck", "Pedestal", "Crane Shot",
            "Steadicam", "Handheld", "Tracking Shot", "Pull Focus"
        ], width=47)
        self.move_combo.grid(column=1, row=7, sticky=(tk.W, tk.E), pady=5)
        self.move_combo.set("None")

        # End Parameters
        ttk.Label(input_frame, text="End Parameters:").grid(column=0, row=8, sticky=tk.W, pady=5)
        self.end_parameters_entry = ttk.Entry(input_frame, width=50)
        self.end_parameters_entry.grid(column=1, row=8, sticky=(tk.W, tk.E), pady=5)

        # Generate Button
        self.generate_button = ttk.Button(input_frame, text="🚀 Generate Prompt", command=self.generate_button_click)
        self.generate_button.grid(column=1, row=9, sticky=tk.E, pady=10)

        # Add Undo and Redo buttons
        undo_redo_frame = ttk.Frame(input_frame)
        undo_redo_frame.grid(column=1, row=10, sticky=tk.E, pady=5)

        self.undo_button = ttk.Button(undo_redo_frame, text="↩ Undo", command=self.undo)
        self.undo_button.pack(side=tk.LEFT, padx=2)

        self.redo_button = ttk.Button(undo_redo_frame, text="Redo ↪", command=self.redo)
        self.redo_button.pack(side=tk.LEFT, padx=2)

        input_frame.columnconfigure(1, weight=1)

        # Bind keyboard shortcuts
        self.master.bind('<Control-z>', lambda event: self.undo())
        self.master.bind('<Control-y>', lambda event: self.redo())

    async def handle_generate_button_click(self):
        try:
            # Get input values
            shot_description = self.shot_text.get("1.0", tk.END).strip()
            style_prefix = self.style_prefix_entry.get()
            style_suffix = self.style_suffix_entry.get()
            camera_shot = self.shot_var.get()
            camera_move = self.move_var.get()
            directors_notes = self.notes_text.get("1.0", tk.END).strip()
            script = self.script_text.get("1.0", tk.END).strip()
            stick_to_script = self.stick_to_script_var.get()
            end_parameters = self.end_parameters_entry.get()
            length = "medium"  # You can add a dropdown for this if you want to let users choose

            # Generate prompt
            prompt = await self.core.generate_prompt(
                shot_description=shot_description,
                style_prefix=style_prefix,
                style_suffix=style_suffix,
                camera_shot=camera_shot,
                camera_move=camera_move,
                directors_notes=directors_notes,
                script=script,
                stick_to_script=stick_to_script,
                end_parameters=end_parameters,
                length=length
            )

            # Display generated prompt
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert(tk.END, prompt)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def generate_button_click(self):
        asyncio.create_task(self.handle_generate_button_click())

    def create_output_area(self, parent):
        output_frame = ttk.LabelFrame(parent, text="Generated Prompt", padding="10")
        output_frame.pack(fill="both", expand=True)

        # Create a PanedWindow to allow resizing
        paned_window = ttk.PanedWindow(output_frame, orient=tk.VERTICAL)
        paned_window.pack(fill="both", expand=True)

        # Add the ScrolledText widget to the PanedWindow
        self.results_text = scrolledtext.ScrolledText(paned_window, wrap=tk.WORD)
        paned_window.add(self.results_text, weight=1)

        button_frame = ttk.Frame(output_frame)
        button_frame.pack(fill="x", pady=5)

        self.save_button = ttk.Button(button_frame, text="Save Prompt", command=self.save_prompt)
        self.save_button.pack(side="left", padx=2)

        self.copy_button = ttk.Button(button_frame, text="Copy to Clipboard", command=self.copy_prompt_to_clipboard)
        self.copy_button.pack(side="left", padx=2)

        self.show_prompts_button = ttk.Button(button_frame, text="Show All Prompts", command=self.show_all_prompts)
        self.show_prompts_button.pack(side="left", padx=2)

        self.show_logs_button = ttk.Button(button_frame, text="Show Logs", command=self.show_logs)
        self.show_logs_button.pack(side="left", padx=2)

    def save_prompt(self):
        prompt = self.results_text.get("1.0", tk.END).strip()
        if prompt:
            components = {
                "style": self.style_entry.get(),
                "shot_description": self.shot_text.get("1.0", tk.END).strip(),
                "camera_move": self.move_var.get(),
                "directors_notes": self.notes_text.get("1.0", tk.END).strip(),
                "script": self.script_text.get("1.0", tk.END).strip(),
                "stick_to_script": self.stick_to_script_var.get()
            }
            self.core.save_prompt(prompt, components)
            messagebox.showinfo("Saved", "Prompt saved successfully!")
        else:
            messagebox.showwarning("Empty Prompt", "There is no prompt to save.")

    def copy_prompt_to_clipboard(self):
        prompt = self.results_text.get("1.0", tk.END).strip()
        pyperclip.copy(prompt)
        messagebox.showinfo("Copied", "Prompt copied to clipboard!")

    def show_all_prompts(self):
        if self.all_prompts_window is None or not self.all_prompts_window.winfo_exists():
            self.all_prompts_window = tk.Toplevel(self.master)
            self.all_prompts_window.title("All Saved Prompts")
            self.all_prompts_window.geometry("600x400")

            self.all_prompts_text = scrolledtext.ScrolledText(self.all_prompts_window, wrap=tk.WORD)
            self.all_prompts_text.pack(expand=True, fill="both", padx=10, pady=10)

        self.all_prompts_text.delete("1.0", tk.END)
        saved_prompts = self.core.meta_chain.prompt_manager.get_all_prompts()
        for i, prompt_data in enumerate(saved_prompts, 1):
            self.all_prompts_text.insert(tk.END, f"Prompt {i}:\n{prompt_data['prompt']}\n\n")

        self.all_prompts_window.lift()

    def show_logs(self):
        log_window = tk.Toplevel(self.master)
        log_window.title("Application Logs")
        log_window.geometry("800x600")

        log_text = scrolledtext.ScrolledText(log_window, wrap=tk.WORD)
        log_text.pack(expand=True, fill="both", padx=10, pady=10)

        # Read the log file and display its contents
        try:
            with open("promptforge.log", "r") as log_file:
                log_content = log_file.read()
                log_text.insert(tk.END, log_content)
        except FileNotFoundError:
            log_text.insert(tk.END, "Log file not found.")
        except Exception as e:
            log_text.insert(tk.END, f"Error reading log file: {str(e)}")

        log_window.lift()

    # Removed update_model_list method as it's no longer needed

    def save_api_key(self):
        api_key = self.api_key_entry.get()
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            messagebox.showinfo("Success", "API Key saved successfully!")
        else:
            messagebox.showerror("Error", "Please enter an API Key")

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

    def on_script_selection(self, event):
        try:
            if self.script_text.tag_ranges(tk.SEL):
                selected_text = self.script_text.get(tk.SEL_FIRST, tk.SEL_LAST)
                logging.info(f"Selected text: {selected_text}")
            else:
                logging.info("No text selected")
        except Exception as e:
            logging.error(f"Error in on_script_selection: {str(e)}")
        finally:
            # Schedule the UI update for the next idle moment
            self.master.after_idle(self.master.update_idletasks)

    def on_style_selected(self, event):
        selected_style = self.style_combo.get()
        if selected_style == "None":
            self.style_prefix_entry.delete(0, tk.END)
            self.style_suffix_entry.delete(0, tk.END)
        else:
            style_data = self.core.style_manager.get_style(selected_style)
            self.style_prefix_entry.delete(0, tk.END)
            self.style_prefix_entry.insert(0, style_data["prefix"])
            self.style_suffix_entry.delete(0, tk.END)
            self.style_suffix_entry.insert(0, style_data["suffix"])

    def generate_random_style(self):
        random_style = random.choice(list(predefined_styles.keys()))
        self.style_combo.set(random_style)
        self.on_style_selected(None)

    def save_current_style(self):
        style_name = self.style_combo.get()
        prefix = self.style_prefix_entry.get()
        suffix = self.style_suffix_entry.get()
        if style_name and prefix and suffix:
            self.core.style_manager.add_style(style_name, prefix, suffix)
            self.style_combo['values'] = self.core.style_manager.get_style_names()
            messagebox.showinfo("Style Saved", f"Style '{style_name}' has been saved.")
        else:
            messagebox.showerror("Error", "Please enter a style name, prefix, and suffix.")

    def generate_style_details(self):
        prefix = self.style_prefix_entry.get()
        if prefix:
            # Call the AI model to generate detailed visual descriptors
            suffix = self.core.generate_style_details(prefix)
            self.style_suffix_entry.delete(0, tk.END)
            self.style_suffix_entry.insert(0, suffix)
        else:
            messagebox.showerror("Error", "Please enter a style prefix first.")

    def undo(self):
        current_state = self.core.undo()
        self._update_ui_from_state(current_state)

    def redo(self):
        current_state = self.core.redo()
        self._update_ui_from_state(current_state)

    def _update_ui_from_state(self, state):
        # Update UI elements with the current state
        self.shot_text.delete("1.0", tk.END)
        self.shot_text.insert(tk.END, state['shot_description'])

        self.notes_text.delete("1.0", tk.END)
        self.notes_text.insert(tk.END, state['directors_notes'])

        self.script_text.delete("1.0", tk.END)
        self.script_text.insert(tk.END, state['script'])

        self.stick_to_script_var.set(state['stick_to_script'])

        self.style_prefix_entry.delete(0, tk.END)
        self.style_prefix_entry.insert(0, state['style_prefix'])

        self.style_suffix_entry.delete(0, tk.END)
        self.style_suffix_entry.insert(0, state['style_suffix'])

        self.end_parameters_entry.delete(0, tk.END)
        self.end_parameters_entry.insert(0, state['end_parameters'])

        # Update subjects
        self.subject_frame.update_subjects(state['subjects'])

    # ... (rest of the PromptForgeUI methods remain unchanged)

def main():
    root = tk.Tk()
    app = Page2PromptUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
