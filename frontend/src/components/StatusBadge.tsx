import type { IssueStatus } from '../types/issue'

const LABELS: Record<IssueStatus, string> = {
  todo: 'To Do',
  in_progress: 'In Progress',
  done: 'Done',
}

export function StatusBadge({ status }: { status: IssueStatus }) {
  return <span className={`badge status-${status}`}>{LABELS[status]}</span>
}
