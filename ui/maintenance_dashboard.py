# ui/maintenance_dashboard.py
# Maintenance Dashboard - Group 30
# Student ID: 23029574 | Campbell Clark
import tkinter as tk
from ui.base_dashboard import BaseDashboard, CONTENT_BG

NAV = [
    ("Overview", "show_overview"),
    ("Open Requests", "show_open_requests"),
    ("My Assigned Jobs", "show_assigned"),
    ("Resolved Requests", "show_resolved"),
]

class MaintenanceDashboard(BaseDashboard):
    def __init__(self, root, user):
        super().__init__(root, user, NAV)

    def show_open_requests(self):
        from ui.modules.maintenance import MaintenanceModule
        MaintenanceModule(self.page_frame, user=self.user,
                         mode="staff").pack(fill="both", expand=True)

    def show_assigned(self):
        from ui.modules.maintenance import MaintenanceModule
        MaintenanceModule(self.page_frame, user=self.user,
                        mode="staff").pack(fill="both", expand=True)

    def show_resolved(self):
        from ui.modules.maintenance import MaintenanceModule
        MaintenanceModule(self.page_frame, user=self.user,
                        mode="staff").pack(fill="both", expand=True)