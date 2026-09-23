import { Link } from 'react-router-dom'
import { LoginForm } from '../features/auth/LoginForm'

export function LoginPage() {
  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="brand">DevTrack</h1>
        <p className="muted">Sign in to your account</p>
        <LoginForm />
        <p className="auth-switch">
          Don&apos;t have an account? <Link to="/register">Create one</Link>
        </p>
      </div>
    </div>
  )
}
