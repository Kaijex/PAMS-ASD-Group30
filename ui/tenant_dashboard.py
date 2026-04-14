# ui/tenant_dashboard.py
# Tenant Dashboard - Group 30
# Student ID: 23029574 | Campbell Clark
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

    def show_lease(self):
        self.show_coming_soon("My Lease")

    def show_payments(self):
        self.show_coming_soon("Payments")

    def show_maintenance(self):
        self.show_coming_soon("Maintenance Requests")

    def show_complaints(self):
        self.show_coming_soon("Complaints")

    def show_termination(self):
        self.show_coming_soon("Early Termination")