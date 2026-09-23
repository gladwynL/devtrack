import type { IssuePriority } from '../types/issue'

const LABELS: Record<IssuePriority, string> = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
  critical: 'Critical',
}

export function PriorityBadge({ priority }: { priority: IssuePriority }) {
  return <span className={`badge priority-${priority}`}>{LABELS[priority]}</span>
}
