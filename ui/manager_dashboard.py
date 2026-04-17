# ui/manager_dashboard.py
# Manager Dashboard - Group 30
# Student ID: 23029574 | Campbell Clark
import tkinter as tk
from ui.base_dashboard import BaseDashboard, CONTENT_BG

NAV = [
    ("Overview", "show_overview"),
    ("Occupancy Levels", "show_occupancy"),
    ("Performance Reports", "show_reports"),
    ("Expand Business", "show_expand"),
]

class ManagerDashboard(BaseDashboard):
    def __init__(self, root, user):
        super().__init__(root, user, NAV)
    def show_overview(self):
        from ui.modules.overview import OverviewModule
        OverviewModule(self.page_frame, user=self.user,
                       role="MANAGER").pack(fill="both", expand=True)


    def show_occupancy(self):
        self.show_coming_soon("Occupancy Levels")

    def show_reports(self):
        from ui.modules.reports import ReportsModule
        ReportsModule(self.page_frame, user=self.user,
                      role="MANAGER").pack(fill="both", expand=True)

    def show_expand(self):
        self.show_coming_soon("Expand Business")