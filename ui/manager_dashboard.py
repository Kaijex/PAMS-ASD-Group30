# ui/manager_dashboard.py
# Manager Dashboard - Group 30
# Student ID: 23029574 | Campbell Clark
# Student ID: 25013991 | Adjeneg Imed

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
        OverviewModule(
            self.page_frame,
            user=self.user,
            role="MANAGER"
        ).pack(fill="both", expand=True)

    def show_occupancy(self):
        from ui.modules.reports import ReportsModule
        ReportsModule(
            self.page_frame,
            user=self.user,
            role="MANAGER"
        ).pack(fill="both", expand=True)

    def show_reports(self):
        from ui.modules.reports import ReportsModule
        ReportsModule(
            self.page_frame,
            user=self.user,
            role="MANAGER"
        ).pack(fill="both", expand=True)

    def show_expand(self):
        frame = tk.Frame(self.page_frame, bg=CONTENT_BG)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text="Expand Business",
            font=("Helvetica", 16, "bold"),
            bg=CONTENT_BG
        ).pack(pady=20)

        tk.Label(
            frame,
            text="Add New City:",
            bg=CONTENT_BG
        ).pack()

        city_entry = tk.Entry(frame)
        city_entry.pack(pady=5)

        def add_city():
            city = city_entry.get().strip()
            if city:
                tk.Label(
                    frame,
                    text=f"City '{city}' added (demo only)",
                    bg=CONTENT_BG
                ).pack()

        tk.Button(
            frame,
            text="Add City",
            command=add_city
        ).pack(pady=10)