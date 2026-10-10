# QuizForge AI — IDE Agent Prompts

These prompts are designed for Antigravity, Cursor, Windsurf, Copilot Agent, or another repository-aware IDE agent. Place `design.md` at the repository root and provide the four supplied QuizForge AI reference screenshots as visual context. Run the staged prompts in order.

## Prompt 1 — Audit before editing

You are a senior full-stack engineer working in the existing QuizForge AI Flask repository. Read `design.md` completely and inspect the repository before changing any files.

**Visual priority:** the supplied screenshots define the canonical LIGHT theme. Reproduce their mint canvas, white cards, dark-green buttons/active navigation, Inter typography, rounded cards, soft borders/shadows, spacing, and page hierarchy. Implement the coordinated dark theme specified in `design.md` as an additional theme. Do not use the attached Developer Assessment Engine/coding-workspace style as the default. Do not add a code editor, terminal, split-pane coding interface, neon-glow buttons, or JetBrains Mono as the general UI font.

Inspect `app/__init__.py`, routes, auth, database module, `ai.py`, all templates/static assets, tests, `requirements.txt`, `.gitignore`, `Dockerfile`, and `Jenkinsfile`. Map each screenshot/page to actual routes, template variables, schema fields, and current quiz session lifecycle. Identify missing features and data that cannot honestly be calculated. Do not reveal secrets from `.env`. Return a concise implementation plan and risks. Do not edit yet.

## Prompt 2 — Shared design system, shell, and themes

Read `design.md` and implement its design system directly in the existing Flask application.

- Match the screenshots in LIGHT mode as closely as practical: pale mint canvas `#E8FFF4`, white surfaces, soft mint panels, dark-green primary actions `#007A45`, small teal accents, Inter typography, subtle borders/shadows, 10–14px card radii, and generous spacing.
- Use the exact light tokens and dark tokens from `design.md`. Light colors must remain unchanged when adding dark mode.
- Dark mode should use the coordinated deep green-black canvas and forest-green surfaces in `design.md`, while retaining the same page layout, component shapes, spacing, and Inter font.
- Add an accessible theme toggle on authenticated and auth pages. Use explicit saved choice first, otherwise system preference; persist under `quizforge-theme`; avoid a flash of the wrong theme where practical.
- Build shared styles for navigation, buttons, cards, inputs, badges, tables, alerts, empty/loading states, focus rings, and disabled states. Reuse the existing stack; do not introduce a frontend framework without a strong reason.
- Responsive navigation must work without overlap at 320px, tablet, and desktop.
- Keep all links and forms connected to actual Flask endpoints. Do not add placeholder links or fake controls.
- Do not use global invert filters, heavy gradients, glassmorphism, coding-workspace layouts, terminal styling, or all-caps monospaced buttons.
- Do not add fabricated metrics or stock images.

Edit files directly, then list changed files and verification steps. Do not create a separate demo app.

## Prompt 3 — Implement all pages and connect to real routes

Using the shared design system and `design.md`, update the existing Jinja templates for Login, Register, Home/Generate Quiz, Quiz Taking, Results, Dashboard, and Recent Attempts if supported.

Match the screenshots' visual hierarchy and composition. Reuse the current route names, form fields, and template context. Preserve authentication, server-side validation, Gemini generation, scoring, and SQLite persistence.

Dashboard totals, average/best score, distinct topics, and attempt rows must come from the signed-in user's actual records. Use a consistent score definition, handle no attempts, and scope every query to the current user. Show streaks/topic accuracy only if accurately derived. Do not add unsupported SSO, notifications, institution-only fields, fake AI status, or sample metrics.

Keep answer keys server-side until submission. Use Jinja autoescaping; never mark AI-generated output safe. Preserve topic/difficulty/count on recoverable errors. Make tables usable on mobile and ensure every button/link performs a real action. Do not delete or weaken tests. Run the existing suite and fix regressions.

## Prompt 4 — Add the stopwatch end-to-end

