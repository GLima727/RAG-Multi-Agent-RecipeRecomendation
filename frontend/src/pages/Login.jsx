import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { MiseLogo } from '../components/MiseLogo'
import client from '../api/client'

export default function Login() {
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const endpoint = mode === 'login' ? '/auth/login' : '/auth/register'
      const { data } = await client.post(endpoint, { email, password })
      login(data.access_token, email)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const switchMode = () => {
    setMode((m) => (m === 'login' ? 'register' : 'login'))
    setError('')
  }

  return (
    <div className="min-h-screen bg-charcoal flex items-center justify-center p-4">
      {/* Radial glow */}
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_40%,#242424,#1a1a1a)]" />

      <div className="relative w-full max-w-md">
        {/* Logo */}
        <div className="flex justify-center mb-10">
          <MiseLogo size="lg" />
        </div>

        {/* Card */}
        <div className="bg-charcoal-light rounded-2xl p-8 border border-charcoal-border shadow-2xl">
          <h1 className="text-2xl font-serif text-cream mb-1">
            {mode === 'login' ? 'Welcome back' : 'Create your account'}
          </h1>
          <p className="text-sm text-cream-muted mb-8">
            {mode === 'login'
              ? 'Sign in to get personalized recipe recommendations.'
              : 'Join Mise and start cooking smarter.'}
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-cream-muted uppercase tracking-wider mb-1.5">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@example.com"
                className="w-full bg-charcoal border border-charcoal-border rounded-lg px-4 py-3 text-cream placeholder-cream-subtle text-sm focus:outline-none focus:border-saffron transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-cream-muted uppercase tracking-wider mb-1.5">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="••••••••"
                className="w-full bg-charcoal border border-charcoal-border rounded-lg px-4 py-3 text-cream placeholder-cream-subtle text-sm focus:outline-none focus:border-saffron transition-colors"
              />
            </div>

            {error && (
              <p className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-saffron hover:bg-saffron-dark text-charcoal font-semibold py-3 rounded-lg transition-colors disabled:opacity-60 disabled:cursor-not-allowed mt-2 text-sm"
            >
              {loading
                ? 'Please wait…'
                : mode === 'login'
                ? 'Sign in'
                : 'Create account'}
            </button>
          </form>

          <p className="text-center text-cream-muted text-sm mt-6">
            {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
            <button
              onClick={switchMode}
              className="text-saffron hover:text-saffron-light transition-colors"
            >
              {mode === 'login' ? 'Create one' : 'Sign in'}
            </button>
          </p>
        </div>

        <p className="text-center text-cream-subtle text-xs mt-6 tracking-wide">
          AI-powered · mise en place
        </p>
      </div>
    </div>
  )
}
