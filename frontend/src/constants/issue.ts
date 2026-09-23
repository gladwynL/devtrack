import type { IssuePriority, IssueStatus } from '../types/issue'

export const STATUS_OPTIONS: { value: IssueStatus; label: string }[] = [
  { value: 'todo', label: 'To Do' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'done', label: 'Done' },
]

export const PRIORITY_OPTIONS: { value: IssuePriority; label: string }[] = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'critical', label: 'Critical' },
]

export const STATUS_LABELS: Record<IssueStatus, string> = {
  todo: 'To Do',
  in_progress: 'In Progress',
  done: 'Done',
}

export const PRIORITY_LABELS: Record<IssuePriority, string> = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
  critical: 'Critical',
}

/** Ordering weight for the "priority" and "status" sort options — higher sorts first for priority. */
export const PRIORITY_WEIGHT: Record<IssuePriority, number> = {
  low: 0,
  medium: 1,
  high: 2,
  critical: 3,
}

export const STATUS_WEIGHT: Record<IssueStatus, number> = {
  todo: 0,
  in_progress: 1,
  done: 2,
}
