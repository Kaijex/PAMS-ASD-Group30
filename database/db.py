# database/db.py
# Database connection and initialisation
# Group 30 - PAMS
# Student ID: 23029574 | Campbell Clark
import sqlite3
import os
import bcrypt

DB_PATH = os.path.join(os.path.dirname(__file__), 'pams.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialise_db():
    """Create tables and seed default accounts on first run."""
    conn = get_connection()
    cursor = conn.cursor()

    with open(SCHEMA_PATH, 'r') as f:
        cursor.executescript(f.read())

    # Hash the placeholder passwords for seed accounts
    default_accounts = {
        'admin': 'admin123',
        'manager': 'manager123',
        'frontdesk': 'front123',
        'finance': 'finance123',
        'maintenance': 'maint123'
    }

    for username, password in default_accounts.items():
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("""
            UPDATE users SET password_hash = ? 
            WHERE username = ? AND password_hash = 'PLACEHOLDER'
        """, (hashed, username))

    conn.commit()
    conn.close()
    print("Database initialised successfully.")

if __name__ == "__main__":
    initialise_db()