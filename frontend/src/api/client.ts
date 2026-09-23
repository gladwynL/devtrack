import { clearToken, getToken } from './tokenStorage'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

type UnauthorizedListener = () => void
let unauthorizedListener: UnauthorizedListener | null = null

/** Called whenever a request is rejected with 401 (e.g. token expired). */
export function onUnauthorized(listener: UnauthorizedListener): void {
  unauthorizedListener = listener
}

interface PydanticValidationError {
  msg?: string
}

function extractErrorMessage(body: unknown, fallback: string): string {
  if (body && typeof body === 'object' && 'detail' in body) {
    const detail = (body as { detail: unknown }).detail
    if (typeof detail === 'string') {
      return detail
    }
    if (Array.isArray(detail)) {
      const messages = (detail as PydanticValidationError[])
        .map((item) => item.msg)
        .filter((msg): msg is string => Boolean(msg))
      if (messages.length > 0) {
        return messages.join(' ')
      }
    }
  }
  return fallback
}

interface RequestOptions {
  method?: string
  body?: unknown
  /** Set false for endpoints that must not send a stale/absent token, e.g. register/login. */
  auth?: boolean
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, auth = true } = options

  const headers = new Headers({ Accept: 'application/json' })
  if (body !== undefined) {
    headers.set('Content-Type', 'application/json')
  }
  if (auth) {
    const token = getToken()
    if (token) {
      headers.set('Authorization', `Bearer ${token}`)
    }
  }

  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new ApiError(0, 'Could not reach the server. Check your connection and try again.')
  }

  if (response.status === 204) {
    return undefined as T
  }

  const text = await response.text()
  let parsed: unknown = null
  if (text) {
    try {
      parsed = JSON.parse(text)
    } catch {
      parsed = null
    }
  }

  if (!response.ok) {
    if (response.status === 401 && auth) {
      clearToken()
      unauthorizedListener?.()
    }
    throw new ApiError(response.status, extractErrorMessage(parsed, response.statusText))
  }

  return parsed as T
}
