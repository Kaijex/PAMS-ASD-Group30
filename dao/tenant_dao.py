# dao/tenant_dao.py
# Tenant data access
# Student ID: 23029574 | Campbell Clark
# Student ID: 25013991 | Adjeneg Imed
# Group 30 - PAMS

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection

class TenantDAO:

    def create(self, user_id, full_name, ni_number, phone,
               email, occupation, references_info, preferred_location):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO tenants 
                (user_id, full_name, ni_number, phone, email, 
                 occupation, references_info, preferred_location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, full_name, ni_number, phone, email,
                  occupation, references_info, preferred_location))
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
            SELECT t.*, u.username, u.is_active
            FROM tenants t
            JOIN users u ON t.user_id = u.user_id
            ORDER BY t.full_name
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_by_id(self, tenant_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.*, u.username, u.is_active
            FROM tenants t
            JOIN users u ON t.user_id = u.user_id
            WHERE t.tenant_id = ?
        """, (tenant_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_by_user_id(self, user_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tenants WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def ni_exists(self, ni_number):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT tenant_id FROM tenants WHERE ni_number = ?", (ni_number,))
        row = cursor.fetchone()
        conn.close()
        return row is not None

    def update(self, tenant_id, full_name, phone, email,
               occupation, references_info, preferred_location):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tenants
            SET full_name=?, phone=?, email=?, occupation=?,
                references_info=?, preferred_location=?
            WHERE tenant_id=?
        """, (full_name, phone, email, occupation,
              references_info, preferred_location, tenant_id))
        conn.commit()
        conn.close()

    def search(self, query):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.*, u.username, u.is_active
            FROM tenants t
            JOIN users u ON t.user_id = u.user_id
            WHERE t.full_name LIKE ?
            OR t.ni_number LIKE ?
            OR t.email LIKE ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]