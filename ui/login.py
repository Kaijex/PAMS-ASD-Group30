# ui/login.py
# PAMS Login Screen - Group 30
# Student ID: 23029574 | Campbell Clark
import tkinter as tk
from tkinter import messagebox
import bcrypt
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("PAMS - Paragon Apartment Management System")
        self.root.geometry("900x550")
        self.root.resizable(False, False)
        self.root.configure(bg="#185FA5")
        self.build()

    def build(self):
        main = tk.Frame(self.root, bg="#185FA5")
        main.pack(fill="both", expand=True)

        # Left panel
        left = tk.Frame(main, bg="#185FA5", width=360)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="PAMS", font=("Helvetica", 28, "bold"),
                 bg="#185FA5", fg="white").pack(pady=(80, 4), padx=40, anchor="w")
        tk.Label(left, text="Paragon Apartment\nManagement System",
                 font=("Helvetica", 12), bg="#185FA5",
                 fg="#B5D4F4", justify="left").pack(padx=40, anchor="w")

        tk.Frame(left, bg="white", height=1, width=260).pack(padx=40, pady=30)

        tk.Label(left, text="Locations", font=("Helvetica", 10),
                 bg="#185FA5", fg="#7aafd4").pack(padx=40, anchor="w", pady=(0, 8))
        for city in ["Bristol", "Cardiff", "London", "Manchester"]:
            tk.Label(left, text=city, font=("Helvetica", 11),
                     bg="#185FA5", fg="#e8f4fc").pack(padx=40, anchor="w", pady=2)

        # Right panel
        right = tk.Frame(main, bg="white")
        right.pack(side="right", fill="both", expand=True)

        inner = tk.Frame(right, bg="white")
        inner.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(inner, text="Welcome back", font=("Helvetica", 20, "bold"),
                 bg="white", fg="#1a1a1a").pack(anchor="w", pady=(0, 4))
        tk.Label(inner, text="Sign in to your account", font=("Helvetica", 11),
                 bg="white", fg="#888").pack(anchor="w", pady=(0, 24))

        tk.Label(inner, text="Username", font=("Helvetica", 10),
                 bg="white", fg="#555").pack(anchor="w")
        self.user_entry = tk.Entry(inner, font=("Helvetica", 12),
                                       width=28, relief="solid", bd=1)
        self.user_entry.pack(pady=(4, 16), ipady=6)

        tk.Label(inner, text="Password", font=("Helvetica", 10),
                 bg="white", fg="#555").pack(anchor="w")
        self.password_entry = tk.Entry(inner, font=("Helvetica", 12),
                                       width=28, relief="solid", bd=1, show="*")
        self.password_entry.pack(pady=(4, 24), ipady=6)

        self.root.bind("<Return>", lambda e: self.attempt_login())

        login_btn = tk.Button(inner, text="Sign in", font=("Helvetica", 12, "bold"),
                              bg="#185FA5", fg="white", relief="flat",
                              width=26, cursor="hand2", command=self.attempt_login)
        login_btn.pack(ipady=8)

        hint = tk.Frame(inner, bg="#f5f5f5", pady=8, padx=12)
        hint.pack(pady=(20, 0), fill="x")
        tk.Label(hint, text="Demo: admin / admin123",
                 font=("Helvetica", 9), bg="#f5f5f5", fg="#999").pack()

    def attempt_login(self):
        user = self.user_entry.get().strip()
        passwrd = self.password_entry.get().strip()

        if not user or not passwrd:
            messagebox.showwarning("Missing fields", "Please enter both username and password.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (user,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.checkpw(passwrd.encode('utf-8'), user['password_hash'].encode('utf-8')):
            self.login_success(dict(user))
        else:
            messagebox.showerror("Login failed", "Invalid username or password.")
            self.password_entry.delete(0, tk.END)

    def login_success(self, user):
        self.root.destroy()
        root = tk.Tk()
        role = user['role']

        if role == 'ADMIN':
            from ui.admin_dashboard import AdminDashboard
            AdminDashboard(root, user)
        elif role == 'MANAGER':
            from ui.manager_dashboard import ManagerDashboard
            ManagerDashboard(root, user)
        elif role == 'FRONTDESK':
            from ui.frontdesk_dashboard import FrontDeskDashboard
            FrontDeskDashboard(root, user)
        elif role == 'FINANCE':
            from ui.finance_dashboard import FinanceDashboard
            FinanceDashboard(root, user)
        elif role == 'MAINTENANCE':
            from ui.maintenance_dashboard import MaintenanceDashboard
            MaintenanceDashboard(root, user)
        elif role == 'TENANT':
            from ui.tenant_dashboard import TenantDashboard
            TenantDashboard(root, user)

        root.mainloop()