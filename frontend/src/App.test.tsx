import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import App from './App'

describe('App', () => {
  it('renders the DevTrack landing screen', () => {
    render(<App />)

    expect(screen.getByRole('heading', { name: 'DevTrack' })).toBeInTheDocument()
    expect(screen.getByText(/early development/i)).toBeInTheDocument()
  })
})
