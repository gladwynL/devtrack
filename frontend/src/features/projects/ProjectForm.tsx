import { useState, type FormEvent } from 'react'
import type { ProjectFormValues } from '../../types/project'
import { Button } from '../../components/Button'
import { ErrorMessage } from '../../components/ErrorMessage'

interface ProjectFormProps {
  initialValues?: ProjectFormValues
  submitLabel: string
  onSubmit: (values: ProjectFormValues) => Promise<void>
  onCancel?: () => void
}

/** Shared by project creation and project metadata editing. */
export function ProjectForm({ initialValues, submitLabel, onSubmit, onCancel }: ProjectFormProps) {
  const [name, setName] = useState(initialValues?.name ?? '')
  const [description, setDescription] = useState(initialValues?.description ?? '')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (name.trim().length === 0) {
      setError('Project name is required.')
      return
    }
    setError(null)
    setSubmitting(true)
    try {
      await onSubmit({
        name: name.trim(),
        description: description.trim() ? description.trim() : null,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save the project.')
      setSubmitting(false)
    }
  }

  return (
    <form className="stack-form" onSubmit={handleSubmit}>
      <div className="field">
        <label htmlFor="project-name">Name</label>
        <input
          id="project-name"
          type="text"
          required
          value={name}
          onChange={(event) => setName(event.target.value)}
        />
      </div>
      <div className="field">
        <label htmlFor="project-description">Description</label>
        <textarea
          id="project-description"
          rows={3}
          value={description}
          onChange={(event) => setDescription(event.target.value)}
        />
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
