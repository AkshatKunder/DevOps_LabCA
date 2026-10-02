# DevOps Theory IA

## Interactive DevOps Theory Application

This project provides an interactive web application for learning and testing DevOps theory concepts.

### Features

- **Quiz**: Test your knowledge with DevOps theory questions
- **Results**: View your quiz performance and scores
- **Responsive Design**: Works on desktop and mobile devices

### Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python run.py
   ```

3. Open your browser and visit `http://localhost:5000`

### Tech Stack

- **Flask**: Web framework
- **HTML5/CSS3/JavaScript**: Frontend
- **Testing**: Python unit tests

### Project Structure

```
app/              # Python application code
├── __init__.py
├── routes.py      # URL routing
├── quiz.py        # Quiz logic
└── ai.py          # AI integration

templates/        # HTML templates
├── index.html     # Home page
├── quiz.html      # Quiz page
└── result.html    # Result page

static/           # Static assets
├── css/style.css  # Styles
└── js/script.js   # Client-side script

tests/            # Test suite
└── test_app.py    # Unit tests

.gitignore        # Git ignore rules
requirements.txt  # Python dependencies
run.py            # Application entry point
Dockerfile        # Docker configuration
Jenkinsfile       # CI/CD pipeline
```

### License

MIT