import { useState } from 'react'

export default function TweetResult({ result }) {
  const [copied, setCopied] = useState(false)

  function copy() {
    navigator.clipboard.writeText(result.tweet)
    setCopied(true)
    setTimeout(() => setCopied(false), 1800)
  }

  const approved = result.evaluation === 'approved'
  const tweetCount = result.tweet_history?.length ?? 0
  const feedbackCount = result.feedback_history?.length ?? 0

  return (
    <div className="card">
      <p className="card-title">Backend Response</p>
      <div className="result-summary">
        <div className="result-stat">
          <span className="result-stat-label">Evaluation</span>
          <span className={`badge ${approved ? 'badge-approved' : 'badge-needs-improvement'}`}>
            {approved ? 'Approved' : 'Needs improvement'}
          </span>
        </div>
        <div className="result-stat">
          <span className="result-stat-label">Iteration</span>
          <span className="result-stat-value">{result.iteration}</span>
        </div>
        <div className="result-stat">
          <span className="result-stat-label">Tweets</span>
          <span className="result-stat-value">{tweetCount}</span>
        </div>
        <div className="result-stat">
          <span className="result-stat-label">Feedback rounds</span>
          <span className="result-stat-value">{feedbackCount}</span>
        </div>
      </div>

      <div style={{ marginTop: 18 }}>
        <p className="card-title">Final Tweet</p>
        <p className="tweet-text">{result.tweet}</p>
      </div>

      <div className="tweet-meta">
        <button className="copy-btn" onClick={copy}>
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>

      <div style={{ marginTop: 20, paddingTop: 18, borderTop: '1px solid var(--border)' }}>
        <p className="card-title">Evaluator Feedback</p>
        <p className="feedback-text">{result.feedback}</p>
      </div>
    </div>
  )
}
