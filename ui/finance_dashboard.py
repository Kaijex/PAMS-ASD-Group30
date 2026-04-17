# ui/finance_dashboard.py
# Finance Dashboard - Group 30
# Student ID: 23029574 | Campbell Clark
import tkinter as tk
from ui.base_dashboard import BaseDashboard, CONTENT_BG

NAV = [
    ("Overview", "show_overview"),
    ("Invoices", "show_invoices"),
    ("Payments", "show_payments"),
    ("Late Payments", "show_late_payments"),
    ("Financial Reports", "show_reports"),
]

class FinanceDashboard(BaseDashboard):
    def __init__(self, root, user):
        super().__init__(root, user, NAV)
    
    def show_overview(self):
        from ui.modules.overview import OverviewModule
        OverviewModule(self.page_frame, user=self.user,
                       role="FINANCE").pack(fill="both", expand=True)

    def show_invoices(self):
        from ui.modules.payments import PaymentsModule
        PaymentsModule(self.page_frame).pack(fill="both", expand=True)

    def show_payments(self):
        from ui.modules.payments import PaymentsModule
        PaymentsModule(self.page_frame).pack(fill="both", expand=True)

    def show_late_payments(self):
        from ui.modules.payments import PaymentsModule
        PaymentsModule(self.page_frame).pack(fill="both", expand=True)

    def show_reports(self):
        from ui.modules.reports import ReportsModule
        ReportsModule(self.page_frame, user=self.user,
                      role="FINANCE").pack(fill="both", expand=True)