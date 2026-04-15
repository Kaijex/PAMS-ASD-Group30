# ui/modules/overview.py
# Overview Module - Live stats home screen for all roles
# Student ID: 23029574 | Campbell Clark
# Group 30 - PAMS

import tkinter as tk
from tkinter import ttk
from dao.apartment_dao import ApartmentDAO
from dao.tenant_dao import TenantDAO
from dao.lease_dao import LeaseDAO
from dao.payment_dao import PaymentDAO
from dao.maintenance_dao import MaintenanceDAO
from dao.complaint_dao import ComplaintDAO

CONTENT_BG = "#f0f4f8"
WHITE = "#ffffff"
BLUE = "#185FA5"

class OverviewModule(tk.Frame):
    def __init__(self, parent, user=None, role=None, **kwargs):
        super().__init__(parent, bg=CONTENT_BG, **kwargs)
        self.user = user
        self.role = role or (user['role'] if user else 'ADMIN')
        self.apt_dao   = ApartmentDAO()
        self.tenant_dao = TenantDAO()
        self.lease_dao  = LeaseDAO()
        self.pay_dao    = PaymentDAO()
        self.maint_dao  = MaintenanceDAO()
        self.complaint_dao = ComplaintDAO()
        self.build()

    def build(self):
        role = self.role.upper()

        # Page heading
        tk.Label(self, text="Overview",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 4), padx=16)

        username = self.user['username'] if self.user else ""
        tk.Label(self, text=f"Welcome back, {username}.",
                 font=("Helvetica", 10),
                 bg=CONTENT_BG, fg="#888").pack(
                 anchor="w", padx=16, pady=(0, 20))

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
        row.pack(fill="x", padx=16, pady=(0, 14))
        return row

    def stat_card(self, parent, title, value, colour):
        card = tk.Frame(parent, bg=WHITE, padx=20, pady=16)
        card.pack(side="left", padx=(0, 14))
        tk.Label(card, text=title,
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#888").pack(anchor="w")
        tk.Label(card, text=value,
                 font=("Helvetica", 20, "bold"),
                 bg=WHITE, fg=colour).pack(anchor="w", pady=(4, 0))

    def section_label(self, text):
        tk.Label(self, text=text,
                 font=("Helvetica", 11, "bold"),
                 bg=CONTENT_BG, fg="#444").pack(
                 anchor="w", padx=16, pady=(10, 6))

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

        total_apts   = len(apts)
        available    = len([a for a in apts if a['status'] == 'available'])
        occupied     = len([a for a in apts if a['status'] == 'occupied'])

        all_tenants  = self.tenant_dao.get_all()
        if location:
            tenants = [t for t in all_tenants
                       if t.get('preferred_location') == location]
        else:
            tenants = all_tenants

        active_leases = len(self.lease_dao.get_active())

        self.section_label("Apartments")
        row1 = self.card_row()
        self.stat_card(row1, "Total Apartments", str(total_apts), BLUE)
        self.stat_card(row1, "Available",        str(available), "#0F6E56")
        self.stat_card(row1, "Occupied",         str(occupied),  "#BA7517")

        self.section_label("Tenants & Leases")
        row2 = self.card_row()
        self.stat_card(row2, "Registered Tenants", str(len(tenants)), BLUE)
        self.stat_card(row2, "Active Leases",       str(active_leases), "#0F6E56")

        self.build_expiring_table()

    def build_manager(self):
        all_apts  = self.apt_dao.get_all()
        total     = len(all_apts)
        occupied  = len([a for a in all_apts if a['status'] == 'occupied'])
        rate      = f"{(occupied/total*100):.1f}%" if total else "0%"

        active_leases = len(self.lease_dao.get_active())
        all_maint     = self.maint_dao.get_all()
        open_maint    = len([m for m in all_maint
                             if m['status'] == 'open'])

        self.section_label("Portfolio")
        row1 = self.card_row()
        self.stat_card(row1, "Total Apartments",  str(total),         BLUE)
        self.stat_card(row1, "Occupancy Rate",    rate,               "#0F6E56")
        self.stat_card(row1, "Active Leases",     str(active_leases), "#0F6E56")
        self.stat_card(row1, "Open Maintenance",  str(open_maint),    "#A32D2D")

        self.section_label("Apartments by Location")
        self.build_location_breakdown(all_apts)

    def build_frontdesk(self):
        all_apts     = self.apt_dao.get_all()
        available    = len([a for a in all_apts if a['status'] == 'available'])
        tenants      = self.tenant_dao.get_all()
        active_leases = len(self.lease_dao.get_active())
        complaints   = self.complaint_dao.get_all()
        open_comps   = len([c for c in complaints
                            if c['status'] == 'open'])

        self.section_label("At a Glance")
        row1 = self.card_row()
        self.stat_card(row1, "Available Apartments", str(available),         "#0F6E56")
        self.stat_card(row1, "Registered Tenants",   str(len(tenants)),      BLUE)
        self.stat_card(row1, "Active Leases",         str(active_leases),    BLUE)
        self.stat_card(row1, "Open Complaints",       str(open_comps),       "#A32D2D")

    def build_finance(self):
        summary = self.pay_dao.get_summary()

        collected = f"£{float(summary.get('collected') or 0):,.2f}"
        pending   = f"£{float(summary.get('pending') or 0):,.2f}"
        late      = f"£{float(summary.get('late') or 0):,.2f}"
        total_inv = str(summary.get('total_invoices', 0))

        self.section_label("Financial Summary")
        row1 = self.card_row()
        self.stat_card(row1, "Total Collected",  collected,  "#0F6E56")
        self.stat_card(row1, "Pending Invoices", pending,    "#BA7517")
        self.stat_card(row1, "Overdue",          late,       "#A32D2D")
        self.stat_card(row1, "Total Invoices",   total_inv,  BLUE)

    def build_maintenance(self):
        all_maint = self.maint_dao.get_all()
        open_req  = len([m for m in all_maint if m['status'] == 'open'])
        assigned  = len([m for m in all_maint if m['status'] == 'assigned'])
        resolved  = len([m for m in all_maint if m['status'] == 'resolved'])

        # Average resolution time from resolved requests that have a value
        times = [m['time_taken_hours'] for m in all_maint
                 if m['status'] == 'resolved'
                 and m.get('time_taken_hours')]
        avg_time = f"{sum(times)/len(times):.1f}h" if times else "N/A"

        self.section_label("Maintenance Summary")
        row1 = self.card_row()
        self.stat_card(row1, "Open Requests",    str(open_req), "#A32D2D")
        self.stat_card(row1, "Assigned",         str(assigned), "#BA7517")
        self.stat_card(row1, "Resolved",         str(resolved), "#0F6E56")
        self.stat_card(row1, "Avg Resolution",   avg_time,      BLUE)

    def build_tenant(self):
        tenant = self.tenant_dao.get_by_user_id(self.user['user_id'])
        if not tenant:
            tk.Label(self, text="No tenant record linked to this account.",
                     font=("Helvetica", 11),
                     bg=CONTENT_BG, fg="#A32D2D").pack(
                     padx=16, anchor="w")
            return

        tid = tenant['tenant_id']
        leases   = self.lease_dao.get_by_tenant(tid)
        active   = next((l for l in leases if l['status'] == 'active'), None)
        payments = self.pay_dao.get_by_tenant(tid)
        complaints = self.complaint_dao.get_by_tenant(tid)
        open_comps = len([c for c in complaints if c['status'] == 'open'])

        if active:
            rent       = f"£{float(active['monthly_rent']):,.2f}"
            end_date   = active['end_date']
            # Next pending payment
            pending = sorted(
                [p for p in payments if p['status'] == 'pending'],
                key=lambda p: p['due_date']
            )
            if pending:
                next_due    = pending[0]['due_date']
                next_amount = f"£{float(pending[0]['amount']):,.2f}"
            else:
                next_due    = "None"
                next_amount = "—"
        else:
            rent = next_due = next_amount = end_date = "No active lease"

        self.section_label("My Lease")
        row1 = self.card_row()
        self.stat_card(row1, "Monthly Rent",    rent,        BLUE)
        self.stat_card(row1, "Lease Ends",      end_date,    "#BA7517")

        self.section_label("Payments")
        row2 = self.card_row()
        self.stat_card(row2, "Next Payment Due", next_due,    "#A32D2D")
        self.stat_card(row2, "Amount Due",       next_amount, "#A32D2D")
        self.stat_card(row2, "Open Complaints",  str(open_comps), "#BA7517")

    # ------------------------------------------------------------------
    # Shared sub-sections
    # ------------------------------------------------------------------

    def build_expiring_table(self):
        self.section_label("Leases Expiring Within 30 Days")

        table_frame = tk.Frame(self, bg=WHITE)
        table_frame.pack(fill="x", padx=16, pady=(0, 16))

        cols = ("Tenant", "Apartment", "Location", "End Date")
        tree = ttk.Treeview(table_frame, columns=cols,
                             show="headings", height=5)
        widths = [160, 110, 110, 100]
        for col, width in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")

        expiring = self.lease_dao.get_expiring_soon(days=30)
        for l in expiring:
            tree.insert("", "end",
                values=(l['tenant_name'],
                        l['apartment_number'],
                        l['location'],
                        l['end_date']))

        if not expiring:
            tree.insert("", "end",
                values=("No leases expiring soon", "", "", ""))

        tree.pack(fill="x")

    def build_location_breakdown(self, all_apts):
        table_frame = tk.Frame(self, bg=WHITE)
        table_frame.pack(fill="x", padx=16, pady=(0, 16))

        cols = ("Location", "Total", "Available", "Occupied")
        tree = ttk.Treeview(table_frame, columns=cols,
                             show="headings", height=5)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=140, anchor="center")

        locations = ["Bristol", "Cardiff", "London", "Manchester"]
        for loc in locations:
            loc_apts  = [a for a in all_apts if a['location'] == loc]
            total     = len(loc_apts)
            available = len([a for a in loc_apts
                             if a['status'] == 'available'])
            occupied  = len([a for a in loc_apts
                             if a['status'] == 'occupied'])
            tree.insert("", "end",
                values=(loc, total, available, occupied))

        tree.pack(fill="x")