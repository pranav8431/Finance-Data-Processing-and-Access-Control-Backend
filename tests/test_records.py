from datetime import date


def test_filter_by_type_and_category(client, admin_headers, seeded_data):
    response = client.get('/api/v1/records?type=expense&category=rent', headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert body['total'] >= 1
    assert all(item['type'] == 'expense' and item['category'] == 'rent' for item in body['items'])


def test_filter_by_date_range(client, admin_headers, seeded_data):
    start = date.today().replace(day=1).isoformat()
    end = date.today().isoformat()
    response = client.get(f'/api/v1/records?start_date={start}&end_date={end}', headers=admin_headers)
    assert response.status_code == 200
    items = response.json()['items']
    assert all(start <= item['date'] <= end for item in items)


def test_pagination_and_deterministic_order(client, admin_headers, seeded_data):
    first = client.get('/api/v1/records?limit=3&offset=0', headers=admin_headers)
    second = client.get('/api/v1/records?limit=3&offset=3', headers=admin_headers)

    assert first.status_code == 200
    assert second.status_code == 200

    first_items = first.json()['items']
    second_items = second.json()['items']

    assert len(first_items) == 3
    assert len(second_items) == 3

    first_ids = [item['id'] for item in first_items]
    second_ids = [item['id'] for item in second_items]
    assert set(first_ids).isdisjoint(second_ids)

    ordered = first_items + second_items
    sorted_copy = sorted(ordered, key=lambda r: (r['date'], r['id']), reverse=True)
    assert ordered == sorted_copy
