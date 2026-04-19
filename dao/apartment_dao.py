# dao/apartment_dao.py
# Apartment data access - Group 30
# Student ID: 23029574 | Campbell Clark
# Student ID: 25013991 | Adjeneg Imed
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection

class ApartmentDAO:

    def get_all(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM apartments ORDER BY location, apartment_number")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_by_location(self, location):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM apartments WHERE location = ? ORDER BY apartment_number", (location,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_available(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM apartments WHERE status = 'available' ORDER BY location")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add(self, number, location, apt_type, rooms, rent):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO apartments (apartment_number, location, type, rooms, monthly_rent, status)
            VALUES (?, ?, ?, ?, ?, 'available')
        """, (number, location, apt_type, rooms, rent))
        conn.commit()
        conn.close()

    def update_status(self, apartment_id, status):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE apartments SET status = ? WHERE apartment_id = ?",
                       (status, apartment_id))
        conn.commit()
        conn.close()

    def update(self, apartment_id, number, location, apt_type, rooms, rent, status):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE apartments 
            SET apartment_number=?, location=?, type=?, rooms=?, monthly_rent=?, status=?
            WHERE apartment_id=?
        """, (number, location, apt_type, rooms, rent, status, apartment_id))
        conn.commit()
        conn.close()

    def delete(self, apartment_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM apartments WHERE apartment_id = ?", (apartment_id,))
        conn.commit()
        conn.close()