# tests/test_pams.py
# Automated Unit Tests - PAMS
# Student ID: 23029574 - Campbell Clark
# Group 30 - PAMS

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import initialise_db, get_connection

# ── Setup ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def setup_db():
    """Initialise a fresh database before each test."""
    initialise_db()
    yield
    # Clean up test data after each test
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM complaints WHERE title LIKE 'TEST%'")
    cursor.execute("DELETE FROM maintenance_requests WHERE title LIKE 'TEST%'")
    cursor.execute("DELETE FROM payments WHERE notes LIKE 'TEST%'")
    cursor.execute("DELETE FROM leases WHERE deposit_amount = 9999.99")
    cursor.execute("DELETE FROM tenants WHERE ni_number LIKE 'QQ999%'")
    cursor.execute(
        "DELETE FROM users WHERE username LIKE 'testuser%' OR username LIKE 'pytest%'")
    conn.commit()
    conn.close()

# ── User / Authentication Tests ────────────────────────────────────────────

class TestUserDAO:

    def test_seed_accounts_exist(self):
        """Default seed accounts should exist after initialisation."""
        from dao.user_dao import UserDAO
        dao = UserDAO()
        assert dao.get_by_username('admin') is not None
        assert dao.get_by_username('frontdesk') is not None
        assert dao.get_by_username('finance') is not None
        assert dao.get_by_username('maintenance') is not None

    def test_create_user_success(self):
        """Should create a new user and return a valid user_id."""
        from dao.user_dao import UserDAO
        dao = UserDAO()
        user_id = dao.create_user(
            username='testuser1',
            password='password123',
            email='testuser1@pams.com',
            role='FRONTDESK',
            location='Bristol'
        )
        assert user_id is not None
        assert user_id > 0

    def test_username_exists_returns_true(self):
        """username_exists should return True for existing username."""
        from dao.user_dao import UserDAO
        dao = UserDAO()
        assert dao.username_exists('admin') is True

    def test_username_exists_returns_false(self):
        """username_exists should return False for non-existent username."""
        from dao.user_dao import UserDAO
        dao = UserDAO()
        assert dao.username_exists('nonexistentuser999') is False

    def test_email_exists_returns_true(self):
        """email_exists should return True for existing email."""
        from dao.user_dao import UserDAO
        dao = UserDAO()
        assert dao.email_exists('admin@pams.com') is True

    def test_duplicate_username_raises_error(self):
        """Creating a user with duplicate username should raise an error."""
        from dao.user_dao import UserDAO
        dao = UserDAO()
        with pytest.raises(Exception):
            dao.create_user(
                username='admin',
                password='password123',
                email='duplicate@pams.com',
                role='TENANT'
            )

    def test_deactivate_user(self):
        """Deactivating a user should set is_active to 0."""
        from dao.user_dao import UserDAO
        dao = UserDAO()
        user_id = dao.create_user(
            username='testuser2',
            password='password123',
            email='testuser2@pams.com',
            role='MAINTENANCE',
            location='Cardiff'
        )
        dao.deactivate(user_id)
        user = dao.get_by_id(user_id)
        assert user['is_active'] == 0

    def test_reactivate_user(self):
        """Reactivating a user should set is_active back to 1."""
        from dao.user_dao import UserDAO
        dao = UserDAO()
        user_id = dao.create_user(
            username='testuser3',
            password='password123',
            email='testuser3@pams.com',
            role='MAINTENANCE',
            location='London'
        )
        dao.deactivate(user_id)
        dao.reactivate(user_id)
        user = dao.get_by_id(user_id)
        assert user['is_active'] == 1

# ── Tenant Tests ───────────────────────────────────────────────────────────

class TestTenantDAO:

    def test_create_tenant_success(self):
        """Should create a tenant record linked to a user."""
        from dao.user_dao import UserDAO
        from dao.tenant_dao import TenantDAO
        user_dao = UserDAO()
        tenant_dao = TenantDAO()

        user_id = user_dao.create_user(
            username='pytest_tenant1',
            password='password123',
            email='pytest_tenant1@test.com',
            role='TENANT',
            location='Bristol'
        )
        tenant_id = tenant_dao.create(
            user_id=user_id,
            full_name='Test Tenant One',
            ni_number='QQ999001A',
            phone='07700000001',
            email='pytest_tenant1@test.com',
            occupation='Engineer',
            references_info='Test reference',
            preferred_location='Bristol'
        )
        assert tenant_id is not None
        assert tenant_id > 0

    def test_ni_exists_returns_true(self):
        """ni_exists should return True for an existing NI number."""
        from dao.user_dao import UserDAO
        from dao.tenant_dao import TenantDAO
        user_dao = UserDAO()
        tenant_dao = TenantDAO()

        user_id = user_dao.create_user(
            username='pytest_tenant2',
            password='password123',
            email='pytest_tenant2@test.com',
            role='TENANT'
        )
        tenant_dao.create(
            user_id=user_id,
            full_name='Test Tenant Two',
            ni_number='QQ999002A',
            phone='07700000002',
            email='pytest_tenant2@test.com',
            occupation='Teacher',
            references_info='',
            preferred_location='Cardiff'
        )
        assert tenant_dao.ni_exists('QQ999002A') is True

    def test_ni_exists_returns_false(self):
        """ni_exists should return False for a non-existent NI number."""
        from dao.tenant_dao import TenantDAO
        dao = TenantDAO()
        assert dao.ni_exists('ZZ000000Z') is False

    def test_get_by_user_id(self):
        """get_by_user_id should return the correct tenant record."""
        from dao.user_dao import UserDAO
        from dao.tenant_dao import TenantDAO
        user_dao = UserDAO()
        tenant_dao = TenantDAO()

        user_id = user_dao.create_user(
            username='pytest_tenant3',
            password='password123',
            email='pytest_tenant3@test.com',
            role='TENANT'
        )
        tenant_dao.create(
            user_id=user_id,
            full_name='Test Tenant Three',
            ni_number='QQ999003A',
            phone='07700000003',
            email='pytest_tenant3@test.com',
            occupation='Nurse',
            references_info='',
            preferred_location='Manchester'
        )
        tenant = tenant_dao.get_by_user_id(user_id)
        assert tenant is not None
        assert tenant['full_name'] == 'Test Tenant Three'

    def test_duplicate_ni_raises_error(self):
        """Creating two tenants with the same NI number should raise an error."""
        from dao.user_dao import UserDAO
        from dao.tenant_dao import TenantDAO
        user_dao = UserDAO()
        tenant_dao = TenantDAO()

        user_id1 = user_dao.create_user(
            'pytest_tenant4', 'pass123', 'pt4@test.com', 'TENANT')
        user_id2 = user_dao.create_user(
            'pytest_tenant5', 'pass123', 'pt5@test.com', 'TENANT')

        tenant_dao.create(user_id1, 'Tenant Four', 'QQ999004A',
                          '07700000004', 'pt4@test.com', 'Chef', '', 'Bristol')

        with pytest.raises(Exception):
            tenant_dao.create(user_id2, 'Tenant Five', 'QQ999004A',
                              '07700000005', 'pt5@test.com', 'Chef', '', 'London')

