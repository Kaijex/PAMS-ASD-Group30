# dao/user_dao.py
# User account data access
# Student ID: 23029574 | Campbell Clark
# Student ID: 25013991 | Adjeneg Imed
# Group 30 - PAMS

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection
import bcrypt

class UserDAO:

    def create_user(self, username, password, email, role, location=None):
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, role, location)
                VALUES (?, ?, ?, ?, ?)
            """, (username, password_hash, email, role, location))
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
        cursor.execute("SELECT * FROM users ORDER BY role, username")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_by_id(self, user_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_by_username(self, username):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def username_exists(self, username):
        return self.get_by_username(username) is not None

    def email_exists(self, email):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        return row is not None

    def deactivate(self, user_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_active = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

    def reactivate(self, user_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_active = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

    def update(self, user_id, email, role, location):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET email=?, role=?, location=?
            WHERE user_id=?
        """, (email, role, location, user_id))
        conn.commit()
        conn.close()