# ui/modules/reports.py
# Reports Module - Occupancy, financial and maintenance reports
# Student ID: 23029574 | Campbell Clark
# Group 30 - PAMS

import tkinter as tk
from tkinter import ttk
from dao.apartment_dao import ApartmentDAO
from dao.tenant_dao import TenantDAO
from dao.lease_dao import LeaseDAO
from dao.payment_dao import PaymentDAO
from dao.maintenance_dao import MaintenanceDAO

CONTENT_BG = "#f0f4f8"
WHITE = "#ffffff"
BLUE = "#185FA5"

STATUS_COLOURS = {
    "paid":    "#0F6E56",
    "pending": "#BA7517",
    "late":    "#A32D2D",
}

class ReportsModule(tk.Frame):
    def __init__(self, parent, user=None, role=None, **kwargs):
        super().__init__(parent, bg=CONTENT_BG, **kwargs)
        self.user = user
        self.role = role or (user['role'] if user else 'ADMIN')
        self.apt_dao    = ApartmentDAO()
        self.tenant_dao = TenantDAO()
        self.lease_dao  = LeaseDAO()
        self.pay_dao    = PaymentDAO()
        self.maint_dao  = MaintenanceDAO()
        self.build()

    def build(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        role = self.role.upper()

        # Occupancy tab — admin and manager
        if role in ("ADMIN", "MANAGER"):
            occ_tab = tk.Frame(notebook, bg=CONTENT_BG)
            notebook.add(occ_tab, text="  Occupancy Report  ")
            self.build_occupancy_tab(occ_tab)

        # Financial tab — finance and manager
        if role in ("FINANCE", "MANAGER"):
            fin_tab = tk.Frame(notebook, bg=CONTENT_BG)
            notebook.add(fin_tab, text="  Financial Report  ")
            self.build_financial_tab(fin_tab)

        # Maintenance cost tab — admin and manager
        if role in ("ADMIN", "MANAGER"):
            maint_tab = tk.Frame(notebook, bg=CONTENT_BG)
            notebook.add(maint_tab, text="  Maintenance Costs  ")
            self.build_maintenance_tab(maint_tab)

        # Finance gets a dedicated payment breakdown tab too
        if role == "FINANCE":
            pay_tab = tk.Frame(notebook, bg=CONTENT_BG)
            notebook.add(pay_tab, text="  Payment Breakdown  ")
            self.build_payment_breakdown_tab(pay_tab)

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def section_label(self, parent, text):
        tk.Label(parent, text=text,
                 font=("Helvetica", 11, "bold"),
                 bg=CONTENT_BG, fg="#444").pack(
                 anchor="w", padx=16, pady=(12, 6))

    def stat_card(self, parent, title, value, colour):
        card = tk.Frame(parent, bg=WHITE, padx=20, pady=14)
        card.pack(side="left", padx=(0, 14))
        tk.Label(card, text=title,
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#888").pack(anchor="w")
        tk.Label(card, text=value,
                 font=("Helvetica", 18, "bold"),
                 bg=WHITE, fg=colour).pack(anchor="w", pady=(4, 0))

    def make_table(self, parent, cols, widths, height=10):
        frame = tk.Frame(parent, bg=WHITE)
        frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        tree = ttk.Treeview(frame, columns=cols,
                             show="headings", height=height)
        for col, width in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")

        sb = ttk.Scrollbar(frame, orient="vertical",
                            command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
        return tree

    # ------------------------------------------------------------------
    # Occupancy Report
    # ------------------------------------------------------------------

    def build_occupancy_tab(self, parent):
        tk.Label(parent, text="Occupancy Report",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 4), padx=16)

        all_apts = self.apt_dao.get_all()
        total    = len(all_apts)
        occupied = len([a for a in all_apts if a['status'] == 'occupied'])
        available= len([a for a in all_apts if a['status'] == 'available'])
        rate     = f"{(occupied/total*100):.1f}%" if total else "0%"

        self.section_label(parent, "Summary")
        row = tk.Frame(parent, bg=CONTENT_BG)
        row.pack(fill="x", padx=16, pady=(0, 14))
        self.stat_card(row, "Total Apartments", str(total),    BLUE)
        self.stat_card(row, "Occupied",         str(occupied), "#0F6E56")
        self.stat_card(row, "Available",        str(available),"#BA7517")
        self.stat_card(row, "Occupancy Rate",   rate,          "#0F6E56")

        self.section_label(parent, "Breakdown by Location")
        cols   = ("Location", "Total", "Occupied",
                  "Available", "Occupancy Rate")
        widths = [130, 80, 90, 90, 130]
        tree = self.make_table(parent, cols, widths, height=6)

        locations = ["Bristol", "Cardiff", "London", "Manchester"]
        for loc in locations:
            loc_apts  = [a for a in all_apts if a['location'] == loc]
            t = len(loc_apts)
            o = len([a for a in loc_apts if a['status'] == 'occupied'])
            av= len([a for a in loc_apts if a['status'] == 'available'])
            r = f"{(o/t*100):.1f}%" if t else "0%"
            tree.insert("", "end", values=(loc, t, o, av, r))

        self.section_label(parent, "All Apartments")
        cols2   = ("ID", "Number", "Location", "Type",
                   "Rooms", "Rent", "Status")
        widths2 = [40, 90, 110, 100, 60, 90, 90]
        tree2 = self.make_table(parent, cols2, widths2, height=8)

        tree2.tag_configure("occupied",  foreground="#BA7517")
        tree2.tag_configure("available", foreground="#0F6E56")

        for a in all_apts:
            tree2.insert("", "end",
                values=(a['apartment_id'], a['apartment_number'],
                        a['location'], a['type'], a['rooms'],
                        f"£{float(a['monthly_rent']):,.2f}",
                        a['status'].capitalize()),
                tags=(a['status'],))

    # ------------------------------------------------------------------
    # Financial Report
    # ------------------------------------------------------------------

    def build_financial_tab(self, parent):
        tk.Label(parent, text="Financial Report",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 4), padx=16)

        summary = self.pay_dao.get_summary()
        collected = float(summary.get('collected') or 0)
        pending   = float(summary.get('pending')   or 0)
        late      = float(summary.get('late')      or 0)
        total_inv = summary.get('total_invoices', 0)

        self.section_label(parent, "Summary")
        row = tk.Frame(parent, bg=CONTENT_BG)
        row.pack(fill="x", padx=16, pady=(0, 14))
        self.stat_card(row, "Total Collected",
                       f"£{collected:,.2f}", "#0F6E56")
        self.stat_card(row, "Pending",
                       f"£{pending:,.2f}",   "#BA7517")
        self.stat_card(row, "Overdue",
                       f"£{late:,.2f}",      "#A32D2D")
        self.stat_card(row, "Total Invoices",
                       str(total_inv),        BLUE)

        self.section_label(parent, "All Invoices")
        cols   = ("ID", "Tenant", "Apartment", "Location",
                  "Amount", "Due Date", "Paid Date", "Status")
        widths = [40, 140, 100, 100, 90, 90, 90, 80]
        tree = self.make_table(parent, cols, widths, height=10)

        for status, colour in STATUS_COLOURS.items():
            tree.tag_configure(status, foreground=colour)

        payments = self.pay_dao.get_all()
        for p in payments:
            paid_date = p['paid_date'] if p['paid_date'] else "—"
            tree.insert("", "end",
                values=(p['payment_id'], p['tenant_name'],
                        p['apartment_number'], p['location'],
                        f"£{float(p['amount']):,.2f}",
                        p['due_date'], paid_date,
                        p['status'].capitalize()),
                tags=(p['status'],))

    # ------------------------------------------------------------------
    # Maintenance Costs Report
    # ------------------------------------------------------------------

    def build_maintenance_tab(self, parent):
        tk.Label(parent, text="Maintenance Cost Report",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 4), padx=16)

        summary  = self.maint_dao.get_cost_summary()
        total_c  = float(summary.get('total_cost') or 0)
        avg_time = summary.get('avg_time')
        avg_str  = f"{avg_time:.1f}h" if avg_time else "N/A"
        resolved = summary.get('resolved', 0)
        open_c   = summary.get('open_count', 0)

        self.section_label(parent, "Summary")
        row = tk.Frame(parent, bg=CONTENT_BG)
        row.pack(fill="x", padx=16, pady=(0, 14))
        self.stat_card(row, "Total Spend",
                       f"£{total_c:,.2f}", "#A32D2D")
        self.stat_card(row, "Avg Resolution Time",
                       avg_str,             BLUE)
        self.stat_card(row, "Resolved Jobs",
                       str(resolved),       "#0F6E56")
        self.stat_card(row, "Open Requests",
                       str(open_c),         "#BA7517")

        self.section_label(parent, "Resolved Requests with Costs")
        cols   = ("ID", "Apartment", "Location", "Title",
                  "Priority", "Cost", "Time (hrs)", "Resolved Date")
        widths = [40, 90, 100, 160, 80, 80, 90, 110]
        tree = self.make_table(parent, cols, widths, height=10)

        resolved_jobs = self.maint_dao.get_resolved()
        for m in resolved_jobs:
            cost = f"£{float(m['cost']):,.2f}" if m.get('cost') else "—"
            time = str(m['time_taken_hours']) if m.get('time_taken_hours') else "—"
            tree.insert("", "end",
                values=(m['request_id'], m['apartment_number'],
                        m['location'], m['title'],
                        m['priority'].capitalize(),
                        cost, time,
                        m.get('resolved_date', '—')))

    # ------------------------------------------------------------------
    # Payment Breakdown (Finance only)
    # ------------------------------------------------------------------

    def build_payment_breakdown_tab(self, parent):
        tk.Label(parent, text="Payment Breakdown by Location",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 4), padx=16)

        all_payments = self.pay_dao.get_all()

        self.section_label(parent, "By Location")
        cols   = ("Location", "Collected", "Pending",
                  "Overdue", "Total Invoices")
        widths = [130, 120, 110, 110, 120]
        tree = self.make_table(parent, cols, widths, height=6)

        locations = ["Bristol", "Cardiff", "London", "Manchester"]
        for loc in locations:
            loc_pays  = [p for p in all_payments
                         if p['location'] == loc]
            collected = sum(p['amount'] for p in loc_pays
                            if p['status'] == 'paid')
            pending   = sum(p['amount'] for p in loc_pays
                            if p['status'] == 'pending')
            late      = sum(p['amount'] for p in loc_pays
                            if p['status'] == 'late')
            tree.insert("", "end",
                values=(loc,
                        f"£{collected:,.2f}",
                        f"£{pending:,.2f}",
                        f"£{late:,.2f}",
                        str(len(loc_pays))))