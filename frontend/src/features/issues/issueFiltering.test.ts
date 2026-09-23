import { describe, expect, it } from 'vitest'
import { DEFAULT_ISSUE_FILTERS, filterIssues, sortIssues } from './issueFiltering'
import type { Issue } from '../../types/issue'

function buildIssue(overrides: Partial<Issue> = {}): Issue {
  return {
    id: 'issue-1',
    project_id: 'project-1',
    title: 'Fix login bug',
    description: 'Users cannot sign in',
    status: 'todo',
    priority: 'medium',
    assignee_id: null,
    created_by_id: 'user-1',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  }
}

describe('filterIssues', () => {
  const issues = [
    buildIssue({
      id: 'a',
      title: 'Fix login bug',
      description: 'auth broken',
      status: 'todo',
      priority: 'high',
      assignee_id: null,
    }),
    buildIssue({
      id: 'b',
      title: 'Write onboarding docs',
      description: 'new user guide',
      status: 'in_progress',
      priority: 'low',
      assignee_id: 'user-2',
    }),
    buildIssue({
      id: 'c',
      title: 'Improve search speed',
      description: 'slow queries',
      status: 'done',
      priority: 'critical',
      assignee_id: 'user-2',
    }),
  ]

  it('matches search text against title', () => {
    const result = filterIssues(issues, { ...DEFAULT_ISSUE_FILTERS, search: 'login' })
    expect(result.map((i) => i.id)).toEqual(['a'])
  })

  it('matches search text against description', () => {
    const result = filterIssues(issues, { ...DEFAULT_ISSUE_FILTERS, search: 'slow queries' })
    expect(result.map((i) => i.id)).toEqual(['c'])
  })

  it('search is case-insensitive', () => {
    const result = filterIssues(issues, { ...DEFAULT_ISSUE_FILTERS, search: 'ONBOARDING' })
    expect(result.map((i) => i.id)).toEqual(['b'])
  })

  it('filters by status', () => {
    const result = filterIssues(issues, { ...DEFAULT_ISSUE_FILTERS, status: 'done' })
    expect(result.map((i) => i.id)).toEqual(['c'])
  })

  it('filters by priority', () => {
    const result = filterIssues(issues, { ...DEFAULT_ISSUE_FILTERS, priority: 'critical' })
    expect(result.map((i) => i.id)).toEqual(['c'])
  })

  it('filters by a specific assignee', () => {
    const result = filterIssues(issues, { ...DEFAULT_ISSUE_FILTERS, assigneeId: 'user-2' })
    expect(result.map((i) => i.id).sort()).toEqual(['b', 'c'])
  })

  it('filters to unassigned issues', () => {
    const result = filterIssues(issues, { ...DEFAULT_ISSUE_FILTERS, assigneeId: 'unassigned' })
    expect(result.map((i) => i.id)).toEqual(['a'])
  })

  it('combines multiple filters', () => {
    const result = filterIssues(issues, {
      search: 'search',
      status: 'done',
      priority: 'critical',
      assigneeId: 'user-2',
    })
    expect(result.map((i) => i.id)).toEqual(['c'])
  })

  it('returns everything when filters are at their defaults', () => {
    const result = filterIssues(issues, DEFAULT_ISSUE_FILTERS)
    expect(result).toHaveLength(3)
  })
})

describe('sortIssues', () => {
  const issues = [
    buildIssue({ id: 'a', status: 'todo', priority: 'low', created_at: '2026-01-01T00:00:00Z' }),
    buildIssue({
      id: 'b',
      status: 'done',
      priority: 'critical',
      created_at: '2026-01-03T00:00:00Z',
    }),
    buildIssue({
      id: 'c',
      status: 'in_progress',
      priority: 'high',
      created_at: '2026-01-02T00:00:00Z',
    }),
  ]

  it('sorts newest first by created_at', () => {
    expect(sortIssues(issues, 'newest').map((i) => i.id)).toEqual(['b', 'c', 'a'])
  })

  it('sorts oldest first by created_at', () => {
    expect(sortIssues(issues, 'oldest').map((i) => i.id)).toEqual(['a', 'c', 'b'])
  })

  it('sorts by priority, highest first', () => {
    expect(sortIssues(issues, 'priority').map((i) => i.id)).toEqual(['b', 'c', 'a'])
  })

  it('sorts by status in workflow order', () => {
    expect(sortIssues(issues, 'status').map((i) => i.id)).toEqual(['a', 'c', 'b'])
  })

  it('is deterministic for issues with identical timestamps (tiebreaks by id)', () => {
    const tied = [
      buildIssue({ id: 'z', created_at: '2026-01-01T00:00:00Z' }),
      buildIssue({ id: 'y', created_at: '2026-01-01T00:00:00Z' }),
    ]
    const first = sortIssues(tied, 'newest').map((i) => i.id)
    const second = sortIssues(tied, 'newest').map((i) => i.id)
    expect(first).toEqual(second)
    expect(first).toEqual(['y', 'z'])
  })

  it('does not mutate the input array', () => {
    const copy = [...issues]
    sortIssues(issues, 'oldest')
    expect(issues).toEqual(copy)
  })
})
