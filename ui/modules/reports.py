# ui/modules/reports.py
# Reports Module - Occupancy, financial and maintenance reports
# Student ID: 23029574 | Campbell Clark
# Group 30 - PAMS
# UI refinement by Student ID: 25013991 | Adjeneg Imed

import tkinter as tk
from tkinter import ttk
from dao.apartment_dao import ApartmentDAO
from dao.tenant_dao import TenantDAO
from dao.lease_dao import LeaseDAO
from dao.payment_dao import PaymentDAO
from dao.maintenance_dao import MaintenanceDAO

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
    "late": DANGER,
}


class ReportsModule(tk.Frame):
    def __init__(self, parent, user=None, role=None, **kwargs):
        super().__init__(parent, bg=CONTENT_BG, **kwargs)
        self.user = user
        self.role = role or (user['role'] if user else 'ADMIN')
        self.apt_dao = ApartmentDAO()
        self.tenant_dao = TenantDAO()
        self.lease_dao = LeaseDAO()
        self.pay_dao = PaymentDAO()
        self.maint_dao = MaintenanceDAO()
        self.build()

    def build(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        role = self.role.upper()

        if role in ("ADMIN", "MANAGER"):
            occ_tab = tk.Frame(notebook, bg=CONTENT_BG)
            notebook.add(occ_tab, text="  Occupancy Report  ")
            self.build_occupancy_tab(occ_tab)

        if role in ("FINANCE", "MANAGER"):
            fin_tab = tk.Frame(notebook, bg=CONTENT_BG)
            notebook.add(fin_tab, text="  Financial Report  ")
            self.build_financial_tab(fin_tab)

        if role in ("ADMIN", "MANAGER"):
            maint_tab = tk.Frame(notebook, bg=CONTENT_BG)
            notebook.add(maint_tab, text="  Maintenance Costs  ")
            self.build_maintenance_tab(maint_tab)

        if role == "FINANCE":
            pay_tab = tk.Frame(notebook, bg=CONTENT_BG)
            notebook.add(pay_tab, text="  Payment Breakdown  ")
            self.build_payment_breakdown_tab(pay_tab)

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

    def stat_card(self, parent, title, value, colour):
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

    def make_table(self, parent, cols, widths, height=10):
        outer = tk.Frame(
            parent,
            bg=WHITE,
            highlightbackground=CARD_BORDER,
            highlightthickness=1
        )
        outer.pack(fill="both", expand=True, pady=(0, 18))

        frame = tk.Frame(outer, bg=WHITE)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        tree = ttk.Treeview(frame, columns=cols, show="headings", height=height)
        for col, width in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")

        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)

        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
        return tree

    # ------------------------------------------------------------------
    # Occupancy Report
    # ------------------------------------------------------------------

    def build_occupancy_tab(self, parent):
        self.page_title(
            parent,
            "Occupancy Report",
            "View apartment usage, availability, and city-level occupancy trends."
        )

        all_apts = self.apt_dao.get_all()
        total = len(all_apts)
        occupied = len([a for a in all_apts if a['status'] == 'occupied'])
        available = len([a for a in all_apts if a['status'] == 'available'])
        rate = f"{(occupied / total * 100):.1f}%" if total else "0%"

        self.section_label(parent, "Summary")
        row = tk.Frame(parent, bg=CONTENT_BG)
        row.pack(fill="x", pady=(0, 16))
        self.stat_card(row, "Total Apartments", str(total), PRIMARY)
        self.stat_card(row, "Occupied", str(occupied), SUCCESS)
        self.stat_card(row, "Available", str(available), WARNING)
        self.stat_card(row, "Occupancy Rate", rate, SUCCESS)

        self.section_label(parent, "Breakdown by Location")
        cols = ("Location", "Total", "Occupied", "Available", "Occupancy Rate")
        widths = [150, 100, 110, 110, 140]
        tree = self.make_table(parent, cols, widths, height=6)

        locations = ["Bristol", "Cardiff", "London", "Manchester"]
        for loc in locations:
            loc_apts = [a for a in all_apts if a['location'] == loc]
            t = len(loc_apts)
            o = len([a for a in loc_apts if a['status'] == 'occupied'])
            av = len([a for a in loc_apts if a['status'] == 'available'])
            r = f"{(o / t * 100):.1f}%" if t else "0%"
            tree.insert("", "end", values=(loc, t, o, av, r))

        self.section_label(parent, "All Apartments")
        cols2 = ("ID", "Number", "Location", "Type", "Rooms", "Rent", "Status")
        widths2 = [60, 110, 130, 120, 80, 110, 100]
        tree2 = self.make_table(parent, cols2, widths2, height=8)

        tree2.tag_configure("occupied", foreground=WARNING)
        tree2.tag_configure("available", foreground=SUCCESS)

        for a in all_apts:
            tree2.insert(
                "",
                "end",
                values=(
                    a['apartment_id'],
                    a['apartment_number'],
                    a['location'],
                    a['type'],
                    a['rooms'],
                    f"£{float(a['monthly_rent']):,.2f}",
                    a['status'].capitalize()
                ),
                tags=(a['status'],)
            )

    # ------------------------------------------------------------------
    # Financial Report
    # ------------------------------------------------------------------

    def build_financial_tab(self, parent):
        self.page_title(
            parent,
            "Financial Report",
            "Monitor rent collection, unpaid balances, and invoice activity."
        )

        summary = self.pay_dao.get_summary()
        collected = float(summary.get('collected') or 0)
        pending = float(summary.get('pending') or 0)
        late = float(summary.get('late') or 0)
        total_inv = summary.get('total_invoices', 0)

        self.section_label(parent, "Summary")
        row = tk.Frame(parent, bg=CONTENT_BG)
        row.pack(fill="x", pady=(0, 16))
        self.stat_card(row, "Total Collected", f"£{collected:,.2f}", SUCCESS)
        self.stat_card(row, "Pending", f"£{pending:,.2f}", WARNING)
        self.stat_card(row, "Overdue", f"£{late:,.2f}", DANGER)
        self.stat_card(row, "Total Invoices", str(total_inv), PRIMARY)

        self.section_label(parent, "All Invoices")
        cols = ("ID", "Tenant", "Apartment", "Location", "Amount", "Due Date", "Paid Date", "Status")
        widths = [60, 170, 120, 120, 100, 100, 100, 90]
        tree = self.make_table(parent, cols, widths, height=10)

        for status, colour in STATUS_COLOURS.items():
            tree.tag_configure(status, foreground=colour)

        payments = self.pay_dao.get_all()
        for p in payments:
            paid_date = p['paid_date'] if p['paid_date'] else "—"
            tree.insert(
                "",
                "end",
                values=(
                    p['payment_id'],
                    p['tenant_name'],
                    p['apartment_number'],
                    p['location'],
                    f"£{float(p['amount']):,.2f}",
                    p['due_date'],
                    paid_date,
                    p['status'].capitalize()
                ),
                tags=(p['status'],)
            )

    # ------------------------------------------------------------------
    # Maintenance Costs Report
    # ------------------------------------------------------------------

    def build_maintenance_tab(self, parent):
        self.page_title(
            parent,
            "Maintenance Cost Report",
            "Track spending, workload, and repair performance across the portfolio."
        )

        summary = self.maint_dao.get_cost_summary()
        total_c = float(summary.get('total_cost') or 0)
        avg_time = summary.get('avg_time')
        avg_str = f"{avg_time:.1f}h" if avg_time else "N/A"
        resolved = summary.get('resolved', 0)
        open_c = summary.get('open_count', 0)

        self.section_label(parent, "Summary")
        row = tk.Frame(parent, bg=CONTENT_BG)
        row.pack(fill="x", pady=(0, 16))
        self.stat_card(row, "Total Spend", f"£{total_c:,.2f}", DANGER)
        self.stat_card(row, "Avg Resolution Time", avg_str, PRIMARY)
        self.stat_card(row, "Resolved Jobs", str(resolved), SUCCESS)
        self.stat_card(row, "Open Requests", str(open_c), WARNING)

        self.section_label(parent, "Resolved Requests with Costs")
        cols = ("ID", "Apartment", "Location", "Title", "Priority", "Cost", "Time (hrs)", "Resolved Date")
        widths = [60, 100, 120, 180, 100, 90, 100, 120]
        tree = self.make_table(parent, cols, widths, height=10)

        resolved_jobs = self.maint_dao.get_resolved()
        for m in resolved_jobs:
            cost = f"£{float(m['cost']):,.2f}" if m.get('cost') else "—"
            time = str(m['time_taken_hours']) if m.get('time_taken_hours') else "—"
            tree.insert(
                "",
                "end",
                values=(
                    m['request_id'],
                    m['apartment_number'],
                    m['location'],
                    m['title'],
                    m['priority'].capitalize(),
                    cost,
                    time,
                    m.get('resolved_date', '—')
                )
            )

    # ------------------------------------------------------------------
    # Payment Breakdown (Finance only)
    # ------------------------------------------------------------------

    def build_payment_breakdown_tab(self, parent):
        self.page_title(
            parent,
            "Payment Breakdown by Location",
            "Compare rent collection and outstanding balances across city branches."
        )

        all_payments = self.pay_dao.get_all()

        self.section_label(parent, "By Location")
        cols = ("Location", "Collected", "Pending", "Overdue", "Total Invoices")
        widths = [160, 140, 130, 130, 130]
        tree = self.make_table(parent, cols, widths, height=6)

        locations = ["Bristol", "Cardiff", "London", "Manchester"]
        for loc in locations:
            loc_pays = [p for p in all_payments if p['location'] == loc]
            collected = sum(p['amount'] for p in loc_pays if p['status'] == 'paid')
            pending = sum(p['amount'] for p in loc_pays if p['status'] == 'pending')
            late = sum(p['amount'] for p in loc_pays if p['status'] == 'late')

            tree.insert(
                "",
                "end",
                values=(
                    loc,
                    f"£{collected:,.2f}",
                    f"£{pending:,.2f}",
                    f"£{late:,.2f}",
                    str(len(loc_pays))
                )
            )