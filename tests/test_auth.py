def test_login_success(client, seeded_data):
    response = client.post('/api/v1/auth/login', json={'email': 'admin@test.com', 'password': 'admin123'})
    assert response.status_code == 200
    body = response.json()
    assert body['token_type'] == 'bearer'
    assert body['access_token']


def test_login_failure(client, seeded_data):
    response = client.post('/api/v1/auth/login', json={'email': 'admin@test.com', 'password': 'wrong'})
    assert response.status_code == 401
    assert response.json()['error']['code'] == 'unauthorized'


def test_protected_endpoint_without_token_returns_401(client, seeded_data):
    response = client.get('/api/v1/records')
    assert response.status_code == 401
