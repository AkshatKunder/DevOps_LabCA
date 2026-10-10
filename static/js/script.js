/* QuizGenius — UI interactions */

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
      btn.innerHTML = '<span class="spinner"></span> Generating quiz…';
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
      btn.innerHTML = '<span class="spinner"></span> Submitting…';
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

// ── LoanEase chat ────────────────────────────────────────────
const chatForm = document.getElementById('chatForm');
if (chatForm) {
  const input = document.getElementById('chatInput');
  const messages = document.getElementById('messages');
  const emptyState = document.getElementById('emptyState');
  const sendButton = document.getElementById('sendButton');
  const tips = [
    'Rate lock is guaranteed for 30 days.',
    'Paying EMIs on time can strengthen your CIBIL profile.',
    'A shorter tenure usually means less total interest paid.'
  ];
  let tipIndex = 0;

  const scrollToLatest = () => messages.scrollTo({ top: messages.scrollHeight, behavior: 'smooth' });
  const escapeHtml = (value) => value.replace(/[&<>'"]/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#039;', '"':'&quot;' }[char]));
  const actions = () => '<div class="message-actions"><button type="button" title="Copy message" aria-label="Copy message">📋</button><button type="button" title="Helpful" aria-label="Helpful">👍</button><button type="button" title="Not helpful" aria-label="Not helpful">👎</button></div>';
  const addMessage = (content, kind) => {
    if (emptyState) emptyState.remove();
    const row = document.createElement('article');
    row.className = `message-row ${kind}`;
    row.innerHTML = kind === 'assistant'
      ? `<div class="assistant-avatar" aria-hidden="true">₹</div><div class="message-wrap"><div class="message-bubble">${content}</div>${actions()}</div>`
      : `<div class="message-wrap"><div class="message-bubble">${escapeHtml(content)}</div>${actions()}</div>`;
    messages.appendChild(row);
    row.querySelectorAll('.message-actions button').forEach((button, index) => {
      if (index === 0) button.addEventListener('click', () => navigator.clipboard?.writeText(row.querySelector('.message-bubble').innerText));
      else button.addEventListener('click', () => button.classList.toggle('selected'));
    });
    scrollToLatest();
  };
  const responseFor = (question) => {
    const query = question.toLowerCase();
    if (query.includes('emi') || query.includes('monthly') || query.includes('calculate')) return `<p>For your ₹5,00,000 loan at 9.85% over 60 months, your estimated monthly EMI is:</p><div class="structured-card"><p class="structured-title">Monthly repayment estimate</p><div class="emi-highlight"><small>Estimated EMI</small><strong>₹10,579</strong></div><div class="rate-row"><span>Loan amount</span><b>₹5,00,000</b></div><div class="rate-row"><span>Total paid</span><b>₹6,34,740</b></div><div class="rate-row"><span>Total interest</span><b>₹1,34,740</b></div><label class="tenure-control">Tenure <input class="emi-slider" type="range" min="24" max="60" value="60" aria-label="Loan tenure in months"><output>60 months</output></label></div>`;
    if (query.includes('eligible') || query.includes('eligibility') || query.includes('approved')) return `<p>Great news — based on the profile on file, you are pre-approved.</p><div class="structured-card"><span class="status-approved">✓ APPROVED</span><ul class="eligibility-list"><li>CIBIL score: <b>720</b> · GOOD tier</li><li>Approved amount: <b>₹5,00,000</b></li><li>Available tenures: <b>24, 36, 48, or 60 months</b></li><li>Next: select a tenure, review the offer, and accept.</li></ul></div>`;
    if (query.includes('rate') || query.includes('interest')) return `<p>Your personalised interest rate is <b>9.85% p.a.</b> It includes your current CIBIL profile and selected loan tenure.</p><div class="structured-card"><div class="rate-card-head"><div class="rate-gauge" aria-label="Interest rate 9.85 percent"></div><div><p class="structured-title">Your personalised rate</p><p class="structured-sub">Locked risk spread for 30 days</p></div></div><div class="rate-row"><span>Base MCLR</span><b>8.85%</b></div><div class="rate-row"><span>Risk spread 🔒</span><b>1.00%</b></div><div class="rate-final"><span>Final rate</span><strong>9.85%</strong></div></div>`;
    if (query.includes('cibil') || query.includes('score')) return `<p>With a CIBIL score of <b>720</b>, you are in a strong position. Keep every EMI on time, avoid several hard credit checks in a short period, and maintain a low credit-utilisation ratio to support your score.</p>`;
    return `<p>I can help with your interest rate, EMI estimate, eligibility, and ways to strengthen your CIBIL score. What would you like to explore?</p>`;
  };
  const showResponse = (question) => {
    const loader = document.createElement('div'); loader.className = 'message-row assistant'; loader.innerHTML = '<div class="assistant-avatar" aria-hidden="true">₹</div><div class="message-bubble typing-indicator" aria-label="LoanEase is thinking"><i></i><i></i><i></i></div>';
    messages.appendChild(loader); scrollToLatest();
    window.setTimeout(() => { loader.remove(); addMessage(responseFor(question), 'assistant'); document.querySelectorAll('.emi-slider').forEach(slider => slider.addEventListener('input', () => slider.nextElementSibling.value = `${slider.value} months`)); }, 550);
  };
  const send = (text) => { const question = text.trim(); if (!question) return; addMessage(question, 'user'); input.value = ''; sendButton.disabled = true; showResponse(question); window.setTimeout(() => { sendButton.disabled = false; input.focus(); }, 600); };
  chatForm.addEventListener('submit', event => { event.preventDefault(); send(input.value); });
  document.querySelectorAll('[data-prompt]').forEach(button => button.addEventListener('click', () => send(button.dataset.prompt)));
  document.getElementById('tipButton')?.addEventListener('click', () => { tipIndex = (tipIndex + 1) % tips.length; document.getElementById('tipText').textContent = tips[tipIndex]; });
}