Implement the count-up stopwatch from `design.md`. It is a stopwatch, not a countdown.

- Start timing when the quiz is presented/session begins, not on the generation form.
- Show “Time elapsed” near the quiz title/progress, format `MM:SS`, then `HH:MM:SS` after one hour.
- Derive elapsed time from a start timestamp; do not rely on incrementing a counter. Recalculate correctly after tab sleep/visibility changes.
- Preserve the start time across refresh only if the same active quiz session is restored. Ensure a new quiz/user cannot inherit the previous timer.
- Clear timer state after successful submit, cancellation, or new quiz.
- If the current flow supports it, send elapsed seconds as untrusted metadata. Validate it server-side and never use it for scoring.
- If adding `duration_seconds INTEGER NULL`, create a backward-compatible migration for existing SQLite databases using schema inspection and conditional `ALTER TABLE`. Never reset the database or erase history.
- Display duration on results when present; old rows with NULL duration must render normally.
- Prevent double-submit and avoid excessive screen-reader announcements.

Add tests for valid/missing/invalid duration, old-schema migration where relevant, result display, and unchanged scoring. Run the full suite and report exact results.

## Prompt 5 — Secure dashboard and history

Implement dashboard metrics and history from actual schema records only:
- total quiz attempts
- average and best score/percentage
- distinct topics explored
- recent attempts with topic, difficulty, score, percentage, date, and review link if the route supports it

Define score calculations consistently and handle empty data. Scope all reads and result-detail access to the authenticated user's ID. Add or update tests proving one user cannot see or review another user's attempts. Omit unsupported streaks, mastery, cohort comparisons, or invented AI claims.

## Prompt 6 — Final QA and deployment compatibility

Verify implementation against every acceptance item in `design.md`.

1. Run the complete existing test suite and report actual pass/fail output.
2. Verify all route names, forms, authentication guards, redirects, and links.
3. Verify light theme matches the reference screenshots; verify dark theme on all pages.
4. Verify theme preference persists across navigation/reload and defaults to system preference when unset.
5. Verify timer start, refresh, long duration format, submit, new quiz, missing/invalid duration, and results display.
6. Verify responsive behavior at 320px, tablet, desktop, keyboard navigation, focus visibility, and reduced motion.
7. Search for mock metrics, dead links, nonfunctional controls, exposed answer keys, unsafe `|safe`, secrets, `.env`, and committed database artifacts.
8. Confirm SQL is parameterized and attempt queries/details are user-scoped.
9. Verify Dockerfile/Jenkinsfile against the actual Jenkins agent OS. Do not change Windows/Linux commands blindly.
10. Fix issues without removing tests or overwriting unrelated user work. Never claim tests/build/deployment passed unless you ran them.

Final report must list changed files, implemented behavior, exact test results, remaining limitations, local run commands, and Docker/Jenkins verification steps.

## One-shot prompt

Read `design.md` and inspect the existing repository before editing. Implement the QuizForge AI redesign directly in the current Flask app, using the supplied four screenshots as the canonical LIGHT-theme visual reference. Faithfully reproduce the pale mint canvas, white rounded cards, dark-green actions/active nav, teal accents, Inter typography, spacing, dashboard metrics/history composition, centered register/login cards, home quiz-generation form, quiz screen, and results layout. Add the specified coordinated dark mode with persistent accessible theme toggle while keeping the light theme unchanged. Integrate all screens with the actual Flask routes, Flask-Login, Gemini generation, server-side scoring, and user-scoped SQLite history. Add a count-up stopwatch that starts when the quiz starts, survives refresh if that quiz session survives, safely records validated duration metadata, and displays it on results when available; use a backward-compatible database migration if needed. Do not fake dashboard metrics, add unsupported SSO/notifications, or create a coding editor/terminal interface. Preserve tests and Jenkins/Docker behavior. Run tests and fix regressions. Report changed files, exact test results, and limitations. Do not create a separate demo app or rewrite the backend unnecessarily.
