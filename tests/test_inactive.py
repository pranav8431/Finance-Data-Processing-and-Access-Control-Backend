def test_inactive_user_cannot_access_protected_resource(client, inactive_headers, seeded_data):
    response = client.get('/api/v1/records', headers=inactive_headers)
    assert response.status_code == 403
    assert response.json()['error']['code'] == 'forbidden'
