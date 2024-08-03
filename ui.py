# ui.py

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, simpledialog
from tkinterdnd2 import DND_TEXT, TkinterDnD
from tkinter.ttk import Frame, Scrollbar, PanedWindow
import pyperclip
from core import PromptForgeCore
import os
import asyncio
import random
from styles import predefined_styles
from functools import partial
from config import config

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
        category_icons = {
            "Main Character": "👤",
            "Supporting Character": "👥",
            "Location": "🏠",
            "Object": "🔮"
        }
        for subject in subjects:
            status = 'Active' if subject.get('active', True) else 'Inactive'
            icon = category_icons.get(subject['category'], "❓")
            self.subjects_listbox.insert(tk.END, f"{icon} {subject['name']} ({subject['category']}) ({status})")

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
        self.subjects_listbox.bind('<<ListboxSelect>>', self.on_subject_select)

        button_frame = ttk.Frame(self)
        button_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.toggle_button = ttk.Button(button_frame, text="Toggle Active", command=self.toggle_subject)
        self.toggle_button.pack(side="left", padx=2)

        self.edit_button = ttk.Button(button_frame, text="Edit Subject", command=self.edit_subject)
        self.edit_button.pack(side="left", padx=2)

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
            self.update_subjects(self.core.subjects)  # Update the listbox with all subjects
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

    def on_subject_select(self, event):
        selected = self.subjects_listbox.curselection()
        if selected:
            index = selected[0]
            subject = self.core.subjects[index]
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, subject['name'])
            self.category_combo.set(subject['category'])
            self.description_text.delete("1.0", tk.END)
            self.description_text.insert(tk.END, subject['description'])

    def edit_subject(self):
        try:
            selected = self.subjects_listbox.curselection()
            if not selected:
                raise ValueError("No subject selected")
            
            index = selected[0]
            name = self.name_entry.get().strip()
            category = self.category_combo.get()
            description = self.description_text.get("1.0", tk.END).strip()

            if not name or not category or not description:
                raise ValueError("All fields must be filled")

            self.core.subjects[index] = {
                'name': name,
                'category': category,
                'description': description,
                'active': self.core.subjects[index]['active']
            }
            self.update_subjects(self.core.subjects)
            messagebox.showinfo("Success", "Subject updated successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))

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

        generate_subjects_button = ttk.Button(self, text="Generate Subjects", command=self.generate_subjects)
        generate_subjects_button.grid(row=2, column=1, sticky="e", padx=5, pady=5)
        ToolTip(generate_subjects_button, "Analyze the script and generate subjects")

        self.results_text = scrolledtext.ScrolledText(self, height=8, width=60)
        self.results_text.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=5, pady=2)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)

    def generate_subjects(self):
        script_content = self.script_path.get()
        if not script_content:
            messagebox.showerror("Error", "Please select a script file.")
            return

        try:
            with open(script_content, 'r') as file:
                script_text = file.read()

            subjects = self.core.generate_subjects(script_text)
            if not subjects:
                messagebox.showinfo("No Subjects Found", "No subjects were generated. Please refine your script and try again.")
                return
            self.show_subject_selection_window(subjects)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def show_subject_selection_window(self, subjects):
        selection_window = tk.Toplevel(self.master)
        selection_window.title("Generated Subjects")
        selection_window.geometry("600x400")

        main_frame = ttk.Frame(selection_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for subject in subjects:
            subject_frame = ttk.Frame(scrollable_frame)
            subject_frame.pack(fill=tk.X, padx=5, pady=5)

            ttk.Label(subject_frame, text=subject['name'], font=("TkDefaultFont", 12, "bold")).grid(row=0, column=0, sticky="w")

            var = tk.BooleanVar(value=True)
            check = ttk.Checkbutton(subject_frame, variable=var)
            check.grid(row=0, column=1, sticky="e")

            category_var = tk.StringVar(value=subject['category'])
            category_combo = ttk.Combobox(subject_frame, textvariable=category_var, 
                                          values=["Main Character", "Supporting Character", "Location", "Object"])
            category_combo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=2)

            description_text = scrolledtext.ScrolledText(subject_frame, height=4, width=40, wrap=tk.WORD)
            description_text.grid(row=2, column=0, columnspan=2, pady=2)
            description_text.insert(tk.END, subject['description'])

            subject['var'] = var
            subject['category_var'] = category_var
            subject['description_text'] = description_text

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        button_frame = ttk.Frame(selection_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Select All", command=lambda: self.toggle_all_subjects(subjects, True)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Deselect All", command=lambda: self.toggle_all_subjects(subjects, False)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Add Selected", command=lambda: self.add_selected_subjects(subjects, selection_window)).pack(side="right", padx=5)

    def toggle_all_subjects(self, subjects, state):
        for subject in subjects:
            subject['var'].set(state)

    def add_selected_subjects(self, subjects, window):
        for subject in subjects:
            if subject['var'].get():
                self.core.add_subject(
                    name=subject['name'],
                    category=subject['category_var'].get(),
                    description=subject['description_text'].get("1.0", tk.END).strip()
                )
        self.subject_frame.update_subjects(self.core.subjects)
        window.destroy()

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

    def generate_subjects(self):
        script_content = self.script_path.get()
        if not script_content:
            messagebox.showerror("Error", "Please select a script file.")
            return

        try:
            with open(script_content, 'r') as file:
                script_text = file.read()

            subjects = self.core.generate_subjects(script_text)
            self.show_subject_selection_window(subjects)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def show_subject_selection_window(self, subjects):
        selection_window = tk.Toplevel(self.master)
        selection_window.title("Generated Subjects")
        selection_window.geometry("600x400")

        main_frame = ttk.Frame(selection_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for subject in subjects:
            subject_frame = ttk.Frame(scrollable_frame)
            subject_frame.pack(fill=tk.X, padx=5, pady=5)

            var = tk.BooleanVar(value=True)
            check = ttk.Checkbutton(subject_frame, text=subject['name'], variable=var)
            check.grid(row=0, column=0, sticky="w")

            category_var = tk.StringVar(value=subject['category'])
            category_combo = ttk.Combobox(subject_frame, textvariable=category_var, 
                                          values=["Main Character", "Supporting Character", "Location", "Object"])
            category_combo.grid(row=0, column=1, padx=5)

            description_text = scrolledtext.ScrolledText(subject_frame, height=4, width=40, wrap=tk.WORD)
            description_text.grid(row=1, column=0, columnspan=2, pady=5)
            description_text.insert(tk.END, subject['description'])

            subject['var'] = var
            subject['category_var'] = category_var
            subject['description_text'] = description_text

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        button_frame = ttk.Frame(selection_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Select All", command=lambda: self.toggle_all_subjects(subjects, True)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Deselect All", command=lambda: self.toggle_all_subjects(subjects, False)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Add Selected", command=lambda: self.add_selected_subjects(subjects, selection_window)).pack(side="right", padx=5)

    def toggle_all_subjects(self, subjects, state):
        for subject in subjects:
            subject['var'].set(state)

    def add_selected_subjects(self, subjects, window):
        for subject in subjects:
            if subject['var'].get():
                self.core.add_subject(
                    name=subject['name'],
                    category=subject['category_var'].get(),
                    description=subject['description_text'].get("1.0", tk.END).strip()
                )
        self.subject_frame.update_subjects(self.core.subjects)
        window.destroy()

    def generate_subjects(self):
        script_content = self.script_path.get()
        if not script_content:
            messagebox.showerror("Error", "Please select a script file.")
            return

        try:
            with open(script_content, 'r') as file:
                script_text = file.read()

            subjects = self.core.generate_subjects(script_text)
            if not subjects:
                messagebox.showinfo("No Subjects Found", "No subjects were generated. Please refine your script and try again.")
                return
            self.show_subject_selection_window(subjects)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def show_subject_selection_window(self, subjects):
        selection_window = tk.Toplevel(self.master)
        selection_window.title("Generated Subjects")
        selection_window.geometry("600x400")

        main_frame = ttk.Frame(selection_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for subject in subjects:
            subject_frame = ttk.Frame(scrollable_frame)
            subject_frame.pack(fill=tk.X, padx=5, pady=5)

            ttk.Label(subject_frame, text=subject['name'], font=("TkDefaultFont", 12, "bold")).grid(row=0, column=0, sticky="w")

            var = tk.BooleanVar(value=True)
            check = ttk.Checkbutton(subject_frame, variable=var)
            check.grid(row=0, column=1, sticky="e")

            category_var = tk.StringVar(value=subject['category'])
            category_combo = ttk.Combobox(subject_frame, textvariable=category_var, 
                                          values=["Main Character", "Supporting Character", "Location", "Object"])
            category_combo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=2)

            description_text = scrolledtext.ScrolledText(subject_frame, height=4, width=40, wrap=tk.WORD)
            description_text.grid(row=2, column=0, columnspan=2, pady=2)
            description_text.insert(tk.END, subject['description'])

            subject['var'] = var
            subject['category_var'] = category_var
            subject['description_text'] = description_text

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        button_frame = ttk.Frame(selection_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Select All", command=lambda: self.toggle_all_subjects(subjects, True)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Deselect All", command=lambda: self.toggle_all_subjects(subjects, False)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Add Selected", command=lambda: self.add_selected_subjects(subjects, selection_window)).pack(side="right", padx=5)

    def toggle_all_subjects(self, subjects, state):
        for subject in subjects:
            subject['var'].set(state)

    def add_selected_subjects(self, subjects, window):
        for subject in subjects:
            if subject['var'].get():
                self.core.add_subject(
                    name=subject['name'],
                    category=subject['category_var'].get(),
                    description=subject['description_text'].get("1.0", tk.END).strip()
                )
        self.subject_frame.update_subjects(self.core.subjects)
        window.destroy()

    # ... (rest of the AutomatedAnalysisFrame methods remain unchanged)

class TimelineView(ttk.Frame):
    def __init__(self, master, core):
        super().__init__(master)
        self.core = core
        self.setup_ui()

    def setup_ui(self):
        # Create the scrollable canvas
        self.canvas = tk.Canvas(self, width=400, height=300)
        self.scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Frame to hold sentence nodes
        self.timeline_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.timeline_frame, anchor="nw")

        # Bind events for scrolling and zooming
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.bind("<Control-plus>", self.zoom_in)
        self.bind("<Control-minus>", self.zoom_out)

        self.zoom_level = 100
        self.sentence_nodes = []

    def on_canvas_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event):
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def zoom_in(self, event):
        self.zoom_level = min(200, self.zoom_level + 50)
        self.update_zoom()

    def zoom_out(self, event):
        self.zoom_level = max(50, self.zoom_level - 50)
        self.update_zoom()

    def update_zoom(self):
        # Update the size of sentence nodes based on zoom level
        for node in self.sentence_nodes:
            node.update_size(self.zoom_level)

    def add_sentence_node(self, sentence):
        node = SentenceNode(self.timeline_frame, sentence, self.zoom_level)
        node.pack(side="left", padx=5, pady=5)
        self.sentence_nodes.append(node)
        return node

    def clear_timeline(self):
        for node in self.sentence_nodes:
            node.destroy()
        self.sentence_nodes.clear()

    def reorder_nodes(self, source_sentence, target_sentence):
        source_index = next(i for i, node in enumerate(self.sentence_nodes) if node.sentence == source_sentence)
        target_index = next(i for i, node in enumerate(self.sentence_nodes) if node.sentence == target_sentence)

        node = self.sentence_nodes.pop(source_index)
        self.sentence_nodes.insert(target_index, node)

        for i, node in enumerate(self.sentence_nodes):
            node.pack_forget()
            node.pack(side="left", padx=5, pady=5)

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

class SentenceNode(TkinterDnD.Tk):
    def __init__(self, master, sentence, zoom_level):
        super().__init__(master)
        self.sentence = sentence
        self.zoom_level = zoom_level
        self.setup_ui()

    def setup_ui(self):
        self.label = ttk.Label(self, text=self.sentence, wraplength=200)
        self.label.pack(pady=5)

        self.add_card_button = ttk.Button(self, text="➕ Add Card", command=self.add_card)
        self.add_card_button.pack(pady=5)

        self.cards = []

        self.drag_source_register(DND_TEXT)
        self.drop_target_register(DND_TEXT)

        self.dnd_bind('<<DragInitCmd>>', self.drag_init)
        self.dnd_bind('<<DropEnter>>', self.drop_enter)
        self.dnd_bind('<<DropLeave>>', self.drop_leave)
        self.dnd_bind('<<Drop>>', self.drop)

    def add_card(self, prompt=""):
        if len(self.cards) < 4:
            card = PromptCard(self, prompt)
            card.pack(pady=2)
            self.cards.append(card)

    def update_size(self, zoom_level):
        self.zoom_level = zoom_level
        width = int(200 * (zoom_level / 100))
        self.label.configure(wraplength=width)

    def drag_init(self, event):
        return (DND_TEXT, self.sentence)

    def drop_enter(self, event):
        event.widget.focus_set()
        return event.action

    def drop_leave(self, event):
        return event.action

    def drop(self, event):
        if event.data:
            self.master.master.reorder_nodes(event.data, self.sentence)
        return event.action

class PromptCard(ttk.Frame):
    def __init__(self, master, prompt=""):
        super().__init__(master)
        self.prompt = prompt
        self.setup_ui()

    def setup_ui(self):
        self.label = ttk.Label(self, text=self.prompt or "📝 Prompt Card")
        self.label.pack(pady=2)

        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="✂️ Cut", command=self.cut)
        self.menu.add_command(label="📋 Copy", command=self.copy)
        self.menu.add_command(label="📌 Paste", command=self.paste)
        self.menu.add_command(label="🗑️ Remove", command=self.remove)

        self.bind("<Button-3>", self.show_menu)

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def cut(self):
        self.copy()
        self.remove()

    def copy(self):
        self.clipboard_clear()
        self.clipboard_append(self.prompt)

    def paste(self):
        pasted_text = self.clipboard_get()
        self.prompt = pasted_text
        self.label.config(text=self.prompt)

    def remove(self):
        self.master.cards.remove(self)
        self.destroy()

class PageToPromptUI:
    def __init__(self, master):
        self.master = master
        self.core = PromptForgeCore()
        self.loop = asyncio.get_event_loop()
        self.setup_ui()
        self.all_prompts_window = None
        self.all_prompts_text = None
        self.timeline_view = None

    def setup_ui(self):
        self.master.title("🎬 Page to Prompt - Bring Your Script to Life")
        self.master.configure(bg='#f0f0f0')  # Light gray background

        style = ttk.Style()
        style.theme_use('clam')  # Use a modern-looking theme
        style.configure("TFrame", background='#f0f0f0')
        style.configure("TLabel", background='#f0f0f0', font=('Helvetica', 10))
        style.configure("TButton", font=('Helvetica', 10))
        style.configure("TEntry", font=('Helvetica', 10))
        style.configure("TCombobox", font=('Helvetica', 10))

        self.main_paned = PanedWindow(self.master, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(self.main_paned)
        right_frame = ttk.Frame(self.main_paned)

        self.main_paned.add(left_frame, weight=1)
        self.main_paned.add(right_frame, weight=1)

        # Left Frame Contents
        self.create_input_fields(left_frame)

        # Right Frame Contents
        self.right_paned = PanedWindow(right_frame, orient=tk.VERTICAL)
        self.right_paned.pack(fill=tk.BOTH, expand=True)

        output_frame = ttk.Frame(self.right_paned)
        subject_frame = ttk.Frame(self.right_paned)

        self.right_paned.add(output_frame, weight=1)
        self.right_paned.add(subject_frame, weight=1)

        self.create_output_area(output_frame)
        self.create_subject_frame(subject_frame)

        # Add Timeline View
        self.timeline_view = TimelineView(left_frame, self.core)
        self.timeline_view.pack(fill="both", expand=True, pady=(10, 0))

        # Bind event to prevent losing selection
        self.master.bind("<Button-1>", self.maintain_selection)

        # Load saved pane positions
        self.load_pane_positions()

        # Bind pane position saving
        self.main_paned.bind("<ButtonRelease-1>", self.save_pane_positions)
        self.right_paned.bind("<ButtonRelease-1>", self.save_pane_positions)

    def load_pane_positions(self):
        main_sash = config.get('UI_SETTINGS', 'main_paned_sash')
        right_sash = config.get('UI_SETTINGS', 'right_paned_sash')

        if main_sash:
            self.main_paned.sashpos(0, int(main_sash))
        if right_sash:
            self.right_paned.sashpos(0, int(right_sash))

    def save_pane_positions(self, event=None):
        config.set('UI_SETTINGS', 'main_paned_sash', str(self.main_paned.sashpos(0)))
        config.set('UI_SETTINGS', 'right_paned_sash', str(self.right_paned.sashpos(0)))

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
        self.script_text.bind("<<Selection>>", partial(self.on_script_selection))

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

        # Generate Button and Save as Template
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(column=1, row=9, sticky=tk.E, pady=10)

        self.generate_button = ttk.Button(button_frame, text="🚀 Generate Prompt", command=self.generate_button_click)
        self.generate_button.pack(side=tk.LEFT, padx=2)

        self.save_template_button = ttk.Button(button_frame, text="💾 Save as Template", command=self.save_as_template)
        self.save_template_button.pack(side=tk.LEFT, padx=2)

        # Template Management
        template_frame = ttk.Frame(input_frame)
        template_frame.grid(column=1, row=10, sticky=tk.E, pady=5)

        self.load_template_var = tk.StringVar()
        self.load_template_combo = ttk.Combobox(template_frame, textvariable=self.load_template_var, width=20)
        self.load_template_combo.pack(side=tk.LEFT, padx=2)
        self.load_template_combo.bind("<<ComboboxSelected>>", self.load_template)

        self.update_template_list()

        input_frame.columnconfigure(1, weight=1)

    async def handle_generate_button_click(self):
        try:
            # Get input values
            shot_description = self.shot_text.get("1.0", tk.END).strip()
            style_prefix = self.style_prefix_entry.get().strip()
            style_suffix = self.style_suffix_entry.get().strip()
            directors_notes = self.notes_text.get("1.0", tk.END).strip()
            stick_to_script = self.stick_to_script_var.get()
            script = self.script_text.get("1.0", tk.END).strip() if stick_to_script else ""
            end_parameters = self.end_parameters_entry.get()

            # Error checking
            if not shot_description:
                raise ValueError("Shot description is required.")

            style = f"{style_prefix}{style_suffix}"

            # Generate prompts
            prompts = await self.core.generate_prompt(
                style=style,
                highlighted_text="",
                shot_description=shot_description,
                directors_notes=directors_notes,
                script=script,
                stick_to_script=stick_to_script,
                end_parameters=end_parameters
            )

            # Display generated prompts
            self.results_text.delete("1.0", tk.END)
            for length, prompt in prompts.items():
                self.results_text.insert(tk.END, f"{length.capitalize()} Prompt:\n{prompt}\n\n")

        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {str(e)}\n\nPlease report this to the developer.")

    def generate_button_click(self):
        asyncio.create_task(self.handle_generate_button_click())

    def add_prompt_to_timeline(self):
        prompt = self.results_text.get("1.0", tk.END).strip()
        if prompt:
            selected_sentence = self.get_selected_sentence()
            if selected_sentence:
                for node in self.timeline_view.sentence_nodes:
                    if node.sentence == selected_sentence:
                        node.add_card(prompt)
                        break
            else:
                messagebox.showwarning("No Sentence Selected", "Please select a sentence in the script to add the prompt to.")
        else:
            messagebox.showwarning("Empty Prompt", "There is no prompt to add to the timeline.")

    def get_selected_sentence(self):
        try:
            cursor_pos = self.script_text.index(tk.INSERT)
            line_start = self.script_text.index(f"{cursor_pos} linestart")
            line_end = self.script_text.index(f"{cursor_pos} lineend")
            return self.script_text.get(line_start, line_end).strip()
        except:
            return None

    def handle_script_update(self):
        script = self.script_text.get("1.0", tk.END).strip()
        sentences = self.core.parse_script_into_sentences(script)
        self.timeline_view.clear_timeline()
        for sentence in sentences:
            self.timeline_view.add_sentence_node(sentence)

    def save_project(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json")
        if filename:
            self.core.save_project(filename)
            messagebox.showinfo("Project Saved", f"Project saved to {filename}")

    def load_project(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            self.core.load_project(filename)
            self.update_ui_from_project()

    def update_ui_from_project(self):
        # Update script text area
        self.script_text.delete("1.0", tk.END)
        self.script_text.insert(tk.END, self.core.script)

        # Update timeline view
        self.timeline_view.clear_timeline()
        for sentence, prompts in self.core.get_timeline_data().items():
            node = self.timeline_view.add_sentence_node(sentence)
            for prompt in prompts:
                node.add_card(prompt)

        # Update other UI elements as needed
        self.shot_text.delete("1.0", tk.END)
        self.shot_text.insert(tk.END, self.core.shot_description)
        self.notes_text.delete("1.0", tk.END)
        self.notes_text.insert(tk.END, self.core.directors_notes)
        self.style_prefix_entry.delete(0, tk.END)
        self.style_prefix_entry.insert(0, self.core.style_prefix)
        self.style_suffix_entry.delete(0, tk.END)
        self.style_suffix_entry.insert(0, self.core.style_suffix)
        self.stick_to_script_var.set(self.core.stick_to_script)

    def create_output_area(self, parent):
        output_frame = ttk.LabelFrame(parent, text="🎨 Generated Prompt", padding="10")
        output_frame.pack(fill="both", expand=True)

        # Create a PanedWindow to allow resizing
        paned_window = ttk.PanedWindow(output_frame, orient=tk.VERTICAL)
        paned_window.pack(fill="both", expand=True)

        # Add the ScrolledText widget to the PanedWindow
        self.results_text = scrolledtext.ScrolledText(paned_window, wrap=tk.WORD, font=("Courier", 10))
        paned_window.add(self.results_text, weight=1)

        button_frame = ttk.Frame(output_frame)
        button_frame.pack(fill="x", pady=5)

        self.save_button = ttk.Button(button_frame, text="💾 Save Prompt", command=self.save_prompt)
        self.save_button.pack(side="left", padx=2)

        self.copy_button = ttk.Button(button_frame, text="📋 Copy to Clipboard", command=self.copy_prompt_to_clipboard)
        self.copy_button.pack(side="left", padx=2)

        self.show_prompts_button = ttk.Button(button_frame, text="📚 Show All Prompts", command=self.show_all_prompts)
        self.show_prompts_button.pack(side="left", padx=2)

        self.show_logs_button = ttk.Button(button_frame, text="📜 Show Logs", command=self.show_logs)
        self.show_logs_button.pack(side="left", padx=2)

        self.add_to_timeline_button = ttk.Button(button_frame, text="➕ Add to Timeline", command=self.add_prompt_to_timeline)
        self.add_to_timeline_button.pack(side="left", padx=2)

    async def handle_generate_button_click(self):
        try:
            # Get input values
            shot_description = self.shot_text.get("1.0", tk.END).strip()
            style_prefix = self.style_prefix_entry.get().strip()
            style_suffix = self.style_suffix_entry.get().strip()
            directors_notes = self.notes_text.get("1.0", tk.END).strip()
            stick_to_script = self.stick_to_script_var.get()
            script = self.script_text.get("1.0", tk.END).strip() if stick_to_script else ""
            end_parameters = self.end_parameters_entry.get()

            style = f"{style_prefix}{style_suffix}"

            # Generate prompts
            prompts = await self.core.generate_prompt(
                style=style,
                highlighted_text="",
                shot_description=shot_description,
                directors_notes=directors_notes,
                script=script,
                stick_to_script=stick_to_script,
                end_parameters=end_parameters
            )

            # Display generated prompts
            self.results_text.delete("1.0", tk.END)
            for length, prompt in prompts.items():
                self.results_text.insert(tk.END, f"{length}:\n{prompt}\n\n")

            # Apply tags for bold text
            self.results_text.tag_configure("bold", font=("Courier", 10, "bold"))
            for tag in self.results_text.tag_names():
                if tag != "sel":
                    self.results_text.tag_delete(tag)

            start = "1.0"
            while True:
                start = self.results_text.search(r'\*\*', start, tk.END, regexp=True)
                if not start:
                    break
                end = self.results_text.search(r'\*\*', f"{start}+2c", tk.END, regexp=True)
                if not end:
                    break
                self.results_text.delete(start, f"{start}+2c")
                self.results_text.delete(f"{end}-2c", end)
                self.results_text.tag_add("bold", start, end)
                start = end

        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {str(e)}\n\nPlease report this to the developer.")

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
        
        button_frame = ttk.Frame(subject_frame)
        button_frame.pack(fill="x", pady=(0, 5))
        
        generate_subjects_button = ttk.Button(button_frame, text="Generate Subjects", command=self.generate_subjects)
        generate_subjects_button.pack(side="left", padx=5)
        ToolTip(generate_subjects_button, "Generate subjects from script or notes")
        
        self.subject_frame = SubjectFrame(subject_frame, self.core)
        self.subject_frame.pack(fill="both", expand=True)

    def generate_subjects(self):
        script = self.script_text.get("1.0", tk.END).strip()
        directors_notes = self.notes_text.get("1.0", tk.END).strip()
        shot_description = self.shot_text.get("1.0", tk.END).strip()
        
        if script:
            text_to_analyze = script
        elif directors_notes:
            text_to_analyze = directors_notes
        elif shot_description:
            text_to_analyze = shot_description
        else:
            messagebox.showerror("Error", "Please provide a script, director's notes, or shot description.")
            return

        asyncio.create_task(self.async_generate_subjects(text_to_analyze))

    async def async_generate_subjects(self, text_to_analyze):
        try:
            subjects = await self.core.generate_subjects(text_to_analyze)
            if subjects:
                self.master.after(0, self.show_subject_selection_window, subjects)
            else:
                self.master.after(0, messagebox.showinfo, "No Subjects Found", "No subjects were generated. Please provide more detailed information.")
        except Exception as e:
            self.master.after(0, messagebox.showerror, "Error", f"An error occurred while generating subjects: {str(e)}")

    def show_subject_selection_window(self, subjects):
        selection_window = tk.Toplevel(self.master)
        selection_window.title("Generated Subjects")
        selection_window.geometry("600x400")

        main_frame = ttk.Frame(selection_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for subject in subjects:
            subject_frame = ttk.Frame(scrollable_frame)
            subject_frame.pack(fill=tk.X, padx=5, pady=5)

            ttk.Label(subject_frame, text=subject['name'], font=("TkDefaultFont", 12, "bold")).grid(row=0, column=0, sticky="w")

            var = tk.BooleanVar(value=True)
            check = ttk.Checkbutton(subject_frame, variable=var)
            check.grid(row=0, column=1, sticky="e")

            category_var = tk.StringVar(value=subject['category'])
            category_combo = ttk.Combobox(subject_frame, textvariable=category_var, 
                                          values=["Main Character", "Supporting Character", "Location", "Object"])
            category_combo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=2)

            description_text = scrolledtext.ScrolledText(subject_frame, height=4, width=40, wrap=tk.WORD)
            description_text.grid(row=2, column=0, columnspan=2, pady=2)
            description_text.insert(tk.END, subject['description'])

            subject['var'] = var
            subject['category_var'] = category_var
            subject['description_text'] = description_text

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        button_frame = ttk.Frame(selection_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Select All", command=lambda: self.toggle_all_subjects(subjects, True)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Deselect All", command=lambda: self.toggle_all_subjects(subjects, False)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Add Selected", command=lambda: self.add_selected_subjects(subjects, selection_window)).pack(side="right", padx=5)

    def toggle_all_subjects(self, subjects, state):
        for subject in subjects:
            subject['var'].set(state)

    def add_selected_subjects(self, subjects, window):
        for subject in subjects:
            if subject['var'].get():
                self.core.add_subject(
                    name=subject['name'],
                    category=subject['category_var'].get(),
                    description=subject['description_text'].get("1.0", tk.END).strip()
                )
        self.subject_frame.update_subjects(self.core.subjects)
        window.destroy()


    def __init__(self, master, core):
        self.master = master
        self.core = core
        self.loop = asyncio.get_event_loop()
        self.setup_ui()
        self.all_prompts_window = None
        self.all_prompts_text = None
        self.script_selection = None
        self.selection_timer = None

    def on_script_selection(self, event):
        if self.selection_timer is not None:
            self.master.after_cancel(self.selection_timer)
        self.selection_timer = self.master.after(200, self.handle_script_selection)

    def handle_script_selection(self):
        try:
            if self.script_text.tag_ranges(tk.SEL):
                self.script_selection = (self.script_text.index(tk.SEL_FIRST), self.script_text.index(tk.SEL_LAST))
            else:
                self.script_selection = None
        except Exception as e:
            print(f"Error in handle_script_selection: {str(e)}")

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
        prefix = self.style_prefix_entry.get().strip()
        if prefix:
            suffix = self.core.generate_style_details(prefix)
            self.style_suffix_entry.delete(0, tk.END)
            self.style_suffix_entry.insert(0, suffix)
        else:
            messagebox.showerror("Error", "Please enter a style prefix first.")

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


    def maintain_selection(self, event):
        if event.widget == self.script_text:
            return  # Allow default behavior in the script text widget
        if self.script_selection:
            self.script_text.tag_remove(tk.SEL, "1.0", tk.END)
            self.script_text.tag_add(tk.SEL, self.script_selection[0], self.script_selection[1])
            self.script_text.mark_set(tk.INSERT, self.script_selection[1])
        return "break"  # Prevents the default behavior of clearing the selection for other widgets

    def save_as_template(self):
        template_name = simpledialog.askstring("Save Template", "Enter a name for this template:")
        if template_name:
            components = {
                "style_prefix": self.style_prefix_entry.get(),
                "style_suffix": self.style_suffix_entry.get(),
                "shot_description": self.shot_text.get("1.0", tk.END).strip(),
                "directors_notes": self.notes_text.get("1.0", tk.END).strip(),
                "camera_shot": self.shot_combo.get(),
                "camera_move": self.move_combo.get(),
                "end_parameters": self.end_parameters_entry.get(),
                "stick_to_script": self.stick_to_script_var.get(),
                "script": self.script_text.get("1.0", tk.END).strip()
            }
            
            # Create a dialog to select which components to include
            selection_dialog = tk.Toplevel(self.master)
            selection_dialog.title("Select Components to Include")
            
            checkboxes = {}
            for key in components:
                var = tk.BooleanVar(value=True)
                checkboxes[key] = (tk.Checkbutton(selection_dialog, text=key, variable=var), var)
                checkboxes[key][0].pack(anchor="w")
            
            def save_selected():
                selected_components = {k: v for k, v in components.items() if checkboxes[k][1].get()}
                self.core.template_manager.save_template(template_name, selected_components)
                self.update_template_list()
                messagebox.showinfo("Template Saved", f"Template '{template_name}' has been saved.")
                selection_dialog.destroy()
            
            tk.Button(selection_dialog, text="Save", command=save_selected).pack()

    def load_template(self, event=None):
        template_name = self.load_template_var.get()
        if template_name:
            template = self.core.template_manager.load_template(template_name)
            
            # Populate fields with placeholder text for missing components
            self.style_prefix_entry.delete(0, tk.END)
            self.style_prefix_entry.insert(0, template.get("style_prefix", "[Style Prefix]"))
            self.style_suffix_entry.delete(0, tk.END)
            self.style_suffix_entry.insert(0, template.get("style_suffix", "[Style Suffix]"))
            self.shot_text.delete("1.0", tk.END)
            self.shot_text.insert(tk.END, template.get("shot_description", "[Shot Description]"))
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert(tk.END, template.get("directors_notes", "[Director's Notes]"))
            self.shot_combo.set(template.get("camera_shot", "None"))
            self.move_combo.set(template.get("camera_move", "None"))
            self.end_parameters_entry.delete(0, tk.END)
            self.end_parameters_entry.insert(0, template.get("end_parameters", "[End Parameters]"))
            self.stick_to_script_var.set(template.get("stick_to_script", False))
            self.script_text.delete("1.0", tk.END)
            self.script_text.insert(tk.END, template.get("script", "[Script]"))
            
            messagebox.showinfo("Template Loaded", f"Template '{template_name}' has been loaded.")

    def update_template_list(self):
        templates = list(self.core.template_manager.get_all_templates().keys())
        self.load_template_combo['values'] = templates

    # ... (rest of the PromptForgeUI methods remain unchanged)

def main():
    root = tk.Tk()
    app = PageToPromptUI(root, PromptForgeCore())
    root.protocol("WM_DELETE_WINDOW", root.quit)  # Ensure the program closes properly
    root.mainloop()

if __name__ == "__main__":
    main()