# ── Apartment Tests ────────────────────────────────────────────────────────

class TestApartmentDAO:

    def test_add_apartment_success(self):
        """Should add a new apartment and appear in get_all."""
        from dao.apartment_dao import ApartmentDAO
        dao = ApartmentDAO()
        initial_count = len(dao.get_all())
        dao.add('TEST-101', 'Bristol', '2 Bedroom', 2, 1200.00)
        assert len(dao.get_all()) == initial_count + 1

    def test_get_available_returns_only_available(self):
        """get_available should only return apartments with status available."""
        from dao.apartment_dao import ApartmentDAO
        dao = ApartmentDAO()
        available = dao.get_available()
        for apt in available:
            assert apt['status'] == 'available'

    def test_get_by_location(self):
        """get_by_location should only return apartments in that city."""
        from dao.apartment_dao import ApartmentDAO
        dao = ApartmentDAO()
        dao.add('TEST-LOC1', 'Manchester', 'Studio', 1, 800.00)
        results = dao.get_by_location('Manchester')
        for apt in results:
            assert apt['location'] == 'Manchester'

    def test_update_status(self):
        """update_status should change the apartment status correctly."""
        from dao.apartment_dao import ApartmentDAO
        dao = ApartmentDAO()
        dao.add('TEST-STATUS1', 'London', '1 Bedroom', 1, 1500.00)
        all_apts = dao.get_all()
        test_apt = next(
            a for a in all_apts if a['apartment_number'] == 'TEST-STATUS1')
        dao.update_status(test_apt['apartment_id'], 'maintenance')
        updated = dao.get_all()
        updated_apt = next(
            a for a in updated if a['apartment_id'] == test_apt['apartment_id'])
        assert updated_apt['status'] == 'maintenance'

# ── Payment Tests ──────────────────────────────────────────────────────────

class TestPaymentDAO:

    def test_auto_flag_late_updates_status(self):
        """Payments past due date should be flagged as late."""
        from dao.payment_dao import PaymentDAO
        dao = PaymentDAO()

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.payment_id FROM payments p
            WHERE p.status = 'pending'
            AND p.due_date < date('now')
            LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()

        dao.auto_flag_late()

        if row:
            conn2 = get_connection()
            cursor2 = conn2.cursor()
            cursor2.execute(
                "SELECT status FROM payments WHERE payment_id = ?",
                (row[0],))
            result = cursor2.fetchone()
            conn2.close()
            assert result['status'] == 'late'

    def test_get_summary_returns_dict(self):
        """get_summary should return a dictionary with expected keys."""
        from dao.payment_dao import PaymentDAO
        dao = PaymentDAO()
        summary = dao.get_summary()
        assert isinstance(summary, dict)
        assert 'collected' in summary
        assert 'pending' in summary
        assert 'late' in summary

# ── Maintenance Tests ──────────────────────────────────────────────────────

class TestMaintenanceDAO:

    def test_get_cost_summary_returns_dict(self):
        """get_cost_summary should return a dictionary with expected keys."""
        from dao.maintenance_dao import MaintenanceDAO
        dao = MaintenanceDAO()
        summary = dao.get_cost_summary()
        assert isinstance(summary, dict)
        assert 'total_requests' in summary
        assert 'total_cost' in summary

    def test_get_maintenance_staff_returns_list(self):
        """get_maintenance_staff should return a list of maintenance users."""
        from dao.maintenance_dao import MaintenanceDAO
        dao = MaintenanceDAO()
        staff = dao.get_maintenance_staff()
        assert isinstance(staff, list)
        for s in staff:
            assert 'user_id' in s
            assert 'username' in s

# ── Complaint Tests ────────────────────────────────────────────────────────

class TestComplaintDAO:

    def test_get_all_returns_list(self):
        """get_all should return a list."""
        from dao.complaint_dao import ComplaintDAO
        dao = ComplaintDAO()
        result = dao.get_all()
        assert isinstance(result, list)

    def test_get_open_returns_only_open(self):
        """get_open should only return complaints with status open."""
        from dao.complaint_dao import ComplaintDAO
        dao = ComplaintDAO()
        open_complaints = dao.get_open()
        for c in open_complaints:
            assert c['status'] == 'open'