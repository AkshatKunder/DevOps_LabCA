"""Gemini quiz generation service using google-genai."""
from google import genai
from dotenv import load_dotenv
import json
import os

# Load environment variables from .env
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not configured. Please set it in your .env file."
    )

# Initialize the Gemini client using the official google-genai SDK
CLIENT = genai.Client(api_key=API_KEY)

# Use the Gemini Flash-Lite model available on the free tier
MODEL = "gemini-2.0-flash-lite-001"


def generate_quiz(topic, difficulty, number_of_questions=5):
    """Generate multiple-choice questions using Gemini.

    Args:
        topic: The quiz topic (e.g. 'Operating Systems').
        difficulty: The difficulty level ('Easy', 'Medium', 'Hard').
        number_of_questions: How many questions to generate (default 5).

    Returns:
        A list of question dictionaries.

    Raises:
        ValueError: If the Gemini response is invalid.
    """
    prompt = (
        f"You are an expert quiz generator. Create exactly {number_of_questions} "
        f"multiple-choice questions about '{topic}' at {difficulty} difficulty. "
        "Return ONLY valid JSON. Do not include Markdown, code fences, or any extra text. "
        "Each question must have exactly 4 options and an 'answer' that is an integer from 0 to 3.\n\n"
        "Here is the exact JSON format to return:\n"
        "[\n"
        '    {\n'
        '        "question": "Question text",\n'
        '        "options": ["Option A", "Option B", "Option C", "Option D"],\n'
        '        "answer": 0,\n'
        '        "explanation": "Short explanation"\n'
        '    }\n'
        "]"
    )

    # Call the Gemini API
    response = CLIENT.models.generate_content(
        model=MODEL,
        contents=prompt,
        generation_config={"response_mime_type": "application/json"},
    )

    raw_text = response.candidates[0].content.parts[0].text.strip()

    # Remove markdown code fences if Gemini included them
    raw_text = _strip_code_fences(raw_text)

    # Parse the JSON response safely
    try:
        questions = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise ValueError(
            "Gemini returned invalid JSON. Please try again."
        ) from error

    # Validate the generated quiz
    return _validate_quiz(questions, number_of_questions)


def _strip_code_fences(text):
    """Remove surrounding markdown code fences from a string."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`").strip()
    if text.lower().startswith("json"):
        text = text[4:].strip()
    return text


def _validate_quiz(questions, expected_count):
    """Validate that Gemini returned the expected quiz structure."""
    if not isinstance(questions, list):
        raise ValueError(
            "Gemini returned invalid data: expected a list of questions."
        )

    if len(questions) != expected_count:
        raise ValueError(
            f"Gemini returned {len(questions)} questions but {expected_count} were requested."
        )

    for index, question in enumerate(questions, start=1):
        if not isinstance(question, dict):
            raise ValueError(f"Question {index} is not a valid question object.")

        required_keys = {"question", "options", "answer", "explanation"}
        if set(question.keys()) != required_keys:
            raise ValueError(
                f"Question {index} is missing required keys (question, options, answer, explanation)."
            )

        if not question["question"] or not isinstance(question["question"], str):
            raise ValueError(f"Question {index} has no question text.")

        if not isinstance(question["options"], list) or len(question["options"]) != 4:
            raise ValueError(f"Question {index} must have exactly 4 options.")

        if not isinstance(question["answer"], int) or question["answer"] not in (0, 1, 2, 3):
            raise ValueError(f"Question {index} answer must be an integer from 0 to 3.")

        if not question["explanation"] or not isinstance(question["explanation"], str):
            raise ValueError(f"Question {index} has no explanation.")

    return questions