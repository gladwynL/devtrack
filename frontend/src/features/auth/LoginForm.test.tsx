import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { renderWithAuth, createAuthValue } from '../../test/utils'
import { LoginForm } from './LoginForm'

describe('LoginForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders email and password fields', () => {
    renderWithAuth(<LoginForm />, {
      authValue: createAuthValue({ status: 'unauthenticated', user: null }),
    })

    expect(screen.getByLabelText('Email')).toBeInTheDocument()
    expect(screen.getByLabelText('Password')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('calls login with the entered credentials on submit', async () => {
    const user = userEvent.setup()
    const login = vi.fn().mockResolvedValue(undefined)
    renderWithAuth(<LoginForm />, {
      authValue: createAuthValue({ status: 'unauthenticated', user: null, login }),
    })

    await user.type(screen.getByLabelText('Email'), 'alice@example.com')
    await user.type(screen.getByLabelText('Password'), 'password123')
    await user.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => {
      expect(login).toHaveBeenCalledWith('alice@example.com', 'password123')
    })
  })

  it('shows an error message when login fails', async () => {
    const user = userEvent.setup()
    const login = vi.fn().mockRejectedValue(new Error('Incorrect email or password.'))
    renderWithAuth(<LoginForm />, {
      authValue: createAuthValue({ status: 'unauthenticated', user: null, login }),
    })

    await user.type(screen.getByLabelText('Email'), 'alice@example.com')
    await user.type(screen.getByLabelText('Password'), 'wrong-password')
    await user.click(screen.getByRole('button', { name: /sign in/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Incorrect email or password.')
  })
})
