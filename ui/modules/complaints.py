# ui/modules/complaints.py
# Complaints Module
# Student ID: 23029574 | Campbell Clark
# Group 30 - PAMS

import tkinter as tk
from tkinter import ttk, messagebox
from dao.complaint_dao import ComplaintDAO
from dao.tenant_dao import TenantDAO

CONTENT_BG = "#f0f4f8"
WHITE = "#ffffff"
BLUE = "#185FA5"
STATUSES = ["open", "reviewed", "resolved"]

STATUS_COLOURS = {
    "open": "#A32D2D",
    "reviewed": "#BA7517",
    "resolved": "#0F6E56"
}

class ComplaintsModule(tk.Frame):
    def __init__(self, parent, user=None, mode="staff"):
        super().__init__(parent, bg=CONTENT_BG)
        self.dao = ComplaintDAO()
        self.tenant_dao = TenantDAO()
        self.user = user
        self.mode = mode
        self.selected_id = None
        self.build()

    def build(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        if self.mode == "staff":
            all_tab = tk.Frame(notebook, bg=CONTENT_BG)
            notebook.add(all_tab, text="  All Complaints  ")

            log_tab = tk.Frame(notebook, bg=CONTENT_BG)
            notebook.add(log_tab, text="  Log Complaint  ")

            self.build_all_tab(all_tab)
            self.build_log_tab(log_tab)
        else:
            my_tab = tk.Frame(notebook, bg=CONTENT_BG)
            notebook.add(my_tab, text="  My Complaints  ")

            new_tab = tk.Frame(notebook, bg=CONTENT_BG)
            notebook.add(new_tab, text="  New Complaint  ")

            self.build_tenant_view(my_tab)
            self.build_tenant_new(new_tab)

    def build_all_tab(self, parent):
        tk.Label(parent, text="All Complaints",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 8), padx=16)

        table_frame = tk.Frame(parent, bg=WHITE)
        table_frame.pack(fill="both", expand=True, padx=16)

        cols = ("ID", "Tenant", "Title", "Status", "Submitted")
        self.all_tree = ttk.Treeview(table_frame, columns=cols,
                                      show="headings", height=12)
        widths = [40, 150, 220, 90, 100]
        for col, width in zip(cols, widths):
            self.all_tree.heading(col, text=col)
            self.all_tree.column(col, width=width, anchor="center")

        for status, colour in STATUS_COLOURS.items():
            self.all_tree.tag_configure(status, foreground=colour)

        self.all_tree.bind("<<TreeviewSelect>>", self.on_select)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.all_tree.yview)
        self.all_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.all_tree.pack(fill="both", expand=True)

        btn_frame = tk.Frame(parent, bg=CONTENT_BG)
        btn_frame.pack(fill="x", padx=16, pady=10)

        for label, status, colour in [
            ("Mark Reviewed", "reviewed", "#BA7517"),
            ("Mark Resolved", "resolved", "#0F6E56")
        ]:
            tk.Button(btn_frame, text=label,
                      font=("Helvetica", 10), bg=colour, fg=WHITE,
                      relief="flat", cursor="hand2", padx=12,
                      command=lambda s=status: self.update_status(s)
                      ).pack(side="left", ipady=6, padx=(0, 8))

        tk.Button(btn_frame, text="View Details",
                  font=("Helvetica", 10), bg=BLUE, fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.view_details).pack(
                  side="left", ipady=6, padx=(0, 8))

        tk.Button(btn_frame, text="Refresh",
                  font=("Helvetica", 10), bg="#444", fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.load_all).pack(side="left", ipady=6)

        self.load_all()

    def build_log_tab(self, parent):
        card = tk.Frame(parent, bg=WHITE, padx=30, pady=24)
        card.pack(fill="x", padx=16, pady=16)

        tk.Label(card, text="Log Complaint on Behalf of Tenant",
                 font=("Helvetica", 13, "bold"),
                 bg=WHITE, fg=BLUE).pack(anchor="w", pady=(0, 12))

        tk.Label(card, text="Select Tenant",
                 font=("Helvetica", 11, "bold"),
                 bg=WHITE, fg="#1a1a1a").pack(anchor="w", pady=(0, 6))

        tenant_cols = ("ID", "Name", "Location")
        self.log_tenant_tree = ttk.Treeview(card,
                                             columns=tenant_cols,
                                             show="headings", height=4)
        for col in tenant_cols:
            self.log_tenant_tree.heading(col, text=col)
            self.log_tenant_tree.column(col, width=150, anchor="center")
        self.log_tenant_tree.pack(fill="x", pady=(0, 16))

        tenants = self.tenant_dao.get_all()
        for t in tenants:
            self.log_tenant_tree.insert("", "end",
                iid=t['tenant_id'],
                values=(t['tenant_id'], t['full_name'],
                        t.get('preferred_location', '')))

        tk.Frame(card, bg="#eee", height=1).pack(fill="x", pady=(0, 16))

        form = tk.Frame(card, bg=WHITE)
        form.pack(fill="x")

        tk.Label(form, text="Title *",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(row=0, column=0,
                 sticky="w", pady=8, padx=(0, 12))
        self.log_title_var = tk.StringVar()
        tk.Entry(form, textvariable=self.log_title_var,
                 font=("Helvetica", 11), width=38,
                 relief="solid", bd=1).grid(row=0, column=1,
                 sticky="ew", pady=8)

        tk.Label(form, text="Description *",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(row=1, column=0,
                 sticky="nw", pady=8, padx=(0, 12))
        self.log_desc = tk.Text(form, font=("Helvetica", 11),
                                width=38, height=4,
                                relief="solid", bd=1)
        self.log_desc.grid(row=1, column=1, sticky="ew", pady=8)
        form.columnconfigure(1, weight=1)

        tk.Button(card, text="Submit Complaint",
                  font=("Helvetica", 11, "bold"),
                  bg=BLUE, fg=WHITE, relief="flat",
                  cursor="hand2",
                  command=self.log_complaint).pack(
                  fill="x", pady=(20, 0), ipady=10)

    def build_tenant_view(self, parent):
        tk.Label(parent, text="My Complaints",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(
                 anchor="w", pady=(16, 8), padx=16)

        table_frame = tk.Frame(parent, bg=WHITE)
        table_frame.pack(fill="both", expand=True, padx=16)

        cols = ("ID", "Title", "Status", "Submitted")
        self.my_tree = ttk.Treeview(table_frame, columns=cols,
                                     show="headings", height=12)
        widths = [40, 260, 100, 100]
        for col, width in zip(cols, widths):
            self.my_tree.heading(col, text=col)
            self.my_tree.column(col, width=width, anchor="center")

        for status, colour in STATUS_COLOURS.items():
            self.my_tree.tag_configure(status, foreground=colour)

        self.my_tree.bind("<<TreeviewSelect>>",
                          lambda e: self.on_tenant_select())

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.my_tree.yview)
        self.my_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.my_tree.pack(fill="both", expand=True)

        tk.Button(parent, text="Refresh",
                  font=("Helvetica", 10), bg=BLUE, fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.load_tenant_complaints).pack(
                  anchor="w", padx=16, pady=10, ipady=6)

        self.load_tenant_complaints()

    def build_tenant_new(self, parent):
        card = tk.Frame(parent, bg=WHITE, padx=30, pady=24)
        card.pack(fill="x", padx=16, pady=16)

        tk.Label(card, text="Submit a Complaint",
                 font=("Helvetica", 13, "bold"),
                 bg=WHITE, fg=BLUE).pack(anchor="w", pady=(0, 16))

        form = tk.Frame(card, bg=WHITE)
        form.pack(fill="x")

        tk.Label(form, text="Title *",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(row=0, column=0,
                 sticky="w", pady=8, padx=(0, 12))
        self.t_title_var = tk.StringVar()
        tk.Entry(form, textvariable=self.t_title_var,
                 font=("Helvetica", 11), width=36,
                 relief="solid", bd=1).grid(row=0, column=1,
                 sticky="ew", pady=8)

        tk.Label(form, text="Description *",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(row=1, column=0,
                 sticky="nw", pady=8, padx=(0, 12))
        self.t_desc = tk.Text(form, font=("Helvetica", 11),
                              width=36, height=5,
                              relief="solid", bd=1)
        self.t_desc.grid(row=1, column=1, sticky="ew", pady=8)
        form.columnconfigure(1, weight=1)

        tk.Button(card, text="Submit Complaint",
                  font=("Helvetica", 11, "bold"),
                  bg=BLUE, fg=WHITE, relief="flat",
                  cursor="hand2",
                  command=self.tenant_submit).pack(
                  fill="x", pady=(20, 0), ipady=10)

    def load_all(self):
        for row in self.all_tree.get_children():
            self.all_tree.delete(row)
        complaints = self.dao.get_all()
        for c in complaints:
            self.all_tree.insert("", "end",
                iid=c['complaint_id'],
                values=(c['complaint_id'], c['tenant_name'],
                        c['title'], c['status'],
                        c.get('created_at', '')[:10]),
                tags=(c['status'],))

    def load_tenant_complaints(self):
        if not self.user:
            return
        for row in self.my_tree.get_children():
            self.my_tree.delete(row)
        tenant = self.tenant_dao.get_by_user_id(self.user['user_id'])
        if not tenant:
            return
        complaints = self.dao.get_by_tenant(tenant['tenant_id'])
        for c in complaints:
            self.my_tree.insert("", "end",
                values=(c['complaint_id'], c['title'],
                        c['status'],
                        c.get('created_at', '')[:10]),
                tags=(c['status'],))

    def on_select(self, event):
        selected = self.all_tree.selection()
        if selected:
            self.selected_id = int(selected[0])

    def on_tenant_select(self):
        selected = self.my_tree.selection()
        if selected:
            self.selected_id = int(selected[0])

    def update_status(self, status):
        if not self.selected_id:
            messagebox.showwarning("No selection",
                                   "Please select a complaint first.")
            return
        self.dao.update_status(self.selected_id, status)
        self.selected_id = None
        self.load_all()

    def view_details(self):
        if not self.selected_id:
            messagebox.showwarning("No selection",
                                   "Please select a complaint to view.")
            return
        complaints = self.dao.get_all()
        complaint = next((c for c in complaints
                         if c['complaint_id'] == self.selected_id), None)
        if not complaint:
            return

        dialog = tk.Toplevel(self)
        dialog.title("Complaint Details")
        dialog.geometry("440x320")
        dialog.resizable(False, False)
        dialog.configure(bg=WHITE)
        dialog.grab_set()

        header = tk.Frame(dialog, bg=BLUE, pady=16)
        header.pack(fill="x")
        tk.Label(header, text=complaint['title'],
                 font=("Helvetica", 13, "bold"),
                 bg=BLUE, fg=WHITE).pack(padx=20)
        tk.Label(header,
                 text=f"From: {complaint['tenant_name']}",
                 font=("Helvetica", 10),
                 bg=BLUE, fg="#B5D4F4").pack()

        details = tk.Frame(dialog, bg=WHITE, padx=24, pady=16)
        details.pack(fill="both", expand=True)

        fields = [
            ("Status", complaint['status']),
            ("Submitted", complaint.get('created_at', '')[:10]),
        ]
        for label, value in fields:
            row = tk.Frame(details, bg=WHITE)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=f"{label}:",
                     font=("Helvetica", 10),
                     bg=WHITE, fg="#888", width=12,
                     anchor="w").pack(side="left")
            tk.Label(row, text=value,
                     font=("Helvetica", 10),
                     bg=WHITE, fg="#1a1a1a",
                     anchor="w").pack(side="left")

        tk.Label(details, text="Description:",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#888",
                 anchor="w").pack(fill="x", pady=(8, 4))
        tk.Label(details, text=complaint['description'],
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#1a1a1a",
                 wraplength=380, justify="left",
                 anchor="w").pack(fill="x")

        tk.Button(dialog, text="Close",
                  font=("Helvetica", 10), bg="#555", fg=WHITE,
                  relief="flat", cursor="hand2",
                  command=dialog.destroy).pack(
                  pady=16, padx=24, fill="x", ipady=6)

    def log_complaint(self):
        selected = self.log_tenant_tree.selection()
        if not selected:
            messagebox.showwarning("No tenant",
                                   "Please select a tenant.")
            return
        title = self.log_title_var.get().strip()
        description = self.log_desc.get("1.0", tk.END).strip()
        if not title or not description:
            messagebox.showerror("Missing fields",
                                 "Title and description are required.")
            return
        tenant_id = int(selected[0])
        self.dao.create(tenant_id, title, description)
        messagebox.showinfo("Submitted",
                            "Complaint logged successfully!")
        self.log_title_var.set("")
        self.log_desc.delete("1.0", tk.END)
        self.load_all()

    def tenant_submit(self):
        if not self.user:
            return
        tenant = self.tenant_dao.get_by_user_id(self.user['user_id'])
        if not tenant:
            messagebox.showerror("Error",
                "No tenant record found for your account.")
            return
        title = self.t_title_var.get().strip()
        description = self.t_desc.get("1.0", tk.END).strip()
        if not title or not description:
            messagebox.showerror("Missing fields",
                                 "Title and description are required.")
            return
        self.dao.create(tenant['tenant_id'], title, description)
        messagebox.showinfo("Submitted",
                            "Your complaint has been submitted!")
        self.t_title_var.set("")
        self.t_desc.delete("1.0", tk.END)
        self.load_tenant_complaints()