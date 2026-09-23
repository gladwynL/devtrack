import { Link } from 'react-router-dom'
import { RegisterForm } from '../features/auth/RegisterForm'

export function RegisterPage() {
  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="brand">DevTrack</h1>
        <p className="muted">Create your account</p>
        <RegisterForm />
        <p className="auth-switch">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
