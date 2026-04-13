# main.py
# PAMS - Paragon Apartment Management System
# Group 30 - Entry point

from database.db import initialise_db

if __name__ == "__main__":
    initialise_db()
    print("PAMS starting...")