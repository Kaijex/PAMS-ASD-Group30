# ui/modules/manage_users.py
# Admin User Management Module
# Student ID: 23029574 | Campbell Clark
# Group 30 - PAMS

import tkinter as tk
from tkinter import ttk, messagebox
from dao.user_dao import UserDAO

CONTENT_BG = "#f0f4f8"
WHITE = "#ffffff"
BLUE = "#185FA5"

ROLES = ["ADMIN", "MANAGER", "FRONTDESK",
         "FINANCE", "MAINTENANCE"]
LOCATIONS = ["Bristol", "Cardiff", "London", "Manchester"]

STATUS_COLOURS = {
    "Active":   "#0F6E56",
    "Inactive": "#A32D2D",
}

class ManageUsersModule(tk.Frame):
    def __init__(self, parent, user=None, **kwargs):
        super().__init__(parent, bg=CONTENT_BG, **kwargs)
        self.dao = UserDAO()
        self.user = user
        self.selected_id = None
        self.build()

    def build(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        all_tab = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(all_tab, text="  All Staff Accounts  ")

        new_tab = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(new_tab, text="  Create Account  ")

        self.build_all_tab(all_tab)
        self.build_new_tab(new_tab)

    def build_all_tab(self, parent):
        tk.Label(parent, text="Staff Accounts",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 8), padx=16)

        table_frame = tk.Frame(parent, bg=WHITE)
        table_frame.pack(fill="both", expand=True, padx=16)

        cols = ("ID", "Username", "Email", "Role",
                "Location", "Status")
        self.user_tree = ttk.Treeview(table_frame, columns=cols,
                                       show="headings", height=12)
        widths = [40, 120, 180, 110, 110, 80]
        for col, width in zip(cols, widths):
            self.user_tree.heading(col, text=col)
            self.user_tree.column(col, width=width, anchor="center")

        self.user_tree.tag_configure("Active",   foreground="#0F6E56")
        self.user_tree.tag_configure("Inactive", foreground="#A32D2D")

        self.user_tree.bind("<<TreeviewSelect>>", self.on_select)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.user_tree.pack(fill="both", expand=True)

        btn_frame = tk.Frame(parent, bg=CONTENT_BG)
        btn_frame.pack(fill="x", padx=16, pady=10)

        tk.Button(btn_frame, text="Edit Selected",
                  font=("Helvetica", 10), bg=BLUE, fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.open_edit_dialog).pack(
                  side="left", ipady=6, padx=(0, 8))

        tk.Button(btn_frame, text="Deactivate",
                  font=("Helvetica", 10), bg="#A32D2D", fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.deactivate_user).pack(
                  side="left", ipady=6, padx=(0, 8))

        tk.Button(btn_frame, text="Reactivate",
                  font=("Helvetica", 10), bg="#0F6E56", fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.reactivate_user).pack(
                  side="left", ipady=6, padx=(0, 8))

        tk.Button(btn_frame, text="Refresh",
                  font=("Helvetica", 10), bg="#444", fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.load_users).pack(
                  side="left", ipady=6)

        self.load_users()

    def build_new_tab(self, parent):
        card = tk.Frame(parent, bg=WHITE, padx=30, pady=24)
        card.pack(fill="x", padx=16, pady=16)

        tk.Label(card, text="Create New Staff Account",
                 font=("Helvetica", 13, "bold"),
                 bg=WHITE, fg=BLUE).pack(anchor="w", pady=(0, 16))

        form = tk.Frame(card, bg=WHITE)
        form.pack(fill="x")

        fields = [
            ("Username *",  "username"),
            ("Email *",     "email"),
            ("Password *",  "password"),
        ]

        self.form_vars = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(form, text=label,
                     font=("Helvetica", 10),
                     bg=WHITE, fg="#555").grid(
                     row=i, column=0, sticky="w",
                     pady=8, padx=(0, 12))
            show = "*" if key == "password" else ""
            var = tk.StringVar()
            tk.Entry(form, textvariable=var,
                     font=("Helvetica", 11), width=30,
                     relief="solid", bd=1, show=show).grid(
                     row=i, column=1, sticky="ew", pady=8)
            self.form_vars[key] = var

        # Role dropdown
        tk.Label(form, text="Role *",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(
                 row=3, column=0, sticky="w",
                 pady=8, padx=(0, 12))
        self.role_var = tk.StringVar(value=ROLES[0])
        ttk.Combobox(form, textvariable=self.role_var,
                     values=ROLES, state="readonly",
                     font=("Helvetica", 11), width=28).grid(
                     row=3, column=1, sticky="ew", pady=8)

        # Location dropdown
        tk.Label(form, text="Location",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(
                 row=4, column=0, sticky="w",
                 pady=8, padx=(0, 12))
        self.loc_var = tk.StringVar(value=LOCATIONS[0])
        ttk.Combobox(form, textvariable=self.loc_var,
                     values=LOCATIONS, state="readonly",
                     font=("Helvetica", 11), width=28).grid(
                     row=4, column=1, sticky="ew", pady=8)

        form.columnconfigure(1, weight=1)

        tk.Button(card, text="Create Account",
                  font=("Helvetica", 11, "bold"),
                  bg=BLUE, fg=WHITE, relief="flat",
                  cursor="hand2",
                  command=self.create_account).pack(
                  fill="x", pady=(20, 0), ipady=10)

    def load_users(self):
        for row in self.user_tree.get_children():
            self.user_tree.delete(row)
        users = self.dao.get_all()
        for u in users:
            # Skip tenant accounts — this module is staff only
            if u['role'] == 'TENANT':
                continue
            status = "Active" if u['is_active'] else "Inactive"
            self.user_tree.insert("", "end",
                iid=u['user_id'],
                values=(u['user_id'], u['username'],
                        u['email'], u['role'],
                        u.get('location') or '—',
                        status),
                tags=(status,))

    def on_select(self, event):
        selected = self.user_tree.selection()
        if selected:
            self.selected_id = int(selected[0])

    def deactivate_user(self):
        if not self.selected_id:
            messagebox.showwarning("No selection",
                                   "Please select a user first.")
            return
        if self.user and self.selected_id == self.user['user_id']:
            messagebox.showerror("Not allowed",
                "You cannot deactivate your own account.")
            return
        if messagebox.askyesno("Confirm",
                "Deactivate this account? The user will no longer be able to log in."):
            self.dao.deactivate(self.selected_id)
            self.selected_id = None
            self.load_users()

    def reactivate_user(self):
        if not self.selected_id:
            messagebox.showwarning("No selection",
                                   "Please select a user first.")
            return
        if messagebox.askyesno("Confirm",
                "Reactivate this account?"):
            self.dao.reactivate(self.selected_id)
            self.selected_id = None
            self.load_users()

    def create_account(self):
        username = self.form_vars['username'].get().strip()
        email    = self.form_vars['email'].get().strip()
        password = self.form_vars['password'].get().strip()
        role     = self.role_var.get()
        location = self.loc_var.get()

        if not username or not email or not password:
            messagebox.showerror("Missing fields",
                "Username, email and password are required.")
            return
        if self.dao.username_exists(username):
            messagebox.showerror("Username taken",
                "That username is already in use.")
            return
        if self.dao.email_exists(email):
            messagebox.showerror("Email taken",
                "That email address is already registered.")
            return

        self.dao.create_user(username, password, email, role, location)
        messagebox.showinfo("Success",
            f"Account created for {username}.")
        for var in self.form_vars.values():
            var.set("")
        self.load_users()

    def open_edit_dialog(self):
        if not self.selected_id:
            messagebox.showwarning("No selection",
                                   "Please select a user to edit.")
            return

        user = self.dao.get_by_id(self.selected_id)
        if not user:
            return

        dialog = tk.Toplevel(self)
        dialog.title("Edit Staff Account")
        dialog.geometry("400x320")
        dialog.resizable(False, False)
        dialog.configure(bg=WHITE)
        dialog.grab_set()

        header = tk.Frame(dialog, bg=BLUE, pady=16)
        header.pack(fill="x")
        tk.Label(header, text=f"Editing: {user['username']}",
                 font=("Helvetica", 13, "bold"),
                 bg=BLUE, fg=WHITE).pack(padx=20)

        form = tk.Frame(dialog, bg=WHITE, padx=24, pady=16)
        form.pack(fill="both", expand=True)

        # Email
        tk.Label(form, text="Email",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(
                 row=0, column=0, sticky="w",
                 pady=8, padx=(0, 12))
        email_var = tk.StringVar(value=user['email'])
        tk.Entry(form, textvariable=email_var,
                 font=("Helvetica", 11), width=26,
                 relief="solid", bd=1).grid(
                 row=0, column=1, sticky="ew", pady=8)

        # Role
        tk.Label(form, text="Role",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(
                 row=1, column=0, sticky="w",
                 pady=8, padx=(0, 12))
        role_var = tk.StringVar(value=user['role'])
        ttk.Combobox(form, textvariable=role_var,
                     values=ROLES, state="readonly",
                     font=("Helvetica", 11), width=24).grid(
                     row=1, column=1, sticky="ew", pady=8)

        # Location
        tk.Label(form, text="Location",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(
                 row=2, column=0, sticky="w",
                 pady=8, padx=(0, 12))
        loc_var = tk.StringVar(value=user.get('location') or LOCATIONS[0])
        ttk.Combobox(form, textvariable=loc_var,
                     values=LOCATIONS, state="readonly",
                     font=("Helvetica", 11), width=24).grid(
                     row=2, column=1, sticky="ew", pady=8)

        form.columnconfigure(1, weight=1)

        def save():
            self.dao.update(self.selected_id,
                            email_var.get().strip(),
                            role_var.get(),
                            loc_var.get())
            messagebox.showinfo("Saved", "Account updated successfully.")
            dialog.destroy()
            self.load_users()

        tk.Button(dialog, text="Save Changes",
                  font=("Helvetica", 11, "bold"),
                  bg=BLUE, fg=WHITE, relief="flat",
                  cursor="hand2",
                  command=save).pack(
                  fill="x", padx=24, pady=16, ipady=8)