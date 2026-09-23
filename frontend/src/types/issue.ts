export type IssueStatus = 'todo' | 'in_progress' | 'done'
export type IssuePriority = 'low' | 'medium' | 'high' | 'critical'

export interface Issue {
  id: string
  project_id: string
  title: string
  description: string | null
  status: IssueStatus
  priority: IssuePriority
  assignee_id: string | null
  created_by_id: string
  created_at: string
  updated_at: string
}

/** Shape produced by the create/edit issue form; the API layer narrows this
 * to Partial<IssueFormValues> for updates. */
export interface IssueFormValues {
  title: string
  description: string | null
  status: IssueStatus
  priority: IssuePriority
  assignee_id: string | null
}
