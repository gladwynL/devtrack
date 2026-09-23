import { useState, type FormEvent } from 'react'
import type { IssueFormValues, IssuePriority, IssueStatus } from '../../types/issue'
import type { User } from '../../types/user'
import { Button } from '../../components/Button'
import { ErrorMessage } from '../../components/ErrorMessage'
import { PRIORITY_OPTIONS, STATUS_OPTIONS } from '../../constants/issue'

interface IssueFormProps {
  /** Candidate assignees — must be project members. */
  members: User[]
  initialValues?: IssueFormValues
  submitLabel: string
  onSubmit: (values: IssueFormValues) => Promise<void>
  onCancel?: () => void
}

export function IssueForm({
  members,
  initialValues,
  submitLabel,
  onSubmit,
  onCancel,
}: IssueFormProps) {
  const [title, setTitle] = useState(initialValues?.title ?? '')
  const [description, setDescription] = useState(initialValues?.description ?? '')
  const [status, setStatus] = useState<IssueStatus>(initialValues?.status ?? 'todo')
  const [priority, setPriority] = useState<IssuePriority>(initialValues?.priority ?? 'medium')
  const [assigneeId, setAssigneeId] = useState(initialValues?.assignee_id ?? '')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (title.trim().length === 0) {
      setError('Title is required.')
      return
    }
    setError(null)
    setSubmitting(true)
    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim() ? description.trim() : null,
        status,
        priority,
        assignee_id: assigneeId || null,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save issue.')
      setSubmitting(false)
    }
  }

  return (
    <form className="stack-form" onSubmit={handleSubmit}>
      <div className="field">
        <label htmlFor="issue-title">Title</label>
        <input
          id="issue-title"
          type="text"
          required
          value={title}
          onChange={(event) => setTitle(event.target.value)}
        />
      </div>
      <div className="field">
        <label htmlFor="issue-description">Description</label>
        <textarea
          id="issue-description"
          rows={4}
          value={description}
          onChange={(event) => setDescription(event.target.value)}
        />
      </div>
      <div className="field-row">
        <div className="field">
          <label htmlFor="issue-status">Status</label>
          <select
            id="issue-status"
            value={status}
            onChange={(event) => setStatus(event.target.value as IssueStatus)}
          >
            {STATUS_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="issue-priority">Priority</label>
          <select
            id="issue-priority"
            value={priority}
            onChange={(event) => setPriority(event.target.value as IssuePriority)}
          >
            {PRIORITY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="field">
        <label htmlFor="issue-assignee">Assignee</label>
        <select
          id="issue-assignee"
          value={assigneeId ?? ''}
          onChange={(event) => setAssigneeId(event.target.value)}
        >
          <option value="">Unassigned</option>
          {members.map((member) => (
            <option key={member.id} value={member.id}>
              {member.display_name}
            </option>
          ))}
        </select>
      </div>
      {error && <ErrorMessage message={error} />}
      <div className="form-actions">
        <Button type="submit" disabled={submitting}>
          {submitting ? 'Saving…' : submitLabel}
        </Button>
        {onCancel && (
          <Button type="button" variant="ghost" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  )
}
