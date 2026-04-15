# dao/complaint_dao.py
# Complaint data access
# Student ID: 23029574 | Campbell Clark
# Group 30 - PAMS

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection

class ComplaintDAO:

    def create(self, tenant_id, title, description):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO complaints
                (tenant_id, title, description, status)
                VALUES (?, ?, ?, 'open')
            """, (tenant_id, title, description))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_all(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, t.full_name as tenant_name
            FROM complaints c
            JOIN tenants t ON c.tenant_id = t.tenant_id
            ORDER BY c.created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_by_tenant(self, tenant_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM complaints
            WHERE tenant_id = ?
            ORDER BY created_at DESC
        """, (tenant_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_open(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, t.full_name as tenant_name
            FROM complaints c
            JOIN tenants t ON c.tenant_id = t.tenant_id
            WHERE c.status = 'open'
            ORDER BY c.created_at ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def update_status(self, complaint_id, status):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE complaints SET status = ?
            WHERE complaint_id = ?
        """, (status, complaint_id))
        conn.commit()
        conn.close()