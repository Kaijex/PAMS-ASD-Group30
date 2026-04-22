# PAMS — Paragon Apartment Management System
# Group 30 | Campbell Clark (23029574) | Imed Adjeneg (25013991)
# Module: UFCF8S-30-2 Advanced Software Development | UWE Bristol

## Overview
PAMS is a desktop application for managing apartment operations across
multiple UK cities. It supports role-based access for Admin, Front Desk,
Finance, Maintenance and Tenant users.

## Requirements
- Python 3.11+
- bcrypt library

## Installation
1. Clone or extract the project folder
2. Open a terminal in the project root
3. Create and activate a virtual environment:

Windows:
    python -m venv venv
    venv\Scripts\activate

4. Install dependencies:
    pip install -r requirements.txt

## Running the Application
    python main.py

The database will initialise automatically on first run.

## Demo Login Credentials

| Role        | Username    | Password     |
|-------------|-------------|--------------|
| Admin       | admin       | admin123     |
| Front Desk  | frontdesk   | front123     |
| Finance     | finance     | finance123   |
| Maintenance | maintenance | maint123     |
| Tenant      | (create via Front Desk registration) |

## How to Use
1. Run main.py to launch the login screen
2. Log in with any of the credentials above
3. Each role loads a different dashboard with relevant modules
4. To test the full tenant flow:
   - Log in as frontdesk and register a new tenant
   - Assign them an apartment via Lease Assignment
   - Log out and log in with the tenant credentials you created

## Project Structure
- main.py — application entry point
- database/ — schema, db connection and SQLite database file
- dao/ — data access layer, one file per table
- ui/ — login screen, dashboards and all UI modules
- tests/ — automated test file

## Additional Notes
- The database file pams.db is included with mock data for demonstration
- No external database server required, SQLite is built into Python
- All passwords are hashed using bcrypt