# ui/modules/tenant_lookup.py
# Tenant Lookup Module
# Student ID: [Your ID] - Campbell [Surname]
# Group 30 - PAMS

import tkinter as tk
from tkinter import ttk, messagebox
from dao.tenant_dao import TenantDAO

CONTENT_BG = "#f0f4f8"
WHITE = "#ffffff"
BLUE = "#185FA5"

class TenantLookupModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CONTENT_BG)
        self.dao = TenantDAO()
        self.selected_id = None
        self.build()

    def build(self):
        # Search bar
        search_card = tk.Frame(self, bg=WHITE, padx=20, pady=16)
        search_card.pack(fill="x", pady=(0, 16))

        tk.Label(search_card, text="Search Tenants",
                 font=("Helvetica", 13, "bold"),
                 bg=WHITE, fg="#1a1a1a").pack(anchor="w", pady=(0, 10))

        search_row = tk.Frame(search_card, bg=WHITE)
        search_row.pack(fill="x")

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_row, textvariable=self.search_var,
                                font=("Helvetica", 12), relief="solid",
                                bd=1, width=40)
        search_entry.pack(side="left", ipady=6, padx=(0, 10))
        search_entry.bind("<Return>", lambda e: self.do_search())

        tk.Label(search_row, text="Search by name, NI number or email",
                 font=("Helvetica", 9), bg=WHITE,
                 fg="#aaa").pack(side="left", padx=(0, 12))

        tk.Button(search_row, text="Search",
                  font=("Helvetica", 10), bg=BLUE, fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.do_search).pack(side="left", ipady=6)

        tk.Button(search_row, text="Show All",
                  font=("Helvetica", 10), bg="#555", fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.load_all).pack(side="left",
                  ipady=6, padx=(8, 0))

        # Results table
        table_frame = tk.Frame(self, bg=WHITE)
        table_frame.pack(fill="both", expand=True, pady=(0, 12))

        cols = ("ID", "Full Name", "NI Number", "Phone",
                "Email", "Occupation", "Location", "Registered")
        self.tree = ttk.Treeview(table_frame, columns=cols,
                                  show="headings", height=12)

        widths = [40, 140, 100, 100, 160, 110, 90, 90]
        for col, width in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical",
                                     command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal",
                                     command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set,
                            xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", lambda e: self.view_details())

        # Action buttons
        action_frame = tk.Frame(self, bg=CONTENT_BG)
        action_frame.pack(fill="x")

        tk.Button(action_frame, text="View Details",
                  font=("Helvetica", 10), bg=BLUE, fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.view_details).pack(side="left",
                  ipady=6, padx=(0, 8))

        tk.Button(action_frame, text="Edit Tenant",
                  font=("Helvetica", 10), bg="#378ADD", fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.edit_tenant).pack(side="left", ipady=6)

        # Result count label
        self.count_label = tk.Label(action_frame, text="",
                                     font=("Helvetica", 9),
                                     bg=CONTENT_BG, fg="#888")
        self.count_label.pack(side="right")

        self.load_all()

    def load_all(self):
        self.search_var.set("")
        tenants = self.dao.get_all()
        self.populate_table(tenants)

    def do_search(self):
        query = self.search_var.get().strip()
        if not query:
            self.load_all()
            return
        results = self.dao.search(query)
        self.populate_table(results)

    def populate_table(self, tenants):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for t in tenants:
            registered = t.get('created_at', '')[:10] if t.get('created_at') else ''
            self.tree.insert("", "end", iid=t['tenant_id'],
                             values=(
                                 t['tenant_id'],
                                 t['full_name'],
                                 t['ni_number'],
                                 t['phone'],
                                 t['email'],
                                 t['occupation'],
                                 t.get('preferred_location', ''),
                                 registered
                             ))

        count = len(tenants)
        self.count_label.configure(
            text=f"{count} tenant{'s' if count != 1 else ''} found"
        )

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.selected_id = int(selected[0])

    def view_details(self):
        if not self.selected_id:
            messagebox.showwarning("No selection",
                                   "Please select a tenant to view.")
            return

        tenant = self.dao.get_by_id(self.selected_id)
        if not tenant:
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Tenant Details - {tenant['full_name']}")
        dialog.geometry("480x420")
        dialog.resizable(False, False)
        dialog.configure(bg=WHITE)
        dialog.grab_set()

        # Header
        header = tk.Frame(dialog, bg=BLUE, pady=20)
        header.pack(fill="x")

        initials = "".join([n[0] for n in
                            tenant['full_name'].split()[:2]]).upper()
        tk.Label(header, text=initials,
                 font=("Helvetica", 20, "bold"),
                 bg="#378ADD", fg=WHITE,
                 width=3).pack()
        tk.Label(header, text=tenant['full_name'],
                 font=("Helvetica", 13, "bold"),
                 bg=BLUE, fg=WHITE).pack(pady=(8, 2))
        tk.Label(header, text=f"Tenant ID: {tenant['tenant_id']}",
                 font=("Helvetica", 9),
                 bg=BLUE, fg="#B5D4F4").pack()

        # Details grid
        details = tk.Frame(dialog, bg=WHITE, padx=30, pady=20)
        details.pack(fill="both", expand=True)

        fields = [
            ("NI Number", tenant['ni_number']),
            ("Phone", tenant['phone']),
            ("Email", tenant['email']),
            ("Occupation", tenant['occupation']),
            ("Preferred Location", tenant.get('preferred_location', 'N/A')),
            ("Username", tenant.get('username', 'N/A')),
            ("Account Status", "Active" if tenant.get('is_active') else "Inactive"),
            ("Registered", tenant.get('created_at', '')[:10]),
        ]

        for i, (label, value) in enumerate(fields):
            tk.Label(details, text=label,
                     font=("Helvetica", 10),
                     bg=WHITE, fg="#888",
                     width=18, anchor="w").grid(row=i, column=0,
                     pady=5, sticky="w")
            tk.Label(details, text=value,
                     font=("Helvetica", 10),
                     bg=WHITE, fg="#1a1a1a",
                     anchor="w").grid(row=i, column=1,
                     pady=5, sticky="w")

        if tenant.get('references_info'):
            tk.Label(details, text="References",
                     font=("Helvetica", 10),
                     bg=WHITE, fg="#888",
                     anchor="w").grid(row=len(fields), column=0,
                     pady=5, sticky="nw")
            tk.Label(details, text=tenant['references_info'],
                     font=("Helvetica", 10),
                     bg=WHITE, fg="#1a1a1a",
                     wraplength=260, justify="left",
                     anchor="w").grid(row=len(fields), column=1,
                     pady=5, sticky="w")

        tk.Button(dialog, text="Close",
                  font=("Helvetica", 10), bg="#555", fg=WHITE,
                  relief="flat", cursor="hand2",
                  command=dialog.destroy).pack(pady=16, padx=30,
                  fill="x", ipady=6)

    def edit_tenant(self):
        if not self.selected_id:
            messagebox.showwarning("No selection",
                                   "Please select a tenant to edit.")
            return

        tenant = self.dao.get_by_id(self.selected_id)
        if not tenant:
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Edit Tenant - {tenant['full_name']}")
        dialog.geometry("440x400")
        dialog.resizable(False, False)
        dialog.configure(bg=WHITE)
        dialog.grab_set()

        tk.Label(dialog, text="Edit Tenant Details",
                 font=("Helvetica", 13, "bold"),
                 bg=WHITE, fg="#1a1a1a").pack(pady=(20, 16))

        form = tk.Frame(dialog, bg=WHITE, padx=30)
        form.pack(fill="x")

        fields_config = [
            ("Full Name", "full_name"),
            ("Phone", "phone"),
            ("Email", "email"),
            ("Occupation", "occupation"),
        ]

        entry_vars = {}
        for i, (label, key) in enumerate(fields_config):
            tk.Label(form, text=label,
                     font=("Helvetica", 10),
                     bg=WHITE, fg="#555").grid(row=i, column=0,
                     sticky="w", pady=6)
            var = tk.StringVar(value=tenant.get(key, ''))
            tk.Entry(form, textvariable=var,
                     font=("Helvetica", 11), width=28,
                     relief="solid", bd=1).grid(row=i, column=1,
                     sticky="ew", padx=(12, 0), pady=6)
            entry_vars[key] = var

        tk.Label(form, text="Preferred Location",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(row=len(fields_config),
                 column=0, sticky="w", pady=6)
        loc_var = tk.StringVar(value=tenant.get('preferred_location', ''))
        loc_menu = ttk.Combobox(form, textvariable=loc_var,
                                values=["Bristol", "Cardiff",
                                        "London", "Manchester"],
                                state="readonly",
                                font=("Helvetica", 11), width=26)
        loc_menu.grid(row=len(fields_config), column=1,
                      sticky="w", padx=(12, 0), pady=6)

        form.columnconfigure(1, weight=1)

        def save_edits():
            from dao.tenant_dao import TenantDAO
            dao = TenantDAO()
            dao.update(
                tenant_id=self.selected_id,
                full_name=entry_vars['full_name'].get().strip(),
                phone=entry_vars['phone'].get().strip(),
                email=entry_vars['email'].get().strip(),
                occupation=entry_vars['occupation'].get().strip(),
                references_info=tenant.get('references_info', ''),
                preferred_location=loc_var.get()
            )
            messagebox.showinfo("Updated",
                                "Tenant updated successfully.",
                                parent=dialog)
            dialog.destroy()
            self.load_all()

        tk.Button(dialog, text="Save Changes",
                  font=("Helvetica", 11, "bold"),
                  bg=BLUE, fg=WHITE, relief="flat",
                  cursor="hand2",
                  command=save_edits).pack(pady=20, padx=30,
                  fill="x", ipady=8)