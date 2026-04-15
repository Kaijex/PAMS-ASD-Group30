# ui/modules/maintenance.py
# Maintenance Requests Module
# Student ID: 23029574 | Campbell Clark
# Group 30 - PAMS

import tkinter as tk
from tkinter import ttk, messagebox
from dao.maintenance_dao import MaintenanceDAO
from dao.tenant_dao import TenantDAO
from dao.lease_dao import LeaseDAO

CONTENT_BG = "#f0f4f8"
WHITE = "#ffffff"
BLUE = "#185FA5"
PRIORITIES = ["low", "medium", "high"]

PRIORITY_COLOURS = {
    "high": "#A32D2D",
    "medium": "#BA7517",
    "low": "#0F6E56"
}

class MaintenanceModule(tk.Frame):
    def __init__(self, parent, user=None, mode="staff"):
        super().__init__(parent, bg=CONTENT_BG)
        self.dao = MaintenanceDAO()
        self.tenant_dao = TenantDAO()
        self.lease_dao = LeaseDAO()
        self.user = user
        # mode: "staff" for maintenance/frontdesk, "tenant" for tenant view
        self.mode = mode
        self.selected_id = None
        self.build()

    def build(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        if self.mode == "staff":
            open_tab = tk.Frame(notebook, bg=CONTENT_BG)
            notebook.add(open_tab, text="  Open Requests  ")

            progress_tab = tk.Frame(notebook, bg=CONTENT_BG)
            notebook.add(progress_tab, text="  In Progress  ")

            resolved_tab = tk.Frame(notebook, bg=CONTENT_BG)
            notebook.add(resolved_tab, text="  Resolved  ")

            log_tab = tk.Frame(notebook, bg=CONTENT_BG)
            notebook.add(log_tab, text="  Log Request  ")

            self.build_open_tab(open_tab)
            self.build_progress_tab(progress_tab)
            self.build_resolved_tab(resolved_tab)
            self.build_log_tab(log_tab)

        else:
            my_tab = tk.Frame(notebook, bg=CONTENT_BG)
            notebook.add(my_tab, text="  My Requests  ")

            new_tab = tk.Frame(notebook, bg=CONTENT_BG)
            notebook.add(new_tab, text="  New Request  ")

            self.build_tenant_view(my_tab)
            self.build_tenant_new_request(new_tab)

    def build_open_tab(self, parent):
        tk.Label(parent, text="Open Maintenance Requests",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 8), padx=16)

        table_frame = tk.Frame(parent, bg=WHITE)
        table_frame.pack(fill="both", expand=True, padx=16)

        cols = ("ID", "Tenant", "Apartment", "Location",
                "Title", "Priority", "Submitted")
        self.open_tree = ttk.Treeview(table_frame, columns=cols,
                                       show="headings", height=10)
        widths = [40, 130, 90, 90, 160, 80, 90]
        for col, width in zip(cols, widths):
            self.open_tree.heading(col, text=col)
            self.open_tree.column(col, width=width, anchor="center")

        for priority, colour in PRIORITY_COLOURS.items():
            self.open_tree.tag_configure(priority, foreground=colour)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.open_tree.yview)
        self.open_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.open_tree.pack(fill="both", expand=True)

        btn_frame = tk.Frame(parent, bg=CONTENT_BG)
        btn_frame.pack(fill="x", padx=16, pady=10)

        tk.Button(btn_frame, text="Assign Staff & Schedule",
                  font=("Helvetica", 10), bg=BLUE, fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.assign_dialog).pack(
                  side="left", ipady=6, padx=(0, 8))

        tk.Button(btn_frame, text="Change Priority",
                  font=("Helvetica", 10), bg="#BA7517", fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.change_priority).pack(
                  side="left", ipady=6, padx=(0, 8))

        tk.Button(btn_frame, text="Refresh",
                  font=("Helvetica", 10), bg="#444", fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.load_open).pack(side="left", ipady=6)

        self.load_open()

    def build_progress_tab(self, parent):
        tk.Label(parent, text="In Progress",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 8), padx=16)

        table_frame = tk.Frame(parent, bg=WHITE)
        table_frame.pack(fill="both", expand=True, padx=16)

        cols = ("ID", "Tenant", "Apartment", "Title",
                "Priority", "Assigned To", "Scheduled")
        self.progress_tree = ttk.Treeview(table_frame, columns=cols,
                                           show="headings", height=10)
        widths = [40, 130, 100, 150, 80, 110, 100]
        for col, width in zip(cols, widths):
            self.progress_tree.heading(col, text=col)
            self.progress_tree.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.progress_tree.yview)
        self.progress_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.progress_tree.pack(fill="both", expand=True)

        btn_frame = tk.Frame(parent, bg=CONTENT_BG)
        btn_frame.pack(fill="x", padx=16, pady=10)

        tk.Button(btn_frame, text="Mark as Resolved",
                  font=("Helvetica", 10), bg="#0F6E56", fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.resolve_dialog).pack(
                  side="left", ipady=6, padx=(0, 8))

        tk.Button(btn_frame, text="Refresh",
                  font=("Helvetica", 10), bg="#444", fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.load_progress).pack(side="left", ipady=6)

        self.load_progress()

    def build_resolved_tab(self, parent):
        tk.Label(parent, text="Resolved Requests",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 8), padx=16)

        table_frame = tk.Frame(parent, bg=WHITE)
        table_frame.pack(fill="both", expand=True, padx=16)

        cols = ("ID", "Tenant", "Apartment", "Title",
                "Resolved Date", "Cost (£)", "Time (hrs)")
        self.resolved_tree = ttk.Treeview(table_frame, columns=cols,
                                           show="headings", height=12)
        widths = [40, 130, 100, 160, 100, 80, 90]
        for col, width in zip(cols, widths):
            self.resolved_tree.heading(col, text=col)
            self.resolved_tree.column(col, width=width, anchor="center")

        self.resolved_tree.tag_configure("resolved", foreground="#0F6E56")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.resolved_tree.yview)
        self.resolved_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.resolved_tree.pack(fill="both", expand=True)

        self.load_resolved()

    def build_log_tab(self, parent):
        canvas = tk.Canvas(parent, bg=CONTENT_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical",
                                   command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        form_frame = tk.Frame(canvas, bg=CONTENT_BG)
        canvas_win = canvas.create_window((0, 0),
                                          window=form_frame, anchor="nw")
        form_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(canvas_win, width=e.width))

        tk.Label(form_frame, text="Log Maintenance Request",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 20), padx=16)

        card = tk.Frame(form_frame, bg=WHITE, padx=30, pady=24)
        card.pack(fill="x", padx=16)

        tk.Label(card, text="Select Tenant",
                 font=("Helvetica", 11, "bold"),
                 bg=WHITE, fg=BLUE).pack(anchor="w", pady=(0, 8))

        tenant_cols = ("ID", "Name", "Apartment")
        self.log_tenant_tree = ttk.Treeview(card,
                                             columns=tenant_cols,
                                             show="headings", height=4)
        for col in tenant_cols:
            self.log_tenant_tree.heading(col, text=col)
            self.log_tenant_tree.column(col, width=150, anchor="center")
        self.log_tenant_tree.pack(fill="x", pady=(0, 16))
        self.load_tenants_with_leases()

        tk.Frame(card, bg="#eee", height=1).pack(fill="x", pady=(0, 16))

        form = tk.Frame(card, bg=WHITE)
        form.pack(fill="x")

        tk.Label(form, text="Title *", font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(row=0, column=0,
                 sticky="w", pady=8, padx=(0, 12))
        self.log_title_var = tk.StringVar()
        tk.Entry(form, textvariable=self.log_title_var,
                 font=("Helvetica", 11), width=40,
                 relief="solid", bd=1).grid(row=0, column=1,
                 sticky="ew", pady=8)

        tk.Label(form, text="Priority", font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(row=1, column=0,
                 sticky="w", pady=8, padx=(0, 12))
        self.log_priority_var = tk.StringVar(value="medium")
        ttk.Combobox(form, textvariable=self.log_priority_var,
                     values=PRIORITIES, state="readonly",
                     font=("Helvetica", 11),
                     width=15).grid(row=1, column=1,
                     sticky="w", pady=8)

        tk.Label(form, text="Description *",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(row=2, column=0,
                 sticky="nw", pady=8, padx=(0, 12))
        self.log_desc = tk.Text(form, font=("Helvetica", 11),
                                width=40, height=4,
                                relief="solid", bd=1)
        self.log_desc.grid(row=2, column=1, sticky="ew", pady=8)

        form.columnconfigure(1, weight=1)

        tk.Button(card, text="Submit Request",
                  font=("Helvetica", 11, "bold"),
                  bg=BLUE, fg=WHITE, relief="flat",
                  cursor="hand2",
                  command=self.log_request).pack(
                  fill="x", pady=(20, 0), ipady=10)

    def build_tenant_view(self, parent):
        tk.Label(parent, text="My Maintenance Requests",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 8), padx=16)

        table_frame = tk.Frame(parent, bg=WHITE)
        table_frame.pack(fill="both", expand=True, padx=16)

        cols = ("ID", "Title", "Priority", "Status",
                "Assigned To", "Scheduled", "Submitted")
        self.tenant_tree = ttk.Treeview(table_frame, columns=cols,
                                         show="headings", height=12)
        widths = [40, 180, 80, 90, 110, 100, 90]
        for col, width in zip(cols, widths):
            self.tenant_tree.heading(col, text=col)
            self.tenant_tree.column(col, width=width, anchor="center")

        for priority, colour in PRIORITY_COLOURS.items():
            self.tenant_tree.tag_configure(priority, foreground=colour)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.tenant_tree.yview)
        self.tenant_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tenant_tree.pack(fill="both", expand=True)

        tk.Button(parent, text="Refresh",
                  font=("Helvetica", 10), bg=BLUE, fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.load_tenant_requests).pack(
                  anchor="w", padx=16, pady=10, ipady=6)

        self.load_tenant_requests()

    def build_tenant_new_request(self, parent):
        card = tk.Frame(parent, bg=WHITE, padx=30, pady=24)
        card.pack(fill="x", padx=16, pady=16)

        tk.Label(card, text="Submit New Maintenance Request",
                 font=("Helvetica", 13, "bold"),
                 bg=WHITE, fg=BLUE).pack(anchor="w", pady=(0, 16))

        form = tk.Frame(card, bg=WHITE)
        form.pack(fill="x")

        tk.Label(form, text="Title *", font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(row=0, column=0,
                 sticky="w", pady=8, padx=(0, 12))
        self.t_title_var = tk.StringVar()
        tk.Entry(form, textvariable=self.t_title_var,
                 font=("Helvetica", 11), width=36,
                 relief="solid", bd=1).grid(row=0, column=1,
                 sticky="ew", pady=8)

        tk.Label(form, text="Priority", font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(row=1, column=0,
                 sticky="w", pady=8, padx=(0, 12))
        self.t_priority_var = tk.StringVar(value="medium")
        ttk.Combobox(form, textvariable=self.t_priority_var,
                     values=PRIORITIES, state="readonly",
                     font=("Helvetica", 11),
                     width=15).grid(row=1, column=1,
                     sticky="w", pady=8)

        tk.Label(form, text="Description *",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(row=2, column=0,
                 sticky="nw", pady=8, padx=(0, 12))
        self.t_desc = tk.Text(form, font=("Helvetica", 11),
                              width=36, height=5,
                              relief="solid", bd=1)
        self.t_desc.grid(row=2, column=1, sticky="ew", pady=8)

        form.columnconfigure(1, weight=1)

        tk.Button(card, text="Submit Request",
                  font=("Helvetica", 11, "bold"),
                  bg=BLUE, fg=WHITE, relief="flat",
                  cursor="hand2",
                  command=self.tenant_submit).pack(
                  fill="x", pady=(20, 0), ipady=10)

    def load_open(self):
        for row in self.open_tree.get_children():
            self.open_tree.delete(row)
        requests = self.dao.get_open()
        for r in requests:
            self.open_tree.insert("", "end",
                iid=r['request_id'],
                values=(r['request_id'], r['tenant_name'],
                        r['apartment_number'], r['location'],
                        r['title'], r['priority'],
                        r.get('created_at', '')[:10]),
                tags=(r['priority'],))

    def load_progress(self):
        for row in self.progress_tree.get_children():
            self.progress_tree.delete(row)
        all_requests = self.dao.get_all()
        in_progress = [r for r in all_requests
                       if r['status'] == 'in_progress']
        for r in in_progress:
            self.progress_tree.insert("", "end",
                iid=r['request_id'],
                values=(r['request_id'], r['tenant_name'],
                        r['apartment_number'], r['title'],
                        r['priority'],
                        r.get('assigned_to') or 'Unassigned',
                        r.get('scheduled_date') or 'TBC'))

    def load_resolved(self):
        for row in self.resolved_tree.get_children():
            self.resolved_tree.delete(row)
        requests = self.dao.get_resolved()
        for r in requests:
            self.resolved_tree.insert("", "end",
                values=(r['request_id'], r['tenant_name'],
                        r['apartment_number'], r['title'],
                        r.get('resolved_date') or '-',
                        f"£{r.get('cost') or 0:.2f}",
                        r.get('time_taken_hours') or 0),
                tags=("resolved",))

    def load_tenants_with_leases(self):
        for row in self.log_tenant_tree.get_children():
            self.log_tenant_tree.delete(row)
        tenants = self.tenant_dao.get_all()
        for t in tenants:
            leases = self.lease_dao.get_by_tenant(t['tenant_id'])
            if leases:
                apt = leases[0].get('apartment_number', 'N/A')
                self.log_tenant_tree.insert("", "end",
                    iid=t['tenant_id'],
                    values=(t['tenant_id'], t['full_name'], apt))

    def load_tenant_requests(self):
        if not self.user:
            return
        for row in self.tenant_tree.get_children():
            self.tenant_tree.delete(row)
        tenant = self.tenant_dao.get_by_user_id(self.user['user_id'])
        if not tenant:
            return
        requests = self.dao.get_by_tenant(tenant['tenant_id'])
        for r in requests:
            self.tenant_tree.insert("", "end",
                values=(r['request_id'], r['title'],
                        r['priority'], r['status'],
                        r.get('assigned_to') or 'Unassigned',
                        r.get('scheduled_date') or 'TBC',
                        r.get('created_at', '')[:10]),
                tags=(r['priority'],))

    def assign_dialog(self):
        selected = self.open_tree.selection()
        if not selected:
            messagebox.showwarning("No selection",
                                   "Please select a request to assign.")
            return

        request_id = int(selected[0])
        staff_list = self.dao.get_maintenance_staff()

        if not staff_list:
            messagebox.showerror("No staff",
                "No maintenance staff accounts found.")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Assign Staff")
        dialog.geometry("380x280")
        dialog.resizable(False, False)
        dialog.configure(bg=WHITE)
        dialog.grab_set()

        tk.Label(dialog, text="Assign Maintenance Staff",
                 font=("Helvetica", 13, "bold"),
                 bg=WHITE, fg="#1a1a1a").pack(pady=(20, 16))

        form = tk.Frame(dialog, bg=WHITE, padx=30)
        form.pack(fill="x")

        tk.Label(form, text="Staff Member",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(row=0, column=0,
                 sticky="w", pady=8)
        staff_names = [s['username'] for s in staff_list]
        staff_var = tk.StringVar(value=staff_names[0])
        ttk.Combobox(form, textvariable=staff_var,
                     values=staff_names, state="readonly",
                     font=("Helvetica", 11),
                     width=20).grid(row=0, column=1,
                     sticky="ew", padx=(12, 0), pady=8)

        tk.Label(form, text="Scheduled Date",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(row=1, column=0,
                 sticky="w", pady=8)
        from datetime import date, timedelta
        default_date = str(date.today() + timedelta(days=2))
        date_var = tk.StringVar(value=default_date)
        tk.Entry(form, textvariable=date_var,
                 font=("Helvetica", 11), width=20,
                 relief="solid", bd=1).grid(row=1, column=1,
                 sticky="ew", padx=(12, 0), pady=8)

        form.columnconfigure(1, weight=1)

        def confirm():
            selected_name = staff_var.get()
            staff = next((s for s in staff_list
                         if s['username'] == selected_name), None)
            if staff:
                self.dao.assign_staff(request_id,
                                      staff['user_id'],
                                      date_var.get())
                messagebox.showinfo("Assigned",
                    "Staff assigned successfully.", parent=dialog)
                dialog.destroy()
                self.load_open()
                self.load_progress()

        tk.Button(dialog, text="Confirm Assignment",
                  font=("Helvetica", 11, "bold"),
                  bg=BLUE, fg=WHITE, relief="flat",
                  cursor="hand2",
                  command=confirm).pack(pady=20, padx=30,
                  fill="x", ipady=8)

    def resolve_dialog(self):
        selected = self.progress_tree.selection()
        if not selected:
            messagebox.showwarning("No selection",
                                   "Please select a request to resolve.")
            return

        request_id = int(selected[0])

        dialog = tk.Toplevel(self)
        dialog.title("Resolve Request")
        dialog.geometry("360x240")
        dialog.resizable(False, False)
        dialog.configure(bg=WHITE)
        dialog.grab_set()

        tk.Label(dialog, text="Mark Request as Resolved",
                 font=("Helvetica", 13, "bold"),
                 bg=WHITE, fg="#1a1a1a").pack(pady=(20, 16))

        form = tk.Frame(dialog, bg=WHITE, padx=30)
        form.pack(fill="x")

        tk.Label(form, text="Cost (£)",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(row=0, column=0,
                 sticky="w", pady=8)
        cost_var = tk.StringVar(value="0")
        tk.Entry(form, textvariable=cost_var,
                 font=("Helvetica", 11), width=20,
                 relief="solid", bd=1).grid(row=0, column=1,
                 sticky="ew", padx=(12, 0), pady=8)

        tk.Label(form, text="Time Taken (hrs)",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(row=1, column=0,
                 sticky="w", pady=8)
        time_var = tk.StringVar(value="1")
        tk.Entry(form, textvariable=time_var,
                 font=("Helvetica", 11), width=20,
                 relief="solid", bd=1).grid(row=1, column=1,
                 sticky="ew", padx=(12, 0), pady=8)

        form.columnconfigure(1, weight=1)

        def confirm():
            try:
                cost = float(cost_var.get())
                time_taken = float(time_var.get())
            except ValueError:
                messagebox.showerror("Invalid",
                    "Cost and time must be numbers.", parent=dialog)
                return
            self.dao.resolve(request_id, cost, time_taken)
            messagebox.showinfo("Resolved",
                "Request marked as resolved.", parent=dialog)
            dialog.destroy()
            self.load_progress()
            self.load_resolved()

        tk.Button(dialog, text="Mark Resolved",
                  font=("Helvetica", 11, "bold"),
                  bg="#0F6E56", fg=WHITE, relief="flat",
                  cursor="hand2",
                  command=confirm).pack(pady=20, padx=30,
                  fill="x", ipady=8)

    def change_priority(self):
        selected = self.open_tree.selection()
        if not selected:
            messagebox.showwarning("No selection",
                                   "Please select a request.")
            return

        request_id = int(selected[0])

        dialog = tk.Toplevel(self)
        dialog.title("Change Priority")
        dialog.geometry("300x180")
        dialog.resizable(False, False)
        dialog.configure(bg=WHITE)
        dialog.grab_set()

        tk.Label(dialog, text="Select New Priority",
                 font=("Helvetica", 12, "bold"),
                 bg=WHITE, fg="#1a1a1a").pack(pady=(20, 16))

        priority_var = tk.StringVar(value="medium")
        ttk.Combobox(dialog, textvariable=priority_var,
                     values=PRIORITIES, state="readonly",
                     font=("Helvetica", 11),
                     width=20).pack(pady=(0, 16))

        def confirm():
            self.dao.update_priority(request_id, priority_var.get())
            dialog.destroy()
            self.load_open()

        tk.Button(dialog, text="Update Priority",
                  font=("Helvetica", 11, "bold"),
                  bg=BLUE, fg=WHITE, relief="flat",
                  cursor="hand2",
                  command=confirm).pack(padx=30, fill="x", ipady=8)

    def log_request(self):
        selected = self.log_tenant_tree.selection()
        if not selected:
            messagebox.showwarning("No tenant",
                                   "Please select a tenant.")
            return

        tenant_id = int(selected[0])
        title = self.log_title_var.get().strip()
        description = self.log_desc.get("1.0", tk.END).strip()
        priority = self.log_priority_var.get()

        if not title or not description:
            messagebox.showerror("Missing fields",
                                 "Title and description are required.")
            return

        leases = self.lease_dao.get_by_tenant(tenant_id)
        if not leases:
            messagebox.showerror("No lease",
                "This tenant has no active lease.")
            return

        apartment_id = leases[0]['apartment_id']
        self.dao.create(tenant_id, apartment_id, title,
                        description, priority)
        messagebox.showinfo("Submitted",
                            "Maintenance request logged successfully!")
        self.log_title_var.set("")
        self.log_desc.delete("1.0", tk.END)
        self.load_open()

    def tenant_submit(self):
        if not self.user:
            return

        tenant = self.tenant_dao.get_by_user_id(self.user['user_id'])
        if not tenant:
            messagebox.showerror("Error",
                "No tenant record found for your account.")
            return

        leases = self.lease_dao.get_by_tenant(tenant['tenant_id'])
        if not leases:
            messagebox.showerror("No lease",
                "You must have an active lease to submit a request.")
            return

        title = self.t_title_var.get().strip()
        description = self.t_desc.get("1.0", tk.END).strip()
        priority = self.t_priority_var.get()

        if not title or not description:
            messagebox.showerror("Missing fields",
                                 "Title and description are required.")
            return

        apartment_id = leases[0]['apartment_id']
        self.dao.create(tenant['tenant_id'], apartment_id,
                        title, description, priority)
        messagebox.showinfo("Submitted",
                            "Your request has been submitted!")
        self.t_title_var.set("")
        self.t_desc.delete("1.0", tk.END)
        self.load_tenant_requests()