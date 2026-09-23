import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../features/auth/AuthContext'
import { LoadingState } from './LoadingState'

export function ProtectedRoute() {
  const { status } = useAuth()

  if (status === 'loading') {
    return <LoadingState label="Loading your session…" />
  }
  if (status === 'unauthenticated') {
    return <Navigate to="/login" replace />
  }
  return <Outlet />
}
