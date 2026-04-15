// =============================================================================
// main.js — Frontend logic for the Parallel Writing Assessment Engine
//
// This file handles:
//   1. Word count update as the user types
//   2. Sending the POST /evaluate-writing request to the backend
//   3. Rendering the full response (scores, argument analysis, feedback)
//
// BACKEND URL: http://localhost:8000
// ENDPOINT:    POST /evaluate-writing
// =============================================================================

// Relative URL — works because FastAPI now serves both frontend and API
// from the same origin (http://localhost:8000). No cross-origin issues.
const API_URL = "/evaluate-writing";

// -----------------------------------------------------------------------------
// DOM REFERENCES
// Grab all elements we'll read from or write to during the session.
// -----------------------------------------------------------------------------

const textarea      = document.getElementById("writing-input");
const wordCountEl   = document.getElementById("word-count");
const submitBtn     = document.getElementById("submit-btn");
const statusBar     = document.getElementById("status-bar");
const statusMsg     = document.getElementById("status-msg");
const errorBanner   = document.getElementById("error-banner");
const resultsEl     = document.getElementById("results");

// Result sub-elements
const formatBadge   = document.getElementById("format-badge");
const finalScoreEl  = document.getElementById("final-score");
const scoresGrid    = document.getElementById("scores-grid");
const argTableBody  = document.getElementById("arg-table-body");
const strengthsList = document.getElementById("strengths-list");
const weaknessList  = document.getElementById("weakness-list");
const revisionList  = document.getElementById("revision-list");
const styleList     = document.getElementById("style-list");
const bandText      = document.getElementById("band-text");


// -----------------------------------------------------------------------------
// WORD COUNT — updates live as the user types
// -----------------------------------------------------------------------------

textarea.addEventListener("input", () => {
    const words = textarea.value.trim().split(/\s+/).filter(Boolean).length;
    wordCountEl.textContent = `${words} word${words !== 1 ? "s" : ""}`;
});


// -----------------------------------------------------------------------------
// SUBMIT — send text to backend and render response
// -----------------------------------------------------------------------------

submitBtn.addEventListener("click", async () => {
    const text = textarea.value.trim();

    // Basic client-side validation — backend also validates (min 10 chars)
    if (text.length < 10) {
        showError("Please enter at least 10 characters before submitting.");
        return;
    }

    // Reset UI state before new request
    hideError();
    hideResults();
    showStatus("Running parallel evaluation — this may take 10–20 seconds...");
    submitBtn.disabled = true;

    try {
        // -----------------------------------------------------------------
        // POST /evaluate-writing
        // Send the text as JSON, receive the full WritingResponse as JSON.
        // -----------------------------------------------------------------
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });

        // HTTP-level error (e.g. 422 Validation Error from FastAPI)
        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || `Server error: ${response.status}`);
        }

        const data = await response.json();

        // Application-level error (pipeline failed, returned error field)
        if (data.error) {
            throw new Error(data.error);
        }

        // Render the successful response
        renderResults(data);

    } catch (err) {
        showError(err.message || "An unexpected error occurred.");
    } finally {
        hideStatus();
        submitBtn.disabled = false;
    }
});


// -----------------------------------------------------------------------------
// RENDER — populate all result sections from the API response
//
// data shape (matches WritingResponse in schemas.py):
// {
//   format_type: "essay",
//   dimension_scores: {
//     language:    { grammar, clarity, vocabulary, tone },
//     structure:   { structure, coherence, depth },
//     argument:    { claim_presence, supporting_evidence, ... },
//     readability: float
//   },
//   argument_analysis: { claim_presence, supporting_evidence, ... },
//   final_score: 7.6,
//   feedback_report: {
//     strengths, weaknesses, revision_plan,
//     recommended_style_adjustments, target_band_prediction
//   }
// }
// -----------------------------------------------------------------------------

function renderResults(data) {

    // ── Format badge + final score ──────────────────────────────────────────
    formatBadge.textContent  = data.format_type;
    finalScoreEl.textContent = data.final_score.toFixed(1);


    // ── Dimension score cards ───────────────────────────────────────────────
    // Flatten all numeric scores from dimension_scores into one object.
    const ds = data.dimension_scores;

    const allScores = {
        ...ds.language,           // grammar, clarity, vocabulary, tone
        ...ds.structure,          // structure, coherence, depth
        readability: ds.readability,
    };

    scoresGrid.innerHTML = "";

    for (const [dim, score] of Object.entries(allScores)) {
        const pct = (score / 10) * 100;

        const card = document.createElement("div");
        card.className = "score-card";
        card.innerHTML = `
            <div class="dim-name">${dim}</div>
            <div class="dim-value">${score.toFixed(1)}<span> / 10</span></div>
            <div class="score-bar">
                <div class="score-bar-fill" style="width: ${pct}%"></div>
            </div>
        `;
        scoresGrid.appendChild(card);
    }


    // ── Argument analysis table ─────────────────────────────────────────────
    const arg = data.argument_analysis;
    argTableBody.innerHTML = "";

    const argRows = [
        ["Claim Presence",          formatBool(arg.claim_presence)],
        ["Supporting Evidence",     arg.supporting_evidence],
        ["Reasoning Quality",       arg.reasoning_quality],
        ["Counterargument Usage",   formatBool(arg.counterargument_usage)],
        ["Critical Thinking Depth", arg.critical_thinking_depth],
    ];

    for (const [label, value] of argRows) {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${label}</td><td class="value">${value}</td>`;
        argTableBody.appendChild(tr);
    }


    // ── Feedback report ─────────────────────────────────────────────────────
    const fb = data.feedback_report;

    renderList(strengthsList, fb.strengths);
    renderList(weaknessList,  fb.weaknesses);
    renderList(revisionList,  fb.revision_plan);
    renderList(styleList,     fb.recommended_style_adjustments);

    bandText.textContent = fb.target_band_prediction;


    // ── Show results section ────────────────────────────────────────────────
    resultsEl.classList.add("visible");
    resultsEl.scrollIntoView({ behavior: "smooth", block: "start" });
}


// -----------------------------------------------------------------------------
// HELPERS
// -----------------------------------------------------------------------------

function renderList(el, items) {
    el.innerHTML = "";
    for (const item of items) {
        const li = document.createElement("li");
        li.textContent = item;
        el.appendChild(li);
    }
}

function formatBool(val) {
    return val
        ? '<span class="badge-true">Yes</span>'
        : '<span class="badge-false">No</span>';
}

function showStatus(msg) {
    statusMsg.textContent = msg;
    statusBar.classList.add("visible");
}

function hideStatus() {
    statusBar.classList.remove("visible");
}

function showError(msg) {
    errorBanner.textContent = msg;
    errorBanner.classList.add("visible");
}

function hideError() {
    errorBanner.classList.remove("visible");
}

function hideResults() {
    resultsEl.classList.remove("visible");
}
