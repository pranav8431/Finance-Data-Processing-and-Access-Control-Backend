from collections import defaultdict
from datetime import date
from decimal import Decimal


def test_dashboard_summary_totals_and_net(client, admin_headers, seeded_data):
    response = client.get('/api/v1/dashboard/summary', headers=admin_headers)
    assert response.status_code == 200
    body = response.json()

    expected_income = Decimal('6300.00')
    expected_expense = Decimal('1150.00')
    expected_net = expected_income - expected_expense

    assert Decimal(body['total_income']) == expected_income
    assert Decimal(body['total_expenses']) == expected_expense
    assert Decimal(body['net_balance']) == expected_net


def test_dashboard_monthly_trends_shape_and_values(client, admin_headers, seeded_data):
    response = client.get('/api/v1/dashboard/summary', headers=admin_headers)
    assert response.status_code == 200
    body = response.json()

    trends = body['monthly_trends']
    assert len(trends) == 6

    month_map = defaultdict(lambda: {'income': Decimal('0.00'), 'expense': Decimal('0.00')})
    for record in seeded_data['records']:
        key = record.date.replace(day=1).isoformat()
        if record.type.value == 'income':
            month_map[key]['income'] += record.amount
        else:
            month_map[key]['expense'] += record.amount

    for row in trends:
        month = row['month']
        income = Decimal(row['income'])
        expense = Decimal(row['expense'])
        net = Decimal(row['net'])

        assert income == month_map[month]['income']
        assert expense == month_map[month]['expense']
        assert net == income - expense
