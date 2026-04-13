# main.py
# PAMS - Paragon Apartment Management System
# Group 30 - Entry point
import tkinter as tk
from database.db import initialise_db
from ui.login import LoginScreen

if __name__ == "__main__":
    initialise_db()
    root = tk.Tk()
    app = LoginScreen(root)
    root.mainloop()
