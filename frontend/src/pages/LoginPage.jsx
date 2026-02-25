import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { setAuth } from '@/lib/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [mode, setMode] = useState('login') // 'login' | 'register'

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [regToken, setRegToken] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleLogin(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
      if (!res.ok) throw new Error(await res.text())
      const data = await res.json()
      setAuth(data.access_token, username)
      navigate(location.state?.from ?? '/', { replace: true })
    } catch {
      setError('Invalid username or password')
    } finally {
      setLoading(false)
    }
  }

  async function handleRegister(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, registration_token: regToken }),
      })
      if (!res.ok) {
        const text = await res.text()
        let msg = 'Registration failed'
        try { msg = JSON.parse(text).detail } catch { /* use default */ }
        throw new Error(msg)
      }
      setMode('login')
      setError(null)
      setPassword('')
      setRegToken('')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Earthborne Rangers</CardTitle>
          <CardDescription>
            {mode === 'login' ? 'Sign in to continue' : 'Create an account'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {mode === 'login' ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-1">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  autoComplete="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? 'Signing in…' : 'Sign in'}
              </Button>
              <p className="text-center text-sm text-muted-foreground">
                Need an account?{' '}
                <button
                  type="button"
                  className="underline hover:text-foreground"
                  onClick={() => { setMode('register'); setError(null) }}
                >
                  Register
                </button>
              </p>
            </form>
          ) : (
            <form onSubmit={handleRegister} className="space-y-4">
              <div className="space-y-1">
                <Label htmlFor="reg-username">Username</Label>
                <Input
                  id="reg-username"
                  autoComplete="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="reg-password">Password</Label>
                <Input
                  id="reg-password"
                  type="password"
                  autoComplete="new-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="reg-token">Invite token</Label>
                <Input
                  id="reg-token"
                  value={regToken}
                  onChange={(e) => setRegToken(e.target.value)}
                  required
                />
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? 'Creating account…' : 'Create account'}
              </Button>
              <p className="text-center text-sm text-muted-foreground">
                Already have an account?{' '}
                <button
                  type="button"
                  className="underline hover:text-foreground"
                  onClick={() => { setMode('login'); setError(null) }}
                >
                  Sign in
                </button>
              </p>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
