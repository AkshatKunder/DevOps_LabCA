# QuizGenius — AI-Powered Online Quiz

## About the project

QuizGenius is an interactive Flask web application for generating, taking, and reviewing AI-powered quiz questions. Users can register, log in, generate quizzes on any topic with a chosen difficulty, take the quiz, and view their results along with a history of past attempts on their personal dashboard.

### Key features

- **AI-generated quizzes**: Generate quiz questions on any topic and difficulty using the Gemini API.
- **User authentication**: Register, log in, and manage your own quiz sessions securely.
- **Quiz history**: View past attempts, scores, and durations on your personal dashboard.
- **Responsive UI**: Works on desktop and mobile devices.
- **Containerized**: Runs locally via Python or as a Docker image.
- **CI/CD ready**: Jenkins pipeline with unit/integration tests, SonarQube static analysis, Trivy security scanning, and Docker deployment.

## How to start and load the project

### Option 1 — Run locally with Python

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd DevOps_LabCA_pipeline
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Copy the example file and fill in your values:

   ```bash
   copy .env.example .env        # Windows
   cp .env.example .env          # macOS / Linux
   ```

   Edit `.env` and set:
   - `GEMINI_API_KEY` — your Gemini API key (get one at https://aistudio.google.com/apikey)
   - `FLASK_SECRET_KEY` — a random secret for Flask sessions (change in production)

5. **Start the application**

   ```bash
   python run.py
   ```

6. **Open the app**

   Visit `http://localhost:5000` in your browser. Register a new account, then log in to generate and take quizzes.

### Option 2 — Run with Docker

1. **Build the image**

   ```bash
   docker build -t quizgenius:latest .
   ```

2. **Run the container**

   ```bash
   docker run -d --name quizgenius -p 5000:5000 -e GEMINI_API_KEY=your-key -e FLASK_SECRET_KEY=your-secret quizgenius:latest
   ```

3. **Open the app**

   Visit `http://localhost:5000`.

## Project structure

```
app/              # Python application code
├── __init__.py   # Flask app factory and extensions
├── ai.py         # AI quiz generation (Gemini)
├── auth.py       # Authentication blueprint (login/register)
├── database.py   # SQLite database helpers
├── quiz.py       # Quiz constants
└── routes.py     # URL routes (home, generate, result, dashboard)

templates/        # HTML templates
├── base.html     # Base layout
├── index.html    # Quiz generation form
├── quiz.html     # Quiz page
├── result.html   # Quiz result page
├── dashboard.html # Quiz history dashboard
├── login.html    # Login page
└── register.html # Registration page

static/           # Static assets
├── css/style.css # Styles
└── js/script.js  # Client-side script

tests/            # Test suite
├── test_app.py           # Unit tests
└── test_integration.py   # Integration tests

quality/          # Quality gate helper scripts
docs/             # Project documentation

.dockerignore     # Docker ignore rules
Dockerfile        # Docker image definition
Jenkinsfile       # CI/CD pipeline
run.py            # Application entry point
requirements.txt  # Python dependencies
sonar-project.properties  # SonarQube configuration
```

## Tech stack

- **Flask** — Web framework
- **Flask-Login** — User session management
- **SQLite** — Application database
- **Gemini API** — AI quiz question generation
- **HTML5/CSS3/JavaScript** — Frontend
- **pytest** — Unit and integration testing
- **Docker** — Containerization
- **Jenkins** — CI/CD pipeline
- **SonarQube** — Static code analysis
- **Trivy** — Container security scanning

## CI/CD pipeline

The `Jenkinsfile` defines the following stages:

1. **Build** — Install Python dependencies
2. **Unit Tests** — Run `tests/test_app.py`
3. **Integration Tests** — Run `tests/test_integration.py`
4. **SonarQube Analysis** — Static analysis with the Sonar Scanner
5. **SonarQube Quality Gate** — Fail the build if the quality gate is not OK
6. **Docker Build** — Build the application image
7. **Trivy Security Scan** — Vulnerability scan on the Docker image
8. **Deploy** — Run the container on port 5000

## License

MIT