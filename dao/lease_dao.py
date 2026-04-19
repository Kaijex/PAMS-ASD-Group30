# dao/lease_dao.py
# Lease data access
# Student ID: 23029574 | Campbell Clark
# Group 30 - PAMS

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection

class LeaseDAO:

    def create(self, tenant_id, apartment_id, start_date,
               end_date, monthly_rent, deposit_amount):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO leases 
                (tenant_id, apartment_id, start_date, end_date,
                 monthly_rent, deposit_amount, status)
                VALUES (?, ?, ?, ?, ?, ?, 'active')
            """, (tenant_id, apartment_id, start_date,
                  end_date, monthly_rent, deposit_amount))
            lease_id = cursor.lastrowid

            # Automatically mark apartment as occupied
            cursor.execute("""
                UPDATE apartments SET status = 'occupied'
                WHERE apartment_id = ?
            """, (apartment_id,))

            # Generate first month invoice automatically
            cursor.execute("""
                INSERT INTO payments
                (tenant_id, lease_id, amount, due_date, status, notes)
                VALUES (?, ?, ?, ?, 'pending', 'First month rent invoice')
            """, (tenant_id, lease_id, monthly_rent, start_date))

            conn.commit()
            return lease_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_all(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.*, t.full_name as tenant_name,
                   a.apartment_number, a.location
            FROM leases l
            JOIN tenants t ON l.tenant_id = t.tenant_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
            ORDER BY l.created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_by_tenant(self, tenant_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.*, a.apartment_number, a.location, a.type
            FROM leases l
            JOIN apartments a ON l.apartment_id = a.apartment_id
            WHERE l.tenant_id = ?
            ORDER BY l.created_at DESC
        """, (tenant_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_active(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.*, t.full_name as tenant_name,
                   a.apartment_number, a.location
            FROM leases l
            JOIN tenants t ON l.tenant_id = t.tenant_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
            WHERE l.status = 'active'
            ORDER BY l.end_date ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_expiring_soon(self, days=30):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.*, t.full_name as tenant_name,
                   a.apartment_number, a.location
            FROM leases l
            JOIN tenants t ON l.tenant_id = t.tenant_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
            WHERE l.status = 'active'
            AND date(l.end_date) <= date('now', '+' || ? || ' days')
            ORDER BY l.end_date ASC
        """, (days,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def terminate(self, lease_id, apartment_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE leases SET status = 'terminated'
                WHERE lease_id = ?
            """, (lease_id,))
            cursor.execute("""
                UPDATE apartments SET status = 'available'
                WHERE apartment_id = ?
            """, (apartment_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def has_active_lease(self, tenant_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT lease_id FROM leases
            WHERE tenant_id = ? AND status = 'active'
        """, (tenant_id,))
        row = cursor.fetchone()
        conn.close()
        return row is not None