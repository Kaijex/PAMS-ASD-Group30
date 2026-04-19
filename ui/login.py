# ui/login.py
# PAMS Login Screen - Group 30
# Student ID: 23029574 | Campbell Clark
# UI refinement by Student ID: 25013991 | Adjeneg Imed

import tkinter as tk
from tkinter import messagebox
import bcrypt
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection


SIDEBAR_BG = "#071224"
SIDEBAR_PANEL = "#0D1B34"
RIGHT_BG = "#F8FAFC"
CARD_BG = "#FFFFFF"

PRIMARY = "#2563EB"
PRIMARY_HOVER = "#1D4ED8"
TEXT_DARK = "#0F172A"
TEXT_MUTED = "#64748B"
TEXT_LIGHT = "#CBD5E1"
BORDER = "#E2E8F0"
INPUT_BG = "#F8FAFC"
CITY_DOT = "#60A5FA"


class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("PAMS - Paragon Apartment Management System")
        self.root.geometry("1040x620")
        self.root.resizable(False, False)
        self.root.configure(bg=SIDEBAR_BG)
        self.build()

    def build(self):
        main = tk.Frame(self.root, bg=SIDEBAR_BG)
        main.pack(fill="both", expand=True)

        # LEFT PANEL
        left = tk.Frame(main, bg=SIDEBAR_BG, width=380)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        brand_wrap = tk.Frame(left, bg=SIDEBAR_BG)
        brand_wrap.pack(fill="x", padx=34, pady=(60, 24))

        tk.Label(
            brand_wrap,
            text="PAMS",
            font=("Helvetica", 34, "bold"),
            bg=SIDEBAR_BG,
            fg="white"
        ).pack(anchor="w")

        tk.Label(
            brand_wrap,
            text="Paragon Apartment\nManagement System",
            font=("Helvetica", 14),
            bg=SIDEBAR_BG,
            fg=TEXT_LIGHT,
            justify="left"
        ).pack(anchor="w", pady=(10, 0))

        info_card = tk.Frame(
            left,
            bg=SIDEBAR_PANEL,
            padx=24,
            pady=22
        )
        info_card.pack(fill="x", padx=28, pady=(12, 0))

        tk.Label(
            info_card,
            text="Multi-city property operations",
            font=("Helvetica", 12, "bold"),
            bg=SIDEBAR_PANEL,
            fg="white"
        ).pack(anchor="w")

        tk.Label(
            info_card,
            text="Manage tenants, apartments, leases, payments,\nmaintenance, and reporting in one place.",
            font=("Helvetica", 10),
            bg=SIDEBAR_PANEL,
            fg=TEXT_LIGHT,
            justify="left"
        ).pack(anchor="w", pady=(10, 18))

        tk.Label(
            info_card,
            text="Locations",
            font=("Helvetica", 10, "bold"),
            bg=SIDEBAR_PANEL,
            fg=TEXT_MUTED
        ).pack(anchor="w", pady=(4, 10))

        for city in ["Bristol", "Cardiff", "London", "Manchester"]:
            row = tk.Frame(info_card, bg=SIDEBAR_PANEL)
            row.pack(anchor="w", pady=4)

            tk.Label(
                row,
                text="●",
                font=("Helvetica", 10),
                bg=SIDEBAR_PANEL,
                fg=CITY_DOT
            ).pack(side="left")

            tk.Label(
                row,
                text=f"  {city}",
                font=("Helvetica", 11),
                bg=SIDEBAR_PANEL,
                fg="white"
            ).pack(side="left")

        bottom_note = tk.Label(
            left,
            text="Secure role-based access for staff and tenants",
            font=("Helvetica", 10),
            bg=SIDEBAR_BG,
            fg=TEXT_MUTED
        )
        bottom_note.pack(anchor="w", padx=34, pady=(26, 0))

        # RIGHT PANEL
        right = tk.Frame(main, bg=RIGHT_BG)
        right.pack(side="right", fill="both", expand=True)

        form_card = tk.Frame(
            right,
            bg=CARD_BG,
            padx=36,
            pady=34,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        form_card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            form_card,
            text="Welcome back",
            font=("Helvetica", 26, "bold"),
            bg=CARD_BG,
            fg=TEXT_DARK
        ).pack(anchor="w")

        tk.Label(
            form_card,
            text="Sign in to access your dashboard",
            font=("Helvetica", 11),
            bg=CARD_BG,
            fg=TEXT_MUTED
        ).pack(anchor="w", pady=(6, 24))

        # Username
        tk.Label(
            form_card,
            text="Username",
            font=("Helvetica", 10, "bold"),
            bg=CARD_BG,
            fg=TEXT_DARK
        ).pack(anchor="w", pady=(0, 6))

        self.user_entry = tk.Entry(
            form_card,
            font=("Helvetica", 12),
            width=30,
            relief="flat",
            bd=0,
            bg=INPUT_BG,
            fg=TEXT_DARK,
            insertbackground=TEXT_DARK
        )
        self.user_entry.pack(ipady=10, pady=(0, 18), fill="x")

        user_border = tk.Frame(form_card, bg=BORDER, height=1)
        user_border.pack(fill="x", pady=(0, 2))

        # Password
        tk.Label(
            form_card,
            text="Password",
            font=("Helvetica", 10, "bold"),
            bg=CARD_BG,
            fg=TEXT_DARK
        ).pack(anchor="w", pady=(12, 6))

        self.password_entry = tk.Entry(
            form_card,
            font=("Helvetica", 12),
            width=30,
            relief="flat",
            bd=0,
            bg=INPUT_BG,
            fg=TEXT_DARK,
            insertbackground=TEXT_DARK,
            show="*"
        )
        self.password_entry.pack(ipady=10, pady=(0, 18), fill="x")

        pass_border = tk.Frame(form_card, bg=BORDER, height=1)
        pass_border.pack(fill="x", pady=(0, 8))

        self.root.bind("<Return>", lambda e: self.attempt_login())

        login_btn = tk.Label(
            form_card,
            text="Sign in",
            font=("Helvetica", 12, "bold"),
            bg=PRIMARY,
            fg="white",
            padx=16,
            pady=12,
            cursor="hand2"
        )
        login_btn.pack(fill="x", pady=(18, 0))
        login_btn.bind("<Button-1>", lambda e: self.attempt_login())
        login_btn.bind("<Enter>", lambda e: login_btn.configure(bg=PRIMARY_HOVER))
        login_btn.bind("<Leave>", lambda e: login_btn.configure(bg=PRIMARY))

        demo_box = tk.Frame(
            form_card,
            bg="#EEF4FF",
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=14,
            pady=10
        )
        demo_box.pack(fill="x", pady=(18, 0))

        tk.Label(
            demo_box,
            text="Demo login: admin / admin123",
            font=("Helvetica", 10),
            bg="#EEF4FF",
            fg=TEXT_MUTED
        ).pack()

    def attempt_login(self):
        username = self.user_entry.get().strip()
        passwrd = self.password_entry.get().strip()

        if not username or not passwrd:
            messagebox.showwarning("Missing fields", "Please enter both username and password.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.checkpw(passwrd.encode("utf-8"), user["password_hash"].encode("utf-8")):
            self.login_success(dict(user))
        else:
            messagebox.showerror("Login failed", "Invalid username or password.")
            self.password_entry.delete(0, tk.END)

    def login_success(self, user):
        self.root.destroy()
        root = tk.Tk()
        role = user["role"]

        if role == "ADMIN":
            from ui.admin_dashboard import AdminDashboard
            AdminDashboard(root, user)
        elif role == "MANAGER":
            from ui.manager_dashboard import ManagerDashboard
            ManagerDashboard(root, user)
        elif role == "FRONTDESK":
            from ui.frontdesk_dashboard import FrontDeskDashboard
            FrontDeskDashboard(root, user)
        elif role == "FINANCE":
            from ui.finance_dashboard import FinanceDashboard
            FinanceDashboard(root, user)
        elif role == "MAINTENANCE":
            from ui.maintenance_dashboard import MaintenanceDashboard
            MaintenanceDashboard(root, user)
        elif role == "TENANT":
            from ui.tenant_dashboard import TenantDashboard
            TenantDashboard(root, user)

        root.mainloop()