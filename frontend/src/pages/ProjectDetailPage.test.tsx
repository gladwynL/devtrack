import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthContext } from '../features/auth/AuthContext'
import { createAuthValue, mockUser } from '../test/utils'
import * as projectsApi from '../api/projects'
import * as membershipsApi from '../api/memberships'
import * as usersApi from '../api/users'
import * as issuesApi from '../api/issues'
import type { Project } from '../types/project'
import type { Membership } from '../types/membership'
import type { User } from '../types/user'
import type { Issue } from '../types/issue'
import { ProjectDetailPage } from './ProjectDetailPage'

vi.mock('../api/projects')
vi.mock('../api/memberships')
vi.mock('../api/users')
vi.mock('../api/issues')

const otherUser: User = {
  id: 'user-2',
  email: 'bob@example.com',
  display_name: 'Bob Member',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

function buildProject(overrides: Partial<Project> = {}): Project {
  return {
    id: 'project-1',
    name: 'DevTrack Core',
    description: 'Core tracker',
    owner_id: mockUser.id,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  }
}

function buildMembers(): Membership[] {
  return [
    {
      id: 'm1',
      project_id: 'project-1',
      user_id: mockUser.id,
      role: 'owner',
      created_at: '2026-01-01T00:00:00Z',
    },
    {
      id: 'm2',
      project_id: 'project-1',
      user_id: otherUser.id,
      role: 'member',
      created_at: '2026-01-01T00:00:00Z',
    },
  ]
}

function buildIssues(): Issue[] {
  return [
    {
      id: 'issue-1',
      project_id: 'project-1',
      title: 'Fix login bug',
      description: null,
      status: 'todo',
      priority: 'high',
      assignee_id: null,
      created_by_id: mockUser.id,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    },
  ]
}

function renderProjectDetail(authUser: User) {
  return render(
    <MemoryRouter initialEntries={['/projects/project-1']}>
      <AuthContext.Provider value={createAuthValue({ user: authUser })}>
        <Routes>
          <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
          <Route path="/dashboard" element={<div>Dashboard</div>} />
        </Routes>
      </AuthContext.Provider>
    </MemoryRouter>,
  )
}

beforeEach(() => {
  vi.resetAllMocks()
  vi.mocked(projectsApi.getProject).mockResolvedValue(buildProject())
  vi.mocked(membershipsApi.listMembers).mockResolvedValue(buildMembers())
  vi.mocked(usersApi.listUsers).mockResolvedValue([mockUser, otherUser])
  vi.mocked(issuesApi.listProjectIssues).mockResolvedValue(buildIssues())
})

describe('ProjectDetailPage', () => {
  it('shows a loading state before data arrives', () => {
    renderProjectDetail(mockUser)

    expect(screen.getByRole('status')).toBeInTheDocument()
  })

  it('renders project details, members, and issues', async () => {
    renderProjectDetail(mockUser)

    expect(await screen.findByRole('heading', { name: 'DevTrack Core' })).toBeInTheDocument()
    expect(screen.getByText('Core tracker')).toBeInTheDocument()
    expect(screen.getByText('Alice Owner (you)')).toBeInTheDocument()
    expect(screen.getByText('Bob Member')).toBeInTheDocument()
    expect(screen.getByText('Fix login bug')).toBeInTheDocument()
    expect(screen.getByText('To Do')).toBeInTheDocument()
    expect(screen.getByText('High')).toBeInTheDocument()
  })

  it('shows owner-only controls for the project owner', async () => {
    renderProjectDetail(mockUser)
    await screen.findByRole('heading', { name: 'DevTrack Core' })

    expect(screen.getByRole('button', { name: /edit project/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /add member/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /remove/i })).toBeInTheDocument()
  })

  it('hides owner-only controls from a regular member', async () => {
    renderProjectDetail(otherUser)
    await screen.findByRole('heading', { name: 'DevTrack Core' })

    expect(screen.queryByRole('button', { name: /edit project/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /add member/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /remove/i })).not.toBeInTheDocument()

    // Issue management remains available to any member.
    expect(screen.getByRole('button', { name: /new issue/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /^edit$/i })).toBeInTheDocument()
  })

  it('creates an issue through the modal form', async () => {
    const user = userEvent.setup()
    vi.mocked(issuesApi.createIssue).mockResolvedValue({
      id: 'issue-2',
      project_id: 'project-1',
      title: 'Write docs',
      description: null,
      status: 'todo',
      priority: 'medium',
      assignee_id: null,
      created_by_id: mockUser.id,
      created_at: '2026-01-02T00:00:00Z',
      updated_at: '2026-01-02T00:00:00Z',
    })

    renderProjectDetail(mockUser)
    await screen.findByRole('heading', { name: 'DevTrack Core' })

    await user.click(screen.getByRole('button', { name: /new issue/i }))
    await user.type(screen.getByLabelText('Title'), 'Write docs')
    await user.click(screen.getByRole('button', { name: /create issue/i }))

    await waitFor(() => {
      expect(issuesApi.createIssue).toHaveBeenCalledWith('project-1', {
        title: 'Write docs',
        description: null,
        status: 'todo',
        priority: 'medium',
        assignee_id: null,
      })
    })
    expect(await screen.findByText('Write docs')).toBeInTheDocument()
  })

  it('edits an existing issue', async () => {
    const user = userEvent.setup()
    vi.mocked(issuesApi.updateIssue).mockResolvedValue({ ...buildIssues()[0], status: 'done' })

    renderProjectDetail(mockUser)
    await screen.findByText('Fix login bug')

    await user.click(screen.getByRole('button', { name: /^edit$/i }))
    const statusSelect = await screen.findByLabelText('Status')
    await user.selectOptions(statusSelect, 'done')
    await user.click(screen.getByRole('button', { name: /save changes/i }))

    await waitFor(() => {
      expect(issuesApi.updateIssue).toHaveBeenCalledWith(
        'issue-1',
        expect.objectContaining({ status: 'done' }),
      )
    })
  })
})
