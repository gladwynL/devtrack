import { STATUS_LABELS } from '../constants/issue'
import type { IssueStatus } from '../types/issue'

export function StatusBadge({ status }: { status: IssueStatus }) {
  return <span className={`badge status-${status}`}>{STATUS_LABELS[status]}</span>
}
