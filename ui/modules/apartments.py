# ui/modules/apartments.py
# Apartment Management Module - Group 30
# Student ID: 23029574 | Campbell Clark

import tkinter as tk
from tkinter import ttk, messagebox
from dao.apartment_dao import ApartmentDAO

CONTENT_BG = "#f0f4f8"
WHITE = "#ffffff"
BLUE = "#185FA5"

LOCATIONS = ["Bristol", "Cardiff", "London", "Manchester"]
TYPES = ["Studio", "1 Bedroom", "2 Bedroom", "3 Bedroom", "Penthouse"]
STATUSES = ["available", "occupied", "maintenance"]

class ApartmentsModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CONTENT_BG)
        self.dao = ApartmentDAO()
        self.selected_id = None
        self.build()

    def build(self):
        # Top bar with Add button
        top = tk.Frame(self, bg=CONTENT_BG)
        top.pack(fill="x", pady=(0, 16))

        tk.Label(top, text="All Apartments", font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(side="left")

        tk.Button(top, text="+ Add Apartment",
                  font=("Helvetica", 10), bg=BLUE, fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.open_add_dialog).pack(side="right", ipady=6)

        # Filter bar
        filter_frame = tk.Frame(self, bg=WHITE,
                                relief="flat", bd=0)
        filter_frame.pack(fill="x", pady=(0, 12))

        tk.Label(filter_frame, text="Filter by location:",
                 font=("Helvetica", 10), bg=WHITE,
                 fg="#555").pack(side="left", padx=12, pady=10)

        self.location_var = tk.StringVar(value="All")
        locations = ["All"] + LOCATIONS
        for loc in locations:
            tk.Radiobutton(filter_frame, text=loc,
                          variable=self.location_var,
                          value=loc, bg=WHITE,
                          font=("Helvetica", 10),
                          command=self.load_table).pack(side="left", padx=8)

        # Table
        table_frame = tk.Frame(self, bg=WHITE)
        table_frame.pack(fill="both", expand=True)

        cols = ("ID", "Number", "Location", "Type", "Rooms", "Rent (£)", "Status")
        self.tree = ttk.Treeview(table_frame, columns=cols,
                                  show="headings", height=15)

        width = [40, 80, 100, 110, 60, 90, 100]
        for col, width in zip(cols, width):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure("available", foreground="#0F6E56")
        self.tree.tag_configure("occupied", foreground="#185FA5")
        self.tree.tag_configure("maintenance", foreground="#BA7517")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Action buttons
        action_frame = tk.Frame(self, bg=CONTENT_BG)
        action_frame.pack(fill="x", pady=12)

        tk.Button(action_frame, text="Edit Selected",
                  font=("Helvetica", 10), bg="#378ADD", fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.open_edit_dialog).pack(side="left", ipady=6, padx=(0, 8))

        tk.Button(action_frame, text="Delete Selected",
                  font=("Helvetica", 10), bg="#A32D2D", fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.delete_selected).pack(side="left", ipady=6)

        tk.Button(action_frame, text="Refresh",
                  font=("Helvetica", 10), bg="#3B6D11", fg=WHITE,
                  relief="flat", cursor="hand2", padx=12,
                  command=self.load_table).pack(side="right", ipady=6)

        self.load_table()

    def load_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        loc = self.location_var.get()
        if loc == "All":
            apartments = self.dao.get_all()
        else:
            apartments = self.dao.get_by_location(loc)

        for apt in apartments:
            self.tree.insert("", "end", iid=apt['apartment_id'],
                             values=(
                                 apt['apartment_id'],
                                 apt['apartment_number'],
                                 apt['location'],
                                 apt['type'],
                                 apt['rooms'],
                                 f"£{apt['monthly_rent']:.2f}",
                                 apt['status']
                             ), tags=(apt['status'],))

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.selected_id = int(selected[0])

    def open_add_dialog(self):
        self.open_form_dialog("Add Apartment")

    def open_edit_dialog(self):
        if not self.selected_id:
            messagebox.showwarning("No selection", "Please select an apartment to edit.")
            return
        apartments = self.dao.get_all()
        apt = next((a for a in apartments if a['apartment_id'] == self.selected_id), None)
        if apt:
            self.open_form_dialog("Edit Apartment", apt)

    def open_form_dialog(self, title, apt=None):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("400x420")
        dialog.resizable(False, False)
        dialog.configure(bg=WHITE)
        dialog.grab_set()

        tk.Label(dialog, text=title, font=("Helvetica", 14, "bold"),
                 bg=WHITE, fg="#1a1a1a").pack(pady=(20, 16))

        form = tk.Frame(dialog, bg=WHITE)
        form.pack(padx=30, fill="x")

        def field(label, row, widget):
            tk.Label(form, text=label, font=("Helvetica", 10),
                     bg=WHITE, fg="#555").grid(row=row, column=0,
                     sticky="w", pady=6)
            widget.grid(row=row, column=1, sticky="ew", padx=(12, 0), pady=6)
            form.columnconfigure(1, weight=1)

        num_var = tk.StringVar(value=apt['apartment_number'] if apt else "")
        num_entry = tk.Entry(form, textvariable=num_var,
                             font=("Helvetica", 11), relief="solid", bd=1)
        field("Apt Number", 0, num_entry)

        loc_var = tk.StringVar(value=apt['location'] if apt else LOCATIONS[0])
        loc_menu = ttk.Combobox(form, textvariable=loc_var,
                                values=LOCATIONS, state="readonly",
                                font=("Helvetica", 11))
        field("Location", 1, loc_menu)

        type_var = tk.StringVar(value=apt['type'] if apt else TYPES[0])
        type_menu = ttk.Combobox(form, textvariable=type_var,
                                 values=TYPES, state="readonly",
                                 font=("Helvetica", 11))
        field("Type", 2, type_menu)

        rooms_var = tk.StringVar(value=str(apt['rooms']) if apt else "1")
        rooms_entry = tk.Entry(form, textvariable=rooms_var,
                               font=("Helvetica", 11), relief="solid", bd=1)
        field("Rooms", 3, rooms_entry)

        rent_var = tk.StringVar(value=str(apt['monthly_rent']) if apt else "")
        rent_entry = tk.Entry(form, textvariable=rent_var,
                              font=("Helvetica", 11), relief="solid", bd=1)
        field("Monthly Rent (£)", 4, rent_entry)

        status_var = tk.StringVar(value=apt['status'] if apt else "available")
        status_menu = ttk.Combobox(form, textvariable=status_var,
                                   values=STATUSES, state="readonly",
                                   font=("Helvetica", 11))
        field("Status", 5, status_menu)

        def save():
            num = num_var.get().strip()
            location = loc_var.get()
            apt_type = type_var.get()
            status = status_var.get()

            try:
                rooms = int(rooms_var.get())
                rent = float(rent_var.get())
            except ValueError:
                messagebox.showerror("Invalid input",
                                     "Rooms must be a whole number and rent must be a number.",
                                     parent=dialog)
                return

            if not num:
                messagebox.showerror("Missing field",
                                     "Apartment number is required.",
                                     parent=dialog)
                return

            if apt:
                self.dao.update(self.selected_id, num, location,
                                apt_type, rooms, rent, status)
                messagebox.showinfo("Updated",
                                    "Apartment updated successfully.",
                                    parent=dialog)
            else:
                self.dao.add(num, location, apt_type, rooms, rent)
                messagebox.showinfo("Added",
                                    "Apartment added successfully.",
                                    parent=dialog)

            dialog.destroy()
            self.load_table()

        tk.Button(dialog, text="Save",
                  font=("Helvetica", 11, "bold"),
                  bg=BLUE, fg=WHITE, relief="flat",
                  cursor="hand2", command=save).pack(pady=20, ipady=8, padx=30, fill="x")

    def delete_selected(self):
        if not self.selected_id:
            messagebox.showwarning("No selection",
                                   "Please select an apartment to delete.")
            return
        if messagebox.askyesno("Confirm Delete",
                               "Are you sure you want to delete this apartment?"):
            self.dao.delete(self.selected_id)
            self.selected_id = None
            self.load_table()