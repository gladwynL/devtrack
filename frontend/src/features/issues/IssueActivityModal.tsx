import { useEffect, useState } from 'react'
import { listIssueActivity } from '../../api/issues'
import { ApiError } from '../../api/client'
import type { IssueActivity } from '../../types/activity'
import type { User } from '../../types/user'
import { Modal } from '../../components/Modal'
import { LoadingState } from '../../components/LoadingState'
import { ErrorMessage } from '../../components/ErrorMessage'
import { EmptyState } from '../../components/EmptyState'
import { formatDateTime } from '../../utils/formatDate'
import { describeActivity } from './activityText'

interface IssueActivityModalProps {
  issueId: string
  issueTitle: string
  usersById: Map<string, User>
  onClose: () => void
}

export function IssueActivityModal({
  issueId,
  issueTitle,
  usersById,
  onClose,
}: IssueActivityModalProps) {
  const [activity, setActivity] = useState<IssueActivity[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setActivity(null)
    setError(null)

    listIssueActivity(issueId)
      .then((entries) => {
        if (!cancelled) setActivity(entries)
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof ApiError ? err.message : 'Could not load activity.')
      })

    return () => {
      cancelled = true
    }
  }, [issueId])

  return (
    <Modal title={`Activity — ${issueTitle}`} onClose={onClose}>
      {activity === null && !error && <LoadingState label="Loading activity…" />}
      {error && <ErrorMessage message={error} />}
      {activity !== null && activity.length === 0 && <EmptyState title="No activity yet" />}
      {activity !== null && activity.length > 0 && (
        <ul className="activity-list">
          {activity.map((entry) => (
            <li key={entry.id} className="activity-row">
              <span className="activity-text">{describeActivity(entry, usersById)}</span>
              <time className="activity-time" dateTime={entry.created_at}>
                {formatDateTime(entry.created_at)}
              </time>
            </li>
          ))}
        </ul>
      )}
    </Modal>
  )
}
