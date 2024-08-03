# main.py
#!/usr/bin/env python3
import asyncio
import logging
import tkinter as tk
from ui import PageToPromptUI
from core import PromptForgeCore
from config import config

async def main():
    try:
        root = tk.Tk()
        root.title("PromptForge")
        
        # Set the initial window size from config
        root.geometry(config.get('UI_SETTINGS', 'main_window_geometry'))
        
        # Create an instance of PromptForgeCore
        core = PromptForgeCore()
        
        # Create an instance of PageToPromptUI
        app = PageToPromptUI(root, core)
        
        while True:
            root.update()
            await asyncio.sleep(0.1)
    except Exception as e:
        logging.error(f"An error occurred in the main loop: {str(e)}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        asyncio.run(main())
    except Exception as e:
        logging.critical(f"Critical error: {str(e)}")
