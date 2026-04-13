// main.js
// Handles form submission, API call, rendering results, and theme toggle for CAPE.

const API_URL = '/analyze-player';

// ── Theme Toggle ─────────────────────────────────────────────────────────────
function toggleTheme() {
  const html      = document.documentElement;
  const isDark    = html.getAttribute('data-theme') === 'dark';
  const nextTheme = isDark ? 'light' : 'dark';

  html.setAttribute('data-theme', nextTheme);
  document.getElementById('toggleIcon').textContent  = isDark ? '🌙' : '☀️';
  document.getElementById('toggleLabel').textContent = isDark ? 'Dark Mode' : 'Light Mode';

  // Persist preference so it survives page refresh
  localStorage.setItem('cape-theme', nextTheme);
}

// Apply saved theme on load
(function () {
  const saved = localStorage.getItem('cape-theme');
  if (saved) {
    document.documentElement.setAttribute('data-theme', saved);
    if (saved === 'light') {
      document.getElementById('toggleIcon').textContent  = '🌙';
      document.getElementById('toggleLabel').textContent = 'Dark Mode';
    }
  }
})();

// ── Role metadata ────────────────────────────────────────────────────────────
// Maps backend role strings to display labels, icons, and descriptions.
const ROLE_META = {
  power_hitter: {
    icon : '💥',
    label: 'Power Hitter',
    desc : 'Explosive batsman who dominates through boundaries. High strike rate with significant boundary contribution.',
  },
  top_order_anchor: {
    icon : '⚓',
    label: 'Top Order Anchor',
    desc : 'Disciplined batsman who builds innings. Prioritises stability over aggression, rotating strike efficiently.',
  },
  economy_controller: {
    icon : '🎯',
    label: 'Economy Controller',
    desc : 'Miserly bowler who restricts runs. Excellent control and consistency, putting pressure on opposition batters.',
  },
  balanced_all_rounder: {
    icon : '⚖️',
    label: 'Balanced All-Rounder',
    desc : 'Contributes meaningfully with both bat and ball. A flexible asset across all formats of the game.',
  },
  death_over_specialist: {
    icon : '🔥',
    label: 'Death Over Specialist',
    desc : 'Performs under pressure in the final overs — either accelerating the run chase or defending tight totals.',
  },
};

// ── Metric display labels ────────────────────────────────────────────────────
const BATTING_LABELS = {
  strike_rate        : 'Strike Rate',
  boundary_ratio     : 'Boundary Ratio',
  dot_ball_percentage: 'Dot Ball %',
};

const BOWLING_LABELS = {
  economy_rate        : 'Economy Rate',
  bowling_average     : 'Bowling Average',
  bowling_strike_rate : 'Bowling Strike Rate',
};

// ── Helpers ──────────────────────────────────────────────────────────────────

function getVal(id) {
  return document.getElementById(id).value.trim();
}

function showError(msg) {
  const box = document.getElementById('errorBox');
  box.textContent = msg;
  box.classList.add('visible');
}

function clearError() {
  const box = document.getElementById('errorBox');
  box.textContent = '';
  box.classList.remove('visible');
}

function setLoading(on) {
  document.getElementById('analyzeBtn').disabled = on;
  document.getElementById('spinner').classList.toggle('visible', on);
}

// ── Validate inputs before sending ──────────────────────────────────────────
function validate(fields) {
  const ids = ['runs','balls','fours','sixes','overs','runs_conceded','wickets'];

  // Clear previous error highlights
  ids.forEach(id => document.getElementById(id).classList.remove('error-field'));

  // At least one discipline must be active
  if (fields.balls <= 0 && fields.overs <= 0) {
    document.getElementById('balls').classList.add('error-field');
    document.getElementById('overs').classList.add('error-field');
    return 'Fill in at least one discipline: Balls Faced (batting) or Overs Bowled (bowling).';
  }
  for (const id of ids) {
    if (fields[id] === '' || isNaN(fields[id])) {
      document.getElementById(id).classList.add('error-field');
      return `Please fill in "${id.replace('_', ' ')}".`;
    }
    if (fields[id] < 0) {
      document.getElementById(id).classList.add('error-field');
      return `"${id.replace('_', ' ')}" cannot be negative.`;
    }
  }
  return null;
}

