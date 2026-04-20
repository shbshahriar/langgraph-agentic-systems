import { useState, useRef, useEffect } from 'react'
import TweetForm from '../components/TweetForm'
import TweetResult from '../components/TweetResult'
import HistoryPanel from '../components/HistoryPanel'
import { generateTweet } from '../services/api'

export default function Home() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const resultRef = useRef(null)

  useEffect(() => {
    if (result && resultRef.current) {
      resultRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, [result])

  async function handleSubmit(topic, maxIteration) {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const data = await generateTweet(topic, maxIteration)
      setResult(data)
    } catch (err) {
      setError(err.message || 'Something went wrong. Check the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <div className="header">
        <h1>Iterative Tweet Agent</h1>
        <p>Gemini writes. Claude evaluates. The frontend shows the backend response, iteration by iteration.</p>
      </div>

      <TweetForm onSubmit={handleSubmit} loading={loading} />

      {error && <div className="error-banner">{error}</div>}

      {result && (
        <div ref={resultRef}>
          <TweetResult result={result} />
          <HistoryPanel
            tweetHistory={result.tweet_history}
            feedbackHistory={result.feedback_history}
          />
        </div>
      )}
    </div>
  )
}
