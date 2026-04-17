# dao/termination_dao.py
# Termination request data access
# Student ID: 23029574 | Campbell Clark
# Group 30 - PAMS

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection

class TerminationDAO:

    def create(self, lease_id, tenant_id, request_date,
               notice_end_date, penalty_amount):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO termination_requests
                (lease_id, tenant_id, request_date,
                 notice_end_date, penalty_amount, status)
                VALUES (?, ?, ?, ?, ?, 'pending')
            """, (lease_id, tenant_id, request_date,
                  notice_end_date, penalty_amount))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_by_tenant(self, tenant_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tr.*, l.monthly_rent,
                   a.apartment_number, a.location
            FROM termination_requests tr
            JOIN leases l ON tr.lease_id = l.lease_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
            WHERE tr.tenant_id = ?
            ORDER BY tr.created_at DESC
        """, (tenant_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_all(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tr.*, t.full_name as tenant_name,
                   a.apartment_number, a.location,
                   l.monthly_rent
            FROM termination_requests tr
            JOIN tenants t ON tr.tenant_id = t.tenant_id
            JOIN leases l ON tr.lease_id = l.lease_id
            JOIN apartments a ON l.apartment_id = a.apartment_id
            ORDER BY tr.created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def has_pending(self, tenant_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT termination_id FROM termination_requests
            WHERE tenant_id = ? AND status = 'pending'
        """, (tenant_id,))
        row = cursor.fetchone()
        conn.close()
        return row is not None

    def update_status(self, termination_id, status):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE termination_requests SET status = ?
            WHERE termination_id = ?
        """, (status, termination_id))
        conn.commit()
        conn.close()