# ui/frontdesk_dashboard.py
# Front Desk Dashboard - Group 30
# Student ID: 23029574 | Campbell Clark
import tkinter as tk
from ui.base_dashboard import BaseDashboard, CONTENT_BG

NAV = [
    ("Overview", "show_overview"),
    ("Register Tenant", "show_register_tenant"),
    ("Tenant Lookup", "show_tenant_lookup"),
    ("Maintenance Requests", "show_maintenance"),
    ("Complaints", "show_complaints"),
]

class FrontDeskDashboard(BaseDashboard):
    def __init__(self, root, user):
        super().__init__(root, user, NAV)

    def show_register_tenant(self):
        self.show_coming_soon("Register Tenant")

    def show_tenant_lookup(self):
        self.show_coming_soon("Tenant Lookup")

    def show_maintenance(self):
        self.show_coming_soon("Maintenance Requests")

    def show_complaints(self):
        self.show_coming_soon("Complaints")