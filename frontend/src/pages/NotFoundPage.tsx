import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <div className="not-found">
      <h1>Page not found</h1>
      <p>
        <Link to="/dashboard">Return to dashboard</Link>
      </p>
    </div>
  )
}
