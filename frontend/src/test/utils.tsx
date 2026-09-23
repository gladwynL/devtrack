import type { ReactElement } from 'react'
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { vi } from 'vitest'
import { AuthContext, type AuthContextValue } from '../features/auth/AuthContext'
import type { User } from '../types/user'

export const mockUser: User = {
  id: 'user-1',
  email: 'alice@example.com',
  display_name: 'Alice Owner',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

export function createAuthValue(overrides: Partial<AuthContextValue> = {}): AuthContextValue {
  return {
    user: mockUser,
    status: 'authenticated',
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    ...overrides,
  }
}

interface RenderWithAuthOptions {
  authValue?: AuthContextValue
  route?: string
}

/** Renders UI with a pre-set auth context (no real session restore), inside a router. */
export function renderWithAuth(ui: ReactElement, options: RenderWithAuthOptions = {}) {
  const { authValue = createAuthValue(), route = '/' } = options
  return render(
    <MemoryRouter initialEntries={[route]}>
      <AuthContext.Provider value={authValue}>{ui}</AuthContext.Provider>
    </MemoryRouter>,
  )
}
