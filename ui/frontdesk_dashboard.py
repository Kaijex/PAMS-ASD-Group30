# ui/frontdesk_dashboard.py
# Front Desk Dashboard - Group 30
# Student ID: 23029574 | Campbell Clark
import tkinter as tk
from ui.base_dashboard import BaseDashboard, CONTENT_BG

NAV = [
    ("Overview", "show_overview"),
    ("Register Tenant", "show_register_tenant"),
    ("Tenant Lookup", "show_tenant_lookup"),
    ("Lease Assignment", "show_lease_assignment"),
    ("Maintenance Requests", "show_maintenance"),
    ("Complaints", "show_complaints"),
]

class FrontDeskDashboard(BaseDashboard):
    def __init__(self, root, user):
        super().__init__(root, user, NAV)

    def show_register_tenant(self):
        from ui.modules.register_tenant import RegisterTenantModule
        RegisterTenantModule(self.page_frame).pack(fill="both", expand=True)

    def show_tenant_lookup(self):
        from ui.modules.tenant_lookup import TenantLookupModule
        TenantLookupModule(self.page_frame).pack(fill="both", expand=True)

    def show_maintenance(self):
        from ui.modules.maintenance import MaintenanceModule
        MaintenanceModule(self.page_frame, user=self.user,
                      mode="staff").pack(fill="both", expand=True)

    def show_complaints(self):
        from ui.modules.complaints import ComplaintsModule
        ComplaintsModule(self.page_frame, user=self.user,
                     mode="staff").pack(fill="both", expand=True)

    def show_lease_assignment(self):
        from ui.modules.lease_assignment import LeaseAssignmentModule
        LeaseAssignmentModule(self.page_frame).pack(fill="both", expand=True)