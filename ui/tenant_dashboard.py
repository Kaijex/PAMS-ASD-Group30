# ui/tenant_dashboard.py
# Tenant Dashboard - Group 30
# Student ID: 23029574 | Campbell Clark
# Student ID: 25013991 | Adjeneg Imed
import tkinter as tk
from ui.base_dashboard import BaseDashboard, CONTENT_BG

NAV = [
    ("Overview", "show_overview"),
    ("My Lease", "show_lease"),
    ("Payments", "show_payments"),
    ("Maintenance Requests", "show_maintenance"),
    ("Complaints", "show_complaints"),
    ("Early Termination", "show_termination"),
]

class TenantDashboard(BaseDashboard):
    def __init__(self, root, user):
        super().__init__(root, user, NAV)
    
    def show_overview(self):
        from ui.modules.overview import OverviewModule
        OverviewModule(self.page_frame, user=self.user,
                       role="TENANT").pack(fill="both", expand=True)

    def show_lease(self):
        from ui.modules.my_lease import MyLeaseModule
        MyLeaseModule(self.page_frame, user=self.user,
                      mode="tenant").pack(fill="both", expand=True)

    def show_payments(self):
        from ui.modules.my_payments import MyPaymentsModule
        MyPaymentsModule(self.page_frame, user=self.user,
                         mode="tenant").pack(fill="both", expand=True)

    def show_maintenance(self):
        from ui.modules.maintenance import MaintenanceModule
        MaintenanceModule(self.page_frame, user=self.user,
                      mode="tenant").pack(fill="both", expand=True)

    def show_complaints(self):
        from ui.modules.complaints import ComplaintsModule
        ComplaintsModule(self.page_frame, user=self.user,
                     mode="tenant").pack(fill="both", expand=True)

    def show_termination(self):
        from ui.modules.early_termination import EarlyTerminationModule
        EarlyTerminationModule(self.page_frame, user=self.user).pack(fill="both", expand=True)