import { PRIORITY_LABELS } from '../constants/issue'
import type { IssuePriority } from '../types/issue'

export function PriorityBadge({ priority }: { priority: IssuePriority }) {
  return <span className={`badge priority-${priority}`}>{PRIORITY_LABELS[priority]}</span>
}
