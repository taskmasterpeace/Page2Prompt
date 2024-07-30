# main.py
import logging
import tkinter as tk
from ui import PromptForgeUI
from core import PromptForgeCore

def main():
    root = tk.Tk()
    root.title("PromptForge")
    
    # Create an instance of PromptForgeCore
    core = PromptForgeCore()
    
    # Pass the core instance to PromptForgeUI
    app = PromptForgeUI(root, core)
    
    root.mainloop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
