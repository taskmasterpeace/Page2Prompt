# main.py
import logging
import tkinter as tk
from ui import PromptForgeUI

def main():
    root = tk.Tk()
    app = PromptForgeUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()