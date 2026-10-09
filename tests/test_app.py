"""Automated tests for the AI-Powered Online Quiz application."""

from markupsafe import escape
from unittest.mock import patch

import pytest
from werkzeug.security import generate_password_hash

from app import app
import app.database as database


SAMPLE_QUIZ = [
    {
        "question": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Madrid"],
        "answer": 2,
        "explanation": "Paris is the capital of France.",
    },
    {
        "question": "What is 2 + 2?",
        "options": ["3", "4", "5", "6"],
        "answer": 1,
        "explanation": "Two plus two equals four.",
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Saturn"],
        "answer": 1,
        "explanation": "Mars appears red due to iron oxide.",
    },
    {
        "question": "What is the largest ocean on Earth?",
        "options": ["Atlantic", "Indian", "Arctic", "Pacific"],
        "answer": 3,
        "explanation": "The Pacific Ocean is the largest.",
    },
    {
        "question": "Who wrote Romeo and Juliet?",
        "options": [
            "Charles Dickens",
            "William Shakespeare",
            "Mark Twain",
            "Jane Austen",
        ],
        "answer": 1,
        "explanation": "William Shakespeare wrote Romeo and Juliet.",
    },
]


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Use an isolated temporary database for each test."""
    test_database = tmp_path / "test_quiz.db"
    monkeypatch.setattr(database, "DATABASE", str(test_database))
    database.init_db()
    return str(test_database)


@pytest.fixture
def anonymous_client(test_db):
    """Create a client without logging in."""
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"
    return app.test_client()


@pytest.fixture
def client(anonymous_client):
    """Create a client logged in as a test user."""
    anonymous_client.post(
        "/register",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123",
        },
    )

    response = anonymous_client.post(
        "/login",
        data={
            "email": "test@example.com",
            "password": "TestPassword123",
        },
    )
    assert response.status_code == 302

    return anonymous_client


def test_registration_creates_user(anonymous_client):
    response = anonymous_client.post(
        "/register",
        data={
            "username": "alice",
            "email": "alice@example.com",
            "password": "Password123",
        },
    )
    assert response.status_code == 302

    conn = database.get_db()
    user = conn.execute(
        "SELECT username, email, password_hash FROM users WHERE email = ?",
        ("alice@example.com",),
    ).fetchone()
    conn.close()

    assert user is not None
    assert user["username"] == "alice"
    assert user["password_hash"] != "Password123"


def test_duplicate_registration_is_rejected(anonymous_client):
    data = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "Password123",
    }

    anonymous_client.post("/register", data=data)
    response = anonymous_client.post("/register", data=data)

    assert response.status_code == 200
    assert b"already registered" in response.data


def test_login_rejects_invalid_password(anonymous_client):
    anonymous_client.post(
        "/register",
        data={
            "username": "alice",
            "email": "alice@example.com",
            "password": "Password123",
        },
    )

    response = anonymous_client.post(
        "/login",
        data={
            "email": "alice@example.com",
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_homepage_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_homepage_contains_title(client):
    response = client.get("/")
    assert b"QuizGenius" in response.data


def test_logged_out_user_cannot_access_dashboard(anonymous_client):
    response = anonymous_client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.location


def test_generate_rejects_empty_topic(client):
    response = client.post(
        "/generate",
        data={"topic": "", "difficulty": "Easy"},
    )
    assert response.status_code == 400

    response = client.post(
        "/generate",
        data={"topic": "   ", "difficulty": "Easy"},
    )
    assert response.status_code == 400


@patch("app.routes.generate_quiz")
def test_generate_generates_quiz(mock_generate_quiz, client):
    mock_generate_quiz.return_value = SAMPLE_QUIZ

    response = client.post(
        "/generate",
        data={"topic": "Operating Systems", "difficulty": "Medium"},
    )

    assert response.status_code == 200
    response_text = response.data.decode("utf-8")

    for item in SAMPLE_QUIZ:
        assert str(escape(item["question"])) in response_text


@patch("app.routes.generate_quiz")
def test_result_calculates_score_correctly(mock_generate_quiz, client):
    mock_generate_quiz.return_value = SAMPLE_QUIZ

    answers = {
        "question_0": "2",
        "question_1": "1",
        "question_2": "1",
        "question_3": "3",
        "question_4": "1",
    }

    response = client.post(
        "/generate",
        data={"topic": "Test", "difficulty": "Easy"},
    )
    assert response.status_code == 200

    response = client.post("/result", data=answers)
    assert response.status_code == 200
    assert b"Score: 5 / 5" in response.data
    assert b"100.0%" in response.data


@patch("app.routes.generate_quiz")
def test_result_scores_unanswered_as_wrong(mock_generate_quiz, client):
    mock_generate_quiz.return_value = SAMPLE_QUIZ

    response = client.post(
        "/generate",
        data={"topic": "Test", "difficulty": "Easy"},
    )
    assert response.status_code == 200

    response = client.post("/result", data={})
    assert response.status_code == 200
    assert b"Score: 0 / 5" in response.data
    assert b"No answer selected" in response.data


@patch("app.routes.generate_quiz")
def test_quiz_page_shows_topic_and_difficulty(mock_generate_quiz, client):
    mock_generate_quiz.return_value = SAMPLE_QUIZ

    response = client.post(
        "/generate",
        data={"topic": "Operating Systems", "difficulty": "Medium"},
    )

    assert response.status_code == 200
    assert b"Operating Systems" in response.data
    assert b"Medium" in response.data


@patch("app.routes.generate_quiz")
def test_quiz_has_radio_buttons(mock_generate_quiz, client):
    mock_generate_quiz.return_value = SAMPLE_QUIZ

    response = client.post(
        "/generate",
        data={"topic": "Test", "difficulty": "Easy"},
    )

    assert response.status_code == 200
    assert response.data.count(b'type="radio"') == 20


@patch("app.routes.generate_quiz")
def test_result_is_saved_to_database(mock_generate_quiz, client):
    mock_generate_quiz.return_value = SAMPLE_QUIZ

    client.post(
        "/generate",
        data={"topic": "Python", "difficulty": "Easy"},
    )

    response = client.post(
        "/result",
        data={
            "question_0": "2",
            "question_1": "1",
            "question_2": "1",
            "question_3": "3",
            "question_4": "1",
        },
    )
    assert response.status_code == 200

    conn = database.get_db()
    attempt = conn.execute(
        "SELECT * FROM quiz_attempts WHERE topic = ?",
        ("Python",),
    ).fetchone()
    conn.close()

    assert attempt is not None
    assert attempt["score"] == 5
    assert attempt["total_questions"] == 5
    assert attempt["percentage"] == 100.0


def test_users_only_see_their_own_quiz_history(client, test_db):
    # Save an attempt for the first user.
    conn = database.get_db()
    first_user = conn.execute(
        "SELECT id FROM users WHERE email = ?",
        ("test@example.com",),
    ).fetchone()

    conn.execute(
        """
        INSERT INTO quiz_attempts
            (user_id, topic, difficulty, score, total_questions, percentage)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (first_user["id"], "First User Topic", "Easy", 4, 5, 80.0),
    )

    # Create a second user and an attempt belonging to that user.
    conn.execute(
        """
        INSERT INTO users (username, email, password_hash)
        VALUES (?, ?, ?)
        """,
        (
            "seconduser",
            "second@example.com",
            generate_password_hash("SecondPassword123"),
        ),
    )
    second_user = conn.execute(
        "SELECT id FROM users WHERE email = ?",
        ("second@example.com",),
    ).fetchone()

    conn.execute(
        """
        INSERT INTO quiz_attempts
            (user_id, topic, difficulty, score, total_questions, percentage)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (second_user["id"], "Second User Topic", "Medium", 2, 5, 40.0),
    )
    conn.commit()
    conn.close()

    # The first user's dashboard must not expose the second user's topic.
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"First User Topic" in response.data
    assert b"Second User Topic" not in response.data


def test_result_without_session_redirects(client):
    response = client.post("/result")
    assert response.status_code == 302
