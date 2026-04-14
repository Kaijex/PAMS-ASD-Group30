# ui/modules/lease_assignment.py
# Lease Assignment Module
# Student ID: 23029574 | Campbell Clark
# Group 30 - PAMS

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
from dao.lease_dao import LeaseDAO
from dao.tenant_dao import TenantDAO
from dao.apartment_dao import ApartmentDAO

CONTENT_BG = "#f0f4f8"
WHITE = "#ffffff"
BLUE = "#185FA5"

class LeaseAssignmentModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CONTENT_BG)
        self.lease_dao = LeaseDAO()
        self.tenant_dao = TenantDAO()
        self.apt_dao = ApartmentDAO()
        self.selected_lease_id = None
        self.build()

    def build(self):
        # Notebook tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        # Tab 1 - Assign new lease
        assign_tab = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(assign_tab, text="  Assign Lease  ")

        # Tab 2 - View active leases
        view_tab = tk.Frame(notebook, bg=CONTENT_BG)
        notebook.add(view_tab, text="  Active Leases  ")

        self.build_assign_tab(assign_tab)
        self.build_view_tab(view_tab)

    def build_assign_tab(self, parent):
        canvas = tk.Canvas(parent, bg=CONTENT_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical",
                                   command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        form_frame = tk.Frame(canvas, bg=CONTENT_BG)
        canvas_win = canvas.create_window((0, 0), window=form_frame, anchor="nw")

        form_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(canvas_win, width=e.width))

        tk.Label(form_frame, text="Assign Apartment to Tenant",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(anchor="w",
                 pady=(16, 20), padx=16)

        card = tk.Frame(form_frame, bg=WHITE, padx=30, pady=24)
        card.pack(fill="x", padx=16, pady=(0, 16))

        # Tenant selection
        tk.Label(card, text="Select Tenant",
                 font=("Helvetica", 11, "bold"),
                 bg=WHITE, fg=BLUE).pack(anchor="w", pady=(0, 8))

        tenant_row = tk.Frame(card, bg=WHITE)
        tenant_row.pack(fill="x", pady=(0, 16))

        self.tenant_search_var = tk.StringVar()
        tk.Entry(tenant_row, textvariable=self.tenant_search_var,
                 font=("Helvetica", 11), relief="solid",
                 bd=1, width=30).pack(side="left", ipady=5,
                 padx=(0, 8))
        tk.Button(tenant_row, text="Search",
                  font=("Helvetica", 10), bg=BLUE, fg=WHITE,
                  relief="flat", cursor="hand2", padx=10,
                  command=self.search_tenants).pack(side="left", ipady=5)

        tenant_cols = ("ID", "Name", "NI Number", "Location")
        self.tenant_tree = ttk.Treeview(card, columns=tenant_cols,
                                         show="headings", height=4)
        for col in tenant_cols:
            self.tenant_tree.heading(col, text=col)
            self.tenant_tree.column(col, width=130, anchor="center")
        self.tenant_tree.pack(fill="x", pady=(8, 0))
        self.search_tenants()

        tk.Frame(card, bg="#eee", height=1).pack(fill="x", pady=16)

        # Apartment selection
        tk.Label(card, text="Select Available Apartment",
                 font=("Helvetica", 11, "bold"),
                 bg=WHITE, fg=BLUE).pack(anchor="w", pady=(0, 8))

        apt_cols = ("ID", "Number", "Location", "Type", "Rooms", "Rent")
        self.apt_tree = ttk.Treeview(card, columns=apt_cols,
                                      show="headings", height=4)
        widths = [40, 80, 100, 110, 60, 90]
        for col, width in zip(apt_cols, widths):
            self.apt_tree.heading(col, text=col)
            self.apt_tree.column(col, width=width, anchor="center")
        self.apt_tree.pack(fill="x", pady=(0, 16))
        self.load_available_apartments()

        tk.Frame(card, bg="#eee", height=1).pack(fill="x", pady=(0, 16))

        # Lease details
        tk.Label(card, text="Lease Details",
                 font=("Helvetica", 11, "bold"),
                 bg=WHITE, fg=BLUE).pack(anchor="w", pady=(0, 12))

        details_grid = tk.Frame(card, bg=WHITE)
        details_grid.pack(fill="x")

        today = date.today()
        default_end = today + timedelta(days=365)

        def date_field(label, row, col, default):
            tk.Label(details_grid, text=label,
                     font=("Helvetica", 10),
                     bg=WHITE, fg="#555").grid(row=row, column=col*2,
                     sticky="w", padx=(0, 8), pady=8)
            var = tk.StringVar(value=str(default))
            tk.Entry(details_grid, textvariable=var,
                     font=("Helvetica", 11), width=16,
                     relief="solid", bd=1).grid(row=row,
                     column=col*2+1, sticky="w",
                     padx=(0, 24), pady=8)
            return var

        self.start_var = date_field("Start Date (YYYY-MM-DD)",
                                    0, 0, today)
        self.end_var = date_field("End Date (YYYY-MM-DD)",
                                  0, 1, default_end)

        tk.Label(details_grid, text="Monthly Rent (£)",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(row=1, column=0,
                 sticky="w", padx=(0, 8), pady=8)
        self.rent_var = tk.StringVar()
        tk.Entry(details_grid, textvariable=self.rent_var,
                 font=("Helvetica", 11), width=16,
                 relief="solid", bd=1).grid(row=1, column=1,
                 sticky="w", padx=(0, 24), pady=8)

        tk.Label(details_grid, text="Deposit Amount (£)",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(row=1, column=2,
                 sticky="w", padx=(0, 8), pady=8)
        self.deposit_var = tk.StringVar()
        tk.Entry(details_grid, textvariable=self.deposit_var,
                 font=("Helvetica", 11), width=16,
                 relief="solid", bd=1).grid(row=1, column=3,
                 sticky="w", pady=8)

        details_grid.columnconfigure(1, weight=1)
        details_grid.columnconfigure(3, weight=1)

        # Auto fill rent when apartment selected
        self.apt_tree.bind("<<TreeviewSelect>>",
                           self.on_apt_select)

        tk.Button(card, text="Assign Lease",
                  font=("Helvetica", 11, "bold"),
                  bg="#0F6E56", fg=WHITE, relief="flat",
                  cursor="hand2", command=self.assign_lease).pack(
                  fill="x", pady=(20, 0), ipady=10)

    def build_view_tab(self, parent):
        tk.Label(parent, text="Active Leases",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 12), padx=16)

        table_frame = tk.Frame(parent, bg=WHITE)
        table_frame.pack(fill="both", expand=True, padx=16)

        cols = ("ID", "Tenant", "Apartment", "Location",
                "Start", "End", "Rent", "Status")
        self.lease_tree = ttk.Treeview(table_frame, columns=cols,
                                        show="headings", height=14)
        widths = [40, 140, 90, 90, 90, 90, 80, 80]
        for col, width in zip(cols, widths):
            self.lease_tree.heading(col, text=col)
            self.lease_tree.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.lease_tree.yview)
        self.lease_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.lease_tree.pack(fill="both", expand=True)

        btn_frame = tk.Frame(parent, bg=CONTENT_BG)
        btn_frame.pack(fill="x", padx=16, pady=10)

        tk.Button(btn_frame, text="Refresh",
                  font=("Helvetica", 10), bg=BLUE, fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.load_leases).pack(side="left",
                  ipady=6, padx=(0, 8))

        tk.Button(btn_frame, text="Terminate Selected Lease",
                  font=("Helvetica", 10), bg="#A32D2D", fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.terminate_lease).pack(side="left",
                  ipady=6)

        self.load_leases()

    def search_tenants(self):
        for row in self.tenant_tree.get_children():
            self.tenant_tree.delete(row)
        query = self.tenant_search_var.get().strip()
        tenants = (self.tenant_dao.search(query) if query
                   else self.tenant_dao.get_all())
        for t in tenants:
            if not self.lease_dao.has_active_lease(t['tenant_id']):
                self.tenant_tree.insert("", "end",
                    iid=t['tenant_id'],
                    values=(t['tenant_id'], t['full_name'],
                            t['ni_number'],
                            t.get('preferred_location', '')))

    def load_available_apartments(self):
        for row in self.apt_tree.get_children():
            self.apt_tree.delete(row)
        apts = self.apt_dao.get_available()
        for a in apts:
            self.apt_tree.insert("", "end",
                iid=a['apartment_id'],
                values=(a['apartment_id'], a['apartment_number'],
                        a['location'], a['type'],
                        a['rooms'], f"£{a['monthly_rent']:.2f}"))

    def on_apt_select(self, event):
        selected = self.apt_tree.selection()
        if selected:
            apt_id = int(selected[0])
            apts = self.apt_dao.get_all()
            apt = next((a for a in apts
                       if a['apartment_id'] == apt_id), None)
            if apt:
                self.rent_var.set(str(apt['monthly_rent']))
                deposit = apt['monthly_rent'] * 1.5
                self.deposit_var.set(f"{deposit:.2f}")

    def load_leases(self):
        for row in self.lease_tree.get_children():
            self.lease_tree.delete(row)
        leases = self.lease_dao.get_active()
        for l in leases:
            self.lease_tree.insert("", "end",
                iid=l['lease_id'],
                values=(l['lease_id'], l['tenant_name'],
                        l['apartment_number'], l['location'],
                        l['start_date'], l['end_date'],
                        f"£{l['monthly_rent']:.2f}",
                        l['status']))

    def assign_lease(self):
        tenant_sel = self.tenant_tree.selection()
        apt_sel = self.apt_tree.selection()

        if not tenant_sel:
            messagebox.showwarning("No tenant",
                                   "Please select a tenant.")
            return
        if not apt_sel:
            messagebox.showwarning("No apartment",
                                   "Please select an apartment.")
            return

        try:
            rent = float(self.rent_var.get())
            deposit = float(self.deposit_var.get())
        except ValueError:
            messagebox.showerror("Invalid input",
                                 "Rent and deposit must be numbers.")
            return

        start = self.start_var.get().strip()
        end = self.end_var.get().strip()

        if not start or not end:
            messagebox.showerror("Missing dates",
                                 "Please enter start and end dates.")
            return

        tenant_id = int(tenant_sel[0])
        apt_id = int(apt_sel[0])

        if messagebox.askyesno("Confirm",
            "Assign this apartment to the selected tenant?"):
            try:
                self.lease_dao.create(tenant_id, apt_id,
                                      start, end, rent, deposit)
                messagebox.showinfo("Success",
                    "Lease created and first invoice generated!")
                self.search_tenants()
                self.load_available_apartments()
                self.load_leases()
                self.rent_var.set("")
                self.deposit_var.set("")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def terminate_lease(self):
        selected = self.lease_tree.selection()
        if not selected:
            messagebox.showwarning("No selection",
                                   "Please select a lease to terminate.")
            return

        if messagebox.askyesno("Confirm Termination",
            "Are you sure you want to terminate this lease?\n"
            "The apartment will be marked as available."):
            try:
                lease_id = int(selected[0])
                leases = self.lease_dao.get_active()
                lease = next((l for l in leases
                             if l['lease_id'] == lease_id), None)
                if lease:
                    self.lease_dao.terminate(lease_id,
                                            lease['apartment_id'])
                    messagebox.showinfo("Terminated",
                        "Lease terminated successfully.")
                    self.load_leases()
            except Exception as e:
                messagebox.showerror("Error", str(e))