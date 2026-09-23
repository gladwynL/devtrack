import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { renderWithAuth, createAuthValue } from '../../test/utils'
import { RegisterForm } from './RegisterForm'

describe('RegisterForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('rejects a short password without calling the API', async () => {
    const user = userEvent.setup()
    const register = vi.fn()
    renderWithAuth(<RegisterForm />, {
      authValue: createAuthValue({ status: 'unauthenticated', user: null, register }),
    })

    await user.type(screen.getByLabelText('Email'), 'bob@example.com')
    await user.type(screen.getByLabelText('Display name'), 'Bob')
    await user.type(screen.getByLabelText('Password'), 'short')
    await user.click(screen.getByRole('button', { name: /create account/i }))

    expect(screen.getByText('Password must be at least 8 characters.')).toBeInTheDocument()
    expect(register).not.toHaveBeenCalled()
  })

  it('rejects an invalid email without calling the API', async () => {
    const user = userEvent.setup()
    const register = vi.fn()
    renderWithAuth(<RegisterForm />, {
      authValue: createAuthValue({ status: 'unauthenticated', user: null, register }),
    })

    await user.type(screen.getByLabelText('Email'), 'not-an-email')
    await user.type(screen.getByLabelText('Display name'), 'Bob')
    await user.type(screen.getByLabelText('Password'), 'password123')
    await user.click(screen.getByRole('button', { name: /create account/i }))

    expect(screen.getByText(/valid email/i)).toBeInTheDocument()
    expect(register).not.toHaveBeenCalled()
  })

  it('calls register with trimmed values on valid submission', async () => {
    const user = userEvent.setup()
    const register = vi.fn().mockResolvedValue(undefined)
    renderWithAuth(<RegisterForm />, {
      authValue: createAuthValue({ status: 'unauthenticated', user: null, register }),
    })

    await user.type(screen.getByLabelText('Email'), 'bob@example.com')
    await user.type(screen.getByLabelText('Display name'), '  Bob  ')
    await user.type(screen.getByLabelText('Password'), 'password123')
    await user.click(screen.getByRole('button', { name: /create account/i }))

    await waitFor(() => {
      expect(register).toHaveBeenCalledWith('bob@example.com', 'Bob', 'password123')
    })
  })

  it('shows an error message when registration fails', async () => {
    const user = userEvent.setup()
    const register = vi.fn().mockRejectedValue(new Error('A user with that email already exists.'))
    renderWithAuth(<RegisterForm />, {
      authValue: createAuthValue({ status: 'unauthenticated', user: null, register }),
    })

    await user.type(screen.getByLabelText('Email'), 'bob@example.com')
    await user.type(screen.getByLabelText('Display name'), 'Bob')
    await user.type(screen.getByLabelText('Password'), 'password123')
    await user.click(screen.getByRole('button', { name: /create account/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent(/already exists/i)
  })
})
