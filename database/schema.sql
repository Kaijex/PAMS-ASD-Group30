-- PAMS database schema
-- Paragon Apartment Management System
-- Group 30

-- Users
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK(role IN ('ADMIN', 'MANAGER', 'FRONTDESK', 'FINANCE', 'MAINTENANCE', 'TENANT')),
    location TEXT CHECK(location IN ('Bristol', 'Cardiff', 'London', 'Manchester')),
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

-- apartments/flats
CREATE TABLE IF NOT EXISTS apartments (
    apartment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    apartment_number TEXT NOT NULL,
    location TEXT NOT NULL CHECK(location IN ('Bristol', 'Cardiff', 'London', 'Manchester')),
    type TEXT NOT NULL,
    rooms INTEGER NOT NULL,
    monthly_rent REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'available' CHECK(status IN ('available', 'occupied', 'maintenance')),
    created_at TEXT DEFAULT (datetime('now'))
);

-- Tenants
CREATE TABLE IF NOT EXISTS tenants (
    tenant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    full_name TEXT NOT NULL,
    ni_number TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    occupation TEXT NOT NULL,
    references_info TEXT,
    preferred_location TEXT CHECK(preferred_location IN ('Bristol', 'Cardiff', 'London', 'Manchester')),
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Leases
CREATE TABLE IF NOT EXISTS leases (
    lease_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    apartment_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    monthly_rent REAL NOT NULL,
    deposit_amount REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'expired', 'terminated')),
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
    FOREIGN KEY (apartment_id) REFERENCES apartments(apartment_id)
);

-- Payments
CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    lease_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    due_date TEXT NOT NULL,
    paid_date TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'paid', 'late')),
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
    FOREIGN KEY (lease_id) REFERENCES leases(lease_id)
);

-- Maintenance requests
CREATE TABLE IF NOT EXISTS maintenance_requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    apartment_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high')),
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'in_progress', 'resolved')),
    assigned_staff_id INTEGER,
    scheduled_date TEXT,
    resolved_date TEXT,
    cost REAL DEFAULT 0.0,
    time_taken_hours REAL DEFAULT 0.0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
    FOREIGN KEY (apartment_id) REFERENCES apartments(apartment_id),
    FOREIGN KEY (assigned_staff_id) REFERENCES users(user_id)
);

-- Complaints
CREATE TABLE IF NOT EXISTS complaints (
    complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'reviewed', 'resolved')),
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
);

-- Early termination requests
CREATE TABLE IF NOT EXISTS termination_requests (
    termination_id INTEGER PRIMARY KEY AUTOINCREMENT,
    lease_id INTEGER NOT NULL,
    tenant_id INTEGER NOT NULL,
    request_date TEXT NOT NULL,
    notice_end_date TEXT NOT NULL,
    penalty_amount REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected')),
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (lease_id) REFERENCES leases(lease_id),
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
);

-- Seed data - Default admin account
INSERT OR IGNORE INTO users (username, password_hash, email, role, location) VALUES
('admin', 'PLACEHOLDER', 'admin@pams.com', 'ADMIN', 'Bristol'),
('manager', 'PLACEHOLDER', 'manager@pams.com', 'MANAGER', 'Bristol'),
('frontdesk', 'PLACEHOLDER', 'frontdesk@pams.com', 'FRONTDESK', 'Bristol'),
('finance', 'PLACEHOLDER', 'finance@pams.com', 'FINANCE', 'Bristol'),
('maintenance', 'PLACEHOLDER', 'maintenance@pams.com', 'MAINTENANCE', 'Bristol');