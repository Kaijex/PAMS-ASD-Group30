# ui/modules/my_payments.py
# My Payments Module - Tenant view of their payment history
# Student ID: 23029574 | Campbell Clark
# Student ID: 25013991 | Adjeneg Imed
# Group 30 - PAMS

import tkinter as tk
from tkinter import ttk
from dao.payment_dao import PaymentDAO
from dao.tenant_dao import TenantDAO

CONTENT_BG = "#F8FAFC"
WHITE = "#FFFFFF"
PRIMARY = "#2563EB"
TEXT_DARK = "#0F172A"
TEXT_MUTED = "#64748B"
SUCCESS = "#16A34A"
WARNING = "#D97706"
DANGER = "#DC2626"
CARD_BORDER = "#E2E8F0"
SECTION_BG = "#EEF4FF"

STATUS_COLOURS = {
    "paid": SUCCESS,
    "pending": WARNING,
    "late": DANGER
}


class MyPaymentsModule(tk.Frame):
    def __init__(self, parent, user=None, mode="tenant"):
        super().__init__(parent, bg=CONTENT_BG)
        self.payment_dao = PaymentDAO()
        self.tenant_dao = TenantDAO()
        self.user = user
        self.mode = mode
        self.selected_id = None
        self.all_payments = []
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

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def page_title(self, parent, text, subtitle=None):
        tk.Label(
            parent,
            text=text,
            font=("Helvetica", 20, "bold"),
            bg=CONTENT_BG,
            fg=TEXT_DARK
        ).pack(anchor="w", pady=(18, 4), padx=4)

        if subtitle:
            tk.Label(
                parent,
                text=subtitle,
                font=("Helvetica", 10),
                bg=CONTENT_BG,
                fg=TEXT_MUTED
            ).pack(anchor="w", padx=4, pady=(0, 18))

    def section_label(self, parent, text):
        wrapper = tk.Frame(parent, bg=CONTENT_BG)
        wrapper.pack(fill="x", pady=(4, 10))

        label_box = tk.Frame(
            wrapper,
            bg=SECTION_BG,
            highlightbackground=CARD_BORDER,
            highlightthickness=1
        )
        label_box.pack(anchor="w")

        tk.Label(
            label_box,
            text=text,
            font=("Helvetica", 11, "bold"),
            bg=SECTION_BG,
            fg=TEXT_DARK,
            padx=14,
            pady=8
        ).pack()

    def card_stat(self, parent, title, value, colour):
        card = tk.Frame(
            parent,
            bg=WHITE,
            padx=22,
            pady=18,
            highlightbackground=CARD_BORDER,
            highlightthickness=1
        )
        card.pack(side="left", padx=(0, 16))

        tk.Label(
            card,
            text=title,
            font=("Helvetica", 10),
            bg=WHITE,
            fg=TEXT_MUTED
        ).pack(anchor="w")

        tk.Label(
            card,
            text=value,
            font=("Helvetica", 20, "bold"),
            bg=WHITE,
            fg=colour
        ).pack(anchor="w", pady=(8, 0))

    def table_card(self, parent):
        outer = tk.Frame(
            parent,
            bg=WHITE,
            highlightbackground=CARD_BORDER,
            highlightthickness=1
        )
        outer.pack(fill="both", expand=True, pady=(0, 18))

        inner = tk.Frame(outer, bg=WHITE)
        inner.pack(fill="both", expand=True, padx=12, pady=12)
        return inner

    def action_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            font=("Helvetica", 10, "bold"),
            bg=PRIMARY,
            fg=WHITE,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=8,
            activebackground="#1D4ED8",
            activeforeground=WHITE,
            command=command
        )

    # ------------------------------------------------------------------
    # Payments tab
    # ------------------------------------------------------------------

    def build_payments_tab(self, parent):
        self.page_title(
            parent,
            "My Payment History",
            "View your invoices, payment status, and rent payment records."
        )

        self.section_label(parent, "Filter Payments")
        filter_frame = tk.Frame(parent, bg=CONTENT_BG)
        filter_frame.pack(fill="x", pady=(0, 12))

        tk.Label(
            filter_frame,
            text="Show:",
            font=("Helvetica", 10),
            bg=CONTENT_BG,
            fg=TEXT_MUTED
        ).pack(side="left", padx=(0, 10))

        self.filter_var = tk.StringVar(value="all")
        for label, value in [
            ("All", "all"),
            ("Paid", "paid"),
            ("Pending", "pending"),
            ("Late", "late")
        ]:
            tk.Radiobutton(
                filter_frame,
                text=label,
                variable=self.filter_var,
                value=value,
                bg=CONTENT_BG,
                fg=TEXT_DARK,
                font=("Helvetica", 10),
                activebackground=CONTENT_BG,
                selectcolor=WHITE,
                command=self.apply_filter
            ).pack(side="left", padx=6)

        table_frame = self.table_card(parent)

        cols = ("ID", "Apartment", "Location", "Amount", "Due Date", "Paid Date", "Status", "Notes")
        self.pay_tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=12)

        widths = [60, 120, 120, 100, 110, 110, 90, 220]
        for col, width in zip(cols, widths):
            self.pay_tree.heading(col, text=col)
            self.pay_tree.column(col, width=width, anchor="center")

        for status, colour in STATUS_COLOURS.items():
            self.pay_tree.tag_configure(status, foreground=colour)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.pay_tree.yview)
        self.pay_tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.pay_tree.pack(fill="both", expand=True)

        btn_row = tk.Frame(parent, bg=CONTENT_BG)
        btn_row.pack(fill="x", pady=(0, 4))

        self.action_button(btn_row, "Refresh", self.load_payments).pack(anchor="w")

        self.load_payments()

    # ------------------------------------------------------------------
    # Summary tab
    # ------------------------------------------------------------------

    def build_summary_tab(self, parent):
        self.page_title(
            parent,
            "Payment Summary",
            "See an overview of paid, pending, and overdue rent invoices."
        )

        self.summary_frame = tk.Frame(parent, bg=CONTENT_BG)
        self.summary_frame.pack(fill="both", expand=True)

        btn_row = tk.Frame(parent, bg=CONTENT_BG)
        btn_row.pack(fill="x", pady=(0, 4))

        self.action_button(btn_row, "Refresh", self.load_summary).pack(anchor="w")

        self.load_summary()

    # ------------------------------------------------------------------
    # Data helpers
    # ------------------------------------------------------------------

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

        self.all_payments = self.payment_dao.get_by_tenant(tenant['tenant_id'])
        self.populate_table(self.all_payments)

    def populate_table(self, payments):
        for row in self.pay_tree.get_children():
            self.pay_tree.delete(row)

        for p in payments:
            paid_date = p['paid_date'] if p['paid_date'] else "—"
            notes = p['notes'] if p['notes'] else ""

            self.pay_tree.insert(
                "",
                "end",
                iid=p['payment_id'],
                values=(
                    p['payment_id'],
                    p['apartment_number'],
                    p['location'],
                    f"£{float(p['amount']):,.2f}",
                    p['due_date'],
                    paid_date,
                    p['status'].capitalize(),
                    notes
                ),
                tags=(p['status'],)
            )

    def apply_filter(self):
        choice = self.filter_var.get()

        if choice == "all":
            self.populate_table(self.all_payments)
        else:
            filtered = [p for p in self.all_payments if p['status'] == choice]
            self.populate_table(filtered)

    def load_summary(self):
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        tenant = self.get_tenant()
        if not tenant:
            tk.Label(
                self.summary_frame,
                text="No tenant record linked to this account.",
                font=("Helvetica", 11),
                bg=CONTENT_BG,
                fg=DANGER
            ).pack(anchor="w", padx=4, pady=(6, 0))
            return

        payments = self.payment_dao.get_by_tenant(tenant['tenant_id'])

        paid_total = sum(p['amount'] for p in payments if p['status'] == 'paid')
        pending_total = sum(p['amount'] for p in payments if p['status'] == 'pending')
        late_total = sum(p['amount'] for p in payments if p['status'] == 'late')
        total_count = len(payments)

        self.section_label(self.summary_frame, "Summary Cards")
        row_frame = tk.Frame(self.summary_frame, bg=CONTENT_BG)
        row_frame.pack(fill="x", pady=(0, 20))

        cards = [
            ("Total Paid", f"£{paid_total:,.2f}", SUCCESS),
            ("Pending", f"£{pending_total:,.2f}", WARNING),
            ("Overdue", f"£{late_total:,.2f}", DANGER),
            ("Total Invoices", str(total_count), PRIMARY),
        ]

        for title, value, colour in cards:
            self.card_stat(row_frame, title, value, colour)

        self.section_label(self.summary_frame, "Quick Insight")

        insight_box = tk.Frame(
            self.summary_frame,
            bg=WHITE,
            highlightbackground=CARD_BORDER,
            highlightthickness=1,
            padx=18,
            pady=16
        )
        insight_box.pack(fill="x")

        if late_total > 0:
            insight_text = "You currently have overdue payments that need attention."
            insight_colour = DANGER
        elif pending_total > 0:
            insight_text = "You have upcoming unpaid invoices due soon."
            insight_colour = WARNING
        else:
            insight_text = "Your payment record is currently up to date."
            insight_colour = SUCCESS

        tk.Label(
            insight_box,
            text=insight_text,
            font=("Helvetica", 11, "bold"),
            bg=WHITE,
            fg=insight_colour
        ).pack(anchor="w")