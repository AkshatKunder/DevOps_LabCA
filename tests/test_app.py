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
    assert b"AI-Powered Online Quiz" in response.data


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


@patch("app.routes.generate_quiz")
def test_result_stores_valid_duration(mock_generate_quiz, client):
    mock_generate_quiz.return_value = SAMPLE_QUIZ

    client.post(
        "/generate",
        data={"topic": "Timed Topic", "difficulty": "Easy"},
    )

    response = client.post(
        "/result",
        data={
            "question_0": "2",
            "question_1": "1",
            "question_2": "1",
            "question_3": "3",
            "question_4": "1",
            "duration_seconds": "95",
        },
    )
    assert response.status_code == 200
    # Scoring is unchanged by the informational duration metadata.
    assert b"Score: 5 / 5" in response.data
    # Duration is displayed as MM:SS on the results page.
    assert b"01:35" in response.data
    assert b"Time taken" in response.data

    conn = database.get_db()
    attempt = conn.execute(
        "SELECT duration_seconds FROM quiz_attempts WHERE topic = ?",
        ("Timed Topic",),
    ).fetchone()
    conn.close()

    assert attempt is not None
    assert attempt["duration_seconds"] == 95


@patch("app.routes.generate_quiz")
def test_result_without_duration_renders_normally(mock_generate_quiz, client):
    mock_generate_quiz.return_value = SAMPLE_QUIZ

    client.post(
        "/generate",
        data={"topic": "No Timer Topic", "difficulty": "Easy"},
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
    assert b"Score: 5 / 5" in response.data
    assert b"Time taken" not in response.data

    conn = database.get_db()
    attempt = conn.execute(
        "SELECT duration_seconds FROM quiz_attempts WHERE topic = ?",
        ("No Timer Topic",),
    ).fetchone()
    conn.close()

    assert attempt is not None
    assert attempt["duration_seconds"] is None


@patch("app.routes.generate_quiz")
def test_result_rejects_invalid_duration_without_changing_score(
    mock_generate_quiz, client
):
    mock_generate_quiz.return_value = SAMPLE_QUIZ

    for bad_value in ("not-a-number", "-30", "99999999"):
        topic = f"Bad Duration {bad_value}"
        client.post(
            "/generate",
            data={"topic": topic, "difficulty": "Easy"},
        )

        response = client.post(
            "/result",
            data={
                "question_0": "2",
                "question_1": "1",
                "question_2": "1",
                "question_3": "3",
                "question_4": "1",
                "duration_seconds": bad_value,
            },
        )
        assert response.status_code == 200
        assert b"Score: 5 / 5" in response.data
        assert b"Time taken" not in response.data

        conn = database.get_db()
        attempt = conn.execute(
            "SELECT duration_seconds FROM quiz_attempts WHERE topic = ?",
            (topic,),
        ).fetchone()
        conn.close()

        assert attempt is not None
        assert attempt["duration_seconds"] is None


@patch("app.routes.generate_quiz")
def test_result_displays_long_duration_as_hours(mock_generate_quiz, client):
    mock_generate_quiz.return_value = SAMPLE_QUIZ

    client.post(
        "/generate",
        data={"topic": "Long Quiz", "difficulty": "Hard"},
    )

    response = client.post(
        "/result",
        data={
            "question_0": "2",
            "question_1": "1",
            "question_2": "1",
            "question_3": "3",
            "question_4": "1",
            "duration_seconds": "3700",
        },
    )
    assert response.status_code == 200
    assert b"01:01:40" in response.data


def test_init_db_migrates_old_schema_without_losing_history(test_db):
    import sqlite3

    conn = sqlite3.connect(test_db)
    conn.execute("DROP TABLE IF EXISTS quiz_attempts")
    conn.execute(
        """
        CREATE TABLE quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            percentage REAL NOT NULL,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    conn.execute(
        """
        INSERT INTO quiz_attempts
            (user_id, topic, difficulty, score, total_questions, percentage)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (1, "Legacy Topic", "Easy", 3, 5, 60.0),
    )
    conn.commit()
    conn.close()

    database.init_db()

    conn = database.get_db()
    columns = [
        row["name"]
        for row in conn.execute(
            "PRAGMA table_info(quiz_attempts)"
        ).fetchall()
    ]
    assert "duration_seconds" in columns

    row = conn.execute(
        "SELECT * FROM quiz_attempts WHERE topic = ?",
        ("Legacy Topic",),
    ).fetchone()
    conn.close()

    assert row is not None
    assert row["score"] == 3
    assert row["duration_seconds"] is None
