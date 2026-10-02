"""Automated tests for the AI-Powered Online Quiz application.

All tests use pytest and mock Gemini, so no real API quota is consumed.
"""
from unittest.mock import patch

import pytest

from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key-change-in-production"
    return app.test_client()


# A valid quiz response that Gemini might return.
SAMPLE_QUIZ = [
    {
        "question": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Madrid"],
        "answer": 2,
        "explanation": "Paris is the capital and most populous city of France.",
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
        "explanation": "Mars appears red due to iron oxide on its surface.",
    },
    {
        "question": "What is the largest ocean on Earth?",
        "options": ["Atlantic", "Indian", "Arctic", "Pacific"],
        "answer": 3,
        "explanation": "The Pacific Ocean is the largest and deepest ocean.",
    },
    {
        "question": "Who wrote 'Romeo and Juliet'?",
        "options": ["Charles Dickens", "William Shakespeare", "Mark Twain", "Jane Austen"],
        "answer": 1,
        "explanation": "William Shakespeare wrote Romeo and Juliet.",
    },
]


def test_homepage_returns_200(client):
    """The homepage should return HTTP 200."""
    response = client.get("/")
    assert response.status_code == 200


def test_homepage_contains_title(client):
    """The homepage should contain the quiz title."""
    response = client.get("/")
    assert "AI-Powered Online Quiz" in response.data.decode("utf-8")


def test_generate_rejects_empty_topic(client):
    """POST /generate with an empty topic should be rejected."""
    response = client.post("/generate", data={"topic": "", "difficulty": "Easy"})
    assert response.status_code == 400

    response = client.post("/generate", data={"topic": "   ", "difficulty": "Easy"})
    assert response.status_code == 400


@patch("app.routes.generate_quiz")
def test_generate_generates_quiz(mock_generate_quiz, client):
    """POST /generate calls Gemini and displays the quiz page."""
    mock_generate_quiz.return_value = SAMPLE_QUIZ

    response = client.post(
        "/generate", data={"topic": "Operating Systems", "difficulty": "Medium"}
    )
    assert response.status_code == 200
    # The quiz page should list the 5 generated questions.
    for item in SAMPLE_QUIZ:
        assert item["question"] in response.data.decode("utf-8")


@patch("app.routes.generate_quiz")
def test_result_calculates_score_correctly(mock_generate_quiz, client):
    """The /result route calculates the score correctly."""
    mock_generate_quiz.return_value = SAMPLE_QUIZ

    # Answer all 5 correctly: indices 2, 1, 1, 3, 1
    answers = {
        "question_0": "2",
        "question_1": "1",
        "question_2": "1",
        "question_3": "3",
        "question_4": "1",
    }

    response = client.post("/generate", data={"topic": "Test", "difficulty": "Easy"})
    assert response.status_code == 200

    response = client.post("/result", data=answers)
    assert response.status_code == 200

    response_text = response.data.decode("utf-8")
    assert "Score: 5 / 5" in response_text
    assert "100.0%" in response_text


@patch("app.routes.generate_quiz")
def test_result_scores_unanswered_as_wrong(mock_generate_quiz, client):
    """An unanswered question should not be counted as correct."""
    mock_generate_quiz.return_value = SAMPLE_QUIZ

    # Submit nothing
    response = client.post("/generate", data={"topic": "Test", "difficulty": "Easy"})
    assert response.status_code == 200

    response = client.post("/result", data={})
    assert response.status_code == 200

    response_text = response.data.decode("utf-8")
    assert "Score: 0 / 5" in response_text
    assert "No answer selected" in response_text


@patch("app.routes.generate_quiz")
def test_quiz_page_shows_topic_and_difficulty(mock_generate_quiz, client):
    """The quiz page displays the selected topic and difficulty."""
    mock_generate_quiz.return_value = SAMPLE_QUIZ

    response = client.post(
        "/generate", data={"topic": "Operating Systems", "difficulty": "Medium"}
    )
    assert response.status_code == 200

    response_text = response.data.decode("utf-8")
    assert "Operating Systems" in response_text
    assert "Medium" in response_text


@patch("app.routes.generate_quiz")
def test_quiz_has_radio_buttons(mock_generate_quiz, client):
    """Each option should have a radio button."""
    mock_generate_quiz.return_value = SAMPLE_QUIZ

    response = client.post(
        "/generate", data={"topic": "Test", "difficulty": "Easy"}
    )
    assert response.status_code == 200

    response_text = response.data.decode("utf-8")
    # Should have 5 * 4 = 20 radio inputs.
    assert response_text.count('<input type="radio"') == 20


def test_result_without_session_redirects(client):
    """POST /result without a quiz in the session redirects to home."""
    response = client.post("/result")
    assert response.status_code == 302  # redirect