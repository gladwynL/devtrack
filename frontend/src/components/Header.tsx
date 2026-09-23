import { Link } from 'react-router-dom'
import { useAuth } from '../features/auth/AuthContext'
import { Button } from './Button'

export function Header() {
  const { user, logout } = useAuth()

  return (
    <header className="app-header">
      <Link to="/dashboard" className="brand">
        DevTrack
      </Link>
      {user && (
        <div className="header-user">
          <span className="header-user-name">{user.display_name}</span>
          <Button type="button" variant="ghost" onClick={logout}>
            Log out
          </Button>
        </div>
      )}
    </header>
  )
}
