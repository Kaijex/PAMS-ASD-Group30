# dao/payment_dao.py
# Payment data access
# Student ID: 23029574 | Campbell Clark
# Group 30 - PAMS

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection
from datetime import date

class PaymentDAO:

    def get_all(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, t.full_name as tenant_name,
                   a.apartment_number, a.location
            FROM payments p
            JOIN tenants t ON p.tenant_id = t.tenant_id
            JOIN leases l ON p.lease_id = l.lease_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
            ORDER BY p.due_date DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_by_tenant(self, tenant_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, a.apartment_number, a.location
            FROM payments p
            JOIN leases l ON p.lease_id = l.lease_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
            WHERE p.tenant_id = ?
            ORDER BY p.due_date DESC
        """, (tenant_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_pending(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, t.full_name as tenant_name,
                   a.apartment_number, a.location
            FROM payments p
            JOIN tenants t ON p.tenant_id = t.tenant_id
            JOIN leases l ON p.lease_id = l.lease_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
            WHERE p.status = 'pending'
            ORDER BY p.due_date ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_late(self):
        conn = get_connection()
        cursor = conn.cursor()
        today = str(date.today())
        cursor.execute("""
            SELECT p.*, t.full_name as tenant_name,
                   a.apartment_number, a.location
            FROM payments p
            JOIN tenants t ON p.tenant_id = t.tenant_id
            JOIN leases l ON p.lease_id = l.lease_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
            WHERE p.status = 'pending'
            AND p.due_date < ?
            ORDER BY p.due_date ASC
        """, (today,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def mark_paid(self, payment_id):
        conn = get_connection()
        cursor = conn.cursor()
        today = str(date.today())
        cursor.execute("""
            UPDATE payments
            SET status = 'paid', paid_date = ?
            WHERE payment_id = ?
        """, (today, payment_id))
        conn.commit()
        conn.close()

    def mark_late(self, payment_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE payments SET status = 'late'
            WHERE payment_id = ?
        """, (payment_id,))
        conn.commit()
        conn.close()

    def create_invoice(self, tenant_id, lease_id, amount, due_date, notes=""):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO payments
            (tenant_id, lease_id, amount, due_date, status, notes)
            VALUES (?, ?, ?, ?, 'pending', ?)
        """, (tenant_id, lease_id, amount, due_date, notes))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    def get_summary(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                SUM(CASE WHEN status='paid' THEN amount ELSE 0 END) as collected,
                SUM(CASE WHEN status='pending' THEN amount ELSE 0 END) as pending,
                SUM(CASE WHEN status='late' THEN amount ELSE 0 END) as late,
                COUNT(*) as total_invoices
            FROM payments
        """)
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {}

    def auto_flag_late(self):
        conn = get_connection()
        cursor = conn.cursor()
        today = str(date.today())
        cursor.execute("""
            UPDATE payments SET status = 'late'
            WHERE status = 'pending'
            AND due_date < ?
        """, (today,))
        conn.commit()
        conn.close()