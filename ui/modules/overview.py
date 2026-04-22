# ui/modules/overview.py
# Overview Module - Live stats home screen for all roles
# Student ID: 23029574 | Campbell Clark
# Student ID: 25013991 | Adjeneg Imed
# Group 30 - PAMS


import tkinter as tk
from tkinter import ttk
from dao.apartment_dao import ApartmentDAO
from dao.tenant_dao import TenantDAO
from dao.lease_dao import LeaseDAO
from dao.payment_dao import PaymentDAO
from dao.maintenance_dao import MaintenanceDAO
from dao.complaint_dao import ComplaintDAO

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


class OverviewModule(tk.Frame):
    def __init__(self, parent, user=None, role=None, **kwargs):
        super().__init__(parent, bg=CONTENT_BG, **kwargs)
        self.user = user
        self.role = role or (user['role'] if user else 'ADMIN')
        self.apt_dao = ApartmentDAO()
        self.tenant_dao = TenantDAO()
        self.lease_dao = LeaseDAO()
        self.pay_dao = PaymentDAO()
        self.maint_dao = MaintenanceDAO()
        self.complaint_dao = ComplaintDAO()
        self.build()

    def build(self):
        role = self.role.upper()

        # Page heading
        tk.Label(
            self,
            text="Overview",
            font=("Helvetica", 22, "bold"),
            bg=CONTENT_BG,
            fg=TEXT_DARK
        ).pack(anchor="w", pady=(6, 4), padx=4)

        username = self.user['username'] if self.user else ""
        tk.Label(
            self,
            text=f"Welcome back, {username}. Here is your current system snapshot.",
            font=("Helvetica", 11),
            bg=CONTENT_BG,
            fg=TEXT_MUTED
        ).pack(anchor="w", padx=4, pady=(0, 20))

        if role == "ADMIN":
            self.build_admin()
        elif role == "MANAGER":
            self.build_manager()
        elif role == "FRONTDESK":
            self.build_frontdesk()
        elif role == "FINANCE":
            self.build_finance()
        elif role == "MAINTENANCE":
            self.build_maintenance()
        elif role == "TENANT":
            self.build_tenant()

    # ------------------------------------------------------------------
    # Card helpers
    # ------------------------------------------------------------------

    def card_row(self):
        row = tk.Frame(self, bg=CONTENT_BG)
        row.pack(fill="x", padx=0, pady=(0, 16))
        return row

    def stat_card(self, parent, title, value, colour):
        card = tk.Frame(
            parent,
            bg=WHITE,
            padx=22,
            pady=18,
            highlightbackground=CARD_BORDER,
            highlightthickness=1
        )
        card.pack(side="left", padx=(0, 16), pady=0)

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
            font=("Helvetica", 22, "bold"),
            bg=WHITE,
            fg=colour
        ).pack(anchor="w", pady=(8, 0))

    def section_label(self, text):
        wrapper = tk.Frame(self, bg=CONTENT_BG)
        wrapper.pack(fill="x", pady=(6, 10))

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

    def table_card(self, height=5):
        outer = tk.Frame(
            self,
            bg=WHITE,
            highlightbackground=CARD_BORDER,
            highlightthickness=1
        )
        outer.pack(fill="x", pady=(0, 18))

        inner = tk.Frame(outer, bg=WHITE)
        inner.pack(fill="both", expand=True, padx=12, pady=12)

        return outer, inner

    # ------------------------------------------------------------------
    # Role overviews
    # ------------------------------------------------------------------

    def build_admin(self):
        location = self.user.get('location')
        all_apts = self.apt_dao.get_all()

        if location:
            apts = [a for a in all_apts if a['location'] == location]
        else:
            apts = all_apts

        total_apts = len(apts)
        available = len([a for a in apts if a['status'] == 'available'])
        occupied = len([a for a in apts if a['status'] == 'occupied'])

        all_tenants = self.tenant_dao.get_all()
        if location:
            tenants = [t for t in all_tenants if t.get('preferred_location') == location]
        else:
            tenants = all_tenants

        active_leases = len(self.lease_dao.get_active())

        self.section_label("Apartments")
        row1 = self.card_row()
        self.stat_card(row1, "Total Apartments", str(total_apts), PRIMARY)
        self.stat_card(row1, "Available", str(available), SUCCESS)
        self.stat_card(row1, "Occupied", str(occupied), WARNING)

        self.section_label("Tenants & Leases")
        row2 = self.card_row()
        self.stat_card(row2, "Registered Tenants", str(len(tenants)), PRIMARY)
        self.stat_card(row2, "Active Leases", str(active_leases), SUCCESS)

        self.build_expiring_table()

    def build_manager(self):
        all_apts = self.apt_dao.get_all()
        total = len(all_apts)
        occupied = len([a for a in all_apts if a['status'] == 'occupied'])
        rate = f"{(occupied / total * 100):.1f}%" if total else "0%"

        active_leases = len(self.lease_dao.get_active())
        all_maint = self.maint_dao.get_all()
        open_maint = len([m for m in all_maint if m['status'] == 'open'])

        self.section_label("Portfolio")
        row1 = self.card_row()
        self.stat_card(row1, "Total Apartments", str(total), PRIMARY)
        self.stat_card(row1, "Occupancy Rate", rate, SUCCESS)
        self.stat_card(row1, "Active Leases", str(active_leases), SUCCESS)
        self.stat_card(row1, "Open Maintenance", str(open_maint), DANGER)

        self.section_label("Apartments by Location")
        self.build_location_breakdown(all_apts)

    def build_frontdesk(self):
        all_apts = self.apt_dao.get_all()
        available = len([a for a in all_apts if a['status'] == 'available'])
        tenants = self.tenant_dao.get_all()
        active_leases = len(self.lease_dao.get_active())
        complaints = self.complaint_dao.get_all()
        open_comps = len([c for c in complaints if c['status'] == 'open'])

        self.section_label("At a Glance")
        row1 = self.card_row()
        self.stat_card(row1, "Available Apartments", str(available), SUCCESS)
        self.stat_card(row1, "Registered Tenants", str(len(tenants)), PRIMARY)
        self.stat_card(row1, "Active Leases", str(active_leases), PRIMARY)
        self.stat_card(row1, "Open Complaints", str(open_comps), DANGER)

    def build_finance(self):
        summary = self.pay_dao.get_summary()

        collected = f"£{float(summary.get('collected') or 0):,.2f}"
        pending = f"£{float(summary.get('pending') or 0):,.2f}"
        late = f"£{float(summary.get('late') or 0):,.2f}"
        total_inv = str(summary.get('total_invoices', 0))

        self.section_label("Financial Summary")
        row1 = self.card_row()
        self.stat_card(row1, "Total Collected", collected, SUCCESS)
        self.stat_card(row1, "Pending Invoices", pending, WARNING)
        self.stat_card(row1, "Overdue", late, DANGER)
        self.stat_card(row1, "Total Invoices", total_inv, PRIMARY)

    def build_maintenance(self):
        all_maint = self.maint_dao.get_all()
        open_req = len([m for m in all_maint if m['status'] == 'open'])
        assigned = len([m for m in all_maint if m['status'] == 'assigned'])
        resolved = len([m for m in all_maint if m['status'] == 'resolved'])

        times = [
            m['time_taken_hours'] for m in all_maint
            if m['status'] == 'resolved' and m.get('time_taken_hours')
        ]
        avg_time = f"{sum(times) / len(times):.1f}h" if times else "N/A"

        self.section_label("Maintenance Summary")
        row1 = self.card_row()
        self.stat_card(row1, "Open Requests", str(open_req), DANGER)
        self.stat_card(row1, "Assigned", str(assigned), WARNING)
        self.stat_card(row1, "Resolved", str(resolved), SUCCESS)
        self.stat_card(row1, "Avg Resolution", avg_time, PRIMARY)

    def build_tenant(self):
        tenant = self.tenant_dao.get_by_user_id(self.user['user_id'])
        if not tenant:
            tk.Label(
                self,
                text="No tenant record linked to this account.",
                font=("Helvetica", 11),
                bg=CONTENT_BG,
                fg=DANGER
            ).pack(padx=4, anchor="w")
            return

        tid = tenant['tenant_id']
        leases = self.lease_dao.get_by_tenant(tid)
        active = next((l for l in leases if l['status'] == 'active'), None)
        payments = self.pay_dao.get_by_tenant(tid)
        complaints = self.complaint_dao.get_by_tenant(tid)
        open_comps = len([c for c in complaints if c['status'] == 'open'])

        if active:
            rent = f"£{float(active['monthly_rent']):,.2f}"
            end_date = active['end_date']

            pending = sorted(
                [p for p in payments if p['status'] in ('pending', 'late')],
                key=lambda p: p['due_date']
            )

            if pending:
                next_due = pending[0]['due_date']
                next_amount = f"£{float(pending[0]['amount']):,.2f}"
            else:
                next_due = "None"
                next_amount = "—"
        else:
            rent = next_due = next_amount = end_date = "No active lease"

        self.section_label("My Lease")
        row1 = self.card_row()
        self.stat_card(row1, "Monthly Rent", rent, PRIMARY)
        self.stat_card(row1, "Lease Ends", end_date, WARNING)

        self.section_label("Payments")
        row2 = self.card_row()
        self.stat_card(row2, "Next Payment Due", next_due, DANGER)
        self.stat_card(row2, "Amount Due", next_amount, DANGER)
        self.stat_card(row2, "Open Complaints", str(open_comps), WARNING)

    # ------------------------------------------------------------------
    # Shared sub-sections
    # ------------------------------------------------------------------

    def build_expiring_table(self):
        self.section_label("Leases Expiring Within 30 Days")
        _, table_frame = self.table_card()

        cols = ("Tenant", "Apartment", "Location", "End Date")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=5)

        widths = [180, 130, 130, 120]
        for col, width in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")

        expiring = self.lease_dao.get_expiring_soon(days=30)
        for l in expiring:
            tree.insert(
                "",
                "end",
                values=(
                    l['tenant_name'],
                    l['apartment_number'],
                    l['location'],
                    l['end_date']
                )
            )

        if not expiring:
            tree.insert("", "end", values=("No leases expiring soon", "", "", ""))

        tree.pack(fill="x")

    def build_location_breakdown(self, all_apts):
        _, table_frame = self.table_card()

        cols = ("Location", "Total", "Available", "Occupied")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=5)

        widths = [180, 140, 140, 140]
        for col, width in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")

        locations = ["Bristol", "Cardiff", "London", "Manchester"]
        for loc in locations:
            loc_apts = [a for a in all_apts if a['location'] == loc]
            total = len(loc_apts)
            available = len([a for a in loc_apts if a['status'] == 'available'])
            occupied = len([a for a in loc_apts if a['status'] == 'occupied'])

            tree.insert("", "end", values=(loc, total, available, occupied))

        tree.pack(fill="x")