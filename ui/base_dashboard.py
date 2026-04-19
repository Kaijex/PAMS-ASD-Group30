# ui/base_dashboard.py
import tkinter as tk
from tkinter import messagebox, ttk

SIDEBAR_BG = "#0F172A"
SIDEBAR_WIDTH = 240
HEADER_BG = "#FFFFFF"
CONTENT_BG = "#F8FAFC"
CARD_BG = "#FFFFFF"

PRIMARY = "#2563EB"
PRIMARY_HOVER = "#1D4ED8"
TEXT_DARK = "#0F172A"
TEXT_MUTED = "#64748B"
TEXT_LIGHT = "#CBD5E1"
BORDER = "#E2E8F0"
LOGOUT = "#DC2626"
AVATAR_BG = "#3B82F6"

class BaseDashboard:
    def __init__(self, root, user, nav_items):
        self.root = root
        self.user = user
        self.nav_items = nav_items
        self.nav_buttons = {}

        self.root.title(f"PAMS - {user['role'].title()} Dashboard")
        self.root.geometry("1200x720")
        self.root.resizable(True, True)
        self.root.configure(bg=CONTENT_BG)

        self.setup_styles()
        self.build_layout()

    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass

        style.configure(
            "Treeview",
            background="#FFFFFF",
            foreground=TEXT_DARK,
            rowheight=30,
            fieldbackground="#FFFFFF",
            bordercolor=BORDER,
            borderwidth=1,
            font=("Helvetica", 10)
        )

        style.configure(
            "Treeview.Heading",
            background="#EAF2FF",
            foreground=TEXT_DARK,
            font=("Helvetica", 10, "bold"),
            relief="flat"
        )

        style.map(
            "Treeview",
            background=[("selected", "#DBEAFE")],
            foreground=[("selected", TEXT_DARK)]
        )

        style.map(
            "Treeview.Heading",
            background=[("active", "#DCEAFE")]
        )

    def build_layout(self):
        self.sidebar = tk.Frame(self.root, bg=SIDEBAR_BG, width=SIDEBAR_WIDTH)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_frame = tk.Frame(self.sidebar, bg=SIDEBAR_BG, height=88)
        logo_frame.pack(fill="x", padx=18, pady=(18, 10))
        logo_frame.pack_propagate(False)

        tk.Label(
            logo_frame,
            text="PAMS",
            font=("Helvetica", 22, "bold"),
            bg=SIDEBAR_BG,
            fg="white"
        ).pack(anchor="w", pady=(8, 0))

        tk.Label(
            logo_frame,
            text="Apartment Management",
            font=("Helvetica", 10),
            bg=SIDEBAR_BG,
            fg=TEXT_LIGHT
        ).pack(anchor="w", pady=(4, 0))

        user_frame = tk.Frame(self.sidebar, bg="#111C34", padx=14, pady=14)
        user_frame.pack(fill="x", padx=16, pady=(4, 16))

        initials = self.user["username"][:2].upper()
        tk.Label(
            user_frame,
            text=initials,
            font=("Helvetica", 13, "bold"),
            bg=AVATAR_BG,
            fg="white",
            width=3,
            height=1
        ).pack(anchor="w")

        tk.Label(
            user_frame,
            text=self.user["username"],
            font=("Helvetica", 11, "bold"),
            bg="#111C34",
            fg="white"
        ).pack(anchor="w", pady=(10, 2))

        tk.Label(
            user_frame,
            text=self.user["role"].title(),
            font=("Helvetica", 9),
            bg="#111C34",
            fg=TEXT_LIGHT
        ).pack(anchor="w")

        if self.user.get("location"):
            tk.Label(
                user_frame,
                text=self.user["location"],
                font=("Helvetica", 9),
                bg="#111C34",
                fg=TEXT_MUTED
            ).pack(anchor="w", pady=(2, 0))

        self.nav_frame = tk.Frame(self.sidebar, bg=SIDEBAR_BG)
        self.nav_frame.pack(fill="both", expand=True, padx=12)

        for label, command_name in self.nav_items:
            btn = tk.Button(
                self.nav_frame,
                text=f"  {label}",
                font=("Helvetica", 10, "bold"),
                bg=SIDEBAR_BG,
                fg=TEXT_LIGHT,
                relief="flat",
                anchor="w",
                cursor="hand2",
                bd=0,
                padx=14,
                pady=12,
                activebackground=PRIMARY,
                activeforeground="white",
                command=lambda cn=command_name: self.navigate(cn)
            )
            btn.pack(fill="x", pady=4)
            self.nav_buttons[command_name] = btn

        tk.Button(
            self.sidebar,
            text="  Logout",
            font=("Helvetica", 10, "bold"),
            bg=SIDEBAR_BG,
            fg="#FCA5A5",
            relief="flat",
            anchor="w",
            cursor="hand2",
            bd=0,
            padx=14,
            pady=12,
            activebackground=LOGOUT,
            activeforeground="white",
            command=self.logout
        ).pack(fill="x", padx=12, pady=14)

        self.content_area = tk.Frame(self.root, bg=CONTENT_BG)
        self.content_area.pack(side="right", fill="both", expand=True)

        header = tk.Frame(self.content_area, bg=HEADER_BG, height=74, highlightbackground=BORDER, highlightthickness=1)
        header.pack(fill="x")
        header.pack_propagate(False)

        self.header_title = tk.Label(
            header,
            text="Dashboard",
            font=("Helvetica", 18, "bold"),
            bg=HEADER_BG,
            fg=TEXT_DARK
        )
        self.header_title.pack(side="left", padx=28, pady=20)

        self.page_frame = tk.Frame(self.content_area, bg=CONTENT_BG)
        self.page_frame.pack(fill="both", expand=True, padx=28, pady=28)

        if self.nav_items:
            self.navigate(self.nav_items[0][1])

    def navigate(self, command_name):
        for name, btn in self.nav_buttons.items():
            if name == command_name:
                btn.configure(bg=PRIMARY, fg="white")
            else:
                btn.configure(bg=SIDEBAR_BG, fg=TEXT_LIGHT)

        for widget in self.page_frame.winfo_children():
            widget.destroy()

        label = next((l for l, c in self.nav_items if c == command_name), "")
        self.header_title.configure(text=label)

        method = getattr(self, command_name, None)
        if method:
            method()

    def show_coming_soon(self, feature):
        tk.Label(
            self.page_frame,
            text=feature,
            font=("Helvetica", 22, "bold"),
            bg=CONTENT_BG,
            fg=TEXT_DARK
        ).pack(pady=(50, 10))

        tk.Label(
            self.page_frame,
            text="This module is coming soon.",
            font=("Helvetica", 11),
            bg=CONTENT_BG,
            fg=TEXT_MUTED
        ).pack()

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            import subprocess, sys
            subprocess.Popen([sys.executable, "main.py"])

    def show_overview(self):
        self.show_coming_soon("Overview")