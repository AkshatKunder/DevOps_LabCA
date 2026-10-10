/* QuizGenius UI interactions */

// ── Sidebar toggle (mobile) ──────────────────────────────────
const sidebar  = document.getElementById('sidebar');
const overlay  = document.getElementById('sidebarOverlay');
const openBtn  = document.getElementById('mobileMenuBtn');

function openSidebar() {
  if (!sidebar) return;
  sidebar.classList.add('open');
  overlay.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeSidebar() {
  if (!sidebar) return;
  sidebar.classList.remove('open');
  overlay.classList.remove('active');
  document.body.style.overflow = '';
}

if (openBtn) openBtn.addEventListener('click', openSidebar);
if (overlay) overlay.addEventListener('click', closeSidebar);

// ── Topic chip → fill input ──────────────────────────────────
document.querySelectorAll('.topic-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    const input = document.getElementById('topic');
    if (input) {
      input.value = chip.dataset.topic;
      input.focus();
    }
  });
});

// ── Quiz form: loading overlay + prevent double-submit ───────
const quizForm    = document.getElementById('quizForm');
const loadingOverlay = document.getElementById('loadingOverlay');

if (quizForm) {
  quizForm.addEventListener('submit', function (e) {
    const topicInput = document.getElementById('topic');
    if (!topicInput || !topicInput.value.trim()) return; // HTML5 handles required

    if (loadingOverlay) loadingOverlay.classList.add('active');

    const btn = this.querySelector('button[type="submit"]');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span> Generating quiz...';
    }
  });
}

// ── Result form: confirm before submit ───────────────────────
const resultForm = document.getElementById('resultForm');
if (resultForm) {
  resultForm.addEventListener('submit', function (e) {
    const questions = this.querySelectorAll('.question-card');
    let allAnswered = true;

    questions.forEach((_, i) => {
      const radios = this.querySelectorAll(`input[name="question_${i}"]`);
      const checked = Array.from(radios).some(r => r.checked);
      if (!checked) allAnswered = false;
    });

    if (!allAnswered) {
      e.preventDefault();
      const msg = document.getElementById('validationMsg');
      if (msg) msg.classList.add('visible');
      // Scroll to first unanswered
      for (let i = 0; i < questions.length; i++) {
        const radios = this.querySelectorAll(`input[name="question_${i}"]`);
        const checked = Array.from(radios).some(r => r.checked);
        if (!checked) {
          questions[i].scrollIntoView({ behavior: 'smooth', block: 'center' });
          break;
        }
      }
      return;
    }

    // Confirmed
    const btn = this.querySelector('button[type="submit"]');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span> Submitting...';
    }
  });
}

// ── Score ring animation ─────────────────────────────────────
const scoreRing = document.getElementById('scoreRingFill');
if (scoreRing) {
  const pct = parseFloat(scoreRing.dataset.pct) || 0;
  const r   = 54; // radius
  const circ = 2 * Math.PI * r;
  scoreRing.style.strokeDasharray  = circ;
  scoreRing.style.strokeDashoffset = circ;
  // Delay for entrance
  requestAnimationFrame(() => {
    setTimeout(() => {
      scoreRing.style.strokeDashoffset = circ - (pct / 100) * circ;
      // Color by score
      if (pct >= 70) scoreRing.style.stroke = '#059669';
      else if (pct >= 40) scoreRing.style.stroke = '#D97706';
      else scoreRing.style.stroke = '#DC2626';
    }, 200);
  });

  // Also color the percentage text
  const pctEl = document.getElementById('scorePct');
  if (pctEl) {
    if (pct >= 70) pctEl.style.color = '#059669';
    else if (pct >= 40) pctEl.style.color = '#D97706';
    else pctEl.style.color = '#DC2626';
  }
}

// ── Progress bar animation ───────────────────────────────────
document.querySelectorAll('.perf-bar-fill[data-pct]').forEach(bar => {
  const pct = bar.dataset.pct;
  bar.style.width = '0%';
  setTimeout(() => { bar.style.width = pct + '%'; }, 300);
});
