# ui/modules/payments.py
# Payments and Billing Module
# Student ID: 23029574 | Campbell Clark
# Student ID: 25013991 | Adjeneg Imed
# Group 30 - PAMS

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
from dao.payment_dao import PaymentDAO
from dao.tenant_dao import TenantDAO
from dao.lease_dao import LeaseDAO

CONTENT_BG = "#f0f4f8"
WHITE = "#ffffff"
BLUE = "#185FA5"

class PaymentsModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CONTENT_BG)
        self.payment_dao = PaymentDAO()
        self.tenant_dao = TenantDAO()
        self.lease_dao = LeaseDAO()
        self.selected_payment_id = None
        self.build()

    def build(self):
        # Auto flag any overdue payments on load
        self.payment_dao.auto_flag_late()

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        overview_tab = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(overview_tab, text="  Overview  ")

        invoices_tab = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(invoices_tab, text="  All Invoices  ")

        late_tab = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(late_tab, text="  Late Payments  ")

        new_tab = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(new_tab, text="  New Invoice  ")

        self.build_overview_tab(overview_tab)
        self.build_invoices_tab(invoices_tab)
        self.build_late_tab(late_tab)
        self.build_new_invoice_tab(new_tab)

    def build_overview_tab(self, parent):
        tk.Label(parent, text="Financial Overview",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 20), padx=16)

        summary = self.payment_dao.get_summary()

        stats_frame = tk.Frame(parent, bg=CONTENT_BG)
        stats_frame.pack(fill="x", padx=16, pady=(0, 20))

        stats = [
            ("Total Collected", f"£{summary.get('collected') or 0:.2f}", "#0F6E56"),
            ("Pending", f"£{summary.get('pending') or 0:.2f}", "#185FA5"),
            ("Late / Overdue", f"£{summary.get('late') or 0:.2f}", "#A32D2D"),
            ("Total Invoices", str(summary.get('total_invoices') or 0), "#444"),
        ]

        for label, value, color in stats:
            card = tk.Frame(stats_frame, bg=WHITE,
                           padx=20, pady=16)
            card.pack(side="left", expand=True,
                     fill="both", padx=(0, 12))
            tk.Label(card, text=label,
                     font=("Helvetica", 10),
                     bg=WHITE, fg="#888").pack(anchor="w")
            tk.Label(card, text=value,
                     font=("Helvetica", 18, "bold"),
                     bg=WHITE, fg=color).pack(anchor="w", pady=(4, 0))

        # Pending invoices table
        tk.Label(parent, text="Pending Invoices",
                 font=("Helvetica", 12, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", padx=16, pady=(0, 8))

        table_frame = tk.Frame(parent, bg=WHITE)
        table_frame.pack(fill="both", expand=True, padx=16)

        cols = ("ID", "Tenant", "Apartment", "Amount",
                "Due Date", "Status")
        tree = ttk.Treeview(table_frame, columns=cols,
                            show="headings", height=8)
        widths = [40, 160, 120, 90, 100, 90]
        for col, width in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")

        tree.tag_configure("late", foreground="#A32D2D")
        tree.tag_configure("pending", foreground="#185FA5")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        pending = self.payment_dao.get_pending()
        for p in pending:
            tree.insert("", "end", values=(
                p['payment_id'], p['tenant_name'],
                p['apartment_number'],
                f"£{p['amount']:.2f}",
                p['due_date'], p['status']
            ), tags=(p['status'],))

    def build_invoices_tab(self, parent):
        top = tk.Frame(parent, bg=CONTENT_BG)
        top.pack(fill="x", padx=16, pady=(16, 8))

        tk.Label(top, text="All Invoices",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(side="left")

        tk.Button(top, text="Mark Selected as Paid",
                  font=("Helvetica", 10), bg="#0F6E56", fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.mark_paid).pack(side="right", ipady=6)

        table_frame = tk.Frame(parent, bg=WHITE)
        table_frame.pack(fill="both", expand=True, padx=16)

        cols = ("ID", "Tenant", "Apartment", "Location",
                "Amount", "Due Date", "Paid Date", "Status", "Notes")
        self.invoice_tree = ttk.Treeview(table_frame, columns=cols,
                                          show="headings", height=14)
        widths = [40, 130, 100, 90, 80, 90, 90, 80, 120]
        for col, width in zip(cols, widths):
            self.invoice_tree.heading(col, text=col)
            self.invoice_tree.column(col, width=width, anchor="center")

        self.invoice_tree.tag_configure("paid", foreground="#0F6E56")
        self.invoice_tree.tag_configure("late", foreground="#A32D2D")
        self.invoice_tree.tag_configure("pending", foreground="#185FA5")

        self.invoice_tree.bind("<<TreeviewSelect>>",
                               self.on_invoice_select)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.invoice_tree.yview)
        self.invoice_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.invoice_tree.pack(fill="both", expand=True)

        self.load_all_invoices()

    def build_late_tab(self, parent):
        tk.Label(parent, text="Late & Overdue Payments",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 8), padx=16)

        tk.Label(parent,
                 text="These invoices are past their due date and remain unpaid.",
                 font=("Helvetica", 10),
                 bg=CONTENT_BG, fg="#888").pack(anchor="w", padx=16,
                 pady=(0, 12))

        table_frame = tk.Frame(parent, bg=WHITE)
        table_frame.pack(fill="both", expand=True, padx=16)

        cols = ("ID", "Tenant", "Apartment", "Amount",
                "Due Date", "Days Overdue")
        self.late_tree = ttk.Treeview(table_frame, columns=cols,
                                       show="headings", height=12)
        widths = [40, 160, 120, 90, 100, 100]
        for col, width in zip(cols, widths):
            self.late_tree.heading(col, text=col)
            self.late_tree.column(col, width=width, anchor="center")

        self.late_tree.tag_configure("late", foreground="#A32D2D")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.late_tree.yview)
        self.late_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.late_tree.pack(fill="both", expand=True)

        btn_frame = tk.Frame(parent, bg=CONTENT_BG)
        btn_frame.pack(fill="x", padx=16, pady=10)

        tk.Button(btn_frame, text="Refresh",
                  font=("Helvetica", 10), bg=BLUE, fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.load_late_payments).pack(
                  side="left", ipady=6)

        self.load_late_payments()

    def build_new_invoice_tab(self, parent):
        canvas = tk.Canvas(parent, bg=CONTENT_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical",
                                   command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        form_frame = tk.Frame(canvas, bg=CONTENT_BG)
        canvas_win = canvas.create_window((0, 0),
                                          window=form_frame, anchor="nw")
        form_frame.bind("<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(canvas_win, width=e.width))

        tk.Label(form_frame, text="Create New Invoice",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 20), padx=16)

        card = tk.Frame(form_frame, bg=WHITE, padx=30, pady=24)
        card.pack(fill="x", padx=16)

        # Tenant selection
        tk.Label(card, text="Select Tenant",
                 font=("Helvetica", 11, "bold"),
                 bg=WHITE, fg=BLUE).pack(anchor="w", pady=(0, 8))

        tenant_cols = ("ID", "Name", "Location")
        self.inv_tenant_tree = ttk.Treeview(card,
                                             columns=tenant_cols,
                                             show="headings", height=4)
        for col in tenant_cols:
            self.inv_tenant_tree.heading(col, text=col)
            self.inv_tenant_tree.column(col, width=140, anchor="center")
        self.inv_tenant_tree.pack(fill="x", pady=(0, 16))

        tenants = self.tenant_dao.get_all()
        for t in tenants:
            self.inv_tenant_tree.insert("", "end",
                iid=t['tenant_id'],
                values=(t['tenant_id'], t['full_name'],
                        t.get('preferred_location', '')))

        tk.Frame(card, bg="#eee", height=1).pack(fill="x", pady=(0, 16))

        # Invoice details
        tk.Label(card, text="Invoice Details",
                 font=("Helvetica", 11, "bold"),
                 bg=WHITE, fg=BLUE).pack(anchor="w", pady=(0, 12))

        form = tk.Frame(card, bg=WHITE)
        form.pack(fill="x")

        next_month = date.today() + timedelta(days=30)

        fields = [
            ("Amount (£)", "amount"),
            ("Due Date (YYYY-MM-DD)", "due_date"),
            ("Notes", "notes"),
        ]
        self.inv_entries = {}
        defaults = {"due_date": str(next_month)}

        for i, (label, key) in enumerate(fields):
            tk.Label(form, text=label,
                     font=("Helvetica", 10),
                     bg=WHITE, fg="#555").grid(row=i, column=0,
                     sticky="w", pady=8, padx=(0, 12))
            var = tk.StringVar(value=defaults.get(key, ""))
            tk.Entry(form, textvariable=var,
                     font=("Helvetica", 11), width=30,
                     relief="solid", bd=1).grid(row=i, column=1,
                     sticky="ew", pady=8)
            self.inv_entries[key] = var

        form.columnconfigure(1, weight=1)

        tk.Button(card, text="Generate Invoice",
                  font=("Helvetica", 11, "bold"),
                  bg=BLUE, fg=WHITE, relief="flat",
                  cursor="hand2",
                  command=self.create_invoice).pack(
                  fill="x", pady=(20, 0), ipady=10)

    def load_all_invoices(self):
        for row in self.invoice_tree.get_children():
            self.invoice_tree.delete(row)
        payments = self.payment_dao.get_all()
        for p in payments:
            self.invoice_tree.insert("", "end",
                iid=p['payment_id'],
                values=(
                    p['payment_id'],
                    p['tenant_name'],
                    p['apartment_number'],
                    p['location'],
                    f"£{p['amount']:.2f}",
                    p['due_date'],
                    p.get('paid_date') or '-',
                    p['status'],
                    p.get('notes') or ''
                ), tags=(p['status'],))

    def load_late_payments(self):
        for row in self.late_tree.get_children():
            self.late_tree.delete(row)
        late = self.payment_dao.get_late()
        today = date.today()
        for p in late:
            try:
                due = date.fromisoformat(p['due_date'])
                days_over = (today - due).days
            except Exception:
                days_over = "?"
            self.late_tree.insert("", "end",
                values=(
                    p['payment_id'],
                    p['tenant_name'],
                    p['apartment_number'],
                    f"£{p['amount']:.2f}",
                    p['due_date'],
                    f"{days_over} days"
                ), tags=("late",))

    def on_invoice_select(self, event):
        selected = self.invoice_tree.selection()
        if selected:
            self.selected_payment_id = int(selected[0])

    def mark_paid(self):
        if not self.selected_payment_id:
            messagebox.showwarning("No selection",
                                   "Please select an invoice to mark as paid.")
            return
        if messagebox.askyesno("Confirm",
            "Mark this invoice as paid?"):
            self.payment_dao.mark_paid(self.selected_payment_id)
            self.selected_payment_id = None
            self.load_all_invoices()
            messagebox.showinfo("Updated", "Payment marked as paid.")

    def create_invoice(self):
        selected = self.inv_tenant_tree.selection()
        if not selected:
            messagebox.showwarning("No tenant",
                                   "Please select a tenant.")
            return

        tenant_id = int(selected[0])
        leases = self.lease_dao.get_by_tenant(tenant_id)

        if not leases:
            messagebox.showerror("No lease",
                "This tenant has no active lease.")
            return

        lease_id = leases[0]['lease_id']

        try:
            amount = float(self.inv_entries['amount'].get())
        except ValueError:
            messagebox.showerror("Invalid",
                                 "Amount must be a number.")
            return

        due_date = self.inv_entries['due_date'].get().strip()
        notes = self.inv_entries['notes'].get().strip()

        if not due_date:
            messagebox.showerror("Missing", "Due date is required.")
            return

        self.payment_dao.create_invoice(tenant_id, lease_id,
                                        amount, due_date, notes)
        messagebox.showinfo("Created", "Invoice created successfully!")
        self.inv_entries['amount'].set("")
        self.inv_entries['notes'].set("")