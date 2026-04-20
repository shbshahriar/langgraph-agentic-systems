export default function TweetForm({ onSubmit, loading }) {
  function handleSubmit(e) {
    e.preventDefault()
    const form = e.target
    const topic = form.topic.value.trim()
    const maxIteration = parseInt(form.maxIteration.value, 10)
    if (topic) onSubmit(topic, maxIteration)
  }

  return (
    <div className="card">
      <p className="card-title">Generate Tweet</p>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="topic">Topic</label>
          <input
            id="topic"
            name="topic"
            type="text"
            placeholder="e.g. developers who debug in production"
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="maxIteration">Max Iterations</label>
          <input
            id="maxIteration"
            name="maxIteration"
            type="number"
            defaultValue={5}
            min={1}
            max={10}
          />
        </div>
        <button className="btn" type="submit" disabled={loading}>
          {loading ? 'Generating...' : 'Generate'}
        </button>
        {loading && (
          <div className="status">
            <div className="spinner" />
            Running the agent. Generating, evaluating, and refining the tweet...
          </div>
        )}
      </form>
    </div>
  )
}
