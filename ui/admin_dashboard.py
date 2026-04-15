# ui/admin_dashboard.py
# Admin Dashboard - Group 30
# Student ID: 23029574 | Campbell Clark
import tkinter as tk
from ui.base_dashboard import BaseDashboard, CONTENT_BG

NAV = [
    ("Overview", "show_overview"),
    ("Manage Users", "show_manage_users"),
    ("Manage Apartments", "show_manage_apartments"),
    ("Lease Tracker", "show_lease_tracker"),
    ("Reports", "show_reports"),
]

class AdminDashboard(BaseDashboard):
    def __init__(self, root, user):
        super().__init__(root, user, NAV)
        
    def show_overview(self):
        from ui.modules.overview import OverviewModule
        OverviewModule(self.page_frame, user=self.user,
                       role="ADMIN").pack(fill="both", expand=True)

    def show_manage_users(self):
        self.show_coming_soon("Manage Users")

    def show_manage_apartments(self):
        from ui.modules.apartments import ApartmentsModule
        ApartmentsModule(self.page_frame).pack(fill="both", expand=True)

    def show_lease_tracker(self):
        self.show_coming_soon("Lease Tracker")

    def show_reports(self):
        self.show_coming_soon("Reports")