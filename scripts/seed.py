import sys
from pathlib import Path
from datetime import date
from decimal import Decimal

from sqlalchemy import select

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.session import SessionLocal
from app.models.financial_record import FinancialRecord, RecordType
from app.models.user import User, UserRole, UserStatus
from app.core.security import create_password_hash


def seed_users(session):
    fixtures = [
        {
            'name': 'Admin User',
            'email': 'admin@example.com',
            'role': UserRole.admin,
            'status': UserStatus.active,
            'password': 'admin123',
        },
        {
            'name': 'Viewer User',
            'email': 'viewer@example.com',
            'role': UserRole.viewer,
            'status': UserStatus.active,
            'password': 'viewer123',
        },
        {
            'name': 'Analyst User',
            'email': 'analyst@example.com',
            'role': UserRole.analyst,
            'status': UserStatus.active,
            'password': 'analyst123',
        },
        {
            'name': 'Inactive User',
            'email': 'inactive@example.com',
            'role': UserRole.viewer,
            'status': UserStatus.inactive,
            'password': 'inactive123',
        },
    ]

    users: dict[str, User] = {}
    for row in fixtures:
        existing = session.execute(select(User).where(User.email == row['email'])).scalar_one_or_none()
        if existing:
            users[row['email']] = existing
            continue
        user = User(
            name=row['name'],
            email=row['email'],
            role=row['role'],
            status=row['status'],
            password_hash=create_password_hash(row['password']),
        )
        session.add(user)
        session.flush()
        users[row['email']] = user

    return users


def seed_records(session, admin_user: User):
    if session.execute(select(FinancialRecord.id)).first():
        return

    records = [
        FinancialRecord(amount=Decimal('5000.00'), type=RecordType.income, category='salary', date=date(2025, 11, 10), notes='Monthly salary', created_by=admin_user.id),
        FinancialRecord(amount=Decimal('1200.00'), type=RecordType.expense, category='rent', date=date(2025, 11, 12), notes='Apartment rent', created_by=admin_user.id),
        FinancialRecord(amount=Decimal('400.50'), type=RecordType.expense, category='groceries', date=date(2025, 12, 3), notes='Supermarket', created_by=admin_user.id),
        FinancialRecord(amount=Decimal('2000.00'), type=RecordType.income, category='freelance', date=date(2025, 12, 15), notes='Client project', created_by=admin_user.id),
        FinancialRecord(amount=Decimal('6000.00'), type=RecordType.income, category='salary', date=date(2026, 1, 10), notes='Monthly salary', created_by=admin_user.id),
        FinancialRecord(amount=Decimal('1500.00'), type=RecordType.expense, category='rent', date=date(2026, 1, 12), notes='Apartment rent', created_by=admin_user.id),
        FinancialRecord(amount=Decimal('320.00'), type=RecordType.expense, category='utilities', date=date(2026, 2, 10), notes='Electricity and water', created_by=admin_user.id),
        FinancialRecord(amount=Decimal('6100.00'), type=RecordType.income, category='salary', date=date(2026, 2, 11), notes='Monthly salary', created_by=admin_user.id),
        FinancialRecord(amount=Decimal('210.00'), type=RecordType.expense, category='transport', date=date(2026, 3, 7), notes='Fuel and metro', created_by=admin_user.id),
        FinancialRecord(amount=Decimal('6200.00'), type=RecordType.income, category='salary', date=date(2026, 3, 10), notes='Monthly salary', created_by=admin_user.id),
        FinancialRecord(amount=Decimal('700.00'), type=RecordType.expense, category='insurance', date=date(2026, 4, 1), notes='Policy renewal', created_by=admin_user.id),
        FinancialRecord(amount=Decimal('1500.00'), type=RecordType.income, category='bonus', date=date(2026, 4, 2), notes='Performance bonus', created_by=admin_user.id),
    ]
    session.add_all(records)


def main() -> None:
    with SessionLocal() as session:
        users = seed_users(session)
        seed_records(session, users['admin@example.com'])
        session.commit()

    print('Seed complete.')
    print('Credentials:')
    print('admin@example.com / admin123')
    print('viewer@example.com / viewer123')
    print('analyst@example.com / analyst123')
    print('inactive@example.com / inactive123')


if __name__ == '__main__':
    main()
