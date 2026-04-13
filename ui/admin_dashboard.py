# ui/admin_dashboard.py
# Admin Dashboard - Group 30

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

    def show_manage_users(self):
        self.show_coming_soon("Manage Users")

    def show_manage_apartments(self):
        self.show_coming_soon("Manage Apartments")

    def show_lease_tracker(self):
        self.show_coming_soon("Lease Tracker")

    def show_reports(self):
        self.show_coming_soon("Reports")