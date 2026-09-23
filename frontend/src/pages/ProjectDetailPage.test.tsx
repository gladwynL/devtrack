import { render, screen, waitFor, within } from '@testing-library/react'
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

    const membersPanel = screen
      .getByRole('heading', { name: 'Members' })
      .closest('section') as HTMLElement
    expect(within(membersPanel).getByText('Alice Owner (you)')).toBeInTheDocument()
    expect(within(membersPanel).getByText('Bob Member')).toBeInTheDocument()

    const issueRow = screen.getByText('Fix login bug').closest('li') as HTMLElement
    expect(issueRow).toBeInTheDocument()
    expect(within(issueRow).getByText('To Do')).toBeInTheDocument()
    expect(within(issueRow).getByText('High')).toBeInTheDocument()
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
    const dialog = await screen.findByRole('dialog')
    await user.selectOptions(within(dialog).getByLabelText('Status'), 'done')
    await user.click(within(dialog).getByRole('button', { name: /save changes/i }))

    await waitFor(() => {
      expect(issuesApi.updateIssue).toHaveBeenCalledWith(
        'issue-1',
        expect.objectContaining({ status: 'done' }),
      )
    })
  })

  it('filters issues by search text', async () => {
    const user = userEvent.setup()
    vi.mocked(issuesApi.listProjectIssues).mockResolvedValue([
      buildIssues()[0],
      {
        ...buildIssues()[0],
        id: 'issue-2',
        title: 'Improve search speed',
        description: 'queries are slow',
      },
    ])

    renderProjectDetail(mockUser)
    await screen.findByText('Fix login bug')
    expect(screen.getByText('Improve search speed')).toBeInTheDocument()

    await user.type(screen.getByLabelText('Search issues'), 'login')

    expect(screen.getByText('Fix login bug')).toBeInTheDocument()
    expect(screen.queryByText('Improve search speed')).not.toBeInTheDocument()
  })

  it('filters issues by status', async () => {
    const user = userEvent.setup()
    vi.mocked(issuesApi.listProjectIssues).mockResolvedValue([
      buildIssues()[0],
      { ...buildIssues()[0], id: 'issue-2', title: 'Done already', status: 'done' },
    ])

    renderProjectDetail(mockUser)
    await screen.findByText('Fix login bug')

    await user.selectOptions(screen.getByLabelText('Status'), 'done')

    expect(screen.queryByText('Fix login bug')).not.toBeInTheDocument()
    expect(screen.getByText('Done already')).toBeInTheDocument()
  })

  it('sorts issues by oldest first', async () => {
    const user = userEvent.setup()
    vi.mocked(issuesApi.listProjectIssues).mockResolvedValue([
      {
        ...buildIssues()[0],
        id: 'issue-new',
        title: 'Newer issue',
        created_at: '2026-01-05T00:00:00Z',
      },
      {
        ...buildIssues()[0],
        id: 'issue-old',
        title: 'Older issue',
        created_at: '2026-01-01T00:00:00Z',
      },
    ])

    renderProjectDetail(mockUser)
    await screen.findByText('Newer issue')

    await user.selectOptions(screen.getByLabelText('Sort by'), 'oldest')

    const titles = screen.getAllByText(/(Newer|Older) issue/).map((el) => el.textContent)
    expect(titles).toEqual(['Older issue', 'Newer issue'])
  })

  it('shows issue activity with readable, resolved names', async () => {
    const user = userEvent.setup()
    vi.mocked(issuesApi.listIssueActivity).mockResolvedValue([
      {
        id: 'a1',
        issue_id: 'issue-1',
        actor_id: mockUser.id,
        event_type: 'created',
        field_name: null,
        old_value: null,
        new_value: null,
        created_at: '2026-01-01T00:00:00Z',
      },
      {
        id: 'a2',
        issue_id: 'issue-1',
        actor_id: otherUser.id,
        event_type: 'status_changed',
        field_name: 'status',
        old_value: 'todo',
        new_value: 'in_progress',
        created_at: '2026-01-02T00:00:00Z',
      },
    ])

    renderProjectDetail(mockUser)
    await screen.findByText('Fix login bug')

    await user.click(screen.getByRole('button', { name: /activity/i }))

    expect(await screen.findByText('Alice Owner created the issue')).toBeInTheDocument()
    expect(
      screen.getByText('Bob Member changed status from To Do to In Progress'),
    ).toBeInTheDocument()
  })

  it('shows an error state when activity fails to load', async () => {
    const user = userEvent.setup()
    vi.mocked(issuesApi.listIssueActivity).mockRejectedValue(new Error('Network error'))

    renderProjectDetail(mockUser)
    await screen.findByText('Fix login bug')

    await user.click(screen.getByRole('button', { name: /activity/i }))

    expect(await screen.findByRole('alert')).toBeInTheDocument()
  })

  it('requires confirmation before deleting an issue, and cancel keeps it', async () => {
    const user = userEvent.setup()
    renderProjectDetail(mockUser)
    await screen.findByText('Fix login bug')

    await user.click(screen.getByRole('button', { name: /^delete$/i }))
    expect(await screen.findByRole('heading', { name: 'Delete issue' })).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Cancel' }))

    expect(issuesApi.deleteIssue).not.toHaveBeenCalled()
    expect(screen.getByText('Fix login bug')).toBeInTheDocument()
  })

  it('deletes an issue after confirming', async () => {
    const user = userEvent.setup()
    vi.mocked(issuesApi.deleteIssue).mockResolvedValue(undefined)
    renderProjectDetail(mockUser)
    await screen.findByText('Fix login bug')

    await user.click(screen.getByRole('button', { name: /^delete$/i }))
    const dialog = await screen.findByRole('dialog')
    await user.click(within(dialog).getByRole('button', { name: 'Delete issue' }))

    await waitFor(() => {
      expect(issuesApi.deleteIssue).toHaveBeenCalledWith('issue-1')
    })
    expect(screen.queryByText('Fix login bug')).not.toBeInTheDocument()
  })

  it('lets the owner delete the project after confirming', async () => {
    const user = userEvent.setup()
    vi.mocked(projectsApi.deleteProject).mockResolvedValue(undefined)
    renderProjectDetail(mockUser)
    await screen.findByRole('heading', { name: 'DevTrack Core' })

    await user.click(screen.getByRole('button', { name: /delete project/i }))
    const dialog = await screen.findByRole('dialog')
    await user.click(within(dialog).getByRole('button', { name: 'Delete project' }))

    await waitFor(() => {
      expect(projectsApi.deleteProject).toHaveBeenCalledWith('project-1')
    })
    expect(await screen.findByText('Dashboard')).toBeInTheDocument()
  })

  it('hides the delete project control from a non-owner', async () => {
    renderProjectDetail(otherUser)
    await screen.findByRole('heading', { name: 'DevTrack Core' })

    expect(screen.queryByRole('button', { name: /delete project/i })).not.toBeInTheDocument()
  })
})
