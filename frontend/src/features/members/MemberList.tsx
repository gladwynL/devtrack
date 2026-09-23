import type { Membership } from '../../types/membership'
import type { User } from '../../types/user'
import { Button } from '../../components/Button'

interface MemberListProps {
  members: Membership[]
  usersById: Map<string, User>
  currentUserId: string
  canManage: boolean
  onRemove: (userId: string) => void
  removingUserId: string | null
}

export function MemberList({
  members,
  usersById,
  currentUserId,
  canManage,
  onRemove,
  removingUserId,
}: MemberListProps) {
  return (
    <ul className="member-list">
      {members.map((member) => {
        const user = usersById.get(member.user_id)
        const isOwnerRole = member.role === 'owner'
        return (
          <li key={member.id} className="member-row">
            <div className="member-identity">
              <span className="member-name">
                {user ? user.display_name : 'Unknown user'}
                {member.user_id === currentUserId && ' (you)'}
              </span>
              {user && <span className="member-email">{user.email}</span>}
            </div>
            <div className="member-row-actions">
              <span className={`role-badge ${isOwnerRole ? 'role-owner' : 'role-member'}`}>
                {isOwnerRole ? 'Owner' : 'Member'}
              </span>
              {canManage && !isOwnerRole && (
                <Button
                  type="button"
                  variant="danger"
                  onClick={() => onRemove(member.user_id)}
                  disabled={removingUserId === member.user_id}
                >
                  {removingUserId === member.user_id ? 'Removing…' : 'Remove'}
                </Button>
              )}
            </div>
          </li>
        )
      })}
    </ul>
  )
}
