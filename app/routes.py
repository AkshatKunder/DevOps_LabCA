"""Routing for the AI-Powered Online Quiz application."""

from flask import Blueprint, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from app.ai import generate_quiz
from app.database import get_db

main = Blueprint("main", __name__)


def _format_answer(index, options):
    """Return a human-readable answer label."""
    if index is None or index < 0 or index >= len(options):
        return "No answer selected"
    return options[index]


@main.route("/")
@login_required
def home():
    """Display the LoanEase financial assistant."""
    return render_template("index.html", chat_mode=True)


@main.route("/generate", methods=["POST"])
@login_required
def generate():
    """Generate a quiz from the submitted topic and difficulty."""
    topic = request.form.get("topic", "").strip()
    difficulty = request.form.get("difficulty", "")

    if not topic:
        return "Topic is required. Please enter a topic and try again.", 400

    try:
        quiz = generate_quiz(topic, difficulty)

        if not quiz:
            return "No questions were generated. Please try again.", 500
    except Exception:
        return (
            "We were unable to generate the quiz right now. "
            "Please check the Gemini API configuration and try again."
        ), 500

    session["quiz"] = {
        "topic": topic,
        "difficulty": difficulty,
        "questions": quiz,
    }

    return render_template(
        "quiz.html",
        quiz=quiz,
        topic=topic,
        difficulty=difficulty,
    )


@main.route("/result", methods=["POST"])
@login_required
def result():
    """Calculate the score, save the attempt, and display the result."""
    quiz_data = session.get("quiz")

    if not quiz_data:
        return redirect(url_for("main.home"))

    questions = quiz_data["questions"]
    score = 0
    results = []

    for index, question in enumerate(questions):
        user_answer = request.form.get(f"question_{index}")

        try:
            user_answer = int(user_answer)
        except (TypeError, ValueError):
            user_answer = None

        if user_answer == question["answer"]:
            score += 1

        results.append(
            {
                "question": question["question"],
                "options": question["options"],
                "user_answer_text": _format_answer(user_answer, question["options"]),
                "correct_answer_text": question["options"][question["answer"]],
                "explanation": question["explanation"],
            }
        )

    total = len(questions)
    percentage = round(score / total * 100, 1) if total else 0

    conn = get_db()
    try:
        conn.execute(
            """
            INSERT INTO quiz_attempts
                (user_id, topic, difficulty, score,
                 total_questions, percentage)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                int(current_user.id),
                quiz_data["topic"],
                quiz_data["difficulty"],
                score,
                total,
                percentage,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    session.pop("quiz", None)

    return render_template(
        "result.html",
        topic=quiz_data["topic"],
        difficulty=quiz_data["difficulty"],
        score=score,
        total=total,
        percentage=percentage,
        results=results,
    )


@main.route("/dashboard")
@login_required
def dashboard():
    """Display quiz history for the logged-in user."""
    conn = get_db()

    try:
        attempts = conn.execute(
            """
            SELECT topic, difficulty, score, total_questions,
                   percentage, attempted_at
            FROM quiz_attempts
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (int(current_user.id),),
        ).fetchall()
    finally:
        conn.close()

    total_attempts = len(attempts)

    average_percentage = (
        round(sum(row["percentage"] for row in attempts) / total_attempts, 1)
        if total_attempts
        else 0
    )

    return render_template(
        "dashboard.html",
        attempts=attempts,
        total_attempts=total_attempts,
        average_percentage=average_percentage,
    )