// ── Animate the score ring and counter ──────────────────────────────────────
function animateScore(score) {
  const arc         = document.getElementById('scoreArc');
  const numEl       = document.getElementById('impactScoreNum');
  const circumference = 339.29;  // 2 * π * 54

  // Animate SVG ring fill
  const offset = circumference - (circumference * score / 100);
  arc.style.strokeDashoffset = offset;

  // Animate counter from 0 → score
  let current = 0;
  const step  = score / 60;  // ~60 frames
  const timer = setInterval(() => {
    current = Math.min(current + step, score);
    numEl.textContent = Math.round(current);
    if (current >= score) clearInterval(timer);
  }, 16);
}

// ── Render role badge ────────────────────────────────────────────────────────
function renderRole(role) {
  const meta   = ROLE_META[role] || { icon: '❓', label: role, desc: '' };
  const badge  = document.getElementById('roleBadge');
  const desc   = document.getElementById('roleDesc');

  badge.textContent = `${meta.icon} ${meta.label}`;
  badge.className   = `role-badge role-${role}`;
  desc.textContent  = meta.desc;
}

// ── Render a metrics card ────────────────────────────────────────────────────
function renderMetrics(containerId, metrics, labelMap, insightId) {
  const rows = document.getElementById(containerId);
  rows.innerHTML = '';

  for (const [key, label] of Object.entries(labelMap)) {
    const val = metrics[key];
    if (val === undefined || val === null) continue;

    const row = document.createElement('div');
    row.className = 'metric-row';
    row.innerHTML = `
      <span class="metric-key">${label}</span>
      <span class="metric-val">${typeof val === 'number' ? val.toFixed(2) : val}</span>
    `;
    rows.appendChild(row);
  }

  // Batting / bowling insight from LLM (stored inside the metrics dict)
  const insightKey = containerId.includes('batting') ? 'batting_insight' : 'bowling_insight';
  const insightText = metrics[insightKey];
  const insightEl = document.getElementById(insightId);
  if (insightText) {
    insightEl.textContent = insightText;
    insightEl.style.display = 'block';
  } else {
    insightEl.style.display = 'none';
  }
}

// ── Render full results panel ────────────────────────────────────────────────
function renderResults(data) {
  animateScore(data.impact_score);
  renderRole(data.player_role);

  renderMetrics('battingRows', data.batting_metrics, BATTING_LABELS, 'battingInsight');
  renderMetrics('bowlingRows', data.bowling_metrics, BOWLING_LABELS, 'bowlingInsight');

  document.getElementById('finalReport').textContent = data.final_report;

  const results = document.getElementById('results');
  results.classList.add('visible');

  // Smooth scroll to results
  setTimeout(() => {
    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 100);
}

// ── Main function ────────────────────────────────────────────────────────────
async function analyzePlayer() {
  clearError();

  // Collect field values
  const fields = {
    runs         : Number(getVal('runs')),
    balls        : Number(getVal('balls')),
    fours        : Number(getVal('fours')),
    sixes        : Number(getVal('sixes')),
    overs        : Number(getVal('overs')),
    runs_conceded: Number(getVal('runs_conceded')),
    wickets      : Number(getVal('wickets')),
  };

  // Validate
  const validationError = validate(fields);
  if (validationError) {
    showError(validationError);
    return;
  }

  // Hide old results, show spinner
  document.getElementById('results').classList.remove('visible');
  setLoading(true);

  try {
    const res = await fetch(API_URL, {
      method : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify(fields),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Server error: ${res.status}`);
    }

    const data = await res.json();
    renderResults(data);

  } catch (err) {
    showError(err.message);

  } finally {
    setLoading(false);
  }
}

// Allow Enter key to trigger analysis from any input field
document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') analyzePlayer();
});
