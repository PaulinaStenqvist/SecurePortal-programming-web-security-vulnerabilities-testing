
import re
import sqlite3

import pytest
import app as secure_app


def get_csrf_token(client, path):
    response = client.get(path)
    assert response.status_code == 200

    html = response.get_data(as_text=True)
    match = re.search(
        r'name="csrf_token"\s+value="([^"]+)"',
        html,
    )

    assert match is not None, "CSRF token not found in form"
    return match.group(1)


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"
    monkeypatch.setattr(secure_app, "DATABASE", test_db)

    with sqlite3.connect(test_db) as db:
        db.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            )
        """)

    secure_app.app.config.update(
        TESTING=True,
        SECRET_KEY="test-only-secret-key",
        WTF_CSRF_ENABLED=True,
    )

    with secure_app.app.test_client() as client:
        yield client


def test_dashboard_redirects_when_logged_out(client):
    response = client.get("/dashboard")

    assert response.status_code == 302
    assert "/login" in response.location


def test_login_page_is_available(client):
    response = client.get("/login")

    assert response.status_code == 200


def test_registration_page_is_available(client):
    response = client.get("/register")

    assert response.status_code == 200


def test_invalid_login_is_rejected(client):
    token = get_csrf_token(client, "/login")

    response = client.post(
        "/login",
        data={
            "username": "unknown-user",
            "password": "wrong-password",
            "csrf_token": token,
        },
    )

    assert response.status_code == 401


def test_registration_stores_hashed_password(client):
    token = get_csrf_token(client, "/register")

    response = client.post(
        "/register",
        data={
            "username": "securitytester",
            "password": "Correct-Horse-42!",
            "csrf_token": token,
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with sqlite3.connect(secure_app.DATABASE) as db:
        row = db.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            ("securitytester",),
        ).fetchone()

    assert row is not None
    assert row[0] != "Correct-Horse-42!"

    from werkzeug.security import check_password_hash

    assert check_password_hash(row[0], "Correct-Horse-42!")


def test_registered_user_can_log_in(client):
    register_token = get_csrf_token(client, "/register")

    client.post(
        "/register",
        data={
            "username": "login_tester",
            "password": "Correct-Horse-42!",
            "csrf_token": register_token,
        },
    )

    login_token = get_csrf_token(client, "/login")

    response = client.post(
        "/login",
        data={
            "username": "login_tester",
            "password": "Correct-Horse-42!",
            "csrf_token": login_token,
        },
    )

    assert response.status_code == 302
    assert "/dashboard" in response.location

    dashboard = client.get("/dashboard")

    assert dashboard.status_code == 200
    assert b"login_tester" in dashboard.data
def test_login_page_contains_csrf_token(client):
    response = client.get("/login")
    html = response.get_data(as_text=True)

    print(html)

    assert 'name="csrf_token"' in html