# QuizForge AI — Design System & Implementation Specification

**Version:** 2.0  
**Purpose:** Recreate the supplied QuizForge AI reference screenshots as a responsive, production-ready frontend integrated into the existing Flask quiz application. This document is the source of truth for visual design, interactions, accessibility, and backend integration.

## 1. Design direction

**Light mode is the canonical design and must faithfully match the four supplied QuizForge AI screenshots.** Dark mode is an additional, coordinated theme; it must not change or compromise the light theme.

Reference screens:
1. My Learning Dashboard
2. Create Your Account / Register
3. Home / Generate Quiz
4. Quiz Completed / Results

The visual identity is a friendly, polished learning platform: pale mint canvas, white cards, deep green actions, small teal accents, Inter typography, modest radii, soft borders/shadows, and generous spacing. Do not use the attached dark Developer Assessment Engine/coding-workspace style as the default, and do not introduce code editors, terminal panes, code-run controls, or dense developer-tooling layouts.

Build original implementation code based on the references. Preserve the existing Flask backend, authentication, Gemini integration, scoring, SQLite persistence, tests, and Jenkins/Docker deployment. Inspect the repository before editing. Adapt templates and CSS to real route names and context variables; do not create a disconnected demo or parallel backend.

Use the existing project stack. Prefer Jinja templates, CSS, and small amounts of JavaScript if that is the current architecture. Do not add a frontend framework without a clear technical reason. Do not fake analytics, AI status, streaks, SSO, or quiz history; use actual data or omit unsupported elements gracefully.

## 2. Screens and behavior

### A. Shared navigation
- Slim top bar on pale mint in light mode, with a subtle lower border/shadow.
- Left: small green shield/star brand mark and **QuizForge AI**.
- Navigation: **Home**, **My Dashboard**, **Topics**, **Recent Attempts**. Highlight the active supported route with a dark-green filled rounded rectangle and white text. Hide unsupported navigation features rather than adding dead links.
- Right: **AI Ready** chip only if status is real/known; notification control only if implemented; authenticated user's actual display name/avatar or initials and a working account/logout menu if supported.
- Responsive navigation must not overlap or clip. Collapse or horizontally adapt on small screens.
- Auth pages use a centered account card rather than the full dashboard shell if that matches the existing structure.

### B. Home / Generate Quiz
- Centered hero, small pale-green capability chip, prominent heading **“What would you like to learn today?”**, and short subtitle about generating quizzes.
- White rounded form card with subtle shadow and generous internal spacing.
- Topic field with persistent label and example placeholder; submit to the existing generation route.
- Question count selector with 5 / 10 / 15 only if supported by backend. Otherwise show the valid choices already supported.
- Difficulty selector Easy / Medium / Hard, mapped to backend-accepted values.
- Dark-green **Generate Quiz** primary action, loading/disabled state, no duplicate submissions.
- Suggested topic chips may fill the topic field. Use suggestions as examples, not claims of verified curricula.
- Optional lower recommended-learning section only if supported by actual features; do not add stock-photo cards just to fill space.
- Accessible validation/error messages; preserve input on recoverable failure.

### C. Register
- Centered narrow card on pale mint canvas, with green brand header, **Create your account**, concise subtitle, and restrained info banner.
- Keep fields aligned to the existing account model and registration route. Do not add academic handles, institutional-only requirements, SSO/ORCID buttons, or consent claims unless actually implemented.
- Labels above fields, useful placeholders, field-level errors, password visibility toggle if feasible, full-width dark-green submit button, and a working link to login.
- Preserve existing server-side validation and password hashing. Never claim unsupported security/accreditation promises.

### D. Login
- Same account-card visual system as Register: brand, clear heading, labeled email/password fields, show/hide password if feasible, primary submit, registration link, and accessible errors.
- No third-party sign-in buttons unless implemented.

