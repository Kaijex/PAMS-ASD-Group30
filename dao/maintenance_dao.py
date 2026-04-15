# dao/maintenance_dao.py
# Maintenance request data access
# Student ID: 23029574 | Campbell Clark
# Group 30 - PAMS

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection

class MaintenanceDAO:

    def create(self, tenant_id, apartment_id, title,
               description, priority="medium"):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO maintenance_requests
                (tenant_id, apartment_id, title,
                 description, priority, status)
                VALUES (?, ?, ?, ?, ?, 'open')
            """, (tenant_id, apartment_id, title,
                  description, priority))
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
            SELECT m.*, t.full_name as tenant_name,
                   a.apartment_number, a.location,
                   u.username as assigned_to
            FROM maintenance_requests m
            JOIN tenants t ON m.tenant_id = t.tenant_id
            JOIN apartments a ON m.apartment_id = a.apartment_id
            LEFT JOIN users u ON m.assigned_staff_id = u.user_id
            ORDER BY 
                CASE m.priority 
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                END,
                m.created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_open(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.*, t.full_name as tenant_name,
                   a.apartment_number, a.location,
                   u.username as assigned_to
            FROM maintenance_requests m
            JOIN tenants t ON m.tenant_id = t.tenant_id
            JOIN apartments a ON m.apartment_id = a.apartment_id
            LEFT JOIN users u ON m.assigned_staff_id = u.user_id
            WHERE m.status = 'open'
            ORDER BY
                CASE m.priority
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                END,
                m.created_at ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_by_staff(self, staff_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.*, t.full_name as tenant_name,
                   a.apartment_number, a.location
            FROM maintenance_requests m
            JOIN tenants t ON m.tenant_id = t.tenant_id
            JOIN apartments a ON m.apartment_id = a.apartment_id
            WHERE m.assigned_staff_id = ?
            AND m.status != 'resolved'
            ORDER BY m.created_at DESC
        """, (staff_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_by_tenant(self, tenant_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.*, a.apartment_number,
                   u.username as assigned_to
            FROM maintenance_requests m
            JOIN apartments a ON m.apartment_id = a.apartment_id
            LEFT JOIN users u ON m.assigned_staff_id = u.user_id
            WHERE m.tenant_id = ?
            ORDER BY m.created_at DESC
        """, (tenant_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_resolved(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.*, t.full_name as tenant_name,
                   a.apartment_number, a.location,
                   u.username as assigned_to
            FROM maintenance_requests m
            JOIN tenants t ON m.tenant_id = t.tenant_id
            JOIN apartments a ON m.apartment_id = a.apartment_id
            LEFT JOIN users u ON m.assigned_staff_id = u.user_id
            WHERE m.status = 'resolved'
            ORDER BY m.resolved_date DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def assign_staff(self, request_id, staff_id, scheduled_date):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE maintenance_requests
            SET assigned_staff_id = ?,
                scheduled_date = ?,
                status = 'in_progress'
            WHERE request_id = ?
        """, (staff_id, scheduled_date, request_id))
        conn.commit()
        conn.close()

    def resolve(self, request_id, cost, time_taken):
        conn = get_connection()
        cursor = conn.cursor()
        from datetime import date
        today = str(date.today())
        cursor.execute("""
            UPDATE maintenance_requests
            SET status = 'resolved',
                resolved_date = ?,
                cost = ?,
                time_taken_hours = ?
            WHERE request_id = ?
        """, (today, cost, time_taken, request_id))
        conn.commit()
        conn.close()

    def update_priority(self, request_id, priority):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE maintenance_requests
            SET priority = ?
            WHERE request_id = ?
        """, (priority, request_id))
        conn.commit()
        conn.close()

    def get_maintenance_staff(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, username FROM users
            WHERE role = 'MAINTENANCE'
            AND is_active = 1
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_cost_summary(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COUNT(*) as total_requests,
                SUM(CASE WHEN status='resolved'
                    THEN 1 ELSE 0 END) as resolved,
                SUM(CASE WHEN status='open'
                    THEN 1 ELSE 0 END) as open_count,
                SUM(CASE WHEN status='in_progress'
                    THEN 1 ELSE 0 END) as in_progress,
                SUM(cost) as total_cost,
                AVG(time_taken_hours) as avg_time
            FROM maintenance_requests
        """)
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {}