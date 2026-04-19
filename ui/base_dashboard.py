# ui/base_dashboard.py
# Shared dashboard layout - Group 30
# Student ID: 23029574 | Campbell Clark
# Student ID: 25013991 | Adjeneg Imed

import tkinter as tk
from tkinter import messagebox, ttk

SIDEBAR_BG = "#071224"
SIDEBAR_PANEL = "#0D1B34"
SIDEBAR_WIDTH = 240

HEADER_BG = "#FFFFFF"
CONTENT_BG = "#F8FAFC"
WHITE = "#FFFFFF"

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
        except Exception:
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

    def build_layout(self):
        self.sidebar = tk.Frame(self.root, bg=SIDEBAR_BG, width=SIDEBAR_WIDTH)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        top = tk.Frame(self.sidebar, bg=SIDEBAR_BG)
        top.pack(fill="x", padx=18, pady=(22, 12))

        tk.Label(
            top,
            text="PAMS",
            font=("Helvetica", 24, "bold"),
            bg=SIDEBAR_BG,
            fg=WHITE
        ).pack(anchor="w")

        tk.Label(
            top,
            text="Apartment Management",
            font=("Helvetica", 10),
            bg=SIDEBAR_BG,
            fg=TEXT_LIGHT
        ).pack(anchor="w", pady=(6, 0))

        user_card = tk.Frame(
            self.sidebar,
            bg=SIDEBAR_PANEL,
            padx=18,
            pady=18
        )
        user_card.pack(fill="x", padx=16, pady=(8, 18))

        initials = self.user["username"][:2].upper()
        tk.Label(
            user_card,
            text=initials,
            font=("Helvetica", 14, "bold"),
            bg=AVATAR_BG,
            fg=WHITE,
            width=3,
            height=1
        ).pack(anchor="w")

        tk.Label(
            user_card,
            text=self.user["username"],
            font=("Helvetica", 12, "bold"),
            bg=SIDEBAR_PANEL,
            fg=WHITE
        ).pack(anchor="w", pady=(12, 3))

        tk.Label(
            user_card,
            text=self.user["role"].title(),
            font=("Helvetica", 10),
            bg=SIDEBAR_PANEL,
            fg=TEXT_LIGHT
        ).pack(anchor="w")

        if self.user.get("location"):
            tk.Label(
                user_card,
                text=self.user["location"],
                font=("Helvetica", 10),
                bg=SIDEBAR_PANEL,
                fg=TEXT_MUTED
            ).pack(anchor="w", pady=(4, 0))

        self.nav_frame = tk.Frame(self.sidebar, bg=SIDEBAR_BG)
        self.nav_frame.pack(fill="both", expand=True, padx=14)

        for label, command_name in self.nav_items:
            item = tk.Label(
                self.nav_frame,
                text=label,
                font=("Helvetica", 11, "bold"),
                bg=SIDEBAR_BG,
                fg=TEXT_LIGHT,
                anchor="w",
                padx=16,
                pady=14,
                cursor="hand2"
            )
            item.pack(fill="x", pady=5)
            item.bind("<Button-1>", lambda e, cn=command_name: self.navigate(cn))
            item.bind("<Enter>", lambda e, w=item, cn=command_name: self.on_nav_hover(w, cn))
            item.bind("<Leave>", lambda e, w=item, cn=command_name: self.on_nav_leave(w, cn))
            self.nav_buttons[command_name] = item

        logout_label = tk.Label(
            self.sidebar,
            text="Logout",
            font=("Helvetica", 11, "bold"),
            bg=SIDEBAR_BG,
            fg="#FCA5A5",
            anchor="w",
            padx=16,
            pady=14,
            cursor="hand2"
        )
        logout_label.pack(fill="x", padx=14, pady=16)
        logout_label.bind("<Button-1>", lambda e: self.logout())
        logout_label.bind("<Enter>", lambda e: logout_label.configure(bg="#3A1010", fg=WHITE))
        logout_label.bind("<Leave>", lambda e: logout_label.configure(bg=SIDEBAR_BG, fg="#FCA5A5"))

        self.content_area = tk.Frame(self.root, bg=CONTENT_BG)
        self.content_area.pack(side="right", fill="both", expand=True)

        header = tk.Frame(
            self.content_area,
            bg=HEADER_BG,
            height=72,
            highlightbackground=BORDER,
            highlightthickness=1
        )
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

    def on_nav_hover(self, widget, command_name):
        active = getattr(self, "active_command", None)
        if command_name != active:
            widget.configure(bg="#102444", fg=WHITE)

    def on_nav_leave(self, widget, command_name):
        active = getattr(self, "active_command", None)
        if command_name != active:
            widget.configure(bg=SIDEBAR_BG, fg=TEXT_LIGHT)

    def navigate(self, command_name):
        self.active_command = command_name

        for name, widget in self.nav_buttons.items():
            if name == command_name:
                widget.configure(bg=PRIMARY, fg=WHITE)
            else:
                widget.configure(bg=SIDEBAR_BG, fg=TEXT_LIGHT)

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