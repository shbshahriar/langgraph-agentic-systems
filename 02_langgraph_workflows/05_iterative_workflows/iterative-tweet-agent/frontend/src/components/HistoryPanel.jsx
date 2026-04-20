import ReactMarkdown from 'react-markdown'

export default function HistoryPanel({ tweetHistory, feedbackHistory }) {
  if (!tweetHistory?.length) return null

  return (
    <div className="card">
      <p className="card-title">Iteration History</p>
      <div className="history-grid">
        <div>
          <p className="card-title" style={{ marginBottom: 10 }}>Tweets</p>
          <div className="history-list">
            {tweetHistory.map((tweet, i) => (
              <div className="history-item" key={i}>
                <p className="history-item-num">v{i + 1}</p>
                <div className="history-item-text markdown-body"><ReactMarkdown>{tweet}</ReactMarkdown></div>
              </div>
            ))}
          </div>
        </div>
        <div>
          <p className="card-title" style={{ marginBottom: 10 }}>Feedback</p>
          <div className="history-list">
            {feedbackHistory.map((fb, i) => (
              <div className="history-item" key={i}>
                <p className="history-item-num">v{i + 1}</p>
                <div className="history-item-text markdown-body"><ReactMarkdown>{fb}</ReactMarkdown></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
