# main.py
# PAMS - Paragon Apartment Management System
# Student ID: 23029574 | Campbell Clark
# Student ID: 25013991 | Adjeneg Imed
import tkinter as tk
from database.db import initialise_db
from ui.login import LoginScreen

if __name__ == "__main__":
    initialise_db()
    root = tk.Tk()
    app = LoginScreen(root)
    root.mainloop()
