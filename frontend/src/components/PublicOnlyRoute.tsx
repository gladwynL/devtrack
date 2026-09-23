import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../features/auth/AuthContext'
import { LoadingState } from './LoadingState'

/** Keeps already-authenticated users off /login and /register. */
export function PublicOnlyRoute() {
  const { status } = useAuth()

  if (status === 'loading') {
    return <LoadingState label="Loading your session…" />
  }
  if (status === 'authenticated') {
    return <Navigate to="/dashboard" replace />
  }
  return <Outlet />
}
