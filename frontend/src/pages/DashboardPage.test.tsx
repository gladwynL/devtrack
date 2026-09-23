import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { renderWithAuth, mockUser } from '../test/utils'
import * as projectsApi from '../api/projects'
import { ApiError } from '../api/client'
import type { Project } from '../types/project'
import { DashboardPage } from './DashboardPage'

vi.mock('../api/projects')

const project: Project = {
  id: 'project-1',
  name: 'DevTrack Core',
  description: 'Core tracker',
  owner_id: mockUser.id,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it("renders the signed-in user's projects", async () => {
    vi.mocked(projectsApi.listProjects).mockResolvedValue([project])

    renderWithAuth(<DashboardPage />)

    expect(await screen.findByText('DevTrack Core')).toBeInTheDocument()
    expect(screen.getByText('Owner')).toBeInTheDocument()
    expect(screen.getByText(/signed in as alice owner/i)).toBeInTheDocument()
  })

  it('shows an empty state when there are no projects', async () => {
    vi.mocked(projectsApi.listProjects).mockResolvedValue([])

    renderWithAuth(<DashboardPage />)

    expect(await screen.findByText('No projects yet')).toBeInTheDocument()
  })

  it('shows an error message when the project list fails to load', async () => {
    vi.mocked(projectsApi.listProjects).mockRejectedValue(new ApiError(500, 'Network error'))

    renderWithAuth(<DashboardPage />)

    expect(await screen.findByRole('alert')).toHaveTextContent('Network error')
  })

  it('creates a project through the modal form', async () => {
    const user = userEvent.setup()
    vi.mocked(projectsApi.listProjects).mockResolvedValue([])
    vi.mocked(projectsApi.createProject).mockResolvedValue({ ...project, id: 'new-project' })

    renderWithAuth(<DashboardPage />)
    await screen.findByText('No projects yet')

    await user.click(screen.getByRole('button', { name: /new project/i }))
    await user.type(screen.getByLabelText('Name'), 'New Project')
    await user.click(screen.getByRole('button', { name: /^create project$/i }))

    await waitFor(() => {
      expect(projectsApi.createProject).toHaveBeenCalledWith({
        name: 'New Project',
        description: null,
      })
    })
  })
})
