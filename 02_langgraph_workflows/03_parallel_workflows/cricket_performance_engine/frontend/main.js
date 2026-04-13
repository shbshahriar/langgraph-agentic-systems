// main.js

const API_URL = '/analyze-player';

// ── Role metadata ─────────────────────────────────────────────────────────────
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

// ── Helpers ───────────────────────────────────────────────────────────────────
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

// ── Pipeline stage animation ──────────────────────────────────────────────────
let stageTimer;

function startStages() {
  const stages = document.querySelectorAll('.stage');
  let idx = 0;
  stages[idx].classList.add('active');
  stageTimer = setInterval(() => {
    stages[idx].classList.remove('active');
    idx = (idx + 1) % stages.length;
    stages[idx].classList.add('active');
  }, 900);
}

function stopStages() {
  clearInterval(stageTimer);
  document.querySelectorAll('.stage').forEach(s => s.classList.remove('active'));
}

function setLoading(on) {
  document.getElementById('analyzeBtn').disabled = on;
  const spinner = document.getElementById('spinner');
  if (on) {
    spinner.classList.add('visible');
    startStages();
  } else {
    spinner.classList.remove('visible');
    stopStages();
  }
}

// ── Validate ──────────────────────────────────────────────────────────────────
function validate(fields) {
  const ids = ['runs', 'balls', 'fours', 'sixes', 'overs', 'runs_conceded', 'wickets'];
  ids.forEach(id => document.getElementById(id).classList.remove('error-field'));

  if (fields.balls <= 0 && fields.overs <= 0) {
    document.getElementById('balls').classList.add('error-field');
    document.getElementById('overs').classList.add('error-field');
    return 'Fill in at least one discipline: Balls Faced (batting) or Overs Bowled (bowling).';
  }

  for (const id of ids) {
    if (fields[id] === '' || isNaN(fields[id])) {
      document.getElementById(id).classList.add('error-field');
      return `Please fill in "${id.replace(/_/g, ' ')}".`;
    }
    if (fields[id] < 0) {
      document.getElementById(id).classList.add('error-field');
      return `"${id.replace(/_/g, ' ')}" cannot be negative.`;
    }
  }
  return null;
}

// ── Animate score ring ────────────────────────────────────────────────────────
function animateScore(score) {
  const arc          = document.getElementById('scoreArc');
  const numEl        = document.getElementById('impactScoreNum');
  const circumference = 339.29;

  arc.style.strokeDashoffset = circumference - (circumference * score / 100);

  let current = 0;
  const step  = score / 60;
  const timer = setInterval(() => {
    current = Math.min(current + step, score);
    numEl.textContent = Math.round(current);
    if (current >= score) clearInterval(timer);
  }, 16);
}

// ── Render role badge ─────────────────────────────────────────────────────────
function renderRole(role) {
  const meta  = ROLE_META[role] || { icon: '❓', label: role, desc: '' };
  const badge = document.getElementById('roleBadge');
  const desc  = document.getElementById('roleDesc');

  badge.textContent = `${meta.icon} ${meta.label}`;
  badge.className   = `role-badge role-${role}`;
  desc.textContent  = meta.desc;
}

// ── Render a metric card ──────────────────────────────────────────────────────
// Returns true if the card has data and was shown, false if hidden.
function renderMetricCard(cardId, rowsId, metrics, labelMap, insightId) {
  const card       = document.getElementById(cardId);
  const insightKey = cardId === 'battingCard' ? 'batting_insight' : 'bowling_insight';

  // Check if any real metric values exist (ignore the insight string)
  const hasMetrics = Object.keys(labelMap).some(k => metrics[k] !== undefined && metrics[k] !== null);

  if (!hasMetrics) {
    card.style.display = 'none';
    return false;
  }

  card.style.display = '';

  // Render stat rows
  const rows = document.getElementById(rowsId);
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

  // Render insight as markdown if present
  const insightEl   = document.getElementById(insightId);
  const insightText = metrics[insightKey];
  if (insightText) {
    insightEl.innerHTML    = marked.parse(insightText);
    insightEl.style.display = 'block';
  } else {
    insightEl.style.display = 'none';
  }

  return true;
}

// ── Render full results ───────────────────────────────────────────────────────
function renderResults(data) {
  animateScore(data.impact_score);
  renderRole(data.player_role);

  const hasBatting = renderMetricCard('battingCard', 'battingRows', data.batting_metrics, BATTING_LABELS, 'battingInsight');
  const hasBowling = renderMetricCard('bowlingCard', 'bowlingRows', data.bowling_metrics, BOWLING_LABELS, 'bowlingInsight');

  // Single card → full width
  const grid = document.getElementById('metricsGrid');
  grid.classList.toggle('full-width', !(hasBatting && hasBowling));

  // Final report rendered as markdown
  document.getElementById('finalReport').innerHTML = marked.parse(data.final_report);

  const results = document.getElementById('results');
  results.classList.add('visible');
  setTimeout(() => results.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function analyzePlayer() {
  clearError();

  const fields = {
    runs         : Number(getVal('runs')),
    balls        : Number(getVal('balls')),
    fours        : Number(getVal('fours')),
    sixes        : Number(getVal('sixes')),
    overs        : Number(getVal('overs')),
    runs_conceded: Number(getVal('runs_conceded')),
    wickets      : Number(getVal('wickets')),
  };

  const err = validate(fields);
  if (err) { showError(err); return; }

  document.getElementById('results').classList.remove('visible');
  setLoading(true);

  try {
    const res = await fetch(API_URL, {
      method : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify(fields),
    });

    if (!res.ok) {
      const e = await res.json().catch(() => ({}));
      throw new Error(e.detail || `Server error: ${res.status}`);
    }

    renderResults(await res.json());

  } catch (err) {
    showError(err.message);
  } finally {
    setLoading(false);
  }
}

// Enter key triggers analysis
document.addEventListener('keydown', e => {
  if (e.key === 'Enter') analyzePlayer();
});
