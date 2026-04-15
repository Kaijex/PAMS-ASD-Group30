# ui/modules/my_payments.py
# My Payments Module - Tenant view of their payment history
# Student ID: 23029574 | Campbell Clark
# Group 30 - PAMS

import tkinter as tk
from tkinter import ttk
from dao.payment_dao import PaymentDAO
from dao.tenant_dao import TenantDAO

CONTENT_BG = "#f0f4f8"
WHITE = "#ffffff"
BLUE = "#185FA5"

STATUS_COLOURS = {
    "paid": "#0F6E56",
    "pending": "#BA7517",
    "late": "#A32D2D"
}

class MyPaymentsModule(tk.Frame):
    def __init__(self, parent, user=None, mode="tenant"):
        super().__init__(parent, bg=CONTENT_BG)
        self.payment_dao = PaymentDAO()
        self.tenant_dao = TenantDAO()
        self.user = user
        self.mode = mode
        self.selected_id = None
        self.build()

    def build(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        all_tab = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(all_tab, text="  All Payments  ")

        summary_tab = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(summary_tab, text="  Summary  ")

        self.build_payments_tab(all_tab)
        self.build_summary_tab(summary_tab)

    def build_payments_tab(self, parent):
        tk.Label(parent, text="My Payment History",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 8), padx=16)

        # Filter row
        filter_frame = tk.Frame(parent, bg=CONTENT_BG)
        filter_frame.pack(fill="x", padx=16, pady=(0, 8))

        tk.Label(filter_frame, text="Filter:",
                 font=("Helvetica", 10),
                 bg=CONTENT_BG, fg="#555").pack(side="left",
                 padx=(0, 8))

        self.filter_var = tk.StringVar(value="all")
        for label, value in [("All", "all"), ("Paid", "paid"),
                              ("Pending", "pending"), ("Late", "late")]:
            tk.Radiobutton(filter_frame, text=label,
                           variable=self.filter_var, value=value,
                           bg=CONTENT_BG, font=("Helvetica", 10),
                           activebackground=CONTENT_BG,
                           command=self.apply_filter).pack(
                           side="left", padx=4)

        table_frame = tk.Frame(parent, bg=WHITE)
        table_frame.pack(fill="both", expand=True, padx=16)

        cols = ("ID", "Apartment", "Location",
                "Amount", "Due Date", "Paid Date", "Status", "Notes")
        self.pay_tree = ttk.Treeview(table_frame, columns=cols,
                                      show="headings", height=12)
        widths = [40, 100, 100, 80, 90, 90, 70, 180]
        for col, width in zip(cols, widths):
            self.pay_tree.heading(col, text=col)
            self.pay_tree.column(col, width=width, anchor="center")

        for status, colour in STATUS_COLOURS.items():
            self.pay_tree.tag_configure(status, foreground=colour)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.pay_tree.yview)
        self.pay_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.pay_tree.pack(fill="both", expand=True)

        tk.Button(parent, text="Refresh",
                  font=("Helvetica", 10), bg=BLUE, fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.load_payments).pack(
                  anchor="w", padx=16, pady=10, ipady=6)

        self.load_payments()

    def build_summary_tab(self, parent):
        tk.Label(parent, text="Payment Summary",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 12), padx=16)

        self.summary_frame = tk.Frame(parent, bg=CONTENT_BG)
        self.summary_frame.pack(fill="x", padx=16)

        tk.Button(parent, text="Refresh",
                  font=("Helvetica", 10), bg=BLUE, fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.load_summary).pack(
                  anchor="w", padx=16, pady=10, ipady=6)

        self.load_summary()

    def get_tenant(self):
        if not self.user:
            return None
        return self.tenant_dao.get_by_user_id(self.user['user_id'])

    def load_payments(self):
        self.all_payments = []
        for row in self.pay_tree.get_children():
            self.pay_tree.delete(row)

        tenant = self.get_tenant()
        if not tenant:
            return

        self.all_payments = self.payment_dao.get_by_tenant(
            tenant['tenant_id'])
        self.populate_table(self.all_payments)

    def populate_table(self, payments):
        for row in self.pay_tree.get_children():
            self.pay_tree.delete(row)
        for p in payments:
            paid_date = p['paid_date'] if p['paid_date'] else "—"
            notes = p['notes'] if p['notes'] else ""
            self.pay_tree.insert("", "end",
                iid=p['payment_id'],
                values=(p['payment_id'],
                        p['apartment_number'],
                        p['location'],
                        f"£{float(p['amount']):,.2f}",
                        p['due_date'],
                        paid_date,
                        p['status'].capitalize(),
                        notes),
                tags=(p['status'],))

    def apply_filter(self):
        choice = self.filter_var.get()
        if choice == "all":
            self.populate_table(self.all_payments)
        else:
            filtered = [p for p in self.all_payments
                        if p['status'] == choice]
            self.populate_table(filtered)

    def load_summary(self):
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        tenant = self.get_tenant()
        if not tenant:
            tk.Label(self.summary_frame,
                     text="No tenant record linked to this account.",
                     font=("Helvetica", 11),
                     bg=CONTENT_BG, fg="#A32D2D").pack(anchor="w")
            return

        payments = self.payment_dao.get_by_tenant(tenant['tenant_id'])

        paid_total    = sum(p['amount'] for p in payments
                            if p['status'] == 'paid')
        pending_total = sum(p['amount'] for p in payments
                            if p['status'] == 'pending')
        late_total    = sum(p['amount'] for p in payments
                            if p['status'] == 'late')
        total_count   = len(payments)

        cards = [
            ("Total Paid",    f"£{paid_total:,.2f}",    "#0F6E56"),
            ("Pending",       f"£{pending_total:,.2f}", "#BA7517"),
            ("Overdue",       f"£{late_total:,.2f}",    "#A32D2D"),
            ("Total Invoices", str(total_count),         BLUE),
        ]

        row_frame = tk.Frame(self.summary_frame, bg=CONTENT_BG)
        row_frame.pack(fill="x", pady=(0, 20))

        for title, value, colour in cards:
            card = tk.Frame(row_frame, bg=WHITE,
                            padx=20, pady=16)
            card.pack(side="left", padx=(0, 14))

            tk.Label(card, text=title,
                     font=("Helvetica", 10),
                     bg=WHITE, fg="#888").pack(anchor="w")
            tk.Label(card, text=value,
                     font=("Helvetica", 16, "bold"),
                     bg=WHITE, fg=colour).pack(anchor="w",
                     pady=(4, 0))