const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') ?? ''

export async function generateTweet(topic, maxIteration) {
  const response = await fetch(`${API_BASE_URL}/api/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, max_iteration: maxIteration }),
  })

  if (!response.ok) {
    let message = `Server error: ${response.status}`
    try {
      const err = await response.json()
      if (typeof err.detail === 'string') message = err.detail
    } catch (_) {}
    throw new Error(message)
  }

  return response.json()
}
