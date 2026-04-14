/**
 * Call Claude API via Vite proxy to analyze reflection text.
 */
export async function analyzeReflection({ scores, win, improve }) {
  const prompt = `You are analyzing a daily self-reflection journal entry. Be concise and insightful.

The user scored themselves:
- Energy: ${scores.energy}/10
- Focus: ${scores.focus}/10
- Mood: ${scores.mood}/10

Their biggest win today: "${win || 'Not provided'}"
Their area to improve: "${improve || 'Not provided'}"

Respond in this exact JSON format, nothing else:
{
  "summary": "A 2-sentence overall assessment of their day combining scores and text responses.",
  "winHighlights": ["Key point 1 from their win (max 10 words)", "Key point 2 (max 10 words)"],
  "improveHighlights": ["Key area 1 to focus on (max 10 words)", "Key area 2 (max 10 words)"],
  "tags": ["Tag1", "Tag2", "Tag3"],
  "advice": "One sentence of actionable advice for tomorrow."
}`

  try {
    const res = await fetch('/api/claude/v1/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 300,
        messages: [{ role: 'user', content: prompt }],
      }),
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      console.warn('Claude API error:', res.status, err?.error?.message)
      return { error: err?.error?.message || `API error ${res.status}` }
    }

    const data = await res.json()
    const text = data.content?.[0]?.text || ''

    // Parse JSON from response
    const jsonMatch = text.match(/\{[\s\S]*\}/)
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0])
    }
    return null
  } catch (e) {
    console.warn('Claude API call failed:', e)
    return null
  }
}
