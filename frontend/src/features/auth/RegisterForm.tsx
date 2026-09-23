import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '../../components/Button'
import { ErrorMessage } from '../../components/ErrorMessage'
import { useAuth } from './AuthContext'

const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/

interface FieldErrors {
  email?: string
  displayName?: string
  password?: string
}

export function RegisterForm() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [password, setPassword] = useState('')
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({})
  const [formError, setFormError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  function validate(): boolean {
    const errors: FieldErrors = {}
    if (!EMAIL_PATTERN.test(email)) {
      errors.email = 'Enter a valid email address.'
    }
    if (displayName.trim().length === 0) {
      errors.displayName = 'Display name is required.'
    }
    if (password.length < 8) {
      errors.password = 'Password must be at least 8 characters.'
    }
    setFieldErrors(errors)
    return Object.keys(errors).length === 0
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)
    if (!validate()) {
      return
    }
    setSubmitting(true)
    try {
      await register(email, displayName.trim(), password)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Could not create your account.')
      setSubmitting(false)
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit} noValidate>
      <div className="field">
        <label htmlFor="register-email">Email</label>
        <input
          id="register-email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          aria-invalid={fieldErrors.email ? true : undefined}
          aria-describedby={fieldErrors.email ? 'register-email-error' : undefined}
        />
        {fieldErrors.email && (
          <p id="register-email-error" className="field-error">
            {fieldErrors.email}
          </p>
        )}
      </div>
      <div className="field">
        <label htmlFor="register-display-name">Display name</label>
        <input
          id="register-display-name"
          type="text"
          autoComplete="name"
          required
          value={displayName}
          onChange={(event) => setDisplayName(event.target.value)}
          aria-invalid={fieldErrors.displayName ? true : undefined}
          aria-describedby={fieldErrors.displayName ? 'register-display-name-error' : undefined}
        />
        {fieldErrors.displayName && (
          <p id="register-display-name-error" className="field-error">
            {fieldErrors.displayName}
          </p>
        )}
      </div>
      <div className="field">
        <label htmlFor="register-password">Password</label>
        <input
          id="register-password"
          type="password"
          autoComplete="new-password"
          required
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          aria-invalid={fieldErrors.password ? true : undefined}
          aria-describedby={fieldErrors.password ? 'register-password-error' : undefined}
        />
        {fieldErrors.password && (
          <p id="register-password-error" className="field-error">
            {fieldErrors.password}
          </p>
        )}
        <p className="field-hint">At least 8 characters.</p>
      </div>
      {formError && <ErrorMessage message={formError} />}
      <Button type="submit" disabled={submitting}>
        {submitting ? 'Creating account…' : 'Create account'}
      </Button>
    </form>
  )
}
