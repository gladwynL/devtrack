import { PRIORITY_WEIGHT, STATUS_WEIGHT } from '../../constants/issue'
import type { Issue, IssuePriority, IssueStatus } from '../../types/issue'

export interface IssueFilters {
  search: string
  status: IssueStatus | 'all'
  priority: IssuePriority | 'all'
  /** A user id, 'all', or 'unassigned'. */
  assigneeId: string
}

export type IssueSortOption = 'newest' | 'oldest' | 'priority' | 'status'

export const DEFAULT_ISSUE_FILTERS: IssueFilters = {
  search: '',
  status: 'all',
  priority: 'all',
  assigneeId: 'all',
}

export const DEFAULT_ISSUE_SORT: IssueSortOption = 'newest'

export function filterIssues(issues: Issue[], filters: IssueFilters): Issue[] {
  const query = filters.search.trim().toLowerCase()

  return issues.filter((issue) => {
    if (filters.status !== 'all' && issue.status !== filters.status) return false
    if (filters.priority !== 'all' && issue.priority !== filters.priority) return false

    if (filters.assigneeId === 'unassigned' && issue.assignee_id !== null) return false
    if (
      filters.assigneeId !== 'all' &&
      filters.assigneeId !== 'unassigned' &&
      issue.assignee_id !== filters.assigneeId
    ) {
      return false
    }

    if (query) {
      const haystack = `${issue.title} ${issue.description ?? ''}`.toLowerCase()
      if (!haystack.includes(query)) return false
    }

    return true
  })
}

function compareDates(a: string, b: string): number {
  return new Date(a).getTime() - new Date(b).getTime()
}

// created_at can tie (or, in tests, be identical strings); id is a stable
// final tiebreaker so sort order never depends on array/insertion order.
function compareIds(a: Issue, b: Issue): number {
  return a.id.localeCompare(b.id)
}

export function sortIssues(issues: Issue[], sort: IssueSortOption): Issue[] {
  const sorted = [...issues]

  switch (sort) {
    case 'newest':
      sorted.sort((a, b) => compareDates(b.created_at, a.created_at) || compareIds(a, b))
      break
    case 'oldest':
      sorted.sort((a, b) => compareDates(a.created_at, b.created_at) || compareIds(a, b))
      break
    case 'priority':
      sorted.sort(
        (a, b) =>
          PRIORITY_WEIGHT[b.priority] - PRIORITY_WEIGHT[a.priority] ||
          compareDates(b.created_at, a.created_at) ||
          compareIds(a, b),
      )
      break
    case 'status':
      sorted.sort(
        (a, b) =>
          STATUS_WEIGHT[a.status] - STATUS_WEIGHT[b.status] ||
          compareDates(b.created_at, a.created_at) ||
          compareIds(a, b),
      )
      break
  }

  return sorted
}
