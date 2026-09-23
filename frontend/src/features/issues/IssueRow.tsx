import type { Issue } from '../../types/issue'
import type { User } from '../../types/user'
import { StatusBadge } from '../../components/StatusBadge'
import { PriorityBadge } from '../../components/PriorityBadge'
import { Button } from '../../components/Button'
import { formatDateTime } from '../../utils/formatDate'

interface IssueRowProps {
  issue: Issue
  assignee: User | null
  onEdit: () => void
  onDelete: () => void
  onViewActivity: () => void
  deleting: boolean
}

export function IssueRow({
  issue,
  assignee,
  onEdit,
  onDelete,
  onViewActivity,
  deleting,
}: IssueRowProps) {
  return (
    <li className="issue-row">
      <div className="issue-row-main">
        <span className="issue-title">{issue.title}</span>
        <span className="issue-assignee">{assignee ? assignee.display_name : 'Unassigned'}</span>
        <time className="issue-updated" dateTime={issue.updated_at}>
          Updated {formatDateTime(issue.updated_at)}
        </time>
      </div>
      <div className="issue-row-meta">
        <StatusBadge status={issue.status} />
        <PriorityBadge priority={issue.priority} />
      </div>
      <div className="issue-row-actions">
        <Button type="button" variant="secondary" onClick={onViewActivity}>
          Activity
        </Button>
        <Button type="button" variant="secondary" onClick={onEdit}>
          Edit
        </Button>
        <Button type="button" variant="danger" onClick={onDelete} disabled={deleting}>
          {deleting ? 'Deleting…' : 'Delete'}
        </Button>
      </div>
    </li>
  )
}
