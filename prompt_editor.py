import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import re
import json
import os
from core import PromptForgeCore

class PromptEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Enhanced Prompt Editor")
        self.master.geometry(config.get('UI_SETTINGS', 'prompt_editor_geometry'))

        self.core = PromptForgeCore()
        self.prompts = {}
        self.current_file = ""

        self.setup_ui()
        self.load_prompts_from_files()

    def setup_ui(self):
        main_paned = PanedWindow(self.master, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(main_paned)
        right_frame = ttk.Frame(main_paned)

        main_paned.add(left_frame, weight=1)
        main_paned.add(right_frame, weight=3)

        # Left frame contents
        self.prompt_listbox = tk.Listbox(left_frame)
        self.prompt_listbox.pack(fill=tk.BOTH, expand=True)
        self.prompt_listbox.bind('<<ListboxSelect>>', self.on_prompt_select)

        # Right frame contents
        self.setup_editor_area(right_frame)

        # Bottom frame for buttons
        button_frame = ttk.Frame(self.master)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(button_frame, text="Save Changes", command=self.save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reload Prompts", command=self.load_prompts_from_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save to File", command=self.save_to_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load from File", command=self.load_from_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test Prompt", command=self.test_prompt).pack(side=tk.LEFT, padx=5)

        # Load saved pane position
        sash_pos = config.get('UI_SETTINGS', 'prompt_editor_sash')
        if sash_pos:
            main_paned.sashpos(0, int(sash_pos))

        # Bind pane position saving
        main_paned.bind("<ButtonRelease-1>", self.save_pane_position)

    def save_pane_position(self, event=None):
        config.set('UI_SETTINGS', 'prompt_editor_sash', str(event.widget.sashpos(0)))

    def setup_editor_area(self, parent):
        editor_frame = ttk.Frame(parent)
        editor_frame.pack(fill=tk.BOTH, expand=True)

        # Prompt editing area
        self.prompt_text = scrolledtext.ScrolledText(editor_frame, wrap=tk.WORD, height=20)
        self.prompt_text.pack(fill=tk.BOTH, expand=True)

        # Input variables area
        input_frame = ttk.LabelFrame(editor_frame, text="Input Variables")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.input_vars = {}
        for var in ["style", "shot_description", "directors_notes", "highlighted_text", "full_script", "subject_info", "length", "camera_shot", "camera_move", "end_parameters"]:
            var_frame = ttk.Frame(input_frame)
            var_frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(var_frame, text=f"{var}:").pack(side=tk.LEFT)
            self.input_vars[var] = tk.StringVar()
            ttk.Entry(var_frame, textvariable=self.input_vars[var]).pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Output area
        output_frame = ttk.LabelFrame(editor_frame, text="Generated Output")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=10)
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def load_prompts_from_files(self):
        self.prompts = {}
        for file in ['core.py', 'ui.py', 'meta_chain.py']:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                    prompt_matches = re.findall(r'(?:f|r)"""(.*?)"""', content, re.DOTALL)
                    for i, match in enumerate(prompt_matches):
                        self.prompts[f"{file}_{i}"] = match.strip()
            except Exception as e:
                messagebox.showerror("Error", f"Error loading prompts from {file}: {str(e)}")

        self.update_prompt_list()

    def update_prompt_list(self):
        self.prompt_listbox.delete(0, tk.END)
        for key in self.prompts.keys():
            self.prompt_listbox.insert(tk.END, key)

    def on_prompt_select(self, event):
        selection = self.prompt_listbox.curselection()
        if selection:
            key = self.prompt_listbox.get(selection[0])
            self.current_file = key
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.insert(tk.END, self.prompts[key])
            self.highlight_variables()

    def highlight_variables(self):
        self.prompt_text.tag_remove("variable", "1.0", tk.END)
        content = self.prompt_text.get("1.0", tk.END)
        for match in re.finditer(r'\{(\w+)\}', content):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.prompt_text.tag_add("variable", start, end)
        self.prompt_text.tag_config("variable", foreground="blue", underline=True)

    def save_changes(self):
        if not self.current_file:
            messagebox.showerror("Error", "No prompt selected")
            return

        new_prompt = self.prompt_text.get("1.0", tk.END).strip()
        self.prompts[self.current_file] = new_prompt

        file, _ = self.current_file.split('_')
        try:
            with open(file, "r") as f:
                content = f.read()

            updated_content = re.sub(
                r'(?:f|r)""".*?"""',
                f'f"""{new_prompt}"""',
                content,
                count=1,
                flags=re.DOTALL
            )

            with open(file, "w") as f:
                f.write(updated_content)

            messagebox.showinfo("Success", f"Changes saved successfully to {file}!")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving changes: {str(e)}")

    def save_to_file(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.prompts, f, indent=2)
                messagebox.showinfo("Success", f"Prompts saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving prompts: {str(e)}")

    def load_from_file(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if filename:
            try:
                with open(filename, 'r') as f:
                    self.prompts = json.load(f)
                self.update_prompt_list()
                messagebox.showinfo("Success", f"Prompts loaded from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error loading prompts: {str(e)}")

    def test_prompt(self):
        if not self.current_file:
            messagebox.showerror("Error", "No prompt selected")
            return

        prompt_template = self.prompt_text.get("1.0", tk.END).strip()
        input_values = {var: self.input_vars[var].get() for var in self.input_vars}

        try:
            result = self.core.meta_chain.generate_prompt(**input_values)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, result)
        except Exception as e:
            messagebox.showerror("Error", f"Error testing prompt: {str(e)}")

def main():
    root = tk.Tk()
    PromptEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
