"""Routing for the AI-Powered Online Quiz application."""
from flask import Blueprint, render_template, request, session, redirect, url_for
from app.ai import generate_quiz

main = Blueprint("main", __name__)


def _format_answer(index, options):
    """Return a human-readable answer label for the result page."""
    if index is None or index < 0 or index >= len(options):
        return "No answer selected"
    return options[index]


@main.route("/")
def home():
    """Display the quiz generation form."""
    return render_template("index.html")


@main.route("/generate", methods=["POST"])
def generate():
    """Generate a quiz from the submitted topic and difficulty."""
    topic = request.form.get("topic")
    difficulty = request.form.get("difficulty")

    # 1. Validate that the topic is not empty
    if not topic or not topic.strip():
        return "Topic is required. Please enter a topic and try again.", 400

    # 2. Call Gemini via the AI service
    try:
        quiz = generate_quiz(topic, difficulty)
    except Exception as error:
        # 3. Do not expose the API key. Return a friendly error instead.
        return (
            "We were unable to generate the quiz right now. "
            "Please check that the Gemini API key is set in .env and try again."
        ), 500

    # 4. Save the generated quiz on the server (session) so that the
    #    correct answers stay server-side, not in the HTML form.
    session["quiz"] = {
        "topic": topic,
        "difficulty": difficulty,
        "questions": quiz,
    }

    # 5. Display the quiz page
    return render_template(
        "quiz.html",
        quiz=quiz,
        topic=topic,
        difficulty=difficulty,
    )


@main.route("/result", methods=["POST"])
def result():
    """Calculate the score and display the result page."""
    quiz_data = session.get("quiz")
    if not quiz_data:
        return redirect(url_for("main.home"))

    questions = quiz_data["questions"]
    score = 0
    results = []

    for index, question in enumerate(questions):
        # Get the user's submitted answer
        user_answer = request.form.get(f"question_{index}")
        try:
            user_answer = int(user_answer)
        except (TypeError, ValueError):
            user_answer = None

        # Compare with the correct answer stored on the server
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

    # Clear the quiz from the session after submission
    session.pop("quiz", None)

    return render_template(
        "result.html",
        topic=quiz_data["topic"],
        difficulty=quiz_data["difficulty"],
        score=score,
        total=len(questions),
        percentage=round(score / len(questions) * 100, 1),
        results=results,
    )