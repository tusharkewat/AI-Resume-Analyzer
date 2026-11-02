from starlette.testclient import TestClient


def test_register_success(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "New User",
            "email": "newuser@example.com",
            "password": "Password1234!"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["full_name"] == "New User"


def test_register_duplicate_email(client: TestClient, test_user_a):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Duplicate User",
            "email": test_user_a.email,
            "password": "Password1234!"
        }
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_success(client: TestClient, test_user_a):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_a.email,
            "password": "StrongPassword123!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == test_user_a.email


def test_login_invalid_password(client: TestClient, test_user_a):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_a.email,
            "password": "WrongPassword999!"
        }
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_get_current_user_me(client: TestClient, auth_headers_user_a, test_user_a):
    response = client.get("/api/v1/auth/me", headers=auth_headers_user_a)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user_a.id
    assert data["email"] == test_user_a.email


def test_unauthenticated_request(client: TestClient):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_update_profile(client: TestClient, auth_headers_user_a):
    response = client.put(
        "/api/v1/auth/me",
        headers=auth_headers_user_a,
        json={"full_name": "Alice Updated"}
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Alice Updated"


def test_change_password(client: TestClient, auth_headers_user_a, test_user_a):
    response = client.put(
        "/api/v1/auth/password",
        headers=auth_headers_user_a,
        json={
            "current_password": "StrongPassword123!",
            "new_password": "NewStrongPassword456!"
        }
    )
    assert response.status_code == 200

    # Verify new password works
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_a.email,
            "password": "NewStrongPassword456!"
        }
    )
    assert login_res.status_code == 200
