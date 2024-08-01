# main.py
import logging
import tkinter as tk
from ui import Page2PromptUI
from core import PromptForgeCore

def main():
    root = tk.Tk()
    root.title("PromptForge")
    
    # Create an instance of PromptForgeCore
    core = PromptForgeCore()
    
    # Pass the core instance to PromptForgeUI
    app = Page2PromptUI(root, core)
    
    root.mainloop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
import asyncio
from core import main

if __name__ == "__main__":
    asyncio.run(main())
