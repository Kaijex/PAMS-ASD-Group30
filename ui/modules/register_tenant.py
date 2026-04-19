# ui/modules/register_tenant.py
# Tenant Registration Module
# Student ID: 23029574 | Campbell Clark
# Group 30 - PAMS

import tkinter as tk
from tkinter import ttk, messagebox
from dao.tenant_dao import TenantDAO
from dao.user_dao import UserDAO

CONTENT_BG = "#f0f4f8"
WHITE = "#ffffff"
BLUE = "#185FA5"
LOCATIONS = ["Bristol", "Cardiff", "London", "Manchester"]

class RegisterTenantModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CONTENT_BG)
        self.tenant_dao = TenantDAO()
        self.user_dao = UserDAO()
        self.build()

    def build(self):
        # Scrollable canvas
        canvas = tk.Canvas(self, bg=CONTENT_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.form_frame = tk.Frame(canvas, bg=CONTENT_BG)
        canvas_window = canvas.create_window((0, 0), window=self.form_frame, anchor="nw")

        def on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(e):
            canvas.itemconfig(canvas_window, width=e.width)

        self.form_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        self.build_form()

    def build_form(self):
        f = self.form_frame

        tk.Label(f, text="Register New Tenant",
                 font=("Helvetica", 14, "bold"),
                 bg=CONTENT_BG, fg="#1a1a1a").pack(anchor="w", pady=(0, 20))

        # Card container
        card = tk.Frame(f, bg=WHITE, padx=30, pady=24)
        card.pack(fill="x", pady=(0, 16))

        tk.Label(card, text="Personal Information",
                 font=("Helvetica", 11, "bold"),
                 bg=WHITE, fg=BLUE).pack(anchor="w", pady=(0, 12))

        grid = tk.Frame(card, bg=WHITE)
        grid.pack(fill="x")

        self.entries = {}

        def make_field(parent, label, row, col, var_name, width=28):
            tk.Label(parent, text=label, font=("Helvetica", 10),
                     bg=WHITE, fg="#555").grid(row=row, column=col*2,
                     sticky="w", padx=(0, 8), pady=6)
            var = tk.StringVar()
            entry = tk.Entry(parent, textvariable=var,
                             font=("Helvetica", 11),
                             width=width, relief="solid", bd=1)
            entry.grid(row=row, column=col*2+1, sticky="ew",
                       padx=(0, 24), pady=6)
            self.entries[var_name] = var
            return var

        make_field(grid, "Full Name *", 0, 0, "full_name")
        make_field(grid, "NI Number *", 0, 1, "ni_number")
        make_field(grid, "Phone *", 1, 0, "phone")
        make_field(grid, "Email *", 1, 1, "email")
        make_field(grid, "Occupation *", 2, 0, "occupation")

        # References
        tk.Label(grid, text="References",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(row=3, column=0,
                 sticky="nw", pady=6)
        ref_text = tk.Text(grid, font=("Helvetica", 11),
                           width=28, height=3,
                           relief="solid", bd=1)
        ref_text.grid(row=3, column=1, sticky="ew",
                      padx=(0, 24), pady=6)
        self.ref_text = ref_text

        # Preferred location
        tk.Label(grid, text="Preferred Location *",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(row=4, column=0,
                 sticky="w", pady=6)
        self.loc_var = tk.StringVar(value=LOCATIONS[0])
        loc_menu = ttk.Combobox(grid, textvariable=self.loc_var,
                                values=LOCATIONS, state="readonly",
                                font=("Helvetica", 11), width=26)
        loc_menu.grid(row=4, column=1, sticky="w", pady=6)

        grid.columnconfigure(1, weight=1)
        grid.columnconfigure(3, weight=1)

        # Account card
        acc_card = tk.Frame(f, bg=WHITE, padx=30, pady=24)
        acc_card.pack(fill="x", pady=(0, 16))

        tk.Label(acc_card, text="Login Account Details",
                 font=("Helvetica", 11, "bold"),
                 bg=WHITE, fg=BLUE).pack(anchor="w", pady=(0, 4))
        tk.Label(acc_card, text="These credentials will be used by the tenant to log in.",
                 font=("Helvetica", 9), bg=WHITE,
                 fg="#888").pack(anchor="w", pady=(0, 12))

        acc_grid = tk.Frame(acc_card, bg=WHITE)
        acc_grid.pack(fill="x")

        tk.Label(acc_grid, text="Username *",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(row=0, column=0,
                 sticky="w", padx=(0, 8), pady=6)
        self.username_var = tk.StringVar()
        tk.Entry(acc_grid, textvariable=self.username_var,
                 font=("Helvetica", 11), width=28,
                 relief="solid", bd=1).grid(row=0, column=1,
                 sticky="ew", padx=(0, 24), pady=6)

        tk.Label(acc_grid, text="Password *",
                 font=("Helvetica", 10),
                 bg=WHITE, fg="#555").grid(row=0, column=2,
                 sticky="w", padx=(0, 8), pady=6)
        self.password_var = tk.StringVar()
        tk.Entry(acc_grid, textvariable=self.password_var,
                 font=("Helvetica", 11), width=28,
                 relief="solid", bd=1, show="*").grid(row=0, column=3,
                 sticky="ew", pady=6)

        acc_grid.columnconfigure(1, weight=1)
        acc_grid.columnconfigure(3, weight=1)

        # Buttons
        btn_frame = tk.Frame(f, bg=CONTENT_BG)
        btn_frame.pack(fill="x", pady=8)

        tk.Button(btn_frame, text="Register Tenant",
                  font=("Helvetica", 11, "bold"),
                  bg=BLUE, fg=WHITE, relief="flat",
                  cursor="hand2", padx=20,
                  command=self.submit).pack(side="left",
                  ipady=8, padx=(0, 12))

        tk.Button(btn_frame, text="Clear Form",
                  font=("Helvetica", 11),
                  bg="#888", fg=WHITE, relief="flat",
                  cursor="hand2", padx=20,
                  command=self.clear_form).pack(side="left", ipady=8)

    def validate(self):
        required = {
            "full_name": "Full Name",
            "ni_number": "NI Number",
            "phone": "Phone",
            "email": "Email",
            "occupation": "Occupation"
        }
        for key, label in required.items():
            if not self.entries[key].get().strip():
                messagebox.showerror("Missing field", f"{label} is required.")
                return False

        if not self.username_var.get().strip():
            messagebox.showerror("Missing field", "Username is required.")
            return False

        if not self.password_var.get().strip():
            messagebox.showerror("Missing field", "Password is required.")
            return False

        if len(self.password_var.get()) < 6:
            messagebox.showerror("Weak password",
                                 "Password must be at least 6 characters.")
            return False

        ni = self.entries["ni_number"].get().strip().upper()
        if self.tenant_dao.ni_exists(ni):
            messagebox.showerror("Duplicate NI",
                                 "A tenant with this NI number already exists.")
            return False

        if self.user_dao.username_exists(self.username_var.get().strip()):
            messagebox.showerror("Duplicate username",
                                 "This username is already taken.")
            return False

        if self.user_dao.email_exists(self.entries["email"].get().strip()):
            messagebox.showerror("Duplicate email",
                                 "This email is already registered.")
            return False

        return True

    def submit(self):
        if not self.validate():
            return

        try:
            user_id = self.user_dao.create_user(
                username=self.username_var.get().strip(),
                password=self.password_var.get().strip(),
                email=self.entries["email"].get().strip(),
                role="TENANT",
                location=self.loc_var.get()
            )

            self.tenant_dao.create(
                user_id=user_id,
                full_name=self.entries["full_name"].get().strip(),
                ni_number=self.entries["ni_number"].get().strip().upper(),
                phone=self.entries["phone"].get().strip(),
                email=self.entries["email"].get().strip(),
                occupation=self.entries["occupation"].get().strip(),
                references_info=self.ref_text.get("1.0", tk.END).strip(),
                preferred_location=self.loc_var.get()
            )

            messagebox.showinfo("Success",
                                f"Tenant registered successfully!\n"
                                f"They can log in with username: "
                                f"{self.username_var.get().strip()}")
            self.clear_form()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to register tenant:\n{str(e)}")

    def clear_form(self):
        for var in self.entries.values():
            var.set("")
        self.username_var.set("")
        self.password_var.set("")
        self.ref_text.delete("1.0", tk.END)
        self.loc_var.set(LOCATIONS[0])