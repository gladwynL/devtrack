// A JWT bearer token has no server-set httpOnly cookie to live in for this
// architecture, so localStorage is the practical place to persist it across
// page refreshes. That carries the usual bearer-token/XSS caveat; isolating
// storage here keeps that tradeoff swappable in one place if this app later
// moves to a cookie-based session.
const STORAGE_KEY = 'devtrack.token'

export function getToken(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY)
  } catch {
    return null
  }
}

export function setToken(token: string): void {
  try {
    localStorage.setItem(STORAGE_KEY, token)
  } catch {
    // Storage may be unavailable (e.g. private browsing). The session
    // simply won't persist across refreshes in that case.
  }
}

export function clearToken(): void {
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch {
    // Ignore.
  }
}
