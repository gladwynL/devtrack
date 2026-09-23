export type MembershipRole = 'owner' | 'member'

export interface Membership {
  id: string
  project_id: string
  user_id: string
  role: MembershipRole
  created_at: string
}
