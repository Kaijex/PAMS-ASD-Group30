# ui/modules/my_lease.py
# My Lease Module - Tenant view of their lease details
# Student ID: 23029574 | Campbell Clark
# Student ID: 25013991 | Adjeneg Imed
# Group 30 - PAMS

import tkinter as tk
from tkinter import ttk
from dao.lease_dao import LeaseDAO
from dao.tenant_dao import TenantDAO

CONTENT_BG = "#f0f4f8"
WHITE = "#ffffff"
BLUE = "#185FA5"

STATUS_COLOURS = {
    "active": "#0F6E56",
    "terminated": "#A32D2D",
    "expired": "#BA7517"
}

class MyLeaseModule(tk.Frame):
    def __init__(self, parent, user=None, mode="tenant"):
        super().__init__(parent, bg=CONTENT_BG)
        self.lease_dao = LeaseDAO()
        self.tenant_dao = TenantDAO()
        self.user = user
        self.mode = mode
        self.build()

    def build(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        active_tab = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(active_tab, text="  My Active Lease  ")

        history_tab = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(history_tab, text="  Lease History  ")

        self.build_active_tab(active_tab)
        self.build_history_tab(history_tab)

    def build_active_tab(self, parent):
        tk.Label(parent, text="My Active Lease",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 12), padx=16)

        self.active_card_frame = tk.Frame(parent, bg=CONTENT_BG)
        self.active_card_frame.pack(fill="x", padx=16)

        tk.Button(parent, text="Refresh",
                  font=("Helvetica", 10), bg=BLUE, fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.load_active_lease).pack(
                  anchor="w", padx=16, pady=10, ipady=6)

        self.load_active_lease()

    def build_history_tab(self, parent):
        tk.Label(parent, text="Lease History",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 8), padx=16)

        table_frame = tk.Frame(parent, bg=WHITE)
        table_frame.pack(fill="both", expand=True, padx=16)

        cols = ("ID", "Apartment", "Location", "Type",
                "Start Date", "End Date", "Rent", "Deposit", "Status")
        self.history_tree = ttk.Treeview(table_frame, columns=cols,
                                          show="headings", height=12)
        widths = [40, 100, 100, 90, 90, 90, 80, 80, 80]
        for col, width in zip(cols, widths):
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=width, anchor="center")

        for status, colour in STATUS_COLOURS.items():
            self.history_tree.tag_configure(status, foreground=colour)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.history_tree.pack(fill="both", expand=True)

        tk.Button(parent, text="Refresh",
                  font=("Helvetica", 10), bg=BLUE, fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.load_history).pack(
                  anchor="w", padx=16, pady=10, ipady=6)

        self.load_history()

    def get_tenant(self):
        if not self.user:
            return None
        return self.tenant_dao.get_by_user_id(self.user['user_id'])

    def load_active_lease(self):
        for widget in self.active_card_frame.winfo_children():
            widget.destroy()

        tenant = self.get_tenant()
        if not tenant:
            tk.Label(self.active_card_frame,
                     text="No tenant record linked to this account.",
                     font=("Helvetica", 11),
                     bg=CONTENT_BG, fg="#A32D2D").pack(anchor="w")
            return

        leases = self.lease_dao.get_by_tenant(tenant['tenant_id'])
        active = next((l for l in leases
                       if l['status'] == 'active'), None)

        if not active:
            tk.Label(self.active_card_frame,
                     text="You do not currently have an active lease.",
                     font=("Helvetica", 11),
                     bg=CONTENT_BG, fg="#BA7517").pack(anchor="w")
            return

        card = tk.Frame(self.active_card_frame, bg=WHITE,
                        padx=24, pady=20)
        card.pack(fill="x", pady=(0, 12))

        # Header row
        header = tk.Frame(card, bg=WHITE)
        header.pack(fill="x", pady=(0, 12))

        tk.Label(header,
                 text=f"Apartment {active['apartment_number']} — {active['location']}",
                 font=("Helvetica", 13, "bold"),
                 bg=WHITE, fg=BLUE).pack(side="left")

        tk.Label(header, text="  ACTIVE  ",
                 font=("Helvetica", 9, "bold"),
                 bg="#0F6E56", fg=WHITE).pack(
                 side="left", padx=(12, 0))

        tk.Frame(card, bg="#eee", height=1).pack(fill="x", pady=(0, 14))

        # Details grid
        details = tk.Frame(card, bg=WHITE)
        details.pack(fill="x")

        fields = [
            ("Apartment Type", active.get('type', 'N/A')),
            ("Start Date",     active['start_date']),
            ("End Date",       active['end_date']),
            ("Monthly Rent",   f"£{float(active['monthly_rent']):,.2f}"),
            ("Deposit Paid",   f"£{float(active['deposit_amount']):,.2f}"),
            ("Lease Status",   active['status'].capitalize()),
        ]

        for i, (label, value) in enumerate(fields):
            row = i // 2
            col_offset = (i % 2) * 4

            tk.Label(details, text=f"{label}:",
                     font=("Helvetica", 10),
                     bg=WHITE, fg="#888").grid(
                     row=row, column=col_offset,
                     sticky="w", padx=(0, 8), pady=6)
            tk.Label(details, text=value,
                     font=("Helvetica", 10, "bold"),
                     bg=WHITE, fg="#1a1a1a").grid(
                     row=row, column=col_offset + 1,
                     sticky="w", padx=(0, 40), pady=6)

    def load_history(self):
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)

        tenant = self.get_tenant()
        if not tenant:
            return

        leases = self.lease_dao.get_by_tenant(tenant['tenant_id'])
        for l in leases:
            self.history_tree.insert("", "end",
                values=(l['lease_id'],
                        l['apartment_number'],
                        l['location'],
                        l.get('type', 'N/A'),
                        l['start_date'],
                        l['end_date'],
                        f"£{float(l['monthly_rent']):,.2f}",
                        f"£{float(l['deposit_amount']):,.2f}",
                        l['status'].capitalize()),
                tags=(l['status'],))