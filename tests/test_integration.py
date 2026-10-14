"""End-to-end integration tests for QuizGenius workflows."""

from unittest.mock import patch

import pytest
from werkzeug.security import generate_password_hash

from app import app
import app.database as database


INTEGRATION_QUIZ = [
    {
        "question": "Which command builds a Docker image?",
        "options": ["docker run", "docker build", "docker push", "docker ps"],
        "answer": 1,
        "explanation": "docker build creates an image from a Dockerfile.",
    },
    {
        "question": "What does CI stand for?",
        "options": [
            "Container Inspection",
            "Continuous Integration",
            "Code Isolation",
            "Cloud Instance",
        ],
        "answer": 1,
        "explanation": "CI stands for Continuous Integration.",
    },
]


@pytest.fixture
def integration_client(tmp_path, monkeypatch):
    """Provide a Flask client backed by an isolated SQLite database."""
    test_database = tmp_path / "integration_quiz.db"
    monkeypatch.setattr(database, "DATABASE", str(test_database))
    monkeypatch.setitem(app.config, "TESTING", True)
    monkeypatch.setitem(app.config, "SECRET_KEY", "integration-test-secret")
    database.init_db()
    return app.test_client()


def _register_and_login(client, username="integration_user", email="user@example.com"):
    """Exercise the real registration and login routes for a test user."""
    registration = client.post(
        "/register",
        data={
            "username": username,
            "email": email,
            "password": "SecurePassword123",
        },
    )
    assert registration.status_code == 302

    login = client.post(
        "/login",
        data={"email": email, "password": "SecurePassword123"},
    )
    assert login.status_code == 302


def test_registration_validation_does_not_persist_invalid_user(integration_client):
    response = integration_client.post(
        "/register",
        data={"username": "", "email": "", "password": "short"},
    )

    assert response.status_code == 200
    assert b"Please fill in all fields" in response.data

    conn = database.get_db()
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    assert user_count == 0


def test_authentication_protects_dashboard_then_allows_logged_in_user(integration_client):
    protected_response = integration_client.get("/dashboard")
    assert protected_response.status_code == 302
    assert "/login" in protected_response.location

    _register_and_login(integration_client)
    dashboard_response = integration_client.get("/dashboard")

    assert dashboard_response.status_code == 200
    assert b"No quiz history yet" in dashboard_response.data


@patch("app.routes.generate_quiz", return_value=INTEGRATION_QUIZ)
def test_quiz_submission_persists_attempt_and_dashboard_retrieves_it(
    mock_generate_quiz, integration_client
):
    _register_and_login(integration_client)

    generated = integration_client.post(
        "/generate",
        data={"topic": "Docker", "difficulty": "Medium"},
    )
    assert generated.status_code == 200
    mock_generate_quiz.assert_called_once_with("Docker", "Medium")

    submitted = integration_client.post(
        "/result",
        data={"question_0": "1", "question_1": "1", "duration_seconds": "42"},
    )
    assert submitted.status_code == 200
    assert b"Score: 2 / 2" in submitted.data

    conn = database.get_db()
    attempt = conn.execute(
        """
        SELECT topic, difficulty, score, total_questions, percentage, duration_seconds
        FROM quiz_attempts
        """
    ).fetchone()
    conn.close()

    assert tuple(attempt) == ("Docker", "Medium", 2, 2, 100.0, 42)

    dashboard = integration_client.get("/dashboard")
    assert dashboard.status_code == 200
    assert b"Docker" in dashboard.data
    assert b"100.0%" in dashboard.data


def test_dashboard_does_not_expose_another_users_attempts(integration_client):
    _register_and_login(integration_client, "first_user", "first@example.com")

    conn = database.get_db()
    first_user = conn.execute(
        "SELECT id FROM users WHERE email = ?", ("first@example.com",)
    ).fetchone()
    conn.execute(
        """
        INSERT INTO quiz_attempts
            (user_id, topic, difficulty, score, total_questions, percentage)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (first_user["id"], "Visible Topic", "Easy", 4, 5, 80.0),
    )
    conn.execute(
        """
        INSERT INTO users (username, email, password_hash)
        VALUES (?, ?, ?)
        """,
        ("second_user", "second@example.com", generate_password_hash("Password123")),
    )
    second_user = conn.execute(
        "SELECT id FROM users WHERE email = ?", ("second@example.com",)
    ).fetchone()
    conn.execute(
        """
        INSERT INTO quiz_attempts
            (user_id, topic, difficulty, score, total_questions, percentage)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (second_user["id"], "Private Topic", "Hard", 1, 5, 20.0),
    )
    conn.commit()
    conn.close()

    dashboard = integration_client.get("/dashboard")
    assert dashboard.status_code == 200
    assert b"Visible Topic" in dashboard.data
    assert b"Private Topic" not in dashboard.data
