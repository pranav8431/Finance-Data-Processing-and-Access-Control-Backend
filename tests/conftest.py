from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.deps import get_db
from app.core.security import create_password_hash
from app.db.session import Base
from app.main import app
from app.models.financial_record import FinancialRecord, RecordType
from app.models.user import User, UserRole, UserStatus

TEST_DATABASE_URL = 'sqlite:///./test_finance.db'

engine = create_engine(TEST_DATABASE_URL, connect_args={'check_same_thread': False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def month_start_shift(today: date, months_back: int) -> date:
    year = today.year
    month = today.month
    for _ in range(months_back):
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return date(year, month, 1)


@pytest.fixture(scope='session', autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_test_db):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def seeded_data(db_session):
    admin = User(
        name='Admin',
        email='admin@test.com',
        role=UserRole.admin,
        status=UserStatus.active,
        password_hash=create_password_hash('admin123'),
    )
    viewer = User(
        name='Viewer',
        email='viewer@test.com',
        role=UserRole.viewer,
        status=UserStatus.active,
        password_hash=create_password_hash('viewer123'),
    )
    analyst = User(
        name='Analyst',
        email='analyst@test.com',
        role=UserRole.analyst,
        status=UserStatus.active,
        password_hash=create_password_hash('analyst123'),
    )
    inactive = User(
        name='Inactive',
        email='inactive@test.com',
        role=UserRole.viewer,
        status=UserStatus.inactive,
        password_hash=create_password_hash('inactive123'),
    )

    db_session.add_all([admin, viewer, analyst, inactive])
    db_session.flush()

    today = date.today()
    records = [
        FinancialRecord(
            amount=Decimal('1000.00'),
            type=RecordType.income,
            category='salary',
            date=month_start_shift(today, 5),
            notes='m-5 income',
            created_by=admin.id,
        ),
        FinancialRecord(
            amount=Decimal('300.00'),
            type=RecordType.expense,
            category='rent',
            date=month_start_shift(today, 5),
            notes='m-5 expense',
            created_by=admin.id,
        ),
        FinancialRecord(
            amount=Decimal('1400.00'),
            type=RecordType.income,
            category='salary',
            date=month_start_shift(today, 4),
            notes='m-4 income',
            created_by=admin.id,
        ),
        FinancialRecord(
            amount=Decimal('500.00'),
            type=RecordType.expense,
            category='groceries',
            date=month_start_shift(today, 3),
            notes='m-3 expense',
            created_by=admin.id,
        ),
        FinancialRecord(
            amount=Decimal('200.00'),
            type=RecordType.expense,
            category='transport',
            date=month_start_shift(today, 2),
            notes='m-2 expense',
            created_by=admin.id,
        ),
        FinancialRecord(
            amount=Decimal('1800.00'),
            type=RecordType.income,
            category='freelance',
            date=month_start_shift(today, 1),
            notes='m-1 income',
            created_by=admin.id,
        ),
        FinancialRecord(
            amount=Decimal('150.00'),
            type=RecordType.expense,
            category='rent',
            date=month_start_shift(today, 0),
            notes='m-0 expense',
            created_by=admin.id,
        ),
        FinancialRecord(
            amount=Decimal('2100.00'),
            type=RecordType.income,
            category='bonus',
            date=today,
            notes='latest income',
            created_by=admin.id,
        ),
    ]

    db_session.add_all(records)
    db_session.commit()

    return {'admin': admin, 'viewer': viewer, 'analyst': analyst, 'inactive': inactive, 'records': records}


def auth_headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    res = client.post('/api/v1/auth/login', json={'email': email, 'password': password})
    token = res.json()['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def admin_headers(client, seeded_data):
    return auth_headers(client, 'admin@test.com', 'admin123')


@pytest.fixture
def viewer_headers(client, seeded_data):
    return auth_headers(client, 'viewer@test.com', 'viewer123')


@pytest.fixture
def analyst_headers(client, seeded_data):
    return auth_headers(client, 'analyst@test.com', 'analyst123')


@pytest.fixture
def inactive_headers(client, seeded_data):
    return auth_headers(client, 'inactive@test.com', 'inactive123')
