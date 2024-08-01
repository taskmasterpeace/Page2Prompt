import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import re
import json
import os

class PromptEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Prompt Editor")
        self.master.geometry("1000x700")

        self.prompts = {}
        self.current_file = ""

        self.setup_ui()
        self.load_prompts_from_files()

    def setup_ui(self):
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.prompt_listbox = tk.Listbox(left_frame, width=40)
        self.prompt_listbox.pack(fill=tk.Y, expand=True)
        self.prompt_listbox.bind('<<ListboxSelect>>', self.on_prompt_select)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.prompt_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD)
        self.prompt_text.pack(fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(self.master)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(button_frame, text="Save Changes", command=self.save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reload Prompts", command=self.load_prompts_from_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save to File", command=self.save_to_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load from File", command=self.load_from_file).pack(side=tk.LEFT, padx=5)

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

def main():
    root = tk.Tk()
    PromptEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
