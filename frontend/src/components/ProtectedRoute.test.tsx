import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import { AuthContext } from '../features/auth/AuthContext'
import { createAuthValue, mockUser } from '../test/utils'
import { ProtectedRoute } from './ProtectedRoute'

function renderProtected(authValue: ReturnType<typeof createAuthValue>) {
  return render(
    <MemoryRouter initialEntries={['/secret']}>
      <AuthContext.Provider value={authValue}>
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/secret" element={<div>Secret content</div>} />
          </Route>
          <Route path="/login" element={<div>Login page</div>} />
        </Routes>
      </AuthContext.Provider>
    </MemoryRouter>,
  )
}

describe('ProtectedRoute', () => {
  it('shows a loading state while the session is being resolved', () => {
    renderProtected(createAuthValue({ status: 'loading', user: null }))

    expect(screen.getByRole('status')).toBeInTheDocument()
    expect(screen.queryByText('Secret content')).not.toBeInTheDocument()
  })

  it('redirects unauthenticated users to /login', () => {
    renderProtected(createAuthValue({ status: 'unauthenticated', user: null }))

    expect(screen.getByText('Login page')).toBeInTheDocument()
    expect(screen.queryByText('Secret content')).not.toBeInTheDocument()
  })

  it('renders the protected content for authenticated users', () => {
    renderProtected(createAuthValue({ status: 'authenticated', user: mockUser }))

    expect(screen.getByText('Secret content')).toBeInTheDocument()
  })
})
