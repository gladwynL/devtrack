import { PRIORITY_LABELS, STATUS_LABELS } from '../../constants/issue'
import type { IssuePriority, IssueStatus } from '../../types/issue'
import type { IssueActivity } from '../../types/activity'
import type { User } from '../../types/user'

function displayName(userId: string | null, usersById: Map<string, User>): string {
  if (!userId) return 'Someone'
  return usersById.get(userId)?.display_name ?? 'A former member'
}

/** Renders one activity entry as a plain-English sentence, resolving actor
 * and assignee ids to display names rather than showing raw UUIDs. */
export function describeActivity(activity: IssueActivity, usersById: Map<string, User>): string {
  const actor = displayName(activity.actor_id, usersById)

  switch (activity.event_type) {
    case 'created':
      return `${actor} created the issue`
    case 'title_changed':
      return `${actor} renamed the issue from "${activity.old_value}" to "${activity.new_value}"`
    case 'description_changed':
      return `${actor} updated the description`
    case 'status_changed':
      return `${actor} changed status from ${statusLabel(activity.old_value)} to ${statusLabel(activity.new_value)}`
    case 'priority_changed':
      return `${actor} changed priority from ${priorityLabel(activity.old_value)} to ${priorityLabel(activity.new_value)}`
    case 'assignee_changed': {
      const oldName = activity.old_value ? displayName(activity.old_value, usersById) : null
      const newName = activity.new_value ? displayName(activity.new_value, usersById) : null
      if (newName && oldName) return `${actor} reassigned the issue from ${oldName} to ${newName}`
      if (newName) return `${actor} assigned the issue to ${newName}`
      return `${actor} unassigned the issue`
    }
    default:
      return `${actor} updated the issue`
  }
}

function statusLabel(value: string | null): string {
  return value ? (STATUS_LABELS[value as IssueStatus] ?? value) : 'none'
}

function priorityLabel(value: string | null): string {
  return value ? (PRIORITY_LABELS[value as IssuePriority] ?? value) : 'none'
}
