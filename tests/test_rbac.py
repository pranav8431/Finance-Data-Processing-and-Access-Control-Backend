def test_viewer_cannot_create_record(client, viewer_headers, seeded_data):
    payload = {'amount': '10.00', 'type': 'income', 'category': 'misc', 'date': '2026-01-01', 'notes': 'test'}
    response = client.post('/api/v1/records', json=payload, headers=viewer_headers)
    assert response.status_code == 403


def test_analyst_cannot_write_records(client, analyst_headers, seeded_data):
    create_payload = {'amount': '10.00', 'type': 'income', 'category': 'misc', 'date': '2026-01-01', 'notes': 'test'}
    create_res = client.post('/api/v1/records', json=create_payload, headers=analyst_headers)
    assert create_res.status_code == 403

    update_res = client.patch('/api/v1/records/1', json={'notes': 'updated'}, headers=analyst_headers)
    assert update_res.status_code == 403

    delete_res = client.delete('/api/v1/records/1', headers=analyst_headers)
    assert delete_res.status_code == 403


def test_admin_can_write_records(client, admin_headers, seeded_data):
    payload = {'amount': '50.00', 'type': 'expense', 'category': 'ops', 'date': '2026-01-01', 'notes': 'admin write'}
    create_res = client.post('/api/v1/records', json=payload, headers=admin_headers)
    assert create_res.status_code == 201
    record_id = create_res.json()['id']

    update_res = client.patch(f'/api/v1/records/{record_id}', json={'notes': 'updated by admin'}, headers=admin_headers)
    assert update_res.status_code == 200

    delete_res = client.delete(f'/api/v1/records/{record_id}', headers=admin_headers)
    assert delete_res.status_code == 204


def test_non_admin_cannot_access_user_management(client, viewer_headers, seeded_data):
    response = client.get('/api/v1/users', headers=viewer_headers)
    assert response.status_code == 403
