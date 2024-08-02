# main.py
import asyncio
import logging
import tkinter as tk
from ui import PageToPromptUI
from core import PromptForgeCore

async def main():
    root = tk.Tk()
    root.title("PromptForge")
    
    # Create an instance of PromptForgeCore
    core = PromptForgeCore()
    
    # Pass the core instance to PromptForgeUI
    app = PageToPromptUI(root, core)
    
    while True:
        root.update()
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
