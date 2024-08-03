# main.py
#!/usr/bin/env python3
import asyncio
import logging
import tkinter as tk
from ui import PageToPromptUI
from core import PromptForgeCore
from config import config

async def main():
    root = tk.Tk()
    root.title("PromptForge")
    
    # Set the initial window size from config
    root.geometry(config.get('UI_SETTINGS', 'main_window_geometry'))
    
    # Create an instance of PageToPromptUI
    app = PageToPromptUI(root)
    
    while True:
        root.update()
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
