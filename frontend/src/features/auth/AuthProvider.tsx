import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { fetchCurrentUser, login as apiLogin, register as apiRegister } from '../../api/auth'
import { onUnauthorized } from '../../api/client'
import { clearToken, getToken, setToken } from '../../api/tokenStorage'
import type { User } from '../../types/user'
import { AuthContext, type AuthContextValue, type AuthStatus } from './AuthContext'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [status, setStatus] = useState<AuthStatus>('loading')

  // Restore the session from a persisted token on first load.
  useEffect(() => {
    let cancelled = false

    const token = getToken()
    if (!token) {
      setStatus('unauthenticated')
      return
    }

    fetchCurrentUser()
      .then((currentUser) => {
        if (!cancelled) {
          setUser(currentUser)
          setStatus('authenticated')
        }
      })
      .catch(() => {
        if (!cancelled) {
          clearToken()
          setUser(null)
          setStatus('unauthenticated')
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  // The API client calls this whenever any request comes back 401, e.g. an
  // expired token discovered mid-session.
  useEffect(() => {
    onUnauthorized(() => {
      setUser(null)
      setStatus('unauthenticated')
    })
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const token = await apiLogin({ email, password })
    setToken(token.access_token)
    const currentUser = await fetchCurrentUser()
    setUser(currentUser)
    setStatus('authenticated')
  }, [])

  const register = useCallback(
    async (email: string, displayName: string, password: string) => {
      await apiRegister({ email, display_name: displayName, password })
      await login(email, password)
    },
    [login],
  )

  const logout = useCallback(() => {
    clearToken()
    setUser(null)
    setStatus('unauthenticated')
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({ user, status, login, register, logout }),
    [user, status, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
