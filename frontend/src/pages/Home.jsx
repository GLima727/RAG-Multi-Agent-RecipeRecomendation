import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { useAuth } from '../context/AuthContext'
import { MiseLogo } from '../components/MiseLogo'
import client from '../api/client'

const DIETARY_OPTIONS = [
  'Vegetarian',
  'Vegan',
  'Gluten-Free',
  'Dairy-Free',
  'Nut-Free',
  'Egg-Free',
  'Low-Carb',
  'Keto',
]

function Spinner() {
  return (
    <div className="flex items-center gap-3 text-cream-muted">
      <div className="w-5 h-5 border-2 border-saffron border-t-transparent rounded-full animate-spin" />
      <span>Finding the best recipes for you…</span>
    </div>
  )
}

export default function Home() {
  const { user, logout } = useAuth()
  const [selected, setSelected] = useState([])
  const [ingredients, setIngredients] = useState('')
  const [result, setResult] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const toggleRestriction = (option) => {
    setSelected((prev) =>
      prev.includes(option) ? prev.filter((o) => o !== option) : [...prev, option]
    )
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setResult('')
    setLoading(true)
    try {
      const { data } = await client.post('/recommend', {
        ingredients: ingredients.trim() || 'pantry staples',
        dietary_restrictions: selected.map((s) => s.toLowerCase()),
      })
      setResult(data.result)
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-charcoal flex flex-col">
      {/* Navbar */}
      <nav className="border-b border-charcoal-border bg-charcoal-light shrink-0">
        <div className="max-w-3xl mx-auto px-6 h-16 flex items-center justify-between">
          <MiseLogo size="sm" />
          <div className="flex items-center gap-3">
            <span className="text-cream-muted text-sm hidden sm:block truncate max-w-[200px]">
              {user}
            </span>
            <button
              onClick={logout}
              className="text-xs text-cream-muted hover:text-cream border border-charcoal-border hover:border-cream-subtle rounded-lg px-3 py-1.5 transition-colors"
            >
              Sign out
            </button>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="flex-1 max-w-3xl mx-auto w-full px-6 py-12">
        {/* Header */}
        <div className="mb-10">
          <h1 className="text-3xl font-serif text-cream mb-2">
            What's in your pantry?
          </h1>
          <p className="text-cream-muted text-sm">
            Tell us what you have and we'll find the perfect recipes.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-7">
          {/* Dietary restrictions */}
          <div>
            <label className="block text-xs font-medium text-cream-muted uppercase tracking-wider mb-3">
              Dietary restrictions
            </label>
            <div className="flex flex-wrap gap-2">
              {DIETARY_OPTIONS.map((option) => {
                const active = selected.includes(option)
                return (
                  <button
                    key={option}
                    type="button"
                    onClick={() => toggleRestriction(option)}
                    className={`px-3 py-1.5 rounded-full text-sm border transition-colors ${
                      active
                        ? 'bg-saffron border-saffron text-charcoal font-medium'
                        : 'border-charcoal-border text-cream-muted hover:border-cream-muted hover:text-cream'
                    }`}
                  >
                    {option}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Ingredients */}
          <div>
            <label className="block text-xs font-medium text-cream-muted uppercase tracking-wider mb-3">
              Available ingredients
            </label>
            <textarea
              value={ingredients}
              onChange={(e) => setIngredients(e.target.value)}
              placeholder="e.g. eggs, spinach, garlic, olive oil, parmesan…"
              rows={4}
              className="w-full bg-charcoal-light border border-charcoal-border rounded-xl px-4 py-3 text-cream placeholder-cream-subtle text-sm focus:outline-none focus:border-saffron transition-colors resize-none"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="bg-saffron hover:bg-saffron-dark text-charcoal font-semibold px-8 py-3 rounded-xl transition-colors disabled:opacity-60 disabled:cursor-not-allowed text-sm"
          >
            {loading ? 'Finding recipes…' : 'Find Recipes'}
          </button>
        </form>

        {/* Results */}
        {(result || loading || error) && (
          <div className="mt-12">
            <div className="h-px bg-charcoal-border mb-8" />

            {loading && <Spinner />}

            {error && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-red-400 text-sm">
                {error}
              </div>
            )}

            {result && (
              <div className="prose prose-invert max-w-none prose-headings:font-serif prose-headings:text-cream prose-p:text-cream-muted prose-li:text-cream-muted prose-strong:text-cream prose-hr:border-charcoal-border">
                <ReactMarkdown>{result}</ReactMarkdown>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
