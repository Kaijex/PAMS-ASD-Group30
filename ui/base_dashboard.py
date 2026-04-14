# ui/base_dashboard.py
# Shared dashboard layout - Group 30
# Student ID: 23029574 | Campbell Clark
import tkinter as tk
from tkinter import messagebox

SIDEBAR_BG = "#0C447C"
SIDEBAR_WIDTH = 220
HEADER_BG = "#185FA5"
CONTENT_BG = "#f0f4f8"
WHITE = "#ffffff"
TEXT_LIGHT = "#B5D4F4"
TEXT_MUTED = "#7aafd4"

class BaseDashboard:
    def __init__(self, root, user, nav_items):
        self.root = root
        self.user = user
        self.nav_items = nav_items
        self.current_frame = None
        self.nav_buttons = {}

        self.root.title(f"PAMS - {user['role'].title()} Dashboard")
        self.root.geometry("1100x650")
        self.root.resizable(True, True)
        self.root.configure(bg=CONTENT_BG)

        self.build_layout()

    def build_layout(self):
        # Sidebar
        self.sidebar = tk.Frame(self.root, bg=SIDEBAR_BG, width=SIDEBAR_WIDTH)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo area
        logo_frame = tk.Frame(self.sidebar, bg=HEADER_BG, height=70)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)
        tk.Label(logo_frame, text="PAMS", font=("Helvetica", 18, "bold"),
                 bg=HEADER_BG, fg=WHITE).pack(expand=True)

        # User info
        user_frame = tk.Frame(self.sidebar, bg=SIDEBAR_BG, pady=16)
        user_frame.pack(fill="x", padx=16)

        initials = self.user['username'][:2].upper()
        avatar = tk.Label(user_frame, text=initials,
                          font=("Helvetica", 14, "bold"),
                          bg="#378ADD", fg=WHITE,
                          width=3, height=1)
        avatar.pack()

        tk.Label(user_frame, text=self.user['username'],
                 font=("Helvetica", 11, "bold"),
                 bg=SIDEBAR_BG, fg=WHITE).pack(pady=(8, 2))
        tk.Label(user_frame, text=self.user['role'].title(),
                 font=("Helvetica", 9),
                 bg=SIDEBAR_BG, fg=TEXT_MUTED).pack()

        if self.user.get('location'):
            tk.Label(user_frame, text=self.user['location'],
                     font=("Helvetica", 9),
                     bg=SIDEBAR_BG, fg=TEXT_MUTED).pack()

        tk.Frame(self.sidebar, bg="#1a5a8a", height=1).pack(fill="x", padx=16, pady=8)

        # Nav buttons
        self.nav_frame = tk.Frame(self.sidebar, bg=SIDEBAR_BG)
        self.nav_frame.pack(fill="both", expand=True, pady=8)

        for label, command_name in self.nav_items:
            btn = tk.Button(self.nav_frame,
                           text=f"  {label}",
                           font=("Helvetica", 10),
                           bg=SIDEBAR_BG, fg=TEXT_LIGHT,
                           relief="flat", anchor="w",
                           cursor="hand2", bd=0,
                           activebackground="#185FA5",
                           activeforeground=WHITE,
                           command=lambda cn=command_name: self.navigate(cn))
            btn.pack(fill="x", padx=8, pady=2, ipady=8)
            self.nav_buttons[command_name] = btn

        # Logout at bottom
        tk.Frame(self.sidebar, bg="#1a5a8a", height=1).pack(fill="x", padx=16, pady=8)
        tk.Button(self.sidebar, text="  Logout",
                  font=("Helvetica", 10),
                  bg=SIDEBAR_BG, fg="#F09595",
                  relief="flat", anchor="w",
                  cursor="hand2", bd=0,
                  command=self.logout).pack(fill="x", padx=8, pady=4, ipady=8)

        # Main content area
        self.content_area = tk.Frame(self.root, bg=CONTENT_BG)
        self.content_area.pack(side="right", fill="both", expand=True)

        # Top header bar
        header = tk.Frame(self.content_area, bg=WHITE, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        self.header_title = tk.Label(header, text="Dashboard",
                                      font=("Helvetica", 14, "bold"),
                                      bg=WHITE, fg="#1a1a1a")
        self.header_title.pack(side="left", padx=24, pady=16)

        # Page frame
        self.page_frame = tk.Frame(self.content_area, bg=CONTENT_BG)
        self.page_frame.pack(fill="both", expand=True, padx=24, pady=24)

        # Load first nav item by default
        if self.nav_items:
            self.navigate(self.nav_items[0][1])

    def navigate(self, command_name):
        # Highlight active button
        for name, btn in self.nav_buttons.items():
            if name == command_name:
                btn.configure(bg="#185FA5", fg=WHITE)
            else:
                btn.configure(bg=SIDEBAR_BG, fg=TEXT_LIGHT)

        # Clear page frame
        for widget in self.page_frame.winfo_children():
            widget.destroy()

        # Update header
        label = next((l for l, c in self.nav_items if c == command_name), "")
        self.header_title.configure(text=label)

        # Call the method
        method = getattr(self, command_name, None)
        if method:
            method()

    def show_coming_soon(self, feature):
        tk.Label(self.page_frame,
                 text=f"{feature}",
                 font=("Helvetica", 18, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(pady=(40, 8))
        tk.Label(self.page_frame,
                 text="This module is coming soon.",
                 font=("Helvetica", 11),
                 bg=CONTENT_BG, fg="#888").pack()

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            import subprocess, sys
            subprocess.Popen([sys.executable, "main.py"])

    def show_overview(self):
        self.show_coming_soon("Overview")