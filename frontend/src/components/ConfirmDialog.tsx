import { useRef } from 'react'
import { Modal } from './Modal'
import { Button } from './Button'
import { ErrorMessage } from './ErrorMessage'

interface ConfirmDialogProps {
  title: string
  message: string
  confirmLabel?: string
  cancelLabel?: string
  /** Uses danger styling and defaults focus to Cancel instead of Confirm, so an accidental Enter/Space doesn't trigger it. */
  destructive?: boolean
  confirming?: boolean
  error?: string | null
  onConfirm: () => void
  onCancel: () => void
}

export function ConfirmDialog({
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  destructive = false,
  confirming = false,
  error = null,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const confirmRef = useRef<HTMLButtonElement>(null)
  const cancelRef = useRef<HTMLButtonElement>(null)

  return (
    <Modal title={title} onClose={onCancel} initialFocusRef={destructive ? cancelRef : confirmRef}>
      <p className="confirm-message">{message}</p>
      {error && <ErrorMessage message={error} />}
      <div className="form-actions">
        <Button
          ref={confirmRef}
          type="button"
          variant={destructive ? 'danger' : 'primary'}
          onClick={onConfirm}
          disabled={confirming}
        >
          {confirming ? 'Working…' : confirmLabel}
        </Button>
        <Button
          ref={cancelRef}
          type="button"
          variant="ghost"
          onClick={onCancel}
          disabled={confirming}
        >
          {cancelLabel}
        </Button>
      </div>
    </Modal>
  )
}
