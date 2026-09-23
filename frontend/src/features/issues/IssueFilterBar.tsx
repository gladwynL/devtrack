import { PRIORITY_OPTIONS, STATUS_OPTIONS } from '../../constants/issue'
import type { IssuePriority, IssueStatus } from '../../types/issue'
import type { User } from '../../types/user'
import type { IssueFilters, IssueSortOption } from './issueFiltering'

interface IssueFilterBarProps {
  filters: IssueFilters
  onFiltersChange: (filters: IssueFilters) => void
  sort: IssueSortOption
  onSortChange: (sort: IssueSortOption) => void
  members: User[]
}

const SORT_OPTIONS: { value: IssueSortOption; label: string }[] = [
  { value: 'newest', label: 'Newest first' },
  { value: 'oldest', label: 'Oldest first' },
  { value: 'priority', label: 'Priority (high to low)' },
  { value: 'status', label: 'Status' },
]

export function IssueFilterBar({
  filters,
  onFiltersChange,
  sort,
  onSortChange,
  members,
}: IssueFilterBarProps) {
  return (
    <div className="issue-filter-bar">
      <div className="field issue-filter-search">
        <label htmlFor="issue-search">Search issues</label>
        <input
          id="issue-search"
          type="search"
          placeholder="Search by title or description"
          value={filters.search}
          onChange={(event) => onFiltersChange({ ...filters, search: event.target.value })}
        />
      </div>
      <div className="field">
        <label htmlFor="issue-filter-status">Status</label>
        <select
          id="issue-filter-status"
          value={filters.status}
          onChange={(event) =>
            onFiltersChange({ ...filters, status: event.target.value as IssueStatus | 'all' })
          }
        >
          <option value="all">All statuses</option>
          {STATUS_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>
      <div className="field">
        <label htmlFor="issue-filter-priority">Priority</label>
        <select
          id="issue-filter-priority"
          value={filters.priority}
          onChange={(event) =>
            onFiltersChange({ ...filters, priority: event.target.value as IssuePriority | 'all' })
          }
        >
          <option value="all">All priorities</option>
          {PRIORITY_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>
      <div className="field">
        <label htmlFor="issue-filter-assignee">Assignee</label>
        <select
          id="issue-filter-assignee"
          value={filters.assigneeId}
          onChange={(event) => onFiltersChange({ ...filters, assigneeId: event.target.value })}
        >
          <option value="all">Everyone</option>
          <option value="unassigned">Unassigned</option>
          {members.map((member) => (
            <option key={member.id} value={member.id}>
              {member.display_name}
            </option>
          ))}
        </select>
      </div>
      <div className="field">
        <label htmlFor="issue-sort">Sort by</label>
        <select
          id="issue-sort"
          value={sort}
          onChange={(event) => onSortChange(event.target.value as IssueSortOption)}
        >
          {SORT_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  )
}
