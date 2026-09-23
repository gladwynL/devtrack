export type IssueActivityEventType =
  | 'created'
  | 'title_changed'
  | 'description_changed'
  | 'status_changed'
  | 'priority_changed'
  | 'assignee_changed'

export interface IssueActivity {
  id: string
  issue_id: string
  actor_id: string | null
  event_type: IssueActivityEventType
  field_name: string | null
  old_value: string | null
  new_value: string | null
  created_at: string
}