### E. Dashboard
- Eyebrow/metadata line, **My Learning Dashboard**, personalized welcome text when user name is available.
- Actions such as **Full Log** and **Generate New Quiz** only when connected to real routes.
- Four metric cards, calculated from the signed-in user's persisted attempts:
  1. Total quizzes attempted
  2. Average score/percentage
  3. Best score/percentage
  4. Distinct topics explored
- Use a consistent definition for score and percentage. Handle zero attempts without division by zero.
- Recent attempts table/list with topic, difficulty, score, percentage, date/time, and a working review link only if the corresponding attempt route exists.
- Right-side streak/topic accuracy panels only if these values can be derived accurately from real stored records. Otherwise omit them or show another real-data section. Never hardcode the screenshot's sample values.
- Empty state for new users: friendly message and clear Generate Quiz action.
- Every dashboard/history query must be scoped to the current authenticated user.

### F. Quiz-taking screen
- Use the shared design system and existing quiz route/flow.
- Show topic/title, question progress (e.g. Question 2 of 10), progress bar, and difficulty when available.
- Preserve the existing question navigation pattern. If one-question-at-a-time is supported, style that step; otherwise style the current all-questions layout.
- Accessible radio inputs for single-choice answers with clear selected state and keyboard support.
- Selecting an answer must not submit the whole quiz. Keep answers while navigating between questions and preserve them on refresh only if the existing quiz session can safely be restored.
- Clear Previous / Next / Submit actions where supported, and prevent duplicate submissions.
- Keep correct answers server-side until submission. Do not embed answer keys in page source or client storage.
- Provide a practical warning before accidental navigation away from an in-progress quiz when feasible.

### G. Quiz stopwatch (required)
- Use a **count-up stopwatch**, not a countdown. Start when the quiz session begins/is presented, not on the topic-generation form.
- Show **Time elapsed** near quiz progress. Format as `MM:SS`, changing to `HH:MM:SS` after one hour.
- Stopwatch is informational: it must not auto-submit, expire, or penalize a quiz.
- Store one start timestamp per active quiz session and derive elapsed time from timestamps; do not depend on a counter incrementing once per second.
- Recalculate after tab sleep/visibility changes. Persist start time only for the active quiz using the existing session mechanism or a namespaced per-session client key. Do not mix users or quiz sessions.
- Clear timer state after successful submission, cancellation, or starting a new quiz.
- If supported safely by the current flow, submit elapsed seconds as non-authoritative metadata. The server must validate/coerce it and must never use it to calculate score.
- Prefer storing `duration_seconds INTEGER NULL` on quiz attempts if feasible. Existing rows may remain NULL. If adding the column, write a backward-compatible SQLite migration using `PRAGMA table_info` and conditional `ALTER TABLE`; do not recreate or delete the database.
- Show duration on the results page when available. Older attempts without duration must render normally.
- Avoid excessive screen-reader announcements; use an accessible timer label and restrained announcements.

### H. Results
- Completion banner with **Quiz completed!**, concise feedback, and working actions such as Try Another Quiz, Back to Home, and View in Dashboard when those routes exist.
- Performance snapshot with actual score, percentage, correct/incorrect/unanswered counts only when these can be computed from result data.
- Topic/difficulty/time summary, including stopwatch duration when available.
- Detailed question breakdown showing question, user's response, correct answer, correctness, and explanation only if supplied by the server after submission.
- Any progress/profile charts must reflect real data. Do not invent mastery scores, diagnoses, or cohort comparisons.
- Use Jinja autoescaping for questions, explanations, and user content; never mark model output safe.

## 3. Light-theme visual tokens — preserve the screenshot look

These tokens are the canonical light theme. Use them consistently; do not replace them with the attached dark slate palette.

| Token | Value | Intended use |
|---|---|---|
| `--page-bg` | `#E8FFF4` | Pale mint page canvas |
| `--surface` | `#FFFFFF` | Cards, inputs, menus |
| `--surface-soft` | `#DFF8ED` | Secondary panels, chips |
| `--surface-soft-2` | `#EAFBF4` | Hover and subtle fills |
| `--brand` | `#007A45` | Primary buttons, active nav |
| `--brand-hover` | `#00663A` | Primary hover |
| `--brand-strong` | `#006B3C` | Emphasis and progress |
| `--brand-tint` | `#DDF7EB` | Selected/soft green surfaces |
| `--teal` | `#61E8E5` | Rare accent/status |
| `--text` | `#102820` | Primary text |
| `--text-secondary` | `#52645C` | Body/supporting text |
| `--text-muted` | `#6B7B73` | Metadata/placeholders |
| `--border` | `#D8EAE1` | Borders/dividers |
| `--success` | `#13834D` | Success states |
| `--success-soft` | `#E0F7EB` | Success background |
| `--danger` | `#D92D20` | Errors/incorrect states |
| `--danger-soft` | `#FFF0EF` | Error background |
| `--warning` | `#B7791F` | Warning state |
| `--focus` | `#0E9F6E` | Focus ring |

The light theme must remain visually faithful to the references: mint canvas, white cards, dark green navigation/buttons, Inter, subtle edges, and the same component hierarchy. Minor implementation adjustments are allowed only for accessibility and responsive behavior.

## 4. Coordinated dark theme

Dark mode is a complementary QuizForge theme, not a copy of a coding IDE. Keep the same page layouts, card hierarchy, spacing, radii, and Inter typography; change surface/text colors for comfortable contrast.

| Token | Value | Intended use |
|---|---|---|
| `--page-bg` | `#0B1511` | Deep green-black canvas |
| `--surface` | `#12221A` | Cards and inputs |
| `--surface-soft` | `#1A3025` | Secondary panels |
| `--surface-soft-2` | `#203A2D` | Hover/subtle fills |
| `--brand` | `#20B875` | Primary buttons and active nav |
| `--brand-hover` | `#36CC89` | Hover |
| `--brand-strong` | `#45D493` | Emphasis/progress |
| `--brand-tint` | `#173F2D` | Selected/soft green surfaces |
| `--teal` | `#61E8E5` | Accent/status |
| `--text` | `#E9F7EF` | Primary text |
| `--text-secondary` | `#C1D5CA` | Supporting text |
| `--text-muted` | `#93AA9D` | Metadata/placeholders |
| `--border` | `#2A4537` | Borders/dividers |
| `--success` | `#45D493` | Success states |
| `--success-soft` | `#173F2D` | Success background |
| `--danger` | `#FF7770` | Error/incorrect states |
| `--danger-soft` | `#3C211F` | Error background |
| `--warning` | `#F2C66D` | Warning state |
| `--focus` | `#61E8E5` | Focus ring |

Implementation requirements:
- Define tokens in `:root` for light and `[data-theme="dark"]` for dark. Use tokens across all components; avoid hardcoded one-off colors.
- Provide a visible theme toggle on app and auth pages with accessible names **Switch to dark mode** / **Switch to light mode**.
- Prefer explicit saved choice in `localStorage` key `quizforge-theme`; if none, respect `prefers-color-scheme`.
- Persist choice across routes and reloads. Apply the theme early to avoid a flash where practical.
- Style forms, tables, badges, focus states, alerts, errors, disabled/loading states, quiz answers, and results in both themes.
- Do not use global invert filters. Do not change layout/typography when switching theme.

## 5. Typography, shape, spacing, and layout

