# ui/modules/early_termination.py
# Early Termination Module - Tenant request to end lease early
# Student ID: 23029574 | Campbell Clark
# Group 30 - PAMS

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
from dao.termination_dao import TerminationDAO
from dao.lease_dao import LeaseDAO
from dao.tenant_dao import TenantDAO

CONTENT_BG = "#f0f4f8"
WHITE = "#ffffff"
BLUE = "#185FA5"

STATUS_COLOURS = {
    "pending":  "#BA7517",
    "approved": "#0F6E56",
    "rejected": "#A32D2D",
}

class EarlyTerminationModule(tk.Frame):
    def __init__(self, parent, user=None, **kwargs):
        super().__init__(parent, bg=CONTENT_BG, **kwargs)
        self.dao         = TerminationDAO()
        self.lease_dao   = LeaseDAO()
        self.tenant_dao  = TenantDAO()
        self.user        = user
        self.build()

    def build(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        request_tab = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(request_tab, text="  Request Termination  ")

        history_tab = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(history_tab, text="  My Requests  ")

        self.build_request_tab(request_tab)
        self.build_history_tab(history_tab)

    def build_request_tab(self, parent):
        tk.Label(parent, text="Request Early Termination",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 4), padx=16)

        tk.Label(parent,
                 text="You must give 1 month notice. A penalty of 5% "
                      "of your monthly rent will be applied.",
                 font=("Helvetica", 10),
                 bg=CONTENT_BG, fg="#888").pack(
                 anchor="w", padx=16, pady=(0, 16))

        self.info_frame = tk.Frame(parent, bg=CONTENT_BG)
        self.info_frame.pack(fill="x", padx=16, pady=(0, 8))

        self.load_lease_info()

        tk.Button(parent, text="Submit Termination Request",
                  font=("Helvetica", 11, "bold"),
                  bg="#A32D2D", fg=WHITE, relief="flat",
                  cursor="hand2",
                  command=self.submit_request).pack(
                  fill="x", padx=16, pady=(8, 0), ipady=10)

    def build_history_tab(self, parent):
        tk.Label(parent, text="My Termination Requests",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 8), padx=16)

        table_frame = tk.Frame(parent, bg=WHITE)
        table_frame.pack(fill="both", expand=True, padx=16)

        cols = ("ID", "Apartment", "Location", "Request Date",
                "Notice End Date", "Penalty", "Status")
        self.history_tree = ttk.Treeview(table_frame, columns=cols,
                                          show="headings", height=12)
        widths = [40, 100, 100, 100, 120, 90, 90]
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

    def load_lease_info(self):
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        tenant = self.get_tenant()
        if not tenant:
            tk.Label(self.info_frame,
                     text="No tenant record linked to this account.",
                     font=("Helvetica", 11),
                     bg=CONTENT_BG, fg="#A32D2D").pack(anchor="w")
            return

        leases = self.lease_dao.get_by_tenant(tenant['tenant_id'])
        self.active_lease = next(
            (l for l in leases if l['status'] == 'active'), None)

        if not self.active_lease:
            tk.Label(self.info_frame,
                     text="You do not have an active lease to terminate.",
                     font=("Helvetica", 11),
                     bg=CONTENT_BG, fg="#BA7517").pack(anchor="w")
            return

        # Calculate notice end date and penalty
        today           = date.today()
        notice_end      = today + timedelta(days=30)
        monthly_rent    = float(self.active_lease['monthly_rent'])
        penalty         = round(monthly_rent * 0.05, 2)

        self.request_date    = str(today)
        self.notice_end_date = str(notice_end)
        self.penalty_amount  = penalty

        card = tk.Frame(self.info_frame, bg=WHITE, padx=24, pady=20)
        card.pack(fill="x", pady=(0, 12))

        tk.Label(card,
                 text=f"Apartment {self.active_lease['apartment_number']}"
                      f" — {self.active_lease['location']}",
                 font=("Helvetica", 13, "bold"),
                 bg=WHITE, fg=BLUE).pack(anchor="w", pady=(0, 12))

        tk.Frame(card, bg="#eee", height=1).pack(fill="x", pady=(0, 14))

        details = tk.Frame(card, bg=WHITE)
        details.pack(fill="x")

        fields = [
            ("Request Date",     self.request_date),
            ("Notice Period",    "1 month"),
            ("Lease Ends",       self.active_lease['end_date']),
            ("Vacate By",        self.notice_end_date),
            ("Monthly Rent",     f"£{monthly_rent:,.2f}"),
            ("Penalty (5%)",     f"£{penalty:,.2f}"),
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

    def submit_request(self):
        tenant = self.get_tenant()
        if not tenant:
            messagebox.showerror("Error",
                "No tenant record found for your account.")
            return

        if not hasattr(self, 'active_lease') or not self.active_lease:
            messagebox.showerror("No active lease",
                "You do not have an active lease to terminate.")
            return

        if self.dao.has_pending(tenant['tenant_id']):
            messagebox.showwarning("Already submitted",
                "You already have a pending termination request.")
            return

        if not messagebox.askyesno("Confirm Termination Request",
            f"Submit early termination request?\n\n"
            f"Notice end date: {self.notice_end_date}\n"
            f"Penalty amount: £{self.penalty_amount:,.2f}\n\n"
            f"This request will be reviewed by staff."):
            return

        self.dao.create(
            self.active_lease['lease_id'],
            tenant['tenant_id'],
            self.request_date,
            self.notice_end_date,
            self.penalty_amount
        )
        messagebox.showinfo("Submitted",
            "Your termination request has been submitted.\n"
            "Staff will review and confirm shortly.")
        self.load_history()

    def load_history(self):
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)

        tenant = self.get_tenant()
        if not tenant:
            return

        requests = self.dao.get_by_tenant(tenant['tenant_id'])
        for r in requests:
            self.history_tree.insert("", "end",
                values=(r['termination_id'],
                        r['apartment_number'],
                        r['location'],
                        r['request_date'],
                        r['notice_end_date'],
                        f"£{float(r['penalty_amount']):,.2f}",
                        r['status'].capitalize()),
                tags=(r['status'],))