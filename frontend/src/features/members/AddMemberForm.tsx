import { useMemo, useState, type FormEvent } from 'react'
import type { User } from '../../types/user'
import { Button } from '../../components/Button'
import { ErrorMessage } from '../../components/ErrorMessage'

interface AddMemberFormProps {
  /** Users not already members of this project. */
  candidates: User[]
  onAdd: (userId: string) => Promise<void>
}

export function AddMemberForm({ candidates, onAdd }: AddMemberFormProps) {
  const [query, setQuery] = useState('')
  const [selectedId, setSelectedId] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return candidates
    return candidates.filter(
      (candidate) =>
        candidate.display_name.toLowerCase().includes(q) ||
        candidate.email.toLowerCase().includes(q),
    )
  }, [candidates, query])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!selectedId) {
      setError('Choose a user to add.')
      return
    }
    setError(null)
    setSubmitting(true)
    try {
      await onAdd(selectedId)
      setSelectedId('')
      setQuery('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not add member.')
    } finally {
      setSubmitting(false)
    }
  }

  if (candidates.length === 0) {
    return <p className="muted">Every registered user is already a member of this project.</p>
  }

  return (
    <form className="stack-form" onSubmit={handleSubmit}>
      <div className="field">
        <label htmlFor="member-search">Search users</label>
        <input
          id="member-search"
          type="text"
          placeholder="Search by name or email"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
      </div>
      <div className="field">
        <label htmlFor="member-select">User</label>
        <select
          id="member-select"
          required
          value={selectedId}
          onChange={(event) => setSelectedId(event.target.value)}
        >
          <option value="">Select a user…</option>
          {filtered.map((candidate) => (
            <option key={candidate.id} value={candidate.id}>
              {candidate.display_name} ({candidate.email})
            </option>
          ))}
        </select>
      </div>
      {error && <ErrorMessage message={error} />}
      <div className="form-actions">
        <Button type="submit" disabled={submitting}>
          {submitting ? 'Adding…' : 'Add member'}
        </Button>
      </div>
    </form>
  )
}