- **Font:** Inter for all UI, matching the references. Use existing bundled font if present; otherwise use `Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`. Do not switch the light theme to JetBrains Mono or a developer-terminal typography system.
- Page title: approximately 30–34px desktop / 26–30px mobile. Section headings 18–22px, body 14–16px, metadata 11–13px.
- Spacing scale: 4, 8, 12, 16, 20, 24, 32, 40, 48px.
- Cards: 10–14px radius, subtle border and low shadow. Keep generous mint canvas around white cards.
- Buttons: 8px radius, generally 42–48px high, clear hover/focus/disabled states.
- Inputs: 44–48px minimum height, labels above fields, visible borders and focus rings.
- Use the existing icon library if available; otherwise small inline SVGs or consistent simple icons. Do not add a dependency only for icons unless necessary.
- Dashboard max width approximately 1280px; home content approximately 900px; auth card approximately 420–480px. Use fluid widths and 16–24px page gutters.
- Avoid heavy gradients, glassmorphism, neon glows, monospaced all-caps buttons, code-editor panes, terminal consoles, and coding-assessment UI. Those do not belong to the screenshot design.

## 6. Responsive behavior

- Desktop (>=1100px): four metric cards in one row; dashboard history panel with sidebar if useful.
- Tablet (700–1099px): metric cards in two columns; sidebar may stack.
- Mobile (<700px): single-column cards, compact/collapsible navigation, no horizontal page overflow, history table converted to stacked cards or contained scrolling, thumb-friendly quiz controls.
- Verify 320px viewport width and long topic/question/explanation strings.
- Respect reduced motion. Do not communicate status through color alone.

## 7. Existing backend and repository integration

Before editing, inspect `app/__init__.py`, `app/routes.py`, auth module/blueprint, database module, `ai.py`, templates, static assets, tests, `requirements.txt`, `.gitignore`, `Dockerfile`, and `Jenkinsfile`.

- Map every page to actual Flask routes, endpoint names, and template context variables before changing code.
- Preserve Flask-Login behavior and authentication guards.
- Use parameterized SQLite queries; scope dashboard and history queries to the current user's ID.
- Keep answer evaluation on the server; do not expose correct answers before submission.
- Validate topic, difficulty, question count, submitted answers, attempt ownership, and duration metadata server-side.
- Keep Gemini keys in environment variables/Jenkins credentials. Never place secrets in templates, JavaScript, or committed files.
- Use Jinja autoescaping; do not mark AI output safe.
- Preserve current test coverage and add tests for new behavior. Never remove or weaken tests to make the suite pass.
- `CREATE TABLE IF NOT EXISTS` does not add a new column to an existing SQLite table. Use a safe migration if adding `duration_seconds`.
- Keep Docker/Gunicorn and Jenkins working. Do not hardcode a developer's local absolute Python path unless the actual Jenkins agent requires it and this is verified.
- Never commit `.env`, `quiz_app.db`, virtual environments, caches, or generated local data.

## 8. Accessibility and quality

- Semantic headings and landmarks; persistent labels for form controls.
- Full keyboard support, visible focus rings, adequate contrast in both themes.
- Use real buttons for actions and links for navigation. No dead `href="#"` links.
- Use restrained live announcements for timer/progress; do not announce every second.
- Respect `prefers-reduced-motion`.
- Prevent accidental quiz loss where practical, but never block intentional submission.
- Provide loading, error, disabled, and empty states.

## 9. Acceptance checklist

- [ ] Light mode faithfully matches the supplied screenshots in palette, Inter typography, spacing, card composition, navigation, and page hierarchy.
- [ ] Dark mode is coordinated with the same green/mint identity and identical layout/typography.
- [ ] Theme toggle works on authenticated and auth pages and persists across routes/reloads.
- [ ] Login, registration, generation, answering, submission, scoring, results, and dashboard history still work.
- [ ] Stopwatch starts when the quiz starts, shows elapsed time, and duration appears on results when available.
- [ ] Dashboard data is real, consistent, and scoped to the signed-in user.
- [ ] No fabricated analytics, fake streaks, unsupported SSO, or nonfunctional controls.
- [ ] Existing tests and new relevant tests pass.
- [ ] Docker/Jenkins behavior remains functional.
- [ ] Responsive at 320px, tablet, and desktop; keyboard/focus checked in both themes.
- [ ] No secrets, database files, or local runtime artifacts committed.
